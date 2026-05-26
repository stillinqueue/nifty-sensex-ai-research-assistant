# Production Data Strategy

## Purpose

This project is designed as a production-style Indian stock market AI research assistant.

The system intentionally avoids demo-only or unofficial market data sources for the production path.

The approved production data sources are:

- Zerodha Kite Connect
- NSE official or licensed market data
- BSE official or licensed market data
- Groww API

---

## Data Source Policy

The project does not use web scraping of broker dashboards, trading terminals, or marketwatch user interfaces.

The project should only use:

1. Official APIs
2. Broker-provided APIs
3. Licensed exchange data feeds
4. User-authorized API credentials

This helps make the project more reliable, legal, and production-ready.

---

## Zerodha Kite Connect

Zerodha Kite Connect is used as the primary broker API option.

Expected use cases:

- Historical OHLCV candles
- Instrument master data
- Live market quotes
- WebSocket streaming
- Portfolio and holdings data, if explicitly enabled by the user

The system will not place trades in the first production version.

---

## NSE and BSE Data

NSE and BSE official or licensed feeds are used as the preferred exchange-grade data source.

Expected use cases:

- Official index data
- Official security metadata
- Corporate actions
- Real-time or snapshot market data
- End-of-day market data
- Index constituents

---

## Groww API

Groww API is included as an additional broker API option.

Expected use cases:

- Market data
- Live quotes
- Portfolio data, if explicitly enabled by the user

---

## Data Freshness

Every ingested data record should include:

- `provider_name`
- `exchange`
- `symbol`
- `instrument_id` or `instrument_token`
- `event_timestamp`
- `ingestion_timestamp`
- `data_frequency`
- `source_type`

These fields help the assistant explain when the data was collected and where it came from.

---

## Data Quality Requirements

The ingestion layer should validate:

- Missing candles
- Duplicate candles
- Negative prices
- Zero or invalid volume
- Invalid OHLC relationships
- Stale quotes
- Large unexplained price jumps
- Missing provider timestamps

Records that fail validation should be logged and reviewed before being used for forecasting or RAG answers.

---

## Storage Strategy

Raw data should be stored before transformation.

Recommended folders:

```text
data/raw/
data/processed/
data/reference/
data/features/
data/predictions/
```

### Folder Purpose

| Folder | Purpose |
|---|---|
| `data/raw/` | Original data from approved providers |
| `data/processed/` | Cleaned and standardized market data |
| `data/reference/` | Instrument metadata, index constituents, and symbol mappings |
| `data/features/` | Engineered features for forecasting |
| `data/predictions/` | Model outputs and research signals |

---

## Production Principle

The assistant should never answer from memory alone.

Every market answer should be grounded in:

- Latest available data
- Retrieved context
- Model output
- Source timestamp

This keeps responses traceable and reduces unsupported claims.

---

## Limitations

Even with production-grade data, stock market forecasting is uncertain.

The system produces research signals, not guaranteed predictions or financial advice.

The assistant should not provide direct buy, sell, or hold instructions.

---

## Future Improvements

- Add provider-specific ingestion modules
- Add source-level freshness checks
- Add automated data quality reports
- Add provider fallback logic
- Add market holiday handling
- Add corporate action adjustment checks
- Add monitoring for stale or missing market data
