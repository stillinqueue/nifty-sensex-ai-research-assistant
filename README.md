# NIFTY-SENSEX AI Research Assistant

An AI-powered Q&A chatbot for the Indian stock market focused on NIFTY 50, SENSEX, and major Indian listed companies.

This project combines historical market data, feature engineering, machine learning forecasting, Retrieval-Augmented Generation, and LLM-based response generation to produce grounded stock research summaries.

## Project Objective

The goal is to build an AI research assistant that can answer questions such as:

- What is the 18-month outlook for Reliance?
- Compare HDFC Bank and ICICI Bank.
- Which NIFTY 50 stocks show strong momentum?
- What is the trend of NIFTY 50?
- Which SENSEX stocks appear highly volatile?
- Explain the risks for Infosys.
- Is Tata Motors showing a bullish, neutral, or bearish research signal?

## Scope

This project focuses only on the Indian stock market:

- NIFTY 50
- SENSEX
- NIFTY 50 constituent stocks
- SENSEX constituent stocks

## Important Disclaimer

This project is for educational and portfolio purposes only.

The assistant does not provide financial advice, investment recommendations, or buy/sell signals. Its responses are AI-generated research summaries based on historical data and selected model features.

Users should consult a qualified financial professional before making investment decisions.

---

## Architecture

```text
Indian Market Data Sources
        ↓
Raw Price Data
        ↓
Cleaned Stock and Index Data
        ↓
Feature Engineering
        ↓
18-Month Forecasting Model
        ↓
Stock Research Documents
        ↓
Embeddings and Vector Store
        ↓
Retriever
        ↓
LLM Q&A Chatbot
        ↓
Evaluation
```

---

## Main Components

### 1. Data Ingestion

Downloads historical data for:

- NIFTY 50 index
- SENSEX index
- Selected NIFTY 50 and SENSEX constituent stocks

### 2. Feature Engineering

Creates analytical features such as:

- Daily returns
- Rolling volatility
- Moving averages
- RSI
- MACD
- Volume trend
- Max drawdown

### 3. Forecasting Model

Builds a machine learning model to classify each stock's 18-month outlook as:

- Bullish
- Neutral
- Bearish

### 4. RAG Document Generation

Converts stock analytics and model outputs into natural-language research documents.

These documents are used as retrievable context for the chatbot.

### 5. Q&A Chatbot

Uses retrieval and an LLM to answer stock market questions with grounded context.

The chatbot should answer using retrieved research context and include a clear educational disclaimer.

### 6. Evaluation

Evaluates:

- Retrieval relevance
- Forecast label correctness
- Answer groundedness
- Disclaimer presence
- Hallucination risk

---

## Tech Stack

- Python
- pandas
- NumPy
- yfinance
- scikit-learn
- LangChain
- ChromaDB
- OpenAI API
- Jupyter Notebook
- GitHub

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
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_forecasting_model.ipynb
│   ├── 04_rag_document_generation.ipynb
│   ├── 05_qna_chatbot.ipynb
│   └── 06_evaluation.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── forecasting.py
│   ├── rag_documents.py
│   ├── vector_store.py
│   ├── chatbot.py
│   └── prompts.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── vector_store/
│   └── chroma/
│
├── docs/
│   ├── architecture.md
│   ├── data_sources.md
│   ├── forecasting_methodology.md
│   ├── rag_design.md
│   ├── evaluation_plan.md
│   └── responsible_ai_disclaimer.md
│
├── images/
└── tests/
```

---

## Planned Workflow

### Step 1: Ingest Market Data

Download historical prices for NIFTY 50, SENSEX, and selected Indian listed companies.

### Step 2: Clean and Prepare Data

Clean missing values, standardize columns, and prepare stock-level and index-level datasets.

### Step 3: Create Features

Generate technical and statistical features such as returns, volatility, moving averages, RSI, MACD, and drawdown.

### Step 4: Train Forecasting Model

Train a machine learning model to classify each stock's 18-month outlook as bullish, neutral, or bearish.

### Step 5: Generate Research Documents

Convert stock metrics, forecasts, risks, and model outputs into readable stock research summaries.

### Step 6: Build Vector Store

Create embeddings from the research documents and store them in ChromaDB.

### Step 7: Build Q&A Chatbot

Use retrieval and an LLM to answer user questions using the most relevant stock research documents.

### Step 8: Evaluate the Assistant

Evaluate retrieval quality, answer groundedness, disclaimer presence, and hallucination risk.

---

## Example Assistant Behavior

Example question:

```text
What is the 18-month outlook for Reliance?
```

Example answer style:

```text
Reliance shows a neutral research signal based on the current model features.

The retrieved context shows moderate momentum, stable long-term moving average behavior, and medium volatility. The 18-month model label is Neutral.

This is not financial advice. This project is for educational and research purposes only.
```

---

## Responsible AI and Financial Safety

The assistant must follow these rules:

- Do not provide financial advice.
- Do not give direct buy, sell, or hold instructions.
- Do not guarantee future returns.
- Do not present model outputs as certainty.
- Always explain that results are educational research summaries.
- Use only retrieved context when answering stock-specific questions.

---

## Project Status

Current status:

- Repository created
- README drafted
- Project scope defined
- Planned structure defined

Next steps:

- Add `requirements.txt`
- Add `.env.example`
- Add `.gitignore`
- Create folder structure
- Build the data ingestion notebook
