"""
Groww API market data provider placeholder.

This module is intentionally structured as a production provider, but the
exact implementation depends on the Groww API plan, authentication method,
and endpoint contract available to the user.

The class follows the same MarketDataProvider interface used by Zerodha
and NSE/BSE providers.
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


class GrowwClient(MarketDataProvider):
    """
    Groww API implementation placeholder.

    This class should be completed after confirming the exact Groww API
    authentication and endpoint specifications.
    """

    provider_name = "groww"

    def __init__(self, config: AppConfig):
        """
        Initialize Groww API client.

        Parameters
        ----------
        config:
            Application configuration containing Groww credentials.
        """

        if not config.groww_api_key:
            raise ValueError("GROWW_API_KEY is required for Groww provider.")

        self.config = config

    def get_instruments(self) -> pd.DataFrame:
        """
        Return available instruments from Groww.

        Returns
        -------
        pd.DataFrame
            Instrument master table.
        """

        raise NotImplementedError(
            "Groww instrument master integration is not implemented yet. "
            "Add implementation after confirming Groww API endpoint details."
        )

    def get_historical_data(self, request: HistoricalDataRequest) -> pd.DataFrame:
        """
        Return historical OHLCV candles from Groww.

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
            "Groww historical data integration is not implemented yet. "
            "Add implementation after confirming Groww API endpoint details."
        )

    def get_quote(self, request: QuoteRequest) -> pd.DataFrame:
        """
        Return latest quote from Groww.

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
            "Groww quote integration is not implemented yet. "
            "Add implementation after confirming Groww API endpoint details."
        )

    def get_quotes(self, requests: List[QuoteRequest]) -> pd.DataFrame:
        """
        Return latest quotes from Groww.

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
            "Groww batch quote integration is not implemented yet. "
            "Add implementation after confirming Groww API endpoint details."
        )
