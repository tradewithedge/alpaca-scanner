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
6. **No major freeze without a development record.** Update the Development Chronicle and any major Architecture Decision Record before declaring a major stage frozen.

When proposing a feature, first ask: **Which roadmap stage does this belong to?**

## Roadmap

| Version | Objective | Status |
|---|---|---|
| V1.0 | Working Alpaca + Streamlit scanner architecture | Complete / Frozen |
| V1.1 | Explicit universes + persistent quality screening | Complete / Frozen |
| V1.1.1 | Consolidated SIP data integrity | Complete / Frozen |
| V1.1.2 | Scanner Audit Integrity | Complete / Frozen |
| V1.2 | Candidate Quality Engine | **CURRENT** |
| V1.2.1 | Relative Leadership & Market-Stress Resilience | Complete / Frozen |
| V1.2.1.1 | Leadership explainability | Complete / Frozen |
| V1.2.1.2–V1.2.1.3c | Ticker Inspector utility/reference engine | Complete / Frozen |
| V1.2.2 | Fundamental Quality Engine | Complete / Frozen |
| V1.2.2.3 | Fundamental Universe Coverage & Cache Validation | Complete / Frozen |
| V1.2.2.2 | Fundamental Metric Integrity & Cross-Company Validation | Complete / Frozen |
| V1.2.2.2a–V1.2.2.2a1 | Concept continuity + annual horizon integrity | Complete / Frozen |
| V1.2.2.1 | Revenue & Earnings Growth — shadow validation | Complete / superseded |
| V1.2.2.1a–V1.2.2.1b1 | SEC access / identity / Fair Access integrity | Complete / Frozen |
| V1.2.3 | Composite Candidate Quality Integration — Shadow Calibration | Calibration captured / not frozen |
| V1.2.3a | Composite Attribution & Incremental Fundamental Impact | Accepted / Frozen |
| V1.2.3b | Composite Weight Robustness & Guardrail Calibration | S&P evidence captured / precision fix required |
| V1.2.3b1 | Full-Precision Robustness Integrity Fix | Accepted / Frozen |
| V1.2.3b2 | Pre-Revenue / Zero-Revenue Domain Integrity | Accepted / Frozen |
| V1.2.3c | Composite Architecture Selection & Explainable Guardrail Layer | **IMPLEMENTED / READY FOR LIVE ACCEPTANCE** |
| V1.3 | Entry Quality / Anti-Chase Engine | Planned |
| V1.4 | Market Regime & Deployment Engine | Planned |
| V1.5 | Earnings / Event Reliability Layer | Planned |
| V1.6 | Trade Plan & Risk Engine | Planned |
| V1.7 | Validation / Backtest / Forward-test Framework | Planned |
| V1.8 | Paper Trading & Trade Journal Integration | Planned |
| V2.0 | Production-grade Daily Swing Scanner | Target |

## Current Stage — V1.2.3c Composite Architecture Selection & Explainable Guardrail Layer

### Architecture decision

The completed S&P 500 and Russell 2000 calibration selects **F15** as the primary Composite Quality architecture candidate:

- Internal formula: **59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality**.
- Equivalent construction: `85% × (70% CQ + 30% Leadership) + 15% Fundamental`.
- **F20 remains a shadow sensitivity benchmark.**
- **No hard ±6/±8 score cap is selected** for the initial V1.2.3c implementation.
- Instead, expose incremental Fundamental impact as:
  - NORMAL: `|impact| < 4 pts`;
  - MATERIAL: `4–6 pts`;
  - HIGH IMPACT: `>6 pts`.
- REVIEW/FAIL/unavailable fundamentals remain unranked for full Composite; no neutral/average imputation.
- Candidate Quality, Leadership, Fundamental Quality, Composite Quality and Entry Quality remain separately visible.
- Initial V1.2.3c remains **shadow-only**: no official scanner ordering, bucket, Entry Quality or trade-decision changes.

### Implementation status

