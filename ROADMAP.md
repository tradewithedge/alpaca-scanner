# ALPACA Scanner Project Charter & Roadmap

**Revision:** Rev.7 - V1.3d Risk/Reward Shadow Acceptance  
**Prepared:** 11 September 2026  
**Current accepted/frozen development checkpoint:** V1.3d - Risk/Reward & Stop-Distance Diagnostics (SHADOW)  
**Official decision-layer authority:** unchanged by V1.3c; Candidate Quality, F15 Composite, official Entry Quality, ranking, buckets, event gates and trade decisions remain on the pre-V1.3b official path  
**Current development stage:** V1.3e - READY / WATCH / WAIT / NO CHASE Decision Architecture

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
10. **Hard anti-chase ceilings are ceilings, not targets.** A name can be technically below the hard NO CHASE gate yet already have poor entry location because most of its extension headroom is consumed.

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
| **V1.3b** | **Entry Location & Anti-Chase Foundation** | **ACCEPTED / FROZEN (SHADOW) - 11 Sep 2026** |
| **V1.3c** | **Trigger & Entry-Zone Architecture** | **ACCEPTED / FROZEN (SHADOW) - 13 Sep 2026** |
| **V1.3d** | **Risk/Reward & Stop-Distance Diagnostics** | **ACCEPTED / FROZEN (SHADOW) - 13 Sep 2026** |
| **V1.3e** | **READY / WATCH / WAIT / NO CHASE Decision Architecture** | **NEXT** |
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
- **22/22 dedicated V1.3a tests PASS** covering completed-session handling, immutability, baseline integrity, setup-specific behavior, confidence behavior, distribution accounting, app integration and official-layer isolation.
- The isolated packaging environment did **not** run the entire pre-existing repository regression suite; no broader claim is made.

### Machine-readable live acceptance

**S&P 500 / STRICT:** 127 official candidates / 127 contextual rows; 127/127 exact population match; duplicates 0; official bucket/setup/CQ/EQ mismatches 0; 127/127 HIGH confidence; states 41 CONFIRMING / 38 MIXED / 34 DIAGNOSTIC ONLY / 14 CONFLICT-WATCH.

**Russell 2000 / STRICT controlled same-session run:** 85 official candidates / 85 contextual rows; 85/85 exact population match; duplicates 0; official bucket/setup/CQ/EQ mismatches 0; 85/85 HIGH confidence; states 24 CONFIRMING / 11 MIXED / 13 CONFLICT-WATCH / 37 DIAGNOSTIC ONLY.

### Session-comparability finding

Frozen official `vol_ratio` and V1.3a `rvol_20` diverged sharply when one reflected a partial latest daily bar and the other deliberately used the latest completed session. In a controlled same-completed-session Russell sample, Pearson correlation was **0.999966**, Spearman **0.999790**, and **85/85 values matched at two-decimal precision**.

**Conclusion:** session completeness caused the earlier mismatch. V1.3a's completed-session safeguard is accepted. A future intraday participation metric must use a like-for-like time-of-day baseline.

### V1.3a acceptance boundary

V1.3a acceptance proves architecture/data integrity and official-layer isolation. It does **not** prove trading expectancy and does **not** authorize a 0-100 Volume Quality score, Candidate/F15 weighting, official Entry Quality modification, a production trade gate, or threshold optimization from limited samples.

## V1.3b - Final Freeze Record: Entry Location & Anti-Chase Foundation

**Status:** **ACCEPTED / FROZEN (SHADOW) - 11 Sep 2026**  
**ADR:** `docs/architecture/ADR-003-entry-location-anti-chase-v13b.md`

### Problem addressed

The frozen anti-chase architecture is intentionally hard and binary:

- EMA8 extension hard ceiling: **> 5.0%**;
- EMA20 extension hard ceiling: **> 8.0%**;
- EMA20 extension in ATR units hard ceiling: **> 2.0 ATR**.

That protects the system from obvious chasing, but a binary gate hides deterioration before the breach. A stock at 99% of a hard ceiling and a stock at 20% of the same ceiling are both technically "not chase" under a binary rule, even though their entry-location quality is very different.

