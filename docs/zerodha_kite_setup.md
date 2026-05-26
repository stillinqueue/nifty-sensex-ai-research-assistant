# Zerodha Kite Connect Setup

## Purpose

This project uses Zerodha Kite Connect as the primary production-style broker API for Indian market data.

The first implementation uses read-only market data operations:

- Instrument master
- Historical OHLCV candles
- Latest quotes

The project does not place trades.

## Required Environment Variables

Add the following values to your local `.env` file:

```env
DATA_PROVIDER=zerodha
KITE_API_KEY=your_kite_api_key_here
KITE_API_SECRET=your_kite_api_secret_here
KITE_ACCESS_TOKEN=your_daily_access_token_here
