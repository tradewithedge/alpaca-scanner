# ALPACA Scanner Project Charter & Roadmap

**Revision:** Rev.2 - V1.2.3c Freeze / V1.3 Reconciliation  
**Prepared:** 7 September 2026  
**Current frozen baseline:** V1.2.3c - Composite Architecture Selection & Explainable Guardrail Layer  
**Current development stage:** V1.3a - Contextual Volume Quality Engine

## North Star

Find high-quality U.S. swing-trade candidates, but act only when the **entry itself has edge**.

**Trade With Edge. Strong stock != good entry. NO TRADE is a valid result.**

## Project Guardrails

1. **Data integrity before intelligence.** Bad or ambiguous market data cannot be repaired with smarter scoring.
2. **Candidate Quality != Entry Quality.** Persistent stock quality and current actionability remain separate.
3. **No silent fallback or imputation.** Critical data/source failures are surfaced explicitly.
4. **NO TRADE is valid.** Thresholds are never weakened merely to populate a candidate list.
5. **Component transparency.** Candidate Quality, Leadership, Fundamental Quality, Composite Quality and Entry Quality remain separately inspectable.
6. **Research does not silently become production.** Shadow work needs explicit acceptance before it can alter official ranking/actionability.
7. **No major freeze without a development record.** Chronicle and relevant ADRs must be updated before a stage is considered fully documented.
8. **No new phase opens without Roadmap Reconciliation.** Outstanding research, case-study lessons and frozen dependencies must be reconciled first.

## Roadmap Reconciliation Gate

Before opening any major phase or sub-phase, reconcile all six control sources:

1. current `ROADMAP.md`;
2. `ALPACA_SCANNER_DEVELOPMENT_CHRONICLE.md`;
3. relevant ADRs under `docs/architecture/`;
4. Outstanding Research / Dependency Register below;
5. lessons from accepted live tests and case studies;
6. frozen architecture dependencies.

Every unresolved item must have exactly one disposition:

- **ASSIGNED** - mapped to a named version/sub-version;
- **DEFERRED** - postponed deliberately with reason and destination;
- **REJECTED** - excluded deliberately with rationale.

No unresolved item may remain only in conversational memory.

## Master Roadmap

| Version | Objective | Status |
|---|---|---|
| V1.0 | Working Alpaca + Streamlit scanner architecture | Complete / Frozen |
| V1.1 | Explicit universes + persistent quality screening | Complete / Frozen |
| V1.1.1 | Consolidated SIP data integrity | Complete / Frozen |
| V1.1.2 | Scanner Audit Integrity | Complete / Frozen |
| **V1.2** | **Candidate Quality Engine** | **Complete / Frozen** |
| V1.2.1 | Relative Leadership & Market-Stress Resilience | Complete / Frozen |
| V1.2.1.1 | Leadership explainability | Complete / Frozen |
| V1.2.1.2-V1.2.1.3c | Ticker Inspector utility/reference engine | Complete / Frozen |
| V1.2.2 | Fundamental Quality Engine | Complete / Frozen |
| V1.2.2.1a-V1.2.2.1b1 | SEC access / identity / Fair Access integrity | Complete / Frozen |
| V1.2.2.2 | Fundamental Metric Integrity & Cross-Company Validation | Complete / Frozen |
| V1.2.2.2a-V1.2.2.2a1 | Concept continuity + annual horizon integrity | Complete / Frozen |
| V1.2.2.3 | Fundamental Universe Coverage & Cache Validation | Complete / Frozen |
| V1.2.3 | Composite Candidate Quality shadow calibration | Calibration captured / superseded by refinements |
| V1.2.3a | Composite Attribution & Incremental Fundamental Impact | Accepted / Frozen |
| V1.2.3b | Composite Weight Robustness & Guardrail Calibration | Research completed |
| V1.2.3b1 | Full-Precision Robustness Integrity Fix | Accepted / Frozen |
| V1.2.3b2 | Pre-Revenue / Zero-Revenue Domain Integrity | Accepted / Frozen |
| **V1.2.3c** | **F15 Composite Architecture + Explainable Guardrail** | **ACCEPTED / FROZEN - 7 Sep 2026** |
| **V1.3** | **Entry Quality / Anti-Chase Engine** | **CURRENT** |
| **V1.3a** | **Contextual Volume Quality Engine** | **OPEN / DESIGN** |
| V1.3b | Entry Location & Anti-Chase Foundation | Planned |
| V1.3c | Trigger & Entry-Zone Architecture | Planned |
| V1.3d | Risk/Reward & Stop-Distance Gate | Planned |
| V1.3e | READY / WATCH / WAIT / NO CHASE Decision Architecture | Planned |
| V1.3f | Shadow Execution-Capture Logging / staged-execution preparation | Planned |
| V1.4 | Market Regime & Deployment Engine | Planned |
| V1.5 | Earnings / Event Reliability Layer | Planned |
| V1.6 | Trade Plan & Portfolio Risk Engine | Planned |
| V1.7 | Validation / Backtest / Forward-Test Lab | Planned |
| V1.8 | Alpaca Paper Trading & Trade Journal Integration | Planned |
| V2.0 | Production-grade Daily Swing Scanner | Target |

