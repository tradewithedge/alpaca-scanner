# ALPACA Scanner V1.1.2

Regime-aware U.S. swing-trading scanner built around **Trade With Edge**.

> Strong stock ≠ good entry. **NO TRADE is a valid result.**

See [ROADMAP.md](ROADMAP.md) for the project charter, guardrails, version roadmap, and current stage.

## V1.1.2 — Scanner Audit Integrity

- Full auditable funnel from selected universe through candidate classification
- True SIP liquidity-pass count separated from the configurable deep-scan cap
- Explicit SIP coverage, missing-bar, and dollar-volume percentile diagnostics
- Cutoff-near SIP liquidity audit sample
- Candidate bucket reconciliation, including visible `WAIT / ENTRY NOT READY`
- Fixed U.S. Market Regime separated from selected-universe breadth
- Explicit Deployment Score (70% market regime + 30% selected-universe breadth)
- No silent fallback when a critical universe or consolidated-data source fails
- Multi-file Streamlit hot-reload guard

## Supported stock universes

- All U.S. Tradable / Liquid
- S&P 500
- NASDAQ-100
- Russell 1000 (IWB proxy)
- Russell 2000 (IWM proxy)
- S&P MidCap 400
- S&P SmallCap 600
- Dow Jones 30

Russell 1000/2000 membership is represented using current IWB/IWM holdings as practical proxies and is explicitly labelled as such.

## Core pipeline

Universe → Alpaca match → completed-session SIP data → price gate → previous-day consolidated dollar-liquidity gate → deep-scan selection → historical-data validation → persistent quality → relative strength → setup → entry quality → event gate → risk plan.

## Data-integrity policy

- Previous-day liquidity uses the last fully completed consolidated SIP daily bar.
- Deep history uses SIP with a safety cutoff of at least 20 minutes.
- IEX-only volume is not used for consolidated liquidity gates.
- Critical source/data failures are surfaced; no silent substitution to another universe or feed.

## Streamlit secrets

```toml
APCA_API_KEY_ID = "YOUR_PAPER_KEY_ID"
APCA_API_SECRET_KEY = "YOUR_PAPER_SECRET_KEY"
APCA_PAPER_BASE_URL = "https://paper-api.alpaca.markets"
APCA_DATA_BASE_URL = "https://data.alpaca.markets"
APCA_DATA_FEED = "delayed_sip"
APCA_HISTORICAL_FEED = "sip"
```

Never commit real Alpaca credentials.

## Local integrity tests

```bash
python -m unittest discover -s tests -v
```

The scanner is a research tool. Paper order execution remains disabled.
