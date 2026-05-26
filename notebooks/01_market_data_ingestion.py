# Databricks / Jupyter notebook-style script
# Phase 1: Production Market Data Ingestion

# COMMAND ----------

"""
This notebook-style script runs the production market data ingestion workflow.

It uses:
- src/config.py
- src/provider_factory.py
- src/market_data_ingestion.py
- config/market_universe.yaml

The first implemented provider is Zerodha Kite Connect.

Before running:
1. Create a local .env file.
2. Add Zerodha Kite credentials.
3. Set DATA_PROVIDER=zerodha.
4. Make sure the required dependencies are installed.
"""

# COMMAND ----------

from datetime import datetime

from src.config import ensure_project_directories, get_config
from src.provider_factory import get_market_data_provider
from src.instrument_master import (
    load_market_universe,
    universe_stocks_to_dataframe,
    universe_indices_to_dataframe,
)
from src.market_data_ingestion import (
    download_and_save_instrument_master,
    build_enriched_universe,
    ingest_historical_ohlcv_for_stocks,
)

# COMMAND ----------

# Load configuration

config = get_config()
ensure_project_directories(config)

print("Project root:", config.project_root)
print("Selected data provider:", config.data_provider)

# COMMAND ----------

# Load provider

provider = get_market_data_provider(config)

print("Active provider:", provider.provider_name)

# COMMAND ----------

# Inspect configured market universe

universe = load_market_universe(config)

stocks_df = universe_stocks_to_dataframe(universe)
indices_df = universe_indices_to_dataframe(universe)

print("Configured stocks:", len(stocks_df))
print("Configured indices:", len(indices_df))

stocks_df.head()

# COMMAND ----------

# Download and save instrument master

instruments_df = download_and_save_instrument_master(
    provider=provider,
    config=config,
)

print("Instrument master rows:", len(instruments_df))

instruments_df.head()

# COMMAND ----------

# Enrich configured universe with provider-specific identifiers

enriched_universe_df = build_enriched_universe(
    config=config,
    provider=provider,
    instruments_df=instruments_df,
)

print("Enriched universe rows:", len(enriched_universe_df))

enriched_universe_df.head()

# COMMAND ----------

# Check stocks with missing instrument tokens

missing_tokens_df = enriched_universe_df[
    enriched_universe_df["instrument_token"].isna()
]

print("Stocks missing instrument tokens:", len(missing_tokens_df))

missing_tokens_df[
    ["symbol", "company_name", "nse_symbol", "zerodha_quote_key", "instrument_token"]
].head(20)

# COMMAND ----------

# Ingest a small test set first
# This avoids pulling the full universe before confirming credentials and token mapping.

test_symbols = ["RELIANCE", "TCS", "INFY"]

ohlcv_test_df = ingest_historical_ohlcv_for_stocks(
    provider=provider,
    config=config,
    enriched_universe_df=enriched_universe_df,
    start_datetime=datetime(2020, 1, 1),
    end_datetime=datetime.utcnow(),
    interval="day",
    symbols=test_symbols,
)

print("Downloaded OHLCV rows:", len(ohlcv_test_df))

ohlcv_test_df.head()

# COMMAND ----------

# After the test succeeds, run full universe ingestion by removing symbols=...
# Uncomment only when ready.

# full_ohlcv_df = ingest_historical_ohlcv_for_stocks(
#     provider=provider,
#     config=config,
#     enriched_universe_df=enriched_universe_df,
#     start_datetime=datetime(2020, 1, 1),
#     end_datetime=datetime.utcnow(),
#     interval="day",
#     symbols=None,
# )

# print("Downloaded full OHLCV rows:", len(full_ohlcv_df))
# full_ohlcv_df.head()

# COMMAND ----------

"""
Expected output files:

data/reference/zerodha_kite_instrument_master.csv
data/reference/stock_universe_configured.csv
data/reference/index_universe_configured.csv
data/reference/stock_universe_enriched.csv

data/raw/ohlcv/day/RELIANCE_day.csv
data/raw/ohlcv/day/TCS_day.csv
data/raw/ohlcv/day/INFY_day.csv
data/raw/ohlcv/day/combined_stock_ohlcv_day.csv
"""
