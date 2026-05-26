# NIFTY-SENSEX AI Research Assistant

A production-style AI research assistant for the Indian stock market focused on NIFTY 50, SENSEX, and major Indian listed companies.

This project is designed for the AI Engineer career track and demonstrates how to build a market research assistant using production-style financial data sources, machine learning forecasting, Retrieval-Augmented Generation, and LLM-based question answering.

The assistant produces grounded research summaries with:

- 18-month bullish, neutral, or bearish outlooks
- Confidence scores
- Technical and risk explanations
- Retrieved market context
- Source timestamps
- Responsible AI and financial disclaimers

> This project is for educational and portfolio purposes only. It does not provide financial advice, investment recommendations, or buy/sell signals.

---

## Project Objective

The goal is to build a Q&A assistant that can answer Indian stock market research questions such as:

- What is the 18-month research outlook for Reliance?
- Why is Infosys marked bearish?
- Compare HDFC Bank and ICICI Bank.
- Which NIFTY 50 stocks have strong momentum?
- Which SENSEX stocks have high volatility?
- Which stocks have bullish signals but high downside risk?
- What is the current trend of NIFTY 50?
- Explain the risks behind Tata Motors’ model outlook.
- Which banking stocks are outperforming the broader market?

The assistant should return evidence-based research summaries, not trading instructions.

---

## Market Scope

This project focuses only on the Indian stock market.

Primary market universe:

- NIFTY 50 index
- SENSEX index
- NIFTY 50 constituent stocks
- SENSEX constituent stocks

The project does not attempt to analyze every listed Indian stock in the first version.

The tracked universe is configured in:

```text
config/market_universe.yaml
```

The universe includes symbols, NSE/BSE mappings, sectors, index membership, provider quote keys, and placeholder instrument tokens.

Index membership and instrument identifiers should be refreshed and validated against Zerodha instrument master, NSE official data, BSE official data, or licensed vendor data before production use.

---

## Production Data Policy

This project is designed to use production-style Indian market data sources.

Approved data sources:

- Zerodha Kite Connect
- NSE official or licensed data
- BSE official or licensed data
- Groww API

The project does not use:

- Web scraping of broker dashboards
- Web scraping of trading terminals
- Web scraping of MarketWatch-style user interfaces
- Unofficial or unreliable production data sources

Every market answer should be grounded in:

- Ingested market data
- Retrieved research context
- Model outputs
- Provider/source timestamps

---

## What the Assistant Does

The assistant is designed to:

- Ingest market data from approved providers
- Validate historical and live market data
- Create stock and index-level technical features
- Train an 18-month directional forecasting model
- Generate stock research documents
- Retrieve relevant context using RAG
- Answer stock market questions using an LLM
- Include confidence, risks, timestamps, and disclaimers

---

## What the Assistant Does Not Do

The assistant does not:

- Guarantee future returns
- Predict exact future stock prices
- Provide buy, sell, or hold instructions
- Place trades
- Replace a SEBI-registered investment adviser
- Make personalized investment recommendations
- Consider a user’s financial goals, risk tolerance, or portfolio situation

The output should be interpreted as an AI-generated research summary, not financial advice.

---

## High-Level Architecture

```text
Zerodha Kite / NSE / BSE / Groww
        ↓
Provider Abstraction Layer
        ↓
Instrument Master + Market Universe
        ↓
Raw Market Data Store
        ↓
Data Quality Validation
        ↓
Feature Engineering
        ↓
Forecasting + Signal Model
        ↓
Backtesting + Model Evaluation
        ↓
Research Document Generator
        ↓
Vector Store / RAG
        ↓
LLM Research Assistant
        ↓
Monitoring, Logging, Guardrails
```

---

## Main Components

### 1. Provider Abstraction Layer

The system uses a clean market-data-provider interface so different production data sources can be plugged in without rewriting the pipeline.

Current provider targets:

- Zerodha Kite Connect
- Groww API
- NSE/BSE licensed data provider

Core files:

```text
src/market_data_provider.py
src/provider_factory.py
src/zerodha_client.py
src/groww_client.py
src/nse_bse_data_client.py
```

The provider layer supports:

- Historical OHLCV candles
- Latest quotes
- Batch quotes
- Instrument metadata
- Source timestamps

Current implementation status:

| Provider | Status |
|---|---|
| Zerodha Kite Connect | Initial read-only implementation |
| Groww API | Placeholder pending endpoint contract |
| NSE/BSE licensed data | Placeholder pending vendor selection |

The first implementation is read-only and does not place trades.

---

### 2. Zerodha Kite Connect Integration

The first production provider implementation is:

```text
src/zerodha_client.py
```

It supports:

- Instrument master download
- Historical OHLCV candle retrieval
- Latest quote retrieval
- Batch quote retrieval