### Frozen V1.3b shadow architecture

V1.3b measures continuous positive extension pressure against the **existing frozen hard ceilings** without relaxing them:

- `EMA8 pressure = max(0, EMA8 extension) / 5.0%`;
- `EMA20 pressure = max(0, EMA20 extension) / 8.0%`;
- `ATR pressure = max(0, EMA20 ATR extension) / 2.0 ATR`;
- dominant/max chase pressure = maximum of the three axes;
- hard-ceiling headroom = `100% - max pressure`.

The hard NO CHASE rule remains strict `>` exactly as before. **100% pressure means at the ceiling, not beyond it.** A breach occurs only above 100% on at least one axis.

Shadow diagnostic states:

- **REPAIR / BELOW EMA20:** EMA20 extension < -1.5%;
- **PRIME / CONTROLLED:** max pressure <= 40% and EMA20 extension <= 3.0%;
- **ACCEPTABLE:** max pressure <= 65%;
- **STRETCHED:** max pressure <= 85%;
- **VERY LATE / AT CEILING:** below the hard breach but above the STRETCHED band, including exactly at a hard ceiling;
- **NO CHASE — HARD CEILING:** at least one frozen official ceiling is exceeded;
- **NOT RANKED:** required extension inputs are incomplete.

These bands are accepted as **shadow diagnostic reference bands**, not as proven expectancy-optimal production gates.

### Integrity controls

- The V1.3b table is separate from the official scored frame.
- Official Candidate Quality, F15 Composite, Entry Quality, ranking, buckets, event gates and trade decisions are not modified.
- V1.3b independently recomputes hard NO CHASE and exposes **hard-no-chase parity** versus the frozen official gate.
- Missing required inputs produce **NOT RANKED / LOW confidence**; no neutral location conclusion is imputed.
- No new 0-100 production Entry Location score is authorized.

### Offline implementation validation

- `py_compile`: PASS.
- Targeted unit/regression/integration validation: **53/53 PASS**.
- Offline replay on previously accepted machine-readable S&P and Russell populations showed full hard-NO-CHASE parity and official-field reconciliation. Replay evidence was treated as engineering smoke testing, not live acceptance.

### Live acceptance - S&P 500 / STRICT

Full Swing Candidates and full Entry Location Diagnostic CSVs were reconciled programmatically:

- official candidates: **119**;
- Entry Location diagnostic rows: **119**;
- exact symbol population match: **119/119**;
- duplicate symbols: **0**;
- Candidate Quality mismatches: **0**;
- Entry Quality mismatches: **0**;
- official bucket mismatches: **0**;
- official setup mismatches: **0**;
- Location Data Confidence: **119/119 HIGH**;
- independent hard NO CHASE parity: **119/119 PASS**;
- states: **68 PRIME/CONTROLLED / 11 ACCEPTABLE / 6 STRETCHED / 4 VERY LATE / 25 REPAIR / 5 HARD NO CHASE = 119/119**;
- near-ceiling non-hard watch (75%-<100% pressure): **5**;
- official ACTIONABLE/TECH ACTIONABLE names already STRETCHED or VERY LATE: **0 - not observed in this sample**.

Representative pre-breach names included DVN at **95.62%**, CVX **94.81%**, HPQ **94.77%**, COP **93.03%**, and ELV **79.80%** max pressure. Hard-breach names included SWKS, VLO, META, PSX and MPC.

### Live acceptance - Russell 2000 (IWM proxy) / STRICT

Controls included strict earnings/event gate **ON**.

