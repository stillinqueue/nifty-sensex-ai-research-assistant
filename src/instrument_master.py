"""
Instrument master utilities.

This module loads the configured NIFTY/SENSEX market universe and helps map
human-friendly symbols to provider-specific identifiers such as Zerodha quote
keys and instrument tokens.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from src.config import AppConfig


def load_market_universe(config: AppConfig) -> dict:
    """
    Load market universe YAML configuration.

    Parameters
    ----------
    config:
        Application configuration.

    Returns
    -------
    dict
        Market universe configuration.
    """

    universe_path = config.project_root / "config" / "market_universe.yaml"

    if not universe_path.exists():
        raise FileNotFoundError(f"Market universe file not found: {universe_path}")

    with universe_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def universe_stocks_to_dataframe(universe: dict) -> pd.DataFrame:
    """
    Convert stock universe YAML entries into a dataframe.

    Parameters
    ----------
    universe:
        Market universe dictionary.

    Returns
    -------
    pd.DataFrame
        Stock universe dataframe.
    """

    stocks = universe.get("stocks", [])
    df = pd.DataFrame(stocks)

    if df.empty:
        return df

    df["index_membership"] = df["index_membership"].apply(
        lambda values: ",".join(values) if isinstance(values, list) else values
    )

    return df


def universe_indices_to_dataframe(universe: dict) -> pd.DataFrame:
    """
    Convert index universe YAML entries into a dataframe.

    Parameters
    ----------
    universe:
        Market universe dictionary.

    Returns
    -------
    pd.DataFrame
        Index universe dataframe.
    """

    indices = universe.get("indices", [])
    return pd.DataFrame(indices)


def save_reference_universe(config: AppConfig) -> None:
    """
    Save stock and index universe as reference CSV files.

    Parameters
    ----------
    config:
        Application configuration.
    """

    universe = load_market_universe(config)

    stocks_df = universe_stocks_to_dataframe(universe)
    indices_df = universe_indices_to_dataframe(universe)

    config.reference_data_dir.mkdir(parents=True, exist_ok=True)

    stocks_path = config.reference_data_dir / "stock_universe.csv"
    indices_path = config.reference_data_dir / "index_universe.csv"

    stocks_df.to_csv(stocks_path, index=False)
    indices_df.to_csv(indices_path, index=False)

    print(f"Saved stock universe: {stocks_path}")
    print(f"Saved index universe: {indices_path}")


def find_stock_by_symbol(universe_df: pd.DataFrame, symbol: str) -> Optional[pd.Series]:
    """
    Find one stock row by symbol.

    Parameters
    ----------
    universe_df:
        Stock universe dataframe.
    symbol:
        Symbol to search for.

    Returns
    -------
    Optional[pd.Series]
        Matching row if found.
    """

    symbol_normalized = symbol.upper().strip()

    matches = universe_df[
        universe_df["symbol"].str.upper().str.strip() == symbol_normalized
    ]

    if matches.empty:
        return None

    return matches.iloc[0]


def enrich_with_zerodha_tokens(
    universe_df: pd.DataFrame,
    zerodha_instruments_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enrich universe with Zerodha instrument tokens.

    Parameters
    ----------
    universe_df:
        Configured stock universe.
    zerodha_instruments_df:
        Zerodha instrument master dataframe.

    Returns
    -------
    pd.DataFrame
        Universe dataframe enriched with instrument tokens where matched.
    """

    if universe_df.empty:
        return universe_df

    if zerodha_instruments_df.empty:
        raise ValueError("Zerodha instrument master is empty.")

    required_columns = {"tradingsymbol", "exchange", "instrument_token"}

    missing = required_columns - set(zerodha_instruments_df.columns)

    if missing:
        raise ValueError(
            f"Zerodha instrument master is missing required columns: {missing}"
        )

    instruments = zerodha_instruments_df.copy()
    instruments["tradingsymbol"] = instruments["tradingsymbol"].astype(str).str.upper()
    instruments["exchange"] = instruments["exchange"].astype(str).str.upper()

    enriched = universe_df.copy()
    enriched["nse_symbol_upper"] = enriched["nse_symbol"].astype(str).str.upper()

    nse_instruments = instruments[instruments["exchange"] == "NSE"][
        ["tradingsymbol", "instrument_token"]
    ].drop_duplicates()

    enriched = enriched.merge(
        nse_instruments,
        left_on="nse_symbol_upper",
        right_on="tradingsymbol",
        how="left",
    )

    enriched["instrument_token"] = enriched["instrument_token_y"].combine_first(
        enriched.get("instrument_token_x")
    )

    enriched = enriched.drop(
        columns=[
            col
            for col in [
                "nse_symbol_upper",
                "tradingsymbol",
                "instrument_token_x",
                "instrument_token_y",
            ]
            if col in enriched.columns
        ]
    )

    return enriched


if __name__ == "__main__":
    from src.config import get_config, ensure_project_directories

    app_config = get_config()
    ensure_project_directories(app_config)
    save_reference_universe(app_config)