The first V1.2.3c shadow implementation is complete and ready for live acceptance. It adds an explainable Section 3F without changing any official ranking or actionability path. Offline regression: **22/22 PASS**.

### Why F15

F15 preserved the same Top-10 overlap as F20 in both 50-name samples while reducing score/rank disruption. Cross-universe Spearman was also much more stable:

- S&P 500: F15 **0.783** vs F20 **0.590**.
- Russell 2000: F15 **0.790** vs F20 **0.723**.

### V1.2.3b2 live acceptance now complete

Russell 2000 Fundamental sample = 50:

- CompanyFacts PASS: **50**
- Integrity PASS: **45**
- REVIEW: **5**
- FAIL: **0**
- Usable coverage: **90.0%**
- SRRK: corrected from hard FAIL to explainable REVIEW; no fabricated annual YoY.

### Documentation control

The new authoritative history file is `ALPACA_SCANNER_DEVELOPMENT_CHRONICLE.md`. Major architecture decisions are supported by ADRs under `docs/architecture/`. V1.2.3c is the first new phase that must be documented under this standard from implementation through freeze.

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `███████████████████░` 95%
- Scanner auditability: `████████████████████` 100%
- Candidate intelligence: `██████████████████░░` 90% — F15 composite architecture is implemented in shadow mode and awaiting V1.2.3c live acceptance
- Entry intelligence: `████████░░░░░░░░░░░░` 40%
- Fundamental-performance intelligence: `██████████████████░░` 90% — single-ticker integrity and representative bounded-universe coverage accepted/frozen
- Event-date confidence: `██░░░░░░░░░░░░░░░░░░` 10%
- Validation/backtesting: `░░░░░░░░░░░░░░░░░░░░` 0%
- Paper execution/journal: `░░░░░░░░░░░░░░░░░░░░` 0%

The progress percentages describe implementation maturity, not expected trading performance.


### V1.2.2.1b — SEC Identity Transport Bypass
- Status: **SUPERSEDED / RESOLVED BY V1.2.2.1b1**
- Scope: ticker→CIK transport only; financial values remain official SEC CompanyFacts.
- Reason: Streamlit Cloud live test returned HTTP 403 from all www.sec.gov identity endpoints.
- Frozen: Candidate Quality, Leadership, Entry Quality, scanner gates, buckets, trade decisions.


### V1.2.2.1b1 — SEC Fair Access / CompanyFacts Connectivity Validation
- Status: **ACCEPTED / FROZEN**
- Scope: declared User-Agent/contact validation and CompanyFacts connectivity diagnosis.
- Financial authority remains official SEC CompanyFacts.
- Candidate/Leadership/Entry/bucket logic remains frozen.


### V1.2.2.2 — Fundamental Metric Integrity & Cross-Company Validation
- Status: **ACCEPTED / FROZEN**
- Scope: validate the exact SEC concept/unit/period pairs used in revenue and earnings YoY calculations.
- Adds fail-visible provenance for quarter and annual calculations.
- Adds structural checks for period duration, YoY date alignment, filing chronology, form/accession availability, and non-calendar fiscal years.
- Adds explicit PASS / REVIEW / FAIL extraction-integrity state.
- Adds an explicit-action live validation suite covering AMZN, MSFT, NVDA, UBER, and JPM.
- REVIEW is a valid result for an explainable sector/domain concept gap; the engine must not manufacture a value.
- Fundamental score remains SHADOW MODE.
- Frozen: Persistent Quality, Candidate Quality, Leadership, Entry Quality, anti-chase logic, candidate buckets, and trade decisions.


### V1.2.2.2a — SEC Concept Continuity & Latest-Period Integrity
- Status: **ACCEPTED / FROZEN**
- Trigger: UBER live validation exposed a 2019 revenue concept being selected while 2026 earnings facts were current.
- Hard rule: a metric labelled Latest Quarter/FY may never fall back to an older reporting period.
- Approved SEC revenue concepts are ranked by current-period coverage before declaration order.
- Quarter and FY may use different approved SEC concepts when tagging transitions; this is displayed explicitly as SPLIT CURRENT SOURCES.
- If no approved current concept exists, the metric is suppressed to N/A — CONCEPT REVIEW REQUIRED.
- Future facts are excluded from latest-period reference selection.
- Fundamental model remains SHADOW MODE; scanner classification logic remains frozen.