- official candidates: **85**;
- Entry Location diagnostic rows: **85**;
- exact symbol population match: **85/85**;
- duplicate symbols: **0**;
- Candidate Quality mismatches: **0**;
- Entry Quality mismatches: **0**;
- official bucket mismatches: **0**;
- official setup mismatches: **0**;
- Location Data Confidence: **85/85 HIGH**;
- independent hard NO CHASE parity: **85/85 PASS**;
- states: **36 PRIME/CONTROLLED / 16 ACCEPTABLE / 10 STRETCHED / 5 VERY LATE / 12 REPAIR / 6 HARD NO CHASE = 85/85**;
- near-ceiling non-hard watch (75%-<100% pressure): **10**;
- official ACTIONABLE/TECH ACTIONABLE names already STRETCHED or VERY LATE: **0 - not observed in this sample**.

Representative pre-breach names included **CRGY at 99.56% max pressure**, TXG 98.85%, ANF 94.70%, CRC 90.44% and AVAH 90.02%. CRGY is a canonical illustration of the architectural purpose: it had only **0.44% normalized hard-ceiling headroom** left while the legacy binary gate still correctly remained "not chase" because no frozen ceiling had yet been exceeded.

### Cross-universe conclusion

The shadow layer exposed substantially more near-ceiling pressure in Russell than S&P without changing any official decision:

- S&P HARD NO CHASE: **5/119 = 4.2%**; Russell: **6/85 = 7.1%**;
- S&P near-ceiling 75%-<100%: **5/119 = 4.2%**; Russell: **10/85 = 11.8%**;
- S&P non-hard STRETCHED + VERY LATE: **10/119 = 8.4%**; Russell: **15/85 = 17.6%**.

This is accepted as useful continuous location information, not proof that the research bands improve future returns.

### V1.3b acceptance boundary

V1.3b is frozen as a **SHADOW entry-location architecture**. Acceptance proves measurement integrity, hard-gate parity, official-layer isolation and cross-universe behavior. It does **not** authorize:

- replacement or relaxation of the frozen hard NO CHASE ceilings;
- modification of official Entry Quality;
- automatic bucket downgrades from PRIME/ACCEPTABLE/STRETCHED/VERY LATE labels;
- a new production Entry Location score;
- claims that the diagnostic bands are expectancy-optimal.

Outcome value and threshold calibration remain dependencies of **V1.7 Expectancy Validation / Backtest / Forward-Test Lab**.

## V1.3c - Final Freeze Record: Trigger & Entry-Zone Architecture

**Status:** **ACCEPTED / FROZEN (SHADOW) - 13 Sep 2026**  
**ADR:** `docs/architecture/ADR-004-trigger-entry-zone-v13c.md`

### Problem addressed

The frozen scanner still used the current close as the practical `entry_px` reference. That is useful as a snapshot, but it does not define an executable plan for a trader who must wait for a structural trigger and avoid chasing after the move.

V1.3c therefore separates:

- observed current price;
- structural trigger;
- confirmation condition;
- preferred entry zone;
- maximum acceptable fill;
- frozen hard NO CHASE boundary.

### Frozen V1.3c shadow architecture

V1.3c is a separate planning layer. It does **not** rewrite the frozen official `entry_px`, stop, T1, T2, Candidate Quality, F15 Composite, Entry Quality, ranking, buckets, event gates or trade decisions.

Reference trigger logic is setup-aware:

- **Breakout:** prior-20-session structure high + small confirmation buffer;
- **EMA20 Pullback:** EMA20 / prior-session-high reclaim structure;
- **VCP / Tight Base:** prior-10-session structure high;
- **MA20 Repair:** reclaim structure is diagnostic, not an automatic actionability decision;
- **No clean setup / Broken:** no invented structured plan.

The preferred entry zone extends **0.25 ATR** above the structural trigger. The raw maximum acceptable fill extends **0.50 ATR** above the trigger, then is capped by the frozen V1.3b hard NO CHASE ceiling. These values are **research references only**, not proven production thresholds.

If the structural trigger itself is beyond the frozen hard ceiling, V1.3c **BLOCKS** the plan rather than moving the ceiling.

### State model

The shadow state vocabulary is:

- **WAITING FOR TRIGGER**;
- **TRIGGERED - IN ENTRY ZONE**;
- **TRIGGERED - ABOVE ZONE / LATE**;
- **MISSED / NO CHASE - ABOVE MAX FILL**;
- **BLOCKED - TRIGGER BEYOND HARD CEILING**;
- **NO STRUCTURED PLAN**.

