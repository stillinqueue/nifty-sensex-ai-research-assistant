# Market Data Provider Architecture

## Purpose

The project uses a provider abstraction layer so the rest of the system does not depend directly on one market data vendor.

Supported production provider targets:

- Zerodha Kite Connect
- Groww API
- NSE/BSE official or licensed data provider

## Provider Selection

The active provider is selected through the `DATA_PROVIDER` environment variable.

```env
DATA_PROVIDER=zerodha