Zerodha historical data requires an `instrument_token`, which should be mapped from the Zerodha instrument master.

The setup guide is documented in:

```text
docs/zerodha_kite_setup.md
```

---

### 3. Market Universe and Instrument Master

The market universe is configured in:

```text
config/market_universe.yaml
```

The helper utilities are implemented in:

```text
src/instrument_master.py
```

The instrument master utilities support:

- Loading the configured market universe
- Converting stocks and indices to DataFrames
- Exporting reference files
- Finding stocks by symbol
- Enriching the configured universe with Zerodha instrument tokens

Expected reference outputs:

```text
data/reference/stock_universe.csv
data/reference/index_universe.csv
```

---

### 4. Raw Market Data Store

Raw provider data is stored before transformation.

Expected folders:

```text
data/raw/
data/reference/
```

Example raw data categories:

- Daily OHLCV candles
- Intraday candles
- Live quote snapshots
- Instrument master data
- Index constituent mappings

---

### 5. Data Quality Validation

The project validates market data before feature engineering.

Planned checks:

- Missing candles
- Duplicate candles
- Negative prices
- Zero or invalid volume
- Invalid OHLC relationships
- Stale quotes
- Large unexplained price jumps
- Missing timestamps
- Missing instrument IDs or tokens

---

### 6. Feature Engineering

The system generates technical and market-relative features such as:

- Daily return
- Weekly return
- Monthly return
- 20-day volatility
- 60-day volatility
- 50-day moving average
- 200-day moving average
- RSI
- MACD
- ATR
- Drawdown
- Volume z-score
- Relative strength versus NIFTY 50

These features are used for forecasting, ranking, and research-document generation.

---

### 7. 18-Month Forecasting Model

The forecasting layer predicts a directional 18-month research outlook.

Target classes:

- Bullish
- Neutral
- Bearish

The model does not predict an exact future price.

Planned modeling approach:

- Historical feature dataset
- 18-month forward return labeling
- Time-series split
- Walk-forward validation
- Backtesting
- Model performance reporting

Example target logic:

```text
future_return_18m > +10%      → Bullish
-10% to +10%                  → Neutral
future_return_18m < -10%      → Bearish
```

Thresholds may be adjusted during model evaluation.

---

### 8. Backtesting and Model Evaluation

The project will evaluate whether forecast signals were historically useful.

Planned metrics:

- Accuracy
- Weighted F1 score
- Precision for bullish class
- Recall for bearish class
- Average forward return by signal class
- Hit rate
- Maximum drawdown
- Confusion matrix
- Walk-forward validation results

The goal is not to prove perfect prediction, but to measure whether the research signals are useful, stable, and explainable.

---

### 9. Research Document Generation

Structured market analytics are converted into natural-language research documents.

Each stock or index document may include:

- Symbol
- Company or index name
- Exchange
- Latest price snapshot
- Trend summary
- Momentum indicators
- Volatility indicators
- Forecast signal
- Confidence score
- Key risk factors
- Data source
- Last updated timestamp

Example document structure:

```text
Stock: RELIANCE
Exchange: NSE
Index Membership: NIFTY 50, SENSEX

Latest Research Signal:
The 18-month model outlook is neutral to bullish with medium confidence.

Evidence:
The stock is trading above its 50-day moving average, volatility is moderate, and relative strength versus NIFTY 50 is positive.

Risks:
The outlook may be affected by energy prices, telecom competition, retail growth expectations, and broader market volatility.

Data Source:
Zerodha Kite Connect

Last Updated:
YYYY-MM-DD HH:MM:SS
```

---

### 10. RAG and Vector Search

The assistant uses Retrieval-Augmented Generation to ground its answers.

Flow:

```text
User Question
    ↓
Retrieve relevant stock/index research documents
    ↓
Rank by relevance, freshness, and risk importance
    ↓
Build prompt context
    ↓
Generate grounded LLM answer
    ↓
Return answer with evidence, confidence, risks, and disclaimer
```

The first implementation may use ChromaDB locally.

The architecture can later be migrated to a managed vector database or Databricks Vector Search.

---

### 11. LLM-Based Q&A Assistant

The chatbot answers questions using only retrieved market context and model outputs.

Expected answer format:

- Direct research answer
- Supporting evidence
- 18-month outlook
- Confidence level
- Key risks
- Data source and timestamp
- Responsible AI disclaimer

The assistant should avoid unsupported claims and should not answer from memory alone.

---

### 12. Evaluation and Guardrails

The assistant will be evaluated for:

- Retrieval relevance
- Answer groundedness
- Forecast label correctness
- Risk explanation quality
- Disclaimer presence
- Hallucination risk
- Refusal of unsupported financial advice requests

Example unsafe request:

```text
Tell me exactly which stock to buy today.
```

Expected safe response:

```text
I cannot provide personalized buy or sell advice. I can provide a research-style comparison based on available market data, model signals, and risk factors.
```

---

## Planned Repository Structure

```text
nifty-sensex-ai-research-assistant/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── config/
│   └── market_universe.yaml
│
├── notebooks/
│   ├── 01_market_data_ingestion.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_forecasting_model.ipynb
│   ├── 04_rag_document_generation.ipynb
│   ├── 05_qna_chatbot.ipynb
│   └── 06_evaluation.ipynb
│
├── src/
│   ├── config.py
│   ├── market_data_provider.py
│   ├── provider_factory.py
│   ├── zerodha_client.py
│   ├── groww_client.py
│   ├── nse_bse_data_client.py
│   ├── instrument_master.py
│   ├── market_data_ingestion.py
│   ├── live_market_stream.py
│   ├── data_validation.py
│   ├── feature_engineering.py
│   ├── forecasting.py
│   ├── backtesting.py
│   ├── risk_scoring.py
│   ├── rag_documents.py
│   ├── vector_store.py
│   ├── chatbot.py
│   ├── prompts.py
│   └── evaluation.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── reference/
│   ├── features/
│   └── predictions/
│
├── vector_store/
│   └── chroma/
│
├── docs/
│   ├── architecture.md
│   ├── production_data_strategy.md
│   ├── provider_architecture.md
│   ├── zerodha_kite_setup.md
│   ├── market_universe.md
│   ├── data_sources.md
│   ├── data_ingestion.md
│   ├── data_quality_rules.md
│   ├── forecasting_methodology.md
│   ├── model_risk_management.md
│   ├── rag_design.md
│   ├── evaluation_plan.md
│   └── responsible_ai_disclaimer.md
│
├── images/
│   ├── architecture_diagram.png
│   ├── forecast_example.png
│   └── chatbot_example.png
│
├── logs/
├── models/
│
└── tests/
    ├── test_data_validation.py
    ├── test_feature_engineering.py
    ├── test_forecasting.py
    ├── test_rag_documents.py
    └── test_guardrails.py
```

---

## Environment Variables

Create a local `.env` file using `.env.example` as a template.

Required variables:

```env
# Data provider selection
DATA_PROVIDER=zerodha

# Zerodha Kite Connect
KITE_API_KEY=your_kite_api_key_here
KITE_API_SECRET=your_kite_api_secret_here
KITE_ACCESS_TOKEN=your_daily_access_token_here

# Groww API
GROWW_API_KEY=your_groww_api_key_here

# NSE / BSE licensed data provider
NSE_BSE_API_KEY=your_exchange_or_vendor_api_key_here
NSE_BSE_API_BASE_URL=your_exchange_or_vendor_base_url_here

# LLM provider
OPENAI_API_KEY=your_openai_api_key_here
```

Never commit real API keys or access tokens.

---

## Tech Stack

### Core

- Python
- pandas
- NumPy
- scikit-learn
- pydantic
- PyYAML
- python-dotenv
- joblib

### Market Data

- Zerodha Kite Connect
- Groww API
- NSE/BSE licensed data provider interface

### ML and Evaluation

- scikit-learn
- MLflow
- Walk-forward validation
- Backtesting

### RAG and LLM

- LangChain
- ChromaDB
- OpenAI API
- tiktoken

### Testing and Quality

- pytest
- Great Expectations

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/nifty-sensex-ai-research-assistant.git
cd nifty-sensex-ai-research-assistant
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Then fill in the required API keys and access tokens.

---

## Current Status

Phase 1: Production repo reset complete.

Phase 2: Production market data foundation in progress.

Completed:

- GitHub repository created
- Initial project structure added
- Production-only data strategy defined
- Production data provider scope selected
- Environment template updated for Zerodha, Groww, NSE/BSE, and OpenAI
- Application configuration module added
- Market data provider interface added
- Zerodha Kite Connect read-only provider added
- Groww provider placeholder added
- NSE/BSE licensed data provider placeholder added
- Provider factory added
- Provider architecture documentation added
- Zerodha setup documentation added
- Market universe configuration added
- Instrument master utilities added
- Market universe documentation added

Next:

- Add market data ingestion layer
- Add ingestion documentation
- Create first ingestion notebook or notebook-style Python script
- Download and store Zerodha instrument master
- Export stock and index universe reference files
- Map configured stocks to Zerodha instrument tokens

---

## Responsible AI and Financial Disclaimer

This project is for educational and portfolio purposes only.

The assistant does not provide financial advice, investment recommendations, or buy/sell signals.

The model outputs are research signals based on historical data, technical features, and retrieved context. They are not guarantees of future performance.

Users should consult a qualified financial professional before making investment decisions.