The state model is descriptive. It is not a production decision gate.

### Live machine-readable acceptance - S&P 500 / STRICT

Full Swing Candidates and full V1.3c Trigger/Entry-Zone Diagnostic CSVs were reconciled:

- official candidates: **116**;
- diagnostic rows: **116**;
- exact symbol population match: **116/116**;
- duplicate symbols: **0** in both files;
- official bucket/setup/CQ/EQ/legacy `entry_px` mismatches: **0/116**;
- current-price equality: **115/116 exact; 116/116 within $0.01 export rounding**;
- Plan Data Confidence: **116/116 HIGH**;
- prior-20 structure parity: **116/116 PASS**;
- state reconciliation: **116/116**;
- states: **63 WAITING / 12 IN ENTRY ZONE / 4 ABOVE ZONE-LATE / 2 MISSED-NO CHASE / 7 BLOCKED / 28 NO STRUCTURED PLAN**.

Representative states included AAPL/TMO/MSFT/COIN in the preferred entry zone; IQV/T/PFG/NTRS above the preferred zone but still below the maximum fill; HPQ/TRV beyond maximum fill and correctly marked MISSED/NO CHASE.

### Live machine-readable acceptance - Russell 2000 (IWM proxy) / STRICT

- official candidates: **90**;
- diagnostic rows: **90**;
- exact symbol population match: **90/90**;
- duplicate symbols: **0** in both files;
- official bucket/setup/CQ/EQ/legacy `entry_px` mismatches: **0/90**;
- current-price equality: **90/90**;
- Plan Data Confidence: **90/90 HIGH**;
- prior-20 structure parity: **90/90 PASS**;
- state reconciliation: **90/90**;
- states: **42 WAITING / 2 IN ENTRY ZONE / 2 ABOVE ZONE-LATE / 1 MISSED-NO CHASE / 11 BLOCKED / 32 NO STRUCTURED PLAN**.

Representative states included URBN/CNXC in the preferred entry zone, DAN/EWTX above the preferred zone but not beyond maximum fill, and HOG correctly marked MISSED/NO CHASE.

### Cross-universe acceptance conclusion

S&P 500 and Russell 2000 both passed the architecture/integrity requirements. The independent trigger/zone layer preserves the frozen official decision path while producing a practical execution map. The architecture is therefore **ACCEPTED / FROZEN (SHADOW)**.

### Acceptance boundary

This freeze proves:

- separation of current price from planned entry;
- independent prior-20 structural reconstruction;
- setup-aware trigger planning;
- preferred entry-zone and maximum-fill calculation;
- hard-ceiling blocking without ceiling relaxation;
- official-layer isolation;
- machine-readable cross-universe reconciliation.

It does **not** prove:

- that 0.25 ATR is the optimal entry-zone width;
- that 0.50 ATR is the optimal maximum-fill width;
- that any V1.3c state has positive expectancy;
- that V1.3c should modify official Entry Quality or production buckets.

Those questions remain assigned to **V1.7 Expectancy Validation / Backtest / Forward-Test Lab**.

## Validation Evidence Standard

Effective with the V1.3a freeze and reinforced by V1.3b:

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

Screenshots remain useful for deployed version, selected controls/settings, integrity banners, headline counts, UI/UX behavior and visible deployment regressions. Screenshots alone must not freeze a quantitative engine when full CSV/data evidence can be exported.

### Export rule

A table may be visually capped for dashboard readability, but quantitative acceptance must use a full underlying export or a full audit table. A capped display export is not proof of the complete population.

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

The forward dataset should preserve, at minimum: signal timestamp, setup/context, Candidate Quality, relevant Leadership/Fundamental/Composite states, Entry Quality, Contextual Volume state, **Entry Location state/pressure/headroom**, planned entry/zone/trigger, stop, targets, event/regime state, trigger time, fill/no-fill, slippage, invalidation, MAE/MFE, exit path, realized R and Missed Opportunity R.