## V1.2.3c - Final Freeze Record

### Frozen architecture

**F15 Composite = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality**

- F20 remains a **shadow sensitivity benchmark**.
- No hard Fundamental-impact score cap is applied.
- Explainable Fundamental impact states:
  - NORMAL: `|impact| < 4 pts`;
  - MATERIAL: `4-6 pts`;
  - HIGH IMPACT: `> 6 pts`.
- REVIEW/FAIL/unavailable Fundamental Quality receives no full Composite score/rank; no neutral imputation.
- F15 remains **shadow-only**. This freeze does **not** give Composite Quality production ranking authority.
- Official Candidate Quality, Leadership, Fundamental Quality, Entry Quality, buckets, event gates and trade decisions remain separately controlled.

### Final live acceptance - S&P 500

Settings: S&P 500 / STRICT / min price $5 / previous-day dollar volume $20M / max deep scan 2000 / strict event gate ON / Fundamental sample 50.

- Scanner audit: 503 universe members; 495 matched; 495 completed SIP bars; 495 deep-scanned; 127 persistent-quality; bucket reconciliation **127/127 PASS**; usable SIP coverage **100%**; missing SIP bars **0**.
- Fundamental batch: CompanyFacts **50/50 PASS**; Integrity **47 PASS / 3 REVIEW / 0 FAIL**; usable coverage **94.0%**.
- V1.2.3b1: **FULL-PRECISION INTEGRITY PASS**.
- V1.2.3c: **INTEGRITY PASS**; F15 rankable **47/50**; F15<->F20 Top-10 **10/10**; Spearman **0.984**; NORMAL **27**; MATERIAL **10**; HIGH IMPACT **10**; median absolute F15 Fundamental impact **3.76 pts**; hard score cap **NONE**.
- Official buckets: 0 ACTIONABLE NOW; 57 TECH+EVENT CHECK; 42 A-QUALITY-WAIT; 2 WAIT/ENTRY NOT READY; 22 DEVELOPING; 4 AVOID/BROKEN = **127/127**.

### Final live acceptance - Russell 2000 (IWM proxy)

Settings: Russell 2000 (IWM proxy) / STRICT / min price $5 / previous-day dollar volume $20M / max deep scan 2000 / strict event gate ON / Fundamental sample 50.

- Scanner audit: 1,954 proxy-universe members; 1,945 matched; 602 deep-scanned; 74 persistent-quality; bucket reconciliation **74/74 PASS**; usable SIP coverage **100%**; missing SIP bars **0**; unmatched symbols disclosed explicitly.
- Fundamental batch: CompanyFacts **50/50 PASS**; Integrity **47 PASS / 3 REVIEW / 0 FAIL**; usable coverage **94.0%**.
- V1.2.3b1: **FULL-PRECISION INTEGRITY PASS**.
- V1.2.3c: **INTEGRITY PASS**; F15 rankable **47/50**; F15<->F20 Top-10 **8/10**; Spearman **0.986**; NORMAL **23**; MATERIAL **12**; HIGH IMPACT **12**; median absolute F15 Fundamental impact **4.14 pts**; hard score cap **NONE**.
- Official buckets: 0 ACTIONABLE NOW; 14 TECH+EVENT CHECK; 51 A-QUALITY-WAIT; 1 WAIT/ENTRY NOT READY; 5 DEVELOPING; 3 AVOID/BROKEN = **74/74**.

### Freeze conclusion

V1.2.3c passed cross-universe live acceptance and is **ACCEPTED / FROZEN**. The architecture mechanics and transparency are accepted; forward trading expectancy remains unproven. F15 must not gain production ranking influence until later validation evidence explicitly authorizes it.

## Current Stage - V1.3a Contextual Volume Quality Engine

### Why Volume comes first

