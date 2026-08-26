# ALPACA Scanner

Regime-aware U.S. swing-trading scanner built around **Trade With Edge**.

## Core logic
Market Regime → Relative Strength → Trend / MA Structure → Setup → Volume → Entry Quality → Risk.

A strong stock is not automatically an actionable trade. Extended leaders are moved to **A-QUALITY — WAIT**.

## V1
- Alpaca paper-account authentication
- IEX/delayed-compatible market data
- Active U.S. equity universe
- Snapshot liquidity prefilter
- Deep scan of 300–2,000 liquid symbols
- SPY / QQQ / IWM regime engine
- EMA8 / EMA20 / MA50
- Relative-strength percentile
- VCP / tightening
- EMA20 pullback
- Breakout + volume confirmation
- Anti-chase gate
- ACTIONABLE / WAIT / DEVELOPING / AVOID buckets
- Structural stop / T1 / T2
- Strict event-data confidence gate

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit secrets
```toml
APCA_API_KEY_ID = "YOUR_PAPER_KEY_ID"
APCA_API_SECRET_KEY = "YOUR_PAPER_SECRET_KEY"
APCA_PAPER_BASE_URL = "https://paper-api.alpaca.markets"
APCA_DATA_BASE_URL = "https://data.alpaca.markets"
APCA_DATA_FEED = "iex"
```

Never commit real Alpaca credentials.
