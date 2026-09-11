# ALPACA Scanner Project Charter & Roadmap

**Revision:** Rev.3 - V1.3a Freeze / Validation Evidence Standard / V1.7 Expectancy Clarification  
**Prepared:** 11 September 2026  
**Current accepted/frozen development checkpoint:** V1.3a - Contextual Volume Quality Diagnostics (SHADOW)  
**Official decision-layer authority:** unchanged by V1.3a; Candidate Quality, Entry Quality, buckets, event gates and trade decisions remain on the pre-V1.3a official path  
**Next development stage:** V1.3b - Entry Location & Anti-Chase Foundation

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
9. **Quantitative acceptance requires machine-readable evidence.** Screenshots prove deployment/UI state; they are not sufficient by themselves to freeze a quantitative engine when full-population CSV/data evidence can be produced.

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
- **REJECTED** - excluded deliberately with rationale;
- **RESOLVED / FROZEN** - accepted at the named stage, while any later outcome-validation dependency remains explicitly mapped.

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
| **V1.3a** | **Contextual Volume Quality Diagnostics** | **ACCEPTED / FROZEN (SHADOW) - 11 Sep 2026** |
| **V1.3b** | **Entry Location & Anti-Chase Foundation** | **NEXT / DESIGN** |
| V1.3c | Trigger & Entry-Zone Architecture | Planned |
| V1.3d | Risk/Reward & Stop-Distance Gate | Planned |
| V1.3e | READY / WATCH / WAIT / NO CHASE Decision Architecture | Planned |
| V1.3f | Shadow Execution-Capture Logging / staged-execution preparation | Planned |
| V1.4 | Market Regime & Deployment Engine | Planned |
| V1.5 | Earnings / Event Reliability Layer | Planned |
| V1.6 | Trade Plan & Portfolio Risk Engine | Planned |
| **V1.7** | **Expectancy Validation / Backtest / Forward-Test Lab** | **Planned** |
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

## V1.3a - Final Freeze Record: Contextual Volume Quality Diagnostics

**Status:** **ACCEPTED / FROZEN (SHADOW) - 11 Sep 2026**  
**ADR:** `docs/architecture/ADR-002-contextual-volume-quality-v13a.md`

### Frozen V1.3a architecture

V1.3a is a setup-aware **diagnostic layer**, not a new production score.

- Price structure is classified first, independently of the new volume diagnostics.
- Volume evidence uses completed consolidated SIP daily sessions.
- A same-day daily bar is excluded before the conservative **16:30 ET** completion cutoff.
- Volume Data Confidence is explicit; LOW confidence is **NOT RANKED**, not neutrally imputed.
- Diagnostic features include completed-session RVOL versus prior 20 sessions, non-overlapping 5D/10D volume trend, up/down-volume participation, up-volume share, accumulation days and distribution days.
- Breakouts seek volume expansion/participation.
- EMA20 pullbacks, VCP/tightening and tight bases seek controlled contraction/dry-up.
- Broken price structure cannot be rescued by favorable volume.
- No 0-100 Contextual Volume Quality score is authorized.
- V1.3a returns a separate shadow table and does not merge its features into official Candidate Quality, Entry Quality, ranking, buckets, event gates or trade decisions.

### Offline implementation validation

- `py_compile` passed for the V1.3a application/module/tests.
- **22/22 dedicated V1.3a tests PASS**:
  - completed-session exclusion/inclusion;
  - immutability;
  - prior-20 baseline integrity;
  - breakout expansion/conflict behavior;
  - pullback dry-up behavior;
  - LOW-confidence NOT RANKED;
  - distribution-watch accounting;
  - app/static integration and official-layer isolation.
- This record does **not** claim that the full pre-existing repository regression suite was run in the isolated V1.3a packaging environment.

### Live acceptance - S&P 500 / STRICT

Machine-readable evidence from full Swing Candidates and full Contextual Volume Diagnostic exports:

- official candidates: **127**;
- contextual-volume rows: **127**;
- unique symbols: **127/127**; duplicates **0**;
- population match: **127/127 exact**;
- official bucket mismatches: **0**;
- official setup mismatches: **0**;
- Candidate Quality mismatches: **0**;
- Entry Quality mismatches: **0**;
- Volume Data Confidence: **127/127 HIGH**;
- evaluation session: **2026-09-04** for all 127 candidates;
- states: **41 CONFIRMING / 38 MIXED / 34 DIAGNOSTIC ONLY / 14 CONFLICT-WATCH = 127/127**;
- contexts: **83 EMA20 PULLBACK / 35 NO CLEAN SETUP / 4 BREAKOUT / 4 MA20 REPAIR / 1 TIGHT BASE = 127/127**.

This sample showed useful contextual discrimination rather than a universal high-volume rule. It also raised legitimate future calibration questions, such as whether strong multi-session accumulation can partially offset weak single-session breakout RVOL. Those questions remain research/outcome-validation questions; they are not integrity failures.

### Live acceptance - Russell 2000 (IWM proxy) / STRICT