The current scanner already uses volume in limited ways (for example breakout relative-volume confirmation and pullback/VCP contraction), but this is not a complete Volume Quality model. Volume meaning is **setup-dependent**:

- breakout: participation/expansion should confirm demand;
- EMA20 pullback: declining/dry-up volume can be constructive;
- VCP/tightening: contraction should support supply absorption;
- abnormal heavy down-volume/distribution can contradict an otherwise attractive setup.

### Architectural boundary

**Liquidity Quality != Contextual Volume Quality.**

- Liquidity asks: **Can this security be traded efficiently?**
- Contextual Volume Quality asks: **Is participation confirming or contradicting this setup and entry?**

Volume Quality belongs close to **Setup / Entry Quality**, not inside F15 Composite. The initial V1.3a implementation must therefore be **shadow-only**.

### V1.3a research/engineering scope

Candidate features to evaluate before selecting weights:

- current relative volume versus 20D baseline;
- 5D/10D volume trend and dry-up behavior;
- breakout participation/expansion quality;
- pullback volume contraction quality;
- VCP/tightening contraction quality;
- up-day versus down-day volume behavior;
- abnormal distribution / heavy selling-volume count;
- price-volume agreement/divergence;
- volume behavior during recent stress/pullback windows;
- **Volume Data Confidence** based on completed consolidated SIP history, coverage and missingness.

No fixed scoring formula is authorized yet. V1.3a must first expose features and shadow diagnostics, validate them across setup types, and only then propose a Contextual Volume Quality score.

## Outstanding Research / Dependency Register

| ID | Item | Disposition | Destination | Status / rule |
|---|---|---|---|---|
| R-001 | Contextual Volume Quality | **ASSIGNED** | **V1.3a** | OPEN - first V1.3 work item |
| R-002 | Candidate-vs-Entry feature separation | ASSIGNED | V1.3b-V1.3e | Preserve separate truth layers |
| R-003 | Entry location / EMA8-EMA20 extension curve | ASSIGNED | V1.3b | Continuous degradation + hard NO CHASE ceiling |
| R-004 | Trigger / entry-zone architecture | ASSIGNED | V1.3c | Current close must not be the only entry assumption |
| R-005 | Stop-distance / available-R gate | ASSIGNED | V1.3d | Prospective R:R before actionability |
| R-006 | Staged execution A/B/C | DEFERRED / PREP | V1.3f -> V1.6/V1.8 | Shadow logging first; fixed total portfolio risk |
| R-007 | Signal Capture Rate / Missed Opportunity R | ASSIGNED | V1.3f -> V1.7 | Start logging before formal Forward Test Lab |
| R-008 | Earnings/event-date reliability | ASSIGNED | V1.5 | UNKNOWN != safe; separate confidence layer |
| R-009 | F15 production ranking influence | DEFERRED | V1.7+ | Requires outcome evidence; remains shadow |
| R-010 | Stress-window sensitivity research | DEFERRED | V1.7 | Re-test 6/10/12-session variants during validation |
| R-011 | Volume-data confidence / source reliability | ASSIGNED | V1.3a | Completed consolidated SIP, fail-visible coverage |
| R-012 | Relative-strength level/direction/resilience research | RESOLVED / VALIDATE LATER | V1.2.1 + V1.7 | Leadership architecture frozen; outcome validation later |

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `███████████████████░` 95%
- Scanner auditability: `████████████████████` 100%
- Candidate intelligence: `████████████████████` 100% architecture-complete through frozen V1.2.3c; F15 still shadow-only
- Fundamental-performance intelligence: `██████████████████░░` 90%
- Entry intelligence: `████████░░░░░░░░░░░░` 40% - V1.3 now active
- Contextual Volume Quality: `██░░░░░░░░░░░░░░░░░░` 10% - rudimentary inputs exist; formal engine not built
- Event-date confidence: `██░░░░░░░░░░░░░░░░░░` 10%
- Validation/backtesting: `░░░░░░░░░░░░░░░░░░░░` 0%
- Paper execution/journal: `░░░░░░░░░░░░░░░░░░░░` 0%

The percentages describe implementation maturity, not expected trading performance.

## Development Order From Here

**V1.2.3c frozen -> V1.3a Volume -> V1.3b Location/Anti-Chase -> V1.3c Trigger/Zone -> V1.3d R:R -> V1.3e Decision UX -> V1.3f Shadow execution capture -> V1.4 Regime -> V1.5 Events -> V1.6 Risk -> V1.7 Forward Test -> V1.8 Paper -> V2.0.**
