"""
Provider factory for market data clients.

This module selects the correct production market data provider based on
the DATA_PROVIDER environment variable.

Supported provider names:
- zerodha
- groww
- nse_bse
"""

from __future__ import annotations

from src.config import AppConfig
from src.market_data_provider import MarketDataProvider
from src.zerodha_client import ZerodhaClient
from src.groww_client import GrowwClient
from src.nse_bse_data_client import NseBseDataClient


def get_market_data_provider(config: AppConfig) -> MarketDataProvider:
    """
    Return the configured market data provider.

    Parameters
    ----------
    config:
        Application configuration object.

    Returns
    -------
    MarketDataProvider
        Configured market data provider implementation.

    Raises
    ------
    ValueError
        If DATA_PROVIDER is unsupported.
    """

    provider_name = config.data_provider.lower().strip()

    if provider_name == "zerodha":
        return ZerodhaClient(config=config)

    if provider_name == "groww":
        return GrowwClient(config=config)

    if provider_name in {"nse_bse", "nse-bse", "exchange"}:
        return NseBseDataClient(config=config)

    raise ValueError(
        f"Unsupported DATA_PROVIDER: {config.data_provider}. "
        "Supported values are: zerodha, groww, nse_bse."
    )
