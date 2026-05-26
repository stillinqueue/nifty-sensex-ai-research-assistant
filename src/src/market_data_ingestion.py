"""
Market data ingestion pipeline.

This module loads the configured market universe, selects the active
production data provider, downloads instrument metadata, maps symbols to
provider identifiers, pulls historical OHLCV data, and stores raw outputs.

Supported provider architecture:
- Zerodha Kite Connect
- Groww API
- NSE/BSE licensed provider

Current fully implemented provider:
- Zerodha Kite Connect
"""

from __future__ import annotations

import argparse
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from src.config import AppConfig, ensure_project_directories, get_config
from src.instrument_master import (
    enrich_with_zerodha_tokens,
    load_market_universe,
    save_reference_universe,
    universe_indices_to_dataframe,
    universe_stocks_to_dataframe,
)
from src.market_data_provider import HistoricalDataRequest, MarketDataProvider
from src.provider_factory import get_market_data_provider


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def safe_file_name(value: str) -> str:
    """
    Convert a symbol or label into a safe file name.

    Parameters
    ----------
    value:
        Input string.

    Returns
    -------
    str
        File-system-safe string.
    """

    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save a dataframe to CSV.

    Parameters
    ----------
    df:
        Dataframe to save.
    output_path:
        Output path.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved %s rows to %s", len(df), output_path)


def download_and_save_instrument_master(
    provider: MarketDataProvider,
    config: AppConfig,
) -> pd.DataFrame:
    """
    Download and save provider instrument master.

    Parameters
    ----------
    provider:
        Configured market data provider.
    config:
        Application configuration.

    Returns
    -------
    pd.DataFrame
        Provider instrument master dataframe.
    """

    logger.info("Downloading instrument master from provider: %s", provider.provider_name)

    instruments_df = provider.get_instruments()

    if instruments_df.empty:
        logger.warning("Instrument master returned no rows.")
    else:
        logger.info("Instrument master rows downloaded: %s", len(instruments_df))

    output_path = (
        config.reference_data_dir
        / f"{provider.provider_name}_instrument_master.csv"
    )

    save_dataframe(instruments_df, output_path)

    return instruments_df


