"""
Market data provider interface.

This module defines a provider abstraction for production-style Indian
market data sources such as Zerodha Kite Connect, NSE/BSE licensed feeds,
and Groww API.

Each provider should implement the same interface so the rest of the
project can work independently of the selected data vendor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd


@dataclass(frozen=True)
class HistoricalDataRequest:
    """
    Request object for historical OHLCV market data.
    """

    symbol: str
    exchange: str
    interval: str
    start_datetime: datetime
    end_datetime: datetime
    instrument_token: Optional[int] = None


@dataclass(frozen=True)
class QuoteRequest:
    """
    Request object for latest quote data.
    """

    symbol: str
    exchange: str
    instrument_token: Optional[int] = None


@dataclass(frozen=True)
class Instrument:
    """
    Standardized instrument metadata.
    """

    symbol: str
    exchange: str
    instrument_name: str
    instrument_token: Optional[int]
    tradingsymbol: Optional[str]
    segment: Optional[str]
    instrument_type: Optional[str]


class MarketDataProvider(ABC):
    """
    Abstract base class for all market data providers.

    Concrete implementations may include:
    - Zerodha Kite Connect
    - Groww API
    - NSE/BSE licensed data vendor
    """

    provider_name: str

    @abstractmethod
    def get_instruments(self) -> pd.DataFrame:
        """
        Return available instruments from the provider.

        Returns
        -------
        pd.DataFrame
            Instrument master table.
        """

    @abstractmethod
    def get_historical_data(self, request: HistoricalDataRequest) -> pd.DataFrame:
        """
        Return historical OHLCV candles for one instrument.

        Parameters
        ----------
        request:
            Historical data request.

        Returns
        -------
        pd.DataFrame
            Standardized OHLCV dataframe with provider metadata.
        """

    @abstractmethod
    def get_quote(self, request: QuoteRequest) -> pd.DataFrame:
        """
        Return latest quote for one instrument.

        Parameters
        ----------
        request:
            Quote request.

        Returns
        -------
        pd.DataFrame
            Standardized quote dataframe with provider metadata.
        """

    @abstractmethod
    def get_quotes(self, requests: List[QuoteRequest]) -> pd.DataFrame:
        """
        Return latest quotes for multiple instruments.

        Parameters
        ----------
        requests:
            List of quote requests.

        Returns
        -------
        pd.DataFrame
            Standardized quote dataframe with provider metadata.
        """


def standardize_ohlcv_columns(
    df: pd.DataFrame,
    provider_name: str,
    exchange: str,
    symbol: str,
    interval: str,
) -> pd.DataFrame:
    """
    Standardize historical OHLCV dataframe columns.

    Expected output columns:
    - provider_name
    - exchange
    - symbol
    - interval
    - event_timestamp
    - open
    - high
    - low
    - close
    - volume
    - ingestion_timestamp

    Parameters
    ----------
    df:
        Provider-specific OHLCV dataframe.
    provider_name:
        Market data provider name.
    exchange:
        Exchange name.
    symbol:
        Trading symbol.
    interval:
        Candle interval.

    Returns
    -------
    pd.DataFrame
        Standardized OHLCV dataframe.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "provider_name",
                "exchange",
                "symbol",
                "interval",
                "event_timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "ingestion_timestamp",
            ]
        )

    standardized = df.copy()

    column_mapping = {
        "date": "event_timestamp",
        "datetime": "event_timestamp",
        "timestamp": "event_timestamp",
        "time": "event_timestamp",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume",
    }

    standardized.columns = [
        column_mapping.get(str(col).lower(), str(col).lower())
        for col in standardized.columns
    ]

    required_columns = ["event_timestamp", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in standardized.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required OHLCV columns for {symbol}: {missing_columns}"
        )

    standardized["provider_name"] = provider_name
    standardized["exchange"] = exchange
    standardized["symbol"] = symbol
    standardized["interval"] = interval
    standardized["ingestion_timestamp"] = datetime.utcnow()

    return standardized[
        [
            "provider_name",
            "exchange",
            "symbol",
            "interval",
            "event_timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "ingestion_timestamp",
        ]
    ]


def standardize_quote_columns(
    df: pd.DataFrame,
    provider_name: str,
    exchange: str,
    symbol: str,
) -> pd.DataFrame:
    """
    Standardize latest quote dataframe columns.

    Expected output columns:
    - provider_name
    - exchange
    - symbol
    - event_timestamp
    - last_price
    - volume
    - average_price
    - open
    - high
    - low
    - close
    - ingestion_timestamp

    Parameters
    ----------
    df:
        Provider-specific quote dataframe.
    provider_name:
        Market data provider name.
    exchange:
        Exchange name.
    symbol:
        Trading symbol.

    Returns
    -------
    pd.DataFrame
        Standardized quote dataframe.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "provider_name",
                "exchange",
                "symbol",
                "event_timestamp",
                "last_price",
                "volume",
                "average_price",
                "open",
                "high",
                "low",
                "close",
                "ingestion_timestamp",
            ]
        )

    standardized = df.copy()

    standardized.columns = [
        str(col).lower().replace(" ", "_")
        for col in standardized.columns
    ]

    standardized["provider_name"] = provider_name
    standardized["exchange"] = exchange
    standardized["symbol"] = symbol
    standardized["ingestion_timestamp"] = datetime.utcnow()

    expected_columns = [
        "provider_name",
        "exchange",
        "symbol",
        "event_timestamp",
        "last_price",
        "volume",
        "average_price",
        "open",
        "high",
        "low",
        "close",
        "ingestion_timestamp",
    ]

    for column in expected_columns:
        if column not in standardized.columns:
            standardized[column] = None

    return standardized[expected_columns]
