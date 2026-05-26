"""
Application configuration for the NIFTY-SENSEX AI Research Assistant.

This module centralizes environment variables and runtime settings.
The project is production-oriented and supports broker-grade or
exchange-grade Indian market data providers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """
    Runtime configuration loaded from environment variables.
    """

    data_provider: str

    kite_api_key: Optional[str]
    kite_api_secret: Optional[str]
    kite_access_token: Optional[str]

    groww_api_key: Optional[str]

    nse_bse_api_key: Optional[str]
    nse_bse_api_base_url: Optional[str]

    openai_api_key: Optional[str]

    project_root: Path
    raw_data_dir: Path
    processed_data_dir: Path
    reference_data_dir: Path
    features_data_dir: Path
    predictions_data_dir: Path


def get_config() -> AppConfig:
    """
    Load application configuration.

    Returns
    -------
    AppConfig
        Application configuration object.
    """

    project_root = Path(__file__).resolve().parents[1]

    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"
    reference_data_dir = project_root / "data" / "reference"
    features_data_dir = project_root / "data" / "features"
    predictions_data_dir = project_root / "data" / "predictions"

    return AppConfig(
        data_provider=os.getenv("DATA_PROVIDER", "zerodha").lower(),

        kite_api_key=os.getenv("KITE_API_KEY"),
        kite_api_secret=os.getenv("KITE_API_SECRET"),
        kite_access_token=os.getenv("KITE_ACCESS_TOKEN"),

        groww_api_key=os.getenv("GROWW_API_KEY"),

        nse_bse_api_key=os.getenv("NSE_BSE_API_KEY"),
        nse_bse_api_base_url=os.getenv("NSE_BSE_API_BASE_URL"),

        openai_api_key=os.getenv("OPENAI_API_KEY"),

        project_root=project_root,
        raw_data_dir=raw_data_dir,
        processed_data_dir=processed_data_dir,
        reference_data_dir=reference_data_dir,
        features_data_dir=features_data_dir,
        predictions_data_dir=predictions_data_dir,
    )


def ensure_project_directories(config: AppConfig) -> None:
    """
    Create required project data directories if they do not exist.

    Parameters
    ----------
    config:
        Application configuration object.
    """

    directories = [
        config.raw_data_dir,
        config.processed_data_dir,
        config.reference_data_dir,
        config.features_data_dir,
        config.predictions_data_dir,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
