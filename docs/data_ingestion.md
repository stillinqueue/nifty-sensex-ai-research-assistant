# Market Data Ingestion

## Purpose

The ingestion layer loads Indian market data from approved production data providers and stores the raw data before transformation.

Approved provider targets:

- Zerodha Kite Connect
- Groww API
- NSE/BSE official or licensed data provider

The first implemented provider is Zerodha Kite Connect.

---

## Core Files

```text
src/config.py
src/provider_factory.py
src/market_data_provider.py
src/zerodha_client.py
src/instrument_master.py
src/market_data_ingestion.py
notebooks/01_market_data_ingestion.py
```

---

## Ingestion Workflow

```text
Load environment configuration
        ↓
Select active market data provider
        ↓
Load configured NIFTY/SENSEX universe
        ↓
Download provider instrument master
        ↓
Save provider instrument master
        ↓
Export configured stock/index universe
        ↓
Map symbols to provider instrument tokens
        ↓
Download historical OHLCV candles
        ↓
Save raw OHLCV files
```

---

## Required Environment Variables

For Zerodha:

```env
DATA_PROVIDER=zerodha
KITE_API_KEY=your_kite_api_key_here
KITE_API_SECRET=your_kite_api_secret_here
KITE_ACCESS_TOKEN=your_daily_access_token_here
```

Do not commit real API credentials.

---

## Market Universe

The configured market universe is stored in:

```text
config/market_universe.yaml
```

It contains:

- NIFTY 50 index
- SENSEX index
- NIFTY/SENSEX constituent stocks
- Sector labels
- Exchange symbols
- Provider quote keys
- Placeholder instrument tokens

---

## Instrument Master

For Zerodha, historical OHLCV downloads require an `instrument_token`.

The pipeline downloads the Zerodha instrument master and saves it to:

```text
data/reference/zerodha_kite_instrument_master.csv
```

The configured stock universe is enriched with instrument tokens and saved to:

```text
data/reference/stock_universe_enriched.csv
```

---

## Raw Data Outputs

Historical stock OHLCV files are saved under:

```text
data/raw/ohlcv/day/
```

Example files:

```text
data/raw/ohlcv/day/RELIANCE_day.csv
data/raw/ohlcv/day/TCS_day.csv
data/raw/ohlcv/day/INFY_day.csv
data/raw/ohlcv/day/combined_stock_ohlcv_day.csv
```

---

## Standard OHLCV Schema

The ingestion layer standardizes historical data into this schema:

```text
provider_name
exchange
symbol
interval
event_timestamp
open
high
low
close
volume
ingestion_timestamp
```

---

## Running the Ingestion Pipeline

Run a small test first:

```bash
python -m src.market_data_ingestion \
  --start 2020-01-01 \
  --end 2024-12-31 \
  --interval day \
  --symbols RELIANCE,TCS,INFY
```

Run the full configured universe:

```bash
python -m src.market_data_ingestion \
  --start 2020-01-01 \
  --end 2024-12-31 \
  --interval day
```

---

## Notebook-Style Script

A guided notebook-style workflow is available at:

```text
notebooks/01_market_data_ingestion.py
```

It walks through:

- Loading configuration
- Selecting the provider
- Inspecting the market universe
- Downloading the instrument master
- Enriching the universe with instrument tokens
- Testing OHLCV ingestion on a small symbol set

---

## Production Notes

The ingestion layer is read-only.

It does not:

- Place trades
- Submit orders
- Modify positions
- Scrape broker dashboards
- Scrape MarketWatch user interfaces

---

## Data Quality Handoff

Raw data from this step should be validated before feature engineering.

The next layer will check for:

- Missing candles
- Duplicate rows
- Invalid OHLC relationships
- Negative prices
- Stale timestamps
- Zero or abnormal volume
- Large unexplained price jumps