def build_enriched_universe(
    config: AppConfig,
    provider: MarketDataProvider,
    instruments_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Load configured universe and enrich it with provider-specific identifiers.

    Parameters
    ----------
    config:
        Application configuration.
    provider:
        Market data provider.
    instruments_df:
        Optional provider instrument master dataframe.

    Returns
    -------
    pd.DataFrame
        Enriched stock universe dataframe.
    """

    logger.info("Loading configured market universe.")

    universe = load_market_universe(config)
    stocks_df = universe_stocks_to_dataframe(universe)
    indices_df = universe_indices_to_dataframe(universe)

    config.reference_data_dir.mkdir(parents=True, exist_ok=True)

    save_dataframe(stocks_df, config.reference_data_dir / "stock_universe_configured.csv")
    save_dataframe(indices_df, config.reference_data_dir / "index_universe_configured.csv")

    enriched_stocks_df = stocks_df.copy()

    if provider.provider_name == "zerodha_kite":
        if instruments_df is None or instruments_df.empty:
            raise ValueError(
                "Zerodha instrument master is required to enrich stock universe."
            )

        logger.info("Enriching stock universe with Zerodha instrument tokens.")
        enriched_stocks_df = enrich_with_zerodha_tokens(stocks_df, instruments_df)

    output_path = config.reference_data_dir / "stock_universe_enriched.csv"
    save_dataframe(enriched_stocks_df, output_path)

    return enriched_stocks_df


def iter_stocks_for_ingestion(
    enriched_universe_df: pd.DataFrame,
    symbols: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Filter enriched stock universe for ingestion.

    Parameters
    ----------
    enriched_universe_df:
        Enriched universe dataframe.
    symbols:
        Optional iterable of symbols to ingest. If None, ingest all rows.

    Returns
    -------
    pd.DataFrame
        Filtered universe dataframe.
    """

    if symbols is None:
        return enriched_universe_df

    requested = {symbol.upper().strip() for symbol in symbols}

    filtered = enriched_universe_df[
        enriched_universe_df["symbol"].astype(str).str.upper().isin(requested)
    ]

    missing = requested - set(filtered["symbol"].astype(str).str.upper())

    if missing:
        logger.warning("Requested symbols not found in universe: %s", sorted(missing))

    return filtered


def ingest_historical_ohlcv_for_stocks(
    provider: MarketDataProvider,
    config: AppConfig,
    enriched_universe_df: pd.DataFrame,
    start_datetime: datetime,
    end_datetime: datetime,
    interval: str = "day",
    symbols: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Ingest historical OHLCV candles for configured stock universe.

    Parameters
    ----------
    provider:
        Configured market data provider.
    config:
        Application configuration.
    enriched_universe_df:
        Enriched stock universe dataframe.
    start_datetime:
        Historical start datetime.
    end_datetime:
        Historical end datetime.
    interval:
        Candle interval. For Zerodha, examples include day, minute, 5minute.
    symbols:
        Optional list of symbols. If None, ingest all configured stocks.

    Returns
    -------
    pd.DataFrame
        Combined historical OHLCV dataframe.
    """

    selected_df = iter_stocks_for_ingestion(enriched_universe_df, symbols)

    if selected_df.empty:
        raise ValueError("No stocks selected for ingestion.")

    output_dir = config.raw_data_dir / "ohlcv" / interval
    output_dir.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []

    for _, row in selected_df.iterrows():
        symbol = str(row["nse_symbol"]).strip()
        exchange = "NSE"

        instrument_token = row.get("instrument_token")

        if pd.isna(instrument_token):
            logger.warning(
                "Skipping %s because instrument_token is missing. "
                "Refresh or enrich the instrument master first.",
                symbol,
            )
            continue

        try:
            instrument_token_int = int(instrument_token)
        except ValueError:
            logger.warning("Skipping %s due to invalid instrument_token: %s", symbol, instrument_token)
            continue

        logger.info(
            "Downloading OHLCV for %s | exchange=%s | interval=%s | token=%s",
            symbol,
            exchange,
            interval,
            instrument_token_int,
        )

        request = HistoricalDataRequest(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            instrument_token=instrument_token_int,
        )

        try:
            ohlcv_df = provider.get_historical_data(request)
        except Exception as exc:
            logger.exception("Failed to download OHLCV for %s: %s", symbol, exc)
            continue

        if ohlcv_df.empty:
            logger.warning("No OHLCV rows returned for %s", symbol)
            continue

        file_name = f"{safe_file_name(symbol)}_{interval}.csv"
        output_path = output_dir / file_name

        save_dataframe(ohlcv_df, output_path)

        frames.append(ohlcv_df)

    if not frames:
        logger.warning("No OHLCV data downloaded.")
        return pd.DataFrame()

    combined_df = pd.concat(frames, ignore_index=True)

    combined_path = output_dir / f"combined_stock_ohlcv_{interval}.csv"
    save_dataframe(combined_df, combined_path)

    return combined_df


def run_market_data_ingestion(
    start_datetime: datetime,
    end_datetime: datetime,
    interval: str = "day",
    symbols: Optional[Iterable[str]] = None,
) -> None:
    """
    Run the full market data ingestion workflow.

    Parameters
    ----------
    start_datetime:
        Historical start datetime.
    end_datetime:
        Historical end datetime.
    interval:
        Candle interval.
    symbols:
        Optional list of stock symbols to ingest.
    """

    config = get_config()
    ensure_project_directories(config)

    logger.info("Selected DATA_PROVIDER=%s", config.data_provider)

    provider = get_market_data_provider(config)

    logger.info("Active provider: %s", provider.provider_name)

    save_reference_universe(config)

    instruments_df = download_and_save_instrument_master(provider, config)

    enriched_universe_df = build_enriched_universe(
        config=config,
        provider=provider,
        instruments_df=instruments_df,
    )

    ingest_historical_ohlcv_for_stocks(
        provider=provider,
        config=config,
        enriched_universe_df=enriched_universe_df,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        interval=interval,
        symbols=symbols,
    )


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """

    default_end = datetime.utcnow().date()
    default_start = default_end - timedelta(days=365 * 5)

    parser = argparse.ArgumentParser(
        description="Run production market data ingestion."
    )

    parser.add_argument(
        "--start",
        type=str,
        default=str(default_start),
        help="Start date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--end",
        type=str,
        default=str(default_end),
        help="End date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--interval",
        type=str,
        default="day",
        help="Candle interval, for example: day, minute, 5minute.",
    )

    parser.add_argument(
        "--symbols",
        type=str,
        default=None,
        help="Optional comma-separated stock symbols, for example: RELIANCE,INFY,TCS.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    symbol_list = None

    if args.symbols:
        symbol_list = [
            symbol.strip().upper()
            for symbol in args.symbols.split(",")
            if symbol.strip()
        ]

    run_market_data_ingestion(
        start_datetime=datetime.fromisoformat(args.start),
        end_datetime=datetime.fromisoformat(args.end),
        interval=args.interval,
        symbols=symbol_list,
    )
