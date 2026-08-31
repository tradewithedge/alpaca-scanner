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
| V1.2.3b1 | Full-Precision Robustness Integrity Fix | **CURRENT / READY FOR LIVE ACCEPTANCE** |
| V1.3 | Entry Quality / Anti-Chase Engine | Planned |
| V1.4 | Market Regime & Deployment Engine | Planned |
| V1.5 | Earnings / Event Reliability Layer | Planned |
| V1.6 | Trade Plan & Risk Engine | Planned |
| V1.7 | Validation / Backtest / Forward-test Framework | Planned |
| V1.8 | Paper Trading & Trade Journal Integration | Planned |
| V2.0 | Production-grade Daily Swing Scanner | Target |

## Current Stage — V1.2.3b1 Full-Precision Robustness Integrity Fix

### Objective

Calibrate how **Technical Candidate Quality + Leadership + Fundamental Quality**
should work together without hiding the separate subscores and without
contaminating Entry Quality.

### Shadow-calibration scope

- Official Candidate Quality remains frozen and separately visible.
- Leadership remains frozen and separately visible.
- Fundamental Quality remains frozen and separately visible.
- Entry Quality remains completely separate from candidate desirability.
- No-Fund reference: **70% Candidate Quality + 30% Leadership**.
- Compare three Fundamental Quality scenarios:
  - F10: 63% Candidate Quality + 27% Leadership + 10% Fundamental.
  - F20: 56% Candidate Quality + 24% Leadership + 20% Fundamental.
  - F30: 49% Candidate Quality + 21% Leadership + 30% Fundamental.
- F20 is the primary shadow comparison, **not a final production weight**.
- REVIEW/FAIL/unavailable fundamentals are never imputed.
- Measure rank correlation, Top-10 overlap, rank shifts, score impact,
  scenario sensitivity and descriptive technical/fundamental alignment.
- No scanner gate, bucket, Entry Quality or trade-decision changes.

### Boundary with V1.5

V1.2.2 measures **reported business performance**.

V1.5 remains responsible for **event timing/reliability**, including the next earnings date and fail-closed event-risk handling.

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `███████████████████░` 95%
- Scanner auditability: `████████████████████` 100%
- Candidate intelligence: `█████████████████░░░` 85% — technical, leadership and fundamental layers are frozen; composite integration is now in shadow calibration
- Entry intelligence: `████████░░░░░░░░░░░░` 40%
- Fundamental-performance intelligence: `██████████████████░░` 90% — single-ticker integrity and representative bounded-universe coverage accepted/frozen
- Event-date confidence: `██░░░░░░░░░░░░░░░░░░` 10%
- Validation/backtesting: `░░░░░░░░░░░░░░░░░░░░` 0%
- Paper execution/journal: `░░░░░░░░░░░░░░░░░░░░` 0%

The progress percentages describe implementation maturity, not expected trading performance.


### V1.2.2.1b — SEC Identity Transport Bypass
- Status: **READY FOR LIVE ACCEPTANCE**
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
- Status: **READY FOR LIVE ACCEPTANCE**
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
- Status: **READY FOR LIVE ACCEPTANCE**
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
- Status: **READY FOR LIVE ACCEPTANCE**
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
- Status: **READY FOR LIVE ACCEPTANCE**
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
