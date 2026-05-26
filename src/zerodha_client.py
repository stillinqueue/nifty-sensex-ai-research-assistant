"""
Zerodha Kite Connect market data provider.

This module implements the MarketDataProvider interface for Zerodha Kite Connect.

Supported read-only operations:
- Instrument master download
- Historical OHLCV candle retrieval
- Latest quote retrieval

This module intentionally does not place trades.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

import pandas as pd
from kiteconnect import KiteConnect

from src.config import AppConfig
from src.market_data_provider import (
    HistoricalDataRequest,
    MarketDataProvider,
    QuoteRequest,
    standardize_ohlcv_columns,
    standardize_quote_columns,
)


class ZerodhaClient(MarketDataProvider):
    """
    Zerodha Kite Connect implementation of MarketDataProvider.
    """

    provider_name = "zerodha_kite"

    def __init__(self, config: AppConfig):
        """
        Initialize the Zerodha Kite Connect client.

        Parameters
        ----------
        config:
            Application configuration containing Kite credentials.
        """

        if not config.kite_api_key:
            raise ValueError("KITE_API_KEY is required for Zerodha provider.")

        if not config.kite_access_token:
            raise ValueError(
                "KITE_ACCESS_TOKEN is required for Zerodha provider. "
                "Kite access tokens are session-based and usually need to be generated daily."
            )

        self.config = config
        self.kite = KiteConnect(api_key=config.kite_api_key)
        self.kite.set_access_token(config.kite_access_token)

    def get_instruments(self) -> pd.DataFrame:
        """
        Download Zerodha instrument master.

        Returns
        -------
        pd.DataFrame
            Instrument master table from Zerodha.
        """

        instruments = self.kite.instruments()
        df = pd.DataFrame(instruments)

        if df.empty:
            return df

        df["provider_name"] = self.provider_name
        df["ingestion_timestamp"] = datetime.utcnow()

        return df

    def get_historical_data(self, request: HistoricalDataRequest) -> pd.DataFrame:
        """
        Get historical OHLCV candles from Zerodha.

        Parameters
        ----------
        request:
            Historical data request.

        Returns
        -------
        pd.DataFrame
            Standardized OHLCV dataframe.
        """

        if request.instrument_token is None:
            raise ValueError(
                "instrument_token is required for Zerodha historical data. "
                "Use the instrument master to map symbol to instrument_token."
            )

        candles = self.kite.historical_data(
            instrument_token=request.instrument_token,
            from_date=request.start_datetime,
            to_date=request.end_datetime,
            interval=request.interval,
            continuous=False,
            oi=False,
        )

        raw_df = pd.DataFrame(candles)

        return standardize_ohlcv_columns(
            df=raw_df,
            provider_name=self.provider_name,
            exchange=request.exchange,
            symbol=request.symbol,
            interval=request.interval,
        )

    def get_quote(self, request: QuoteRequest) -> pd.DataFrame:
        """
        Get latest quote for one instrument.

        Parameters
        ----------
        request:
            Quote request.

        Returns
        -------
        pd.DataFrame
            Standardized quote dataframe.
        """

        instrument_key = self._build_instrument_key(request)
        quote_response = self.kite.quote([instrument_key])

        if instrument_key not in quote_response:
            return standardize_quote_columns(
                df=pd.DataFrame(),
                provider_name=self.provider_name,
                exchange=request.exchange,
                symbol=request.symbol,
            )

        quote_df = self._quote_response_to_dataframe(
            quote_response=quote_response,
            instrument_key=instrument_key,
            symbol=request.symbol,
        )

        return standardize_quote_columns(
            df=quote_df,
            provider_name=self.provider_name,
            exchange=request.exchange,
            symbol=request.symbol,
        )

    def get_quotes(self, requests: List[QuoteRequest]) -> pd.DataFrame:
        """
        Get latest quotes for multiple instruments.

        Parameters
        ----------
        requests:
            List of quote requests.

        Returns
        -------
        pd.DataFrame
            Standardized quote dataframe.
        """

        if not requests:
            return pd.DataFrame()

        instrument_keys = [self._build_instrument_key(request) for request in requests]
        quote_response = self.kite.quote(instrument_keys)

        frames = []

        for request, instrument_key in zip(requests, instrument_keys):
            if instrument_key not in quote_response:
                frames.append(
                    standardize_quote_columns(
                        df=pd.DataFrame(),
                        provider_name=self.provider_name,
                        exchange=request.exchange,
                        symbol=request.symbol,
                    )
                )
                continue

            quote_df = self._quote_response_to_dataframe(
                quote_response=quote_response,
                instrument_key=instrument_key,
                symbol=request.symbol,
            )

            standardized = standardize_quote_columns(
                df=quote_df,
                provider_name=self.provider_name,
                exchange=request.exchange,
                symbol=request.symbol,
            )

            frames.append(standardized)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    @staticmethod
    def _build_instrument_key(request: QuoteRequest) -> str:
        """
        Build Zerodha quote instrument key.

        Zerodha quote keys usually follow EXCHANGE:TRADINGSYMBOL format,
        for example NSE:RELIANCE or BSE:RELIANCE.

        Parameters
        ----------
        request:
            Quote request.

        Returns
        -------
        str
            Zerodha quote instrument key.
        """

        return f"{request.exchange}:{request.symbol}"

    @staticmethod
    def _quote_response_to_dataframe(
        quote_response: dict,
        instrument_key: str,
        symbol: str,
    ) -> pd.DataFrame:
        """
        Convert a Zerodha quote response for one instrument into a dataframe.

        Parameters
        ----------
        quote_response:
            Raw response from kite.quote().
        instrument_key:
            Provider-specific key such as NSE:RELIANCE.
        symbol:
            Trading symbol.

        Returns
        -------
        pd.DataFrame
            One-row quote dataframe.
        """

        quote = quote_response[instrument_key]

        ohlc = quote.get("ohlc", {}) or {}

        row = {
            "event_timestamp": quote.get("timestamp") or quote.get("last_trade_time"),
            "last_price": quote.get("last_price"),
            "volume": quote.get("volume"),
            "average_price": quote.get("average_price"),
            "open": ohlc.get("open"),
            "high": ohlc.get("high"),
            "low": ohlc.get("low"),
            "close": ohlc.get("close"),
            "symbol": symbol,
            "instrument_key": instrument_key,
        }

        return pd.DataFrame([row])