Final controlled same-session machine-readable run before U.S. pre-market:

- official candidates: **85**;
- contextual-volume rows: **85**;
- unique symbols: **85/85**; duplicates **0**;
- population match: **85/85 exact**;
- official bucket mismatches: **0**;
- official setup mismatches: **0**;
- Candidate Quality mismatches: **0**;
- Entry Quality mismatches: **0**;
- Volume Data Confidence: **85/85 HIGH**;
- evaluation session: **2026-09-10** for all 85 candidates;
- states: **24 CONFIRMING / 11 MIXED / 13 CONFLICT-WATCH / 37 DIAGNOSTIC ONLY = 85/85**;
- contexts: **39 EMA20 PULLBACK / 24 NO CLEAN SETUP / 12 MA20 REPAIR / 5 BREAKOUT / 3 BROKEN-BELOW-MA50 / 2 VCP-TIGHTENING = 85/85**.

### Session-comparability finding

During validation, frozen official `vol_ratio` and V1.3a `rvol_20` sometimes diverged sharply intraday. This was investigated as a data-timing question rather than treated as a formula defect.

Three Russell comparisons showed:

| Timing condition | Pearson correlation: official `vol_ratio` vs V1.3a `rvol_20` | Interpretation |
|---|---:|---|
| Regular-session / partial daily bar present | ~0.043 | Different session completeness; not like-for-like |
| Pre-market/session-mismatch sample | ~0.580 | Partially aligned but still not same evaluation session |
| **Controlled pre-pre-market same completed session** | **0.999966** | Essentially identical underlying RVOL concept |

In the controlled 85-stock run:

- Spearman correlation: **0.999790**;
- mean official `vol_ratio`: **0.98847x**;
- mean V1.3a `rvol_20`: **0.98859x**;
- **85/85 values matched when rounded to 2 decimals**.

**Conclusion:** the earlier disagreement was caused by session comparability: a partial/latest daily bar versus a deliberately completed-session bar. V1.3a's completed-session safeguard is accepted. The frozen legacy `vol_ratio` is **not silently rewritten** in V1.3a. A future intraday participation/volume-pace metric, if desired, must compare like-for-like time-of-day participation and requires its own evidence.

### V1.3a acceptance boundary

V1.3a acceptance proves architecture/data integrity and official-layer isolation. It does **not** prove trading expectancy and does **not** authorize:

- a 0-100 Volume Quality score;
- Contextual Volume weighting inside Candidate Quality or F15;
- changes to official Entry Quality;
- a new production trade gate;
- threshold optimization based on one or a few live samples.

Outcome value and threshold calibration remain subject to later Backtest / Forward-Test expectancy evidence.

## Validation Evidence Standard

Effective with the V1.3a freeze:

### Quantitative acceptance evidence

When a stage makes quantitative claims, acceptance should use the full machine-readable population whenever available. At minimum, validate as applicable:

- requested rows versus exported rows;
- unique-symbol/population reconciliation;
- duplicates and null/missingness;
- frozen-layer/copy equality;
- state/bucket count reconciliation;
- confidence/data-quality coverage;
- cross-universe behavior;
- timestamp/session alignment;
- threshold/outlier/borderline cases.

### Role of screenshots

Screenshots remain useful for:

- deployed version;
- selected controls/settings;
- integrity banners;
- headline counts;
- UI/UX behavior;
- visible deployment regressions.

Screenshots alone must not freeze a quantitative engine when full CSV/data evidence can be exported.

### Export rule

A table may be visually capped for dashboard readability, but quantitative acceptance must use a full underlying export or a full audit table. A capped display export (for example `head(40)`) is not proof of the complete population.

## Planned Stage - V1.7 Expectancy Validation / Backtest / Forward-Test Lab

### Governing question

V1.7 must answer:

> **Does the system produce positive, repeatable trading expectancy after realistic execution friction and missed opportunities?**

**Backtesting remains an explicit and mandatory part of V1.7. It is not replaced by forward testing.** Historical backtests and prospective forward tests answer different failure modes and must be reconciled.

Basic R-multiple reference:

`Expectancy = Win Rate x Average Win (R) - Loss Rate x Average Loss (R)`

### Expectancy hierarchy

| Layer | Question |
|---|---|
| **Signal Expectancy** | Did the scanner identify opportunities with positive expectancy under the predefined trade plan? |
| **Entry / Trigger Expectancy** | Does the selected entry/trigger architecture improve or damage the underlying signal expectancy? |
| **Captured Expectancy** | How much of available signal expectancy was actually captured by the execution process? |
| **Realized Expectancy** | What R was actually realized after fills, stops, partial exits and slippage? |
| **Missed Expectancy** | How much positive opportunity was identified but not captured because of no-fill, latency, invalidation or execution rules? |
| **Net Expectancy** | What expectancy remains after realistic transaction costs, slippage and execution friction? |

Signal Capture Rate and Missed Opportunity R are diagnostic KPIs **underneath expectancy**, not substitutes for expectancy.

### Backtest role

