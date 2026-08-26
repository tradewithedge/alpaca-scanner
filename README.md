# ALPACA Scanner V1.1

Regime-aware U.S. swing-trading scanner built around **Trade With Edge**.

## V1.1
- Explicit universe selector: All U.S. Liquid, S&P 500, NASDAQ-100, Russell 1000/2000 proxies, S&P 400, S&P 600, Dow 30
- Universe audit counts and source transparency
- BALANCED / STRICT / ELITE / CUSTOM quality modes
- 20-day average dollar-volume and share-volume gates
- ATR% volatility band
- MA200 and 200-bar history gate
- minimum RS percentile and optional trend gates
- breadth-aware regime score
- bucket counts and reason codes
- `TECH ACTIONABLE — EVENT CHECK` so technical candidates remain visible while event confidence is UNKNOWN
- anti-chase protection retained
- MA200 added to candidate chart

## Pipeline
Universe → Tradability → Liquidity → Quality Eligibility → Regime/Breadth → Relative Strength → Setup → Entry Quality → Event Gate → Risk Plan.

Russell 1000/2000 membership is represented using IWB/IWM holdings as a practical proxy and is explicitly labelled as such.

## Streamlit secrets
```toml
APCA_API_KEY_ID = "YOUR_PAPER_KEY_ID"
APCA_API_SECRET_KEY = "YOUR_PAPER_SECRET_KEY"
APCA_PAPER_BASE_URL = "https://paper-api.alpaca.markets"
APCA_DATA_BASE_URL = "https://data.alpaca.markets"
APCA_DATA_FEED = "iex"
```

Never commit real Alpaca credentials.