### V1.2.2.2a1 — Annual Horizon & Filing-Form Integrity
- Status: **ACCEPTED / FROZEN**
- Narrow hotfix following V1.2.2.2a cross-company validation.
- Annual reference horizons now require annual SEC filing forms in addition to duration.
- Later interim TTM/comparative facts cannot displace authoritative annual filing provenance.
- UBER SEC concept-continuity/latest-period protection remains frozen and must not regress.
- Live freeze target: AMZN/MSFT/NVDA/UBER PASS, JPM explainable REVIEW-or-better, FAIL 0.
- Fundamental Quality remains SHADOW MODE; scanner classifications and trade decisions are unchanged.


### V1.2.2.3 — Fundamental Universe Coverage & Cache Validation
- Status: **ACCEPTED / FROZEN**
- Purpose: prove that the validated single-ticker SEC Fundamental Quality engine can scale across a bounded set of persistent-quality scanner candidates without corrupting scanner state.
- Fetch scope is intentionally bounded to the highest official Candidate Quality names after the existing persistent-quality gate; raw-universe batch fetching is prohibited.
- Candidate selection uses only frozen official scanner fields (Candidate Quality, Leadership, Legacy RS). Fundamental Quality cannot influence its own validation sample.
- Reuses the existing SEC ticker/CIK and CompanyFacts caches.
- Adds explicit CompanyFacts PASS, metric-integrity PASS/REVIEW/FAIL, Fundamental Data Confidence, metric coverage and usable-coverage accounting across the sample.
- Promotion gate for the next stage: zero hard FAIL and at least 90% usable PASS coverage on representative scans.
- Fundamental Quality remains SHADOW MODE.
- Frozen: official Candidate Quality, Persistent Quality, Leadership score definition, Entry Quality, anti-chase rules, candidate buckets and trade decisions.
- Only after V1.2.2.3 acceptance should the roadmap advance to **V1.2.3 Composite Candidate Quality Integration — Shadow Calibration**.


### V1.2.3 — Composite Candidate Quality Integration — Shadow Calibration
- Status: **CALIBRATION CAPTURED / SUPERSEDED BY V1.2.3a–c REFINEMENT**
- No-Fund reference = 70% official Candidate Quality + 30% Leadership.
- F10 = 63% Candidate Quality + 27% Leadership + 10% Fundamental.
- F20 = 56% Candidate Quality + 24% Leadership + 20% Fundamental.
- F30 = 49% Candidate Quality + 21% Leadership + 30% Fundamental.
- F20 is a calibration reference only, not a production commitment.
- REVIEW/FAIL/unavailable fundamentals are never imputed and cannot receive
  a full composite rank.
- Dashboard measures Top-10 overlap, Spearman correlation, rank shifts,
  fundamental impact and scenario sensitivity.
- Frozen throughout: official Candidate Quality, Leadership definition,
  Entry Quality, anti-chase rules, buckets, event-gate behavior and trade decisions.
- Promotion requires multi-universe live calibration and an explicit
  weighting/gating decision. No automatic promotion is permitted.


### V1.2.3a — Composite Attribution & Incremental Fundamental Impact
- Status: **ACCEPTED / FROZEN**
- Narrow attribution refinement; V1.2.3 F10/F20/F30 formulas are unchanged.
- Separates Leadership impact from incremental Fundamental impact.
- Leadership rank impact = Official Candidate Quality rank → No-Fund rank.
- F10/F20/F30 Fundamental rank impact = No-Fund rank → scenario rank.
- Net F20 rank change = Official Candidate Quality rank → F20 rank.
- Fundamental mover panels use F20 versus No-Fund, not F20 versus Official CQ.
- Separate Leadership promotion/demotion panels are displayed.
- Scenario attribution summary reports No-Fund Top-10 overlap, Spearman
  correlation, median absolute Fundamental rank impact and mean Fundamental
  score impact for F10/F20/F30.
