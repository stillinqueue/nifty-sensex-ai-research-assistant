"""
NSE/BSE licensed data provider placeholder.

This module represents an exchange-grade or licensed vendor integration
for NSE and BSE market data.

The exact implementation depends on the licensed data product or vendor API
available to the user.
"""

from __future__ import annotations

from typing import List

import pandas as pd

from src.config import AppConfig
from src.market_data_provider import (
    HistoricalDataRequest,
    MarketDataProvider,
    QuoteRequest,
)


class NseBseDataClient(MarketDataProvider):
    """
    NSE/BSE official or licensed vendor implementation placeholder.

    This class should be completed after choosing the actual exchange data
    product or licensed vendor API.
    """

    provider_name = "nse_bse"

    def __init__(self, config: AppConfig):
        """
        Initialize NSE/BSE licensed data client.

        Parameters
        ----------
        config:
            Application configuration containing vendor credentials.
        """

        if not config.nse_bse_api_key:
            raise ValueError("NSE_BSE_API_KEY is required for NSE/BSE provider.")

        if not config.nse_bse_api_base_url:
            raise ValueError("NSE_BSE_API_BASE_URL is required for NSE/BSE provider.")

        self.config = config

    def get_instruments(self) -> pd.DataFrame:
        """
        Return available NSE/BSE instruments.

        Returns
        -------
        pd.DataFrame
            Instrument master table.
        """

        raise NotImplementedError(
            "NSE/BSE instrument master integration is not implemented yet. "
            "Add implementation after selecting the licensed data provider."
        )

    def get_historical_data(self, request: HistoricalDataRequest) -> pd.DataFrame:
        """
        Return historical OHLCV candles from NSE/BSE provider.

        Parameters
        ----------
        request:
            Historical data request.

        Returns
        -------
        pd.DataFrame
            Standardized OHLCV dataframe.
        """

        raise NotImplementedError(
            "NSE/BSE historical data integration is not implemented yet. "
            "Add implementation after selecting the licensed data provider."
        )

    def get_quote(self, request: QuoteRequest) -> pd.DataFrame:
        """
        Return latest quote from NSE/BSE provider.

        Parameters
        ----------
        request:
            Quote request.

        Returns
        -------
        pd.DataFrame
            Standardized quote dataframe.
        """

        raise NotImplementedError(
            "NSE/BSE quote integration is not implemented yet. "
            "Add implementation after selecting the licensed data provider."
        )

    def get_quotes(self, requests: List[QuoteRequest]) -> pd.DataFrame:
        """
        Return latest quotes from NSE/BSE provider.

        Parameters
        ----------
        requests:
            List of quote requests.

        Returns
        -------
        pd.DataFrame
            Standardized quote dataframe.
        """

        raise NotImplementedError(
            "NSE/BSE batch quote integration is not implemented yet. "
            "Add implementation after selecting the licensed data provider."
        )
