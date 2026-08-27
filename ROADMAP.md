# ALPACA Scanner Project Charter & Roadmap

## North Star

Find high-quality U.S. swing-trade candidates, but act only when the **entry itself has edge**.

**Strong stock ≠ good entry. NO TRADE is a valid result.**

## Project Guardrails

1. **Data integrity before intelligence.** Bad market data cannot be repaired with smarter scoring.
2. **Candidate quality ≠ entry quality.** Keep persistent stock quality and current actionability separate.
3. **No silent fallback.** Critical data/source failures must be surfaced explicitly.
4. **NO TRADE is valid.** Never weaken thresholds just to populate the candidate list.
5. **Every enhancement must improve edge, risk control, data confidence, or explainability.** Otherwise it does not belong in the scanner.

When proposing a feature, first ask: **Which roadmap stage does this belong to?**

## Roadmap

| Version | Objective | Status |
|---|---|---|
| V1.0 | Working Alpaca + Streamlit scanner architecture | Complete |
| V1.1 | Explicit universes + persistent quality screening | Complete |
| V1.1.1 | Consolidated SIP data integrity | Complete |
| V1.1.2 | Scanner Audit Integrity | **Current** |
| V1.2 | Candidate Quality Engine | Planned |
| V1.3 | Entry Quality / Anti-Chase Engine | Planned |
| V1.4 | Market Regime & Deployment Engine | Planned |
| V1.5 | Earnings / Event Reliability Layer | Planned |
| V1.6 | Trade Plan & Risk Engine | Planned |
| V1.7 | Validation / Backtest / Forward-test Framework | Planned |
| V1.8 | Paper Trading & Trade Journal Integration | Planned |
| V2.0 | Production-grade Daily Swing Scanner | Target |

## Current Stage — V1.1.2 Scanner Audit Integrity

Definition of done:

- Full funnel is visible: universe → Alpaca match → SIP data → price → liquidity → deep scan → history → quality → bucket.
- True SIP liquidity-pass count is separate from the deep-scan cap.
- Every persistent-quality stock reconciles into one visible bucket, including `WAIT / ENTRY NOT READY`.
- U.S. Market Regime is fixed from broad-market proxies; selected-universe breadth is separate.
- Deployment score is explicitly labelled as the market/breadth blend used by actionability logic.
- Missing SIP/history counts and liquidity percentile diagnostics are visible.
- Scanner shows cutoff-near liquidity observations for audit.
- No silent source/data fallback.

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `██████████████████░░` 90%
- Scanner auditability: `████████████████░░░░` 80% after V1.1.2 implementation; live verification still required
- Candidate intelligence: `██████████░░░░░░░░░░` 50%
- Entry intelligence: `████████░░░░░░░░░░░░` 40%
- Event/fundamental confidence: `██░░░░░░░░░░░░░░░░░░` 10%
- Validation/backtesting: `░░░░░░░░░░░░░░░░░░░░` 0%
- Paper execution/journal: `░░░░░░░░░░░░░░░░░░░░` 0%

The progress percentages describe implementation maturity, not expected trading performance.