- REVIEW/FAIL/unavailable Fundamental Quality is never imputed.
- Frozen throughout: official Candidate Quality, Leadership definition,
  Fundamental Quality engine, Entry Quality, anti-chase rules, candidate
  buckets, event-gate behavior and trade decisions.
- No permanent production weighting may be selected until V1.2.3a is
  validated on both S&P 500 and Russell 2000.


### V1.2.3b — Composite Weight Robustness & Guardrail Calibration
- Status: **RESEARCH COMPLETED / PRECISION DEFECT REPAIRED BY V1.2.3b1**
- V1.2.3a attribution is accepted/frozen and remains the authority for separating
  Leadership impact from incremental Fundamental impact.
- This stage does **not** merge or overwrite Candidate Quality, Leadership,
  Fundamental Quality or Entry Quality.
- Weight-robustness family:
  - F05, F10, F15, F20, F25, F30.
  - Formula: `(1-w) × No-Fund Reference + w × Fundamental Quality`.
  - F10/F20/F30 must exactly match the accepted V1.2.3a formulas.
- Robustness diagnostics:
  - Top-10 overlap vs No-Fund by weight.
  - Spearman rank correlation vs No-Fund by weight.
  - Median Fundamental rank impact.
  - Mean / maximum Fundamental score impact.
  - Per-stock rank range from F10 through F30.
  - Stable Top-10 membership across the full and center weight bands.
- Guardrail calibration is simulation only:
  - raw F20 remains the uncapped reference.
  - compare symmetric incremental Fundamental-impact caps at ±4, ±6 and ±8
    composite-score points.
  - measure trigger counts, direction, Top-10 overlap vs raw F20, Spearman vs
    raw F20, and rank changes.
- Explicitly watch TECHNICAL-LED / WEAK FUNDAMENTALS names to ensure a continuous
  Fundamental weight does not mechanically erase a legitimate technical edge.
- REVIEW/FAIL/unavailable Fundamental Quality is never imputed.
- Live acceptance uses **50-name samples** on both S&P 500 and Russell 2000.
- Frozen throughout: official Candidate Quality, Leadership definition,
  Fundamental Quality engine, Entry Quality, anti-chase rules, buckets,
  event-gate behavior and trade decisions.
- No production Composite Quality weight or guardrail is selected until both
  50-name universe tests are reviewed.


### V1.2.3b1 — Full-Precision Robustness Integrity Fix
- Status: **ACCEPTED / FROZEN**
- Trigger: S&P 500 50-name V1.2.3b test showed tiny F10/F20/F30
  Spearman differences between accepted 3D attribution and 3E robustness.
- Root cause: the robustness layer reconstructed scenarios from the displayed
  one-decimal No-Fund reference, introducing avoidable rounding contamination.
- Fix discipline:
  - F10/F20/F30 displayed scores and ranks are reused directly from the
    accepted/frozen V1.2.3a attribution layer.
  - Their exact formulas are independently recomputed only as an integrity
    check; rounded scores must match the accepted anchors.
  - New F05/F15/F25 interpolation scores use unrounded internal No-Fund values.
  - F05/F15/F25 rankings use unrounded internal composite scores.
  - Guardrail trigger decisions and guardrail rankings use unrounded exact
    F20 incremental Fundamental impact.
  - Display values remain rounded for readability.
- No weight changes.
- No guardrail changes or enforcement.
- No changes to Candidate Quality, Leadership, Fundamental Quality,
  Entry Quality, scanner buckets, event gates or trade decisions.
- Acceptance sequence:
  1. rerun S&P 500 STRICT with 50-name Fundamental sample;
  2. confirm FULL-PRECISION INTEGRITY PASS;
  3. confirm 3E F10/F20/F30 anchor metrics match 3D exactly;
  4. only then run Russell 2000 with 50-name sample.