### Acceptance discipline

A positive point estimate alone is insufficient. Expectancy evidence should include sample size and, where practical, dispersion, confidence intervals/bootstrap ranges, drawdown, stability across time/universes/regimes/setups and sensitivity to realistic execution assumptions.

V1.7 should evaluate conditional expectancy by setup, Candidate Quality, Entry Quality, Contextual Volume state, **Entry Location state/pressure**, trigger type, regime and event confidence to identify **where edge actually exists**.

## Outstanding Research / Dependency Register

| ID | Item | Disposition | Destination | Status / rule |
|---|---|---|---|---|
| R-001 | Contextual Volume Quality diagnostics architecture | **RESOLVED / FROZEN SHADOW** | **V1.3a** | Architecture accepted; outcome value/threshold calibration deferred to V1.7 evidence |
| R-002 | Candidate-vs-Entry feature separation | ASSIGNED | V1.3b-V1.3e | Preserve separate truth layers |
| R-003 | Entry location / EMA8-EMA20 extension curve | **RESOLVED / FROZEN SHADOW** | **V1.3b** | Continuous pressure/headroom accepted; production thresholds/expectancy deferred to V1.7 |
| R-004 | Trigger / entry-zone architecture | **RESOLVED / FROZEN SHADOW** | **V1.3c** | Trigger/zone/max-fill architecture accepted; parameter expectancy deferred to V1.7 |
| R-005 | Stop-distance / available-R gate | **ASSIGNED** | **V1.3d** | Prospective R:R before actionability |
| R-006 | Staged execution A/B/C | DEFERRED / PREP | V1.3f -> V1.6/V1.8 | Shadow logging first; fixed total portfolio risk |
| R-007 | Signal Capture Rate / Missed Opportunity R | ASSIGNED | V1.3f -> V1.7 | Start logging before formal lab; diagnostics underneath expectancy |
| R-008 | Earnings/event-date reliability | ASSIGNED | V1.5 | UNKNOWN != safe; separate confidence layer |
| R-009 | F15 production ranking influence | DEFERRED | V1.7+ | Requires outcome evidence; remains shadow |
| R-010 | Stress-window sensitivity research | DEFERRED | V1.7 | Re-test 6/10/12-session variants during validation |
| R-011 | Volume-data confidence / completed-session reliability | **RESOLVED / FROZEN** | V1.3a | Completed SIP sessions + fail-visible confidence accepted |
| R-012 | Relative-strength level/direction/resilience research | RESOLVED / VALIDATE LATER | V1.2.1 + V1.7 | Leadership architecture frozen; outcome validation later |
| **R-013** | **Trading expectancy / edge validation** | **ASSIGNED** | **V1.7** | **Central KPI; validate signal, entry/trigger, captured, realized, missed and net expectancy using Backtest + Forward-Test evidence** |
| R-014 | READY / WATCH / WAIT / NO CHASE mapping | ASSIGNED | V1.3e | Decision-first output; never weaken standards to populate a list |
| R-015 | Entry Location band expectancy / calibration | DEFERRED / VALIDATE | V1.7 | Test PRIME/ACCEPTABLE/STRETCHED/VERY LATE outcome separation before any production authority |

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `███████████████████░` 95%
- Scanner auditability: `████████████████████` 100%
- Candidate intelligence: `████████████████████` 100% architecture-complete through frozen V1.2.3c; F15 still shadow-only
- Fundamental-performance intelligence: `██████████████████░░` 90%
- Entry intelligence: `███████████████░░░░░` 75% - V1.3a/V1.3b/V1.3c shadow architecture accepted; V1.3d next
- Contextual Volume Quality diagnostics: `████████████████████` 100% - shadow architecture accepted; production scoring/expectancy deliberately unproven
- Entry Location / Anti-Chase diagnostics: `████████████████████` 100% - shadow architecture accepted; production use/expectancy deliberately unproven
- Event-date confidence: `██░░░░░░░░░░░░░░░░░░` 10%
- Expectancy validation / Backtest / Forward Test: `░░░░░░░░░░░░░░░░░░░░` 0%
- Paper execution/journal: `░░░░░░░░░░░░░░░░░░░░` 0%