Backtesting must provide broader historical sample size and regime diversity while controlling for hindsight and overfitting:

- timestamp-correct feature availability / no look-ahead leakage;
- reconstruction using only information available at decision time;
- realistic entry/trigger, stop, target, slippage and transaction-cost assumptions;
- out-of-sample / walk-forward validation;
- segmentation across periods, regimes, setup types and universes;
- explicit no-fill, gap-through, invalidated-before-entry and competing-trigger treatment;
- parameter sensitivity / robustness testing.

### Forward-test role

Forward testing records signals prospectively before outcomes are known. V1.3f begins the logging foundation so V1.7 is not forced to reconstruct execution history from hindsight.

The forward dataset should preserve, at minimum: signal timestamp, setup/context, Candidate Quality, relevant Leadership/Fundamental/Composite states, Entry Quality, Contextual Volume state, planned entry/zone/trigger, stop, targets, event/regime state, trigger time, fill/no-fill, slippage, invalidation, MAE/MFE, exit path, realized R and Missed Opportunity R.

### Acceptance discipline

A positive point estimate alone is insufficient. Expectancy evidence should include sample size and, where practical, dispersion, confidence intervals/bootstrap ranges, drawdown, stability across time/universes/regimes/setups and sensitivity to realistic execution assumptions.

V1.7 should evaluate conditional expectancy by setup, Candidate Quality, Entry Quality, Contextual Volume state, extension/location, trigger type, regime and event confidence to identify **where edge actually exists**.

## Outstanding Research / Dependency Register

| ID | Item | Disposition | Destination | Status / rule |
|---|---|---|---|---|
| R-001 | Contextual Volume Quality diagnostics architecture | **RESOLVED / FROZEN SHADOW** | **V1.3a** | Architecture accepted; outcome value/threshold calibration deferred to V1.7 evidence |
| R-002 | Candidate-vs-Entry feature separation | ASSIGNED | V1.3b-V1.3e | Preserve separate truth layers |
| R-003 | Entry location / EMA8-EMA20 extension curve | ASSIGNED | V1.3b | Continuous degradation + hard NO CHASE ceiling |
| R-004 | Trigger / entry-zone architecture | ASSIGNED | V1.3c | Current close must not be the only entry assumption |
| R-005 | Stop-distance / available-R gate | ASSIGNED | V1.3d | Prospective R:R before actionability |
| R-006 | Staged execution A/B/C | DEFERRED / PREP | V1.3f -> V1.6/V1.8 | Shadow logging first; fixed total portfolio risk |
| R-007 | Signal Capture Rate / Missed Opportunity R | ASSIGNED | V1.3f -> V1.7 | Start logging before formal lab; diagnostics underneath expectancy |
| R-008 | Earnings/event-date reliability | ASSIGNED | V1.5 | UNKNOWN != safe; separate confidence layer |
| R-009 | F15 production ranking influence | DEFERRED | V1.7+ | Requires outcome evidence; remains shadow |
| R-010 | Stress-window sensitivity research | DEFERRED | V1.7 | Re-test 6/10/12-session variants during validation |
| R-011 | Volume-data confidence / completed-session reliability | **RESOLVED / FROZEN** | V1.3a | Completed SIP sessions + fail-visible confidence accepted |
| R-012 | Relative-strength level/direction/resilience research | RESOLVED / VALIDATE LATER | V1.2.1 + V1.7 | Leadership architecture frozen; outcome validation later |
| **R-013** | **Trading expectancy / edge validation** | **ASSIGNED** | **V1.7** | **Central KPI; validate signal, entry/trigger, captured, realized, missed and net expectancy using Backtest + Forward-Test evidence** |
| R-014 | READY / WATCH / WAIT / NO CHASE mapping | ASSIGNED | V1.3e | Decision-first output; never weaken standards to populate a list |

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `███████████████████░` 95%
- Scanner auditability: `████████████████████` 100%
- Candidate intelligence: `████████████████████` 100% architecture-complete through frozen V1.2.3c; F15 still shadow-only
- Fundamental-performance intelligence: `██████████████████░░` 90%
- Entry intelligence: `█████████░░░░░░░░░░░` 45% - V1.3a accepted; V1.3b next
- Contextual Volume Quality diagnostics: `████████████████████` 100% - shadow architecture accepted; production scoring/expectancy deliberately unproven
- Event-date confidence: `██░░░░░░░░░░░░░░░░░░` 10%
- Expectancy validation / Backtest / Forward Test: `░░░░░░░░░░░░░░░░░░░░` 0%
- Paper execution/journal: `░░░░░░░░░░░░░░░░░░░░` 0%

The percentages describe implementation maturity, not expected trading performance.

## Development Order From Here

**V1.3a frozen -> V1.3b Location/Anti-Chase -> V1.3c Trigger/Zone -> V1.3d R:R -> V1.3e Decision UX -> V1.3f Shadow execution capture -> V1.4 Regime -> V1.5 Events -> V1.6 Risk -> V1.7 Expectancy Validation / Backtest / Forward Test -> V1.8 Paper -> V2.0.**