### V1.2.3b2 — Pre-Revenue / Zero-Revenue Domain Integrity
- Status: **ACCEPTED / FROZEN**
- Trigger: Russell 2000 50-name robustness sample exposed SRRK as a hard FAIL:
  `Structurally suspicious SEC period pairing: Revenue annual`.
- Root cause class: annual YoY logic previously paired the last two annual
  observations merely because they were adjacent rows. Sparse revenue history
  can therefore create a non-consecutive pair (for example 2024 vs 2022).
- Integrity fix:
  - the actual latest annual fact is still the required current endpoint;
  - its comparator must be a genuine prior-year fact with a 320–410 day gap;
  - if no valid comparator exists, annual YoY is N/A and the metric becomes
    explainable REVIEW;
  - non-consecutive/stale historical revenue is never substituted;
  - zero latest annual revenue receives explicit `NO CURRENT REVENUE` state
    when no valid YoY comparator exists;
  - genuine current structural defects (future period, filing before period
    end, etc.) remain hard FAIL.
- This is generic domain integrity; there is **no ticker-specific SRRK rule**.
- No changes to:
  - Candidate Quality;
  - Leadership;
  - Fundamental Quality scoring weights;
  - V1.2.3a composite weights;
  - V1.2.3b guardrail candidates;
  - Entry Quality;
  - official ranking, buckets, event gates or trade decisions.
- Live acceptance result:
  - Russell 2000 STRICT, Fundamental sample = 50.
  - CompanyFacts PASS = 50.
  - Integrity PASS = 45; REVIEW = 5; FAIL = 0.
  - Usable coverage = 90.0%.
  - SRRK class = REVIEW, not FAIL; no fabricated annual YoY.
  - Russell 3D/3E robustness evidence completed after the fix.


### V1.2.3c — Composite Architecture Selection & Explainable Guardrail Layer
- Status: **IMPLEMENTED / READY FOR LIVE ACCEPTANCE**
- Primary Composite candidate: **F15** = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality.
- F20 remains shadow sensitivity benchmark.
- No hard Fundamental-impact cap is selected initially.
- Proposed explainability states: NORMAL <4 pts; MATERIAL 4–6 pts; HIGH IMPACT >6 pts absolute Fundamental contribution.
- REVIEW/FAIL/unavailable Fundamental Quality is never imputed and receives no full Composite rank.
- Initial implementation remains shadow-only and cannot change official Candidate Quality, scanner ranking, buckets, Entry Quality, event gates or trade decisions.
- Architecture rationale and limitations are recorded in `docs/architecture/ADR-001-composite-quality-f15.md`.
- Full history and validation evidence are recorded in `ALPACA_SCANNER_DEVELOPMENT_CHRONICLE.md`.
- Implementation files:
  - `app.py` — adds Section 3F selected-architecture shadow UI.
  - `scanner/composite_architecture.py` — new F15 selection/explainability layer; reuses V1.2.3b1 full-precision F15 and accepted V1.2.3a F20 anchors.
  - `tests/test_composite_architecture_v123c.py` — exact formula, no-cap, label-boundary, no-imputation and anchor-preservation tests.
- Offline regression result: **22/22 PASS** across V1.2.3b1 precision, V1.2.3b2 pre-revenue and V1.2.3c architecture tests.
- Live acceptance sequence:
  1. deploy V1.2.3c;
  2. run Russell 2000 STRICT, Fundamental sample = 50;
  3. confirm 3E still shows FULL-PRECISION INTEGRITY PASS;
  4. confirm 3F shows `V1.2.3c INTEGRITY PASS`, formula `59.5 / 25.5 / 15`, Hard score cap `NONE`, and F20 sensitivity reference;
  5. confirm SRRK/other REVIEW rows receive no full F15 Composite score/rank;
  6. confirm official scanner ordering, buckets, Entry Quality and trade decisions remain unchanged;
  7. after live acceptance, update Chronicle/ADR status to ACCEPTED / FROZEN before moving to V1.3.