The percentages describe implementation maturity, not expected trading performance.

## Development Order From Here

**V1.3a frozen -> V1.3b frozen -> V1.3c Trigger/Zone frozen -> V1.3d R:R -> V1.3e Decision UX -> V1.3f Shadow execution capture -> V1.4 Regime -> V1.5 Events -> V1.6 Risk -> V1.7 Expectancy Validation / Backtest / Forward Test -> V1.8 Paper -> V2.0.**


## V1.3d - Risk/Reward & Stop-Distance Shadow Opening

### Objective
V1.3d adds a transparent risk-geometry layer after the frozen V1.3c trigger/entry-zone architecture. It answers: **if the structural trigger occurs, where is the structural stop, how much R is available, and how quickly does R:R deteriorate as the fill moves through the entry zone?**

### Frozen dependencies
- V1.2.3c F15 architecture remains frozen.
- V1.3a contextual volume remains shadow/frozen.
- V1.3b Entry Location / Anti-Chase remains shadow/frozen.
- V1.3c Trigger / Entry Zone remains shadow/frozen.
- V1.3d must never rewrite official `entry_px`, `stop`, `t1`, `t2`, Entry Quality, Candidate Quality, ranking, buckets, event gates or trade decisions.

### Shadow architecture
V1.3d consumes V1.3c `trigger_price`, `entry_zone_high` and `max_acceptable_fill`. It derives a structural support reference from available EMA20 / prior-10 low / prior-20 low, then places a provisional stop 0.25 ATR below that support. It calculates T1 at 1.5R and T2 at 2.5R from the trigger reference.

R:R is calculated separately at:
1. trigger price;
2. preferred entry-zone high;
3. maximum acceptable fill.

Research bands:
- STRONG: >= 2.0R
- ACCEPTABLE: 1.5R to <2.0R
- WEAK: 1.0R to <1.5R
- POOR: <1.0R
- NOT RANKED: missing/invalid critical inputs

These bands and the 0.25 ATR stop buffer are **research references only**. They are not production gates and are not expectancy-proven.

### Why this design
A single R:R number at the current close hides execution deterioration. The same setup can be attractive at the structural trigger but unattractive at the high end of the preferred zone or maximum fill. V1.3d therefore exposes the full geometry rather than manufacturing a binary pass/fail.

### Non-negotiable safety rules
1. Good R:R cannot rescue broken/poor price structure.
2. A blocked or missed/no-chase V1.3c plan remains non-entry diagnostic state.
3. No neutral/average imputation for missing risk inputs.
4. No target/stop adjustment solely to manufacture a desired R multiple.
5. Official-layer integrity must be checked with a deep-copy equality invariant.
6. Outcome validation belongs to Backtest + Forward Test + Expectancy work, not this shadow phase.

### Acceptance criteria for V1.3d
- Application compiles.
- Shadow module has no dependency on official scoring logic.
- Official `scored` frame is unchanged after shadow construction.
- V1.3c diagnostic rows remain the sole planning input for trigger/zone/max-fill.
- Structural stop is transparent and strictly below planned entry references when ranked.
- R:R is separately available at trigger, zone high and max fill.
- Missing/invalid risk data is NOT RANKED, never imputed.
- UI explicitly labels the layer SHADOW and preserves the official decision layer.
- Existing V1.3b/V1.3c focused tests remain passing.

### Current validation status
Local focused validation completed for the V1.3d implementation: **80 tests PASS** across V1.3b/V1.3c/V1.3d focused suites. This is not a claim of the complete historical repository regression suite. Live universe validation is still pending.

### Research boundary
V1.3d does not prove that 2R is the correct threshold, that 1.5R/2.5R are optimal targets, or that 0.25 ATR is the correct stop buffer. These parameters must later be tested across historical and prospective samples. The central outcome metric remains **expectancy**, with Backtest and Forward-Test evidence.
