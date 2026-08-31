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
| V1.2.2 | Fundamental Quality Engine | **CURRENT** |
| V1.2.2.3 | Fundamental Universe Coverage & Cache Validation | **CURRENT / READY FOR LIVE ACCEPTANCE** |
| V1.2.2.2 | Fundamental Metric Integrity & Cross-Company Validation | Complete / Frozen |
| V1.2.2.2a–V1.2.2.2a1 | Concept continuity + annual horizon integrity | Complete / Frozen |
| V1.2.2.1 | Revenue & Earnings Growth — shadow validation | Complete / superseded |
| V1.2.2.1a–V1.2.2.1b1 | SEC access / identity / Fair Access integrity | Complete / Frozen |
| V1.3 | Entry Quality / Anti-Chase Engine | Planned |
| V1.4 | Market Regime & Deployment Engine | Planned |
| V1.5 | Earnings / Event Reliability Layer | Planned |
| V1.6 | Trade Plan & Risk Engine | Planned |
| V1.7 | Validation / Backtest / Forward-test Framework | Planned |
| V1.8 | Paper Trading & Trade Journal Integration | Planned |
| V2.0 | Production-grade Daily Swing Scanner | Target |

## Current Stage — V1.2.2.3 Fundamental Universe Coverage & Cache Validation

### Objective

Determine whether a technically strong stock is also backed by durable business growth.

### First validation scope

- Official SEC EDGAR CompanyFacts only.
- Latest-quarter revenue YoY growth.
- Latest-quarter earnings YoY growth, preferring diluted EPS and explicitly disclosing a net-income fallback.
- Revenue and earnings growth acceleration/deceleration using real numeric changes.
- Recent positive YoY growth consistency.
- Latest fiscal-year revenue and earnings growth as longer-term confirmation.
- Fundamental Quality Score / Grade in **SHADOW MODE**.
- Explicit Fundamental Data Confidence: HIGH / MEDIUM / LOW / UNKNOWN.
- Ticker Inspector and selected Candidate Detail receive the same explainable view.
- No batch fundamental fetch across the universe yet.
- No change to Persistent Quality, Candidate Quality, Leadership, Entry Quality, buckets, or trade decisions until validation is complete.

### Boundary with V1.5

V1.2.2 measures **reported business performance**.

V1.5 remains responsible for **event timing/reliability**, including the next earnings date and fail-closed event-risk handling.

## Progress Snapshot

- Foundation: `████████████████████` 100%
- Market-data integrity: `███████████████████░` 95%
- Scanner auditability: `████████████████████` 100%
- Candidate intelligence: `████████████████░░░░` 80% — leadership and single-ticker fundamentals validated; universe-level fundamental coverage now in shadow validation
- Entry intelligence: `████████░░░░░░░░░░░░` 40%
- Fundamental-performance intelligence: `███████████████░░░░░` 75% after metric-integrity freeze; bounded universe coverage/cache validation in progress
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
- Status: **READY FOR LIVE ACCEPTANCE**
- Purpose: prove that the validated single-ticker SEC Fundamental Quality engine can scale across a bounded set of persistent-quality scanner candidates without corrupting scanner state.
- Fetch scope is intentionally bounded to the highest official Candidate Quality names after the existing persistent-quality gate; raw-universe batch fetching is prohibited.
- Candidate selection uses only frozen official scanner fields (Candidate Quality, Leadership, Legacy RS). Fundamental Quality cannot influence its own validation sample.
- Reuses the existing SEC ticker/CIK and CompanyFacts caches.
- Adds explicit CompanyFacts PASS, metric-integrity PASS/REVIEW/FAIL, Fundamental Data Confidence, metric coverage and usable-coverage accounting across the sample.
- Promotion gate for the next stage: zero hard FAIL and at least 90% usable PASS coverage on representative scans.
- Fundamental Quality remains SHADOW MODE.
- Frozen: official Candidate Quality, Persistent Quality, Leadership score definition, Entry Quality, anti-chase rules, candidate buckets and trade decisions.
- Only after V1.2.2.3 acceptance should the roadmap advance to **V1.2.3 Composite Candidate Quality Integration — Shadow Calibration**.
