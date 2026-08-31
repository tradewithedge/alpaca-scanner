# ALPACA Scanner — Development Chronicle & Architecture Record

**Revision:** Rev.1  
**Prepared:** 31 August 2026  
**Current accepted implementation baseline:** V1.2.3b2 — Pre-Revenue / Zero-Revenue Domain Integrity  
**Current architecture-selection checkpoint:** V1.2.3c — Composite Architecture Selection & Explainable Guardrail Layer  
**V1.2.3c status:** Architecture selected; implementation and live acceptance not yet completed  

> This is a living engineering record. It preserves why the ALPACA Scanner evolved into its current architecture: the problems encountered, evidence observed, root causes, solutions selected, alternatives rejected, validation performed, frozen principles, known limitations, and decisions still awaiting empirical proof.

---

## 0. Document Control

### 0.1 Purpose

This chronicle is the authoritative development-history record for the ALPACA Scanner. It is not the final production operating manual.

Its job is to answer, for every meaningful development phase:

- What problem were we trying to solve?
- What failure or ambiguity exposed the need for change?
- What was the root cause?
- What architecture or rule was selected?
- Why was that architecture preferred?
- Which alternatives were rejected, and why?
- What changed in code or behavior?
- What explicitly did **not** change?
- What validation evidence justified acceptance?
- What limitations remain?
- What is frozen versus provisional?

A future production manual should describe the finished system and how to operate it. This chronicle should continue to preserve **why the finished system became what it is**.

### 0.2 Evidence hierarchy

This record uses five evidence classes:

1. **Development decisions and acceptance outcomes** captured during the build process.
2. **Retained source artifacts** such as versioned `app.py`, scanner modules, tests, acceptance notes and roadmap files.
3. **Live Streamlit validation evidence**, including screenshots and observed dashboard states.
4. **Calibration datasets/results**, including cross-universe S&P 500 and Russell 2000 samples.
5. **Current implementation behavior** where directly verified from retained code.

If a historical detail cannot be proven from retained evidence, this document marks it as incomplete or provisional rather than inventing a clean narrative.

### 0.3 Status vocabulary

| Status | Meaning |
|---|---|
| WORKING | Active implementation or test stage. |
| SHADOW | Calculated/displayed for research but does not change official scanner decisions. |
| ACCEPTED | Acceptance criteria passed. |
| FROZEN | Accepted behavior is a reference baseline; future changes require a new version. |
| SUPERSEDED | Historical stage replaced by a later accepted design. |
| ARCHITECTURE SELECTED | Design decision made, but implementation/live acceptance not yet complete. |

### 0.4 Change-control rule

No major stage should be considered fully frozen until:

1. its behavior passes the stated acceptance criteria;
2. this chronicle is updated;
3. any major architecture decision is recorded in an ADR;
4. known limitations are documented; and
5. frozen-principle impact is explicitly stated.

---

## 1. Executive Summary

The ALPACA Scanner is a regime-aware U.S. swing-trading decision-support system built around one governing idea:

> **Trade With Edge. Strong stock ≠ good entry. NO TRADE is a valid result.**

The current Candidate Quality work has evolved into a layered model rather than a single opaque score:

- **Candidate Quality (CQ):** technical candidate quality.
- **Leadership:** relative-strength persistence and market-stress resilience.
- **Fundamental Quality (FQ):** reported business-performance quality derived from audited SEC CompanyFacts logic.
- **Composite Quality:** higher-level combined candidate assessment; must not overwrite underlying component scores.
- **Entry Quality:** separate timing/actionability layer; not part of Composite Quality.

The development sequence deliberately followed **data integrity before intelligence**. Leadership was built and explained before Fundamental Quality was allowed into composite experiments. Fundamental extraction was then hardened through cross-company SEC integrity testing, latest-period continuity rules, annual-form integrity, bounded universe coverage, full-precision calibration fixes, and a pre-revenue/zero-revenue domain fix before composite architecture selection.

At the current checkpoint, the cross-universe evidence supports **F15** as the preferred Composite architecture candidate:

> **Composite F15 = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality**

F15 is selected because it preserved essentially the same Top-10 discrimination as F20 while producing materially lower rank churn and much better cross-universe stability. A hard ±6/±8 Fundamental-impact cap is **not** selected for production at this stage. Instead, the next implementation should use explainable Fundamental-impact states while keeping F20 as a shadow sensitivity benchmark.

This is an architecture selection, not yet proof of forward trading edge. Historical/forward validation remains a later critical stage.

---

## 2. Project Identity, Philosophy & Non-Negotiable Principles

### 2.1 Project identity

- Project: **ALPACA Scanner**.
- Primary use: U.S. swing-trading research and decision support.
- Data architecture: Alpaca market data plus official SEC CompanyFacts for Fundamental Quality.
- Decision order: market/data integrity → persistent/candidate quality → leadership/fundamental assessment → entry quality → later trade-plan/action layers.

### 2.2 Governing philosophy

1. **QUALITY COMES FIRST.** A candidate must independently deserve attention.
2. **Entry Quality is separate.** A strong candidate can still be a bad trade now.
3. **NO TRADE is valid.** Never lower standards to force action.
4. **Data integrity before intelligence.** Bad or ambiguous data cannot be repaired with smarter scoring.
5. **No silent substitution.** Missing/REVIEW/FAIL fundamentals are not replaced with neutral averages.
6. **Component transparency.** Candidate Quality, Leadership, Fundamental Quality, Composite Quality and Entry Quality must remain separately inspectable.
7. **Research does not silently become production.** Shadow calibration must pass explicit gates before it can alter official ranking or actionability.

### 2.3 Core architecture invariants

| ID | Frozen principle |
|---|---|
| CQ-01 | Candidate Quality remains the technical candidate-quality layer. |
| CQ-02 | Candidate Quality is not silently overwritten by Composite Quality. |
| L-01 | Leadership remains a separate explainable dimension. |
| FQ-01 | Fundamental Quality is a separate business-quality dimension. |
| FQ-02 | REVIEW/FAIL/unavailable fundamentals are never imputed with a neutral/average score. |
| COMP-01 | Composite Quality is a higher-level assessment, not a replacement for its inputs. |
| ENTRY-01 | Entry Quality remains separate from candidate desirability and Composite Quality. |
| DATA-01 | Invalid/incomplete/ambiguous source data cannot create false precision. |
| CAL-01 | No production weight/gate change without cross-sample evidence. |
| FREEZE-01 | Accepted behavior is not modified in place; future changes receive a new version. |
| ACT-01 | NO TRADE remains a valid outcome. |

---

## 3. Current Position

### 3.1 Roadmap checkpoint

| Version | Theme | Status at this chronicle revision |
|---|---|---|
| V1.2.1 | Relative Leadership & Market-Stress Resilience | Complete / Frozen |
| V1.2.1.1 | Leadership explainability | Complete / Frozen |
| V1.2.1.2–V1.2.1.3c | Ticker Inspector utility/reference engine | Complete / Frozen |
| V1.2.2 | Fundamental Quality Engine | Complete / Frozen |
| V1.2.2.1 | Revenue & Earnings Growth shadow model | Superseded by hardened integrity stages |
| V1.2.2.1a–V1.2.2.1b1 | SEC access / identity / Fair Access integrity | Complete / Frozen |
| V1.2.2.2 | Fundamental Metric Integrity & Cross-Company Validation | Complete / Frozen |
| V1.2.2.2a | SEC Concept Continuity & Latest-Period Integrity | Complete / Frozen |
| V1.2.2.2a1 | Annual Horizon & Filing-Form Integrity | Complete / Frozen |
| V1.2.2.3 | Fundamental Universe Coverage & Cache Validation | Complete / Frozen |
| V1.2.3 | Composite Candidate Quality shadow calibration | Calibration captured / not final architecture |
| V1.2.3a | Composite Attribution & Incremental Fundamental Impact | Accepted / Frozen |
| V1.2.3b | Weight robustness & guardrail calibration | Research stage; exposed precision defect |
| V1.2.3b1 | Full-Precision Robustness Integrity Fix | Accepted / Frozen |
| V1.2.3b2 | Pre-Revenue / Zero-Revenue Domain Integrity | **Accepted / Frozen** |
| V1.2.3c | Composite Architecture Selection & Explainable Guardrail Layer | **Architecture selected; implementation next** |

### 3.2 Current architecture selection

**Primary Composite candidate:** F15  
**Exact internal formula:** `59.5% CQ + 25.5% Leadership + 15% Fundamental`  
**Equivalent construction:** `85% × (70% CQ + 30% Leadership) + 15% Fundamental`  
**F20:** retained as shadow sensitivity benchmark  
**Hard Fundamental-impact cap:** not selected  
**Explainable impact states proposed:**

- NORMAL: `|Fundamental impact| < 4 pts`
- MATERIAL: `4–6 pts`
- HIGH IMPACT: `> 6 pts`

No official scanner ordering/bucket/trade-decision change has yet been authorized by this selection.

---

# 4. Chronological Development Ledger

## 4.1 V1.2.1 — Relative Leadership & Market-Stress Resilience

**Status:** Complete / Frozen  
**Decision confidence:** High for the implemented reference calculation; forward expectancy remains unproven.

### Objective

Add a distinct leadership dimension that measures more than a single blended relative-strength number.

### Problem / motivation

A stock can retain longer-horizon relative strength while losing near-term leadership or behaving poorly during market stress. Candidate Quality alone did not fully expose this distinction.

### Architecture selected

Leadership was calculated independently and kept in shadow mode before any integration with Candidate Quality. The retained implementation used the following composite:

- 30% RS20
- 25% RS50
- 15% RS acceleration
- 20% SPY-pullback resilience
- 10% RS-line proximity to its 100D high

### Why this architecture

It separates several leadership questions:

- Is the stock outperforming recently?
- Is that relative performance persistent across horizons?
- Is leadership improving or deteriorating?
- Does the stock hold up when SPY is weak?
- Is the RS line near its own high?

### What did not change

Persistent-quality eligibility, candidate buckets, Entry Quality and trade decisions remained unchanged during shadow validation.

### Known limitations

The weight mix was architecturally accepted for the current engine but has not yet been proven by forward-outcome validation.

---

## 4.2 V1.2.1.1 — Leadership Explainability

**Status:** Complete / Frozen

### Problem

A useful leadership score is insufficient if the user cannot understand why a name receives that score.

### Solution

Expose leadership as a separate dashboard layer with:

- Leadership score and grade;
- leadership-data confidence;
- component-level interpretation;
- visible distinction between strong leadership and ordinary technical Candidate Quality.

### Why this matters

Leadership later becomes an input to Composite Quality. Keeping the layer explainable before integration reduces the risk of turning the Candidate Quality Engine into an opaque blended score.

### What did not change

The Leadership layer did not change official candidate classification or trade action at this stage.

---

## 4.3 V1.2.1.2–V1.2.1.3c — Ticker Inspector Utility / Reference Engine

**Status:** Complete / Frozen at V1.2.1.3c

### Objective

Provide an audit-safe single-ticker diagnostic without requiring the user to trust a detached point score that lacks a cross-sectional reference.

### Core architecture

The Ticker Inspector:

- never mutates the frozen scanner result;
- uses a completed scan as the percentile/leadership reference when available;
- can build/reuse an independent reference universe when required;
- blocks percentile-dependent conclusions when reference integrity is insufficient;
- keeps direct diagnostics available even when full ranking authority is unavailable.

### Development issues encountered

The retained lineage shows intermediate fixes for Inspector persistence and Streamlit state synchronization. The final V1.2.1.3c Explicit-Action UX established an important UI/state rule:

> **Run Scanner must never create or reactivate Inspector implicitly. Inspector is user-requested and read-only.**

### Why this architecture

Cross-sectional scores are only meaningful when the reference distribution is known and current. The Inspector therefore distinguishes direct ticker facts from reference-dependent conclusions rather than silently manufacturing percentile authority.

### What did not change

Frozen V1.2.1 Leadership and official scanner classifications remained unchanged.

### Historical-record limitation

The exact issue-by-issue chronology of every V1.2.1.2–V1.2.1.3 intermediate patch is not fully reconstructed here. The retained artifacts clearly establish the final read-only/reference-integrity architecture and the persistence/state-sync repair lineage; additional details should be appended only when verified from retained notes/code.

---

## 4.4 V1.2.2 / V1.2.2.1 — Fundamental Quality & Revenue/Earnings Growth Shadow Model

**Status:** V1.2.2 complete/frozen as a layer; V1.2.2.1 shadow implementation superseded by later integrity hardening.

### Objective

Create a separate Fundamental Quality dimension based on reported business performance rather than mixing earnings/fundamental information directly into technical Candidate Quality.

### Architecture principle

Fundamental Quality answers a different question from Candidate Quality:

> **Is the reported business-performance profile supportive?**

It remains separate from Entry Quality and, until later composite calibration, separate from official candidate ranking.

### Important boundary

V1.2.2 measures **reported business performance**. Future event-date timing/reliability remains a different roadmap layer and must not be conflated with Fundamental Quality.

### Limitation exposed

Initial growth calculations proved that getting a numeric SEC value is not enough. The engine also had to prove that the selected concept, period, form and comparator were structurally correct.

---

## 4.5 V1.2.2.1a–V1.2.2.1b1 — SEC Access, Identity & Fair Access Integrity

**Status:** Complete / Frozen

### Problem

Live Streamlit Cloud testing produced SEC access/identity failures, including HTTP 403 behavior on identity endpoints. A fundamental engine cannot be trusted if ticker→CIK resolution and CompanyFacts connectivity are not operationally reliable.

### Solutions

- Added explicit SEC Fair Access User-Agent/contact handling.
- Separated identity-transport problems from CompanyFacts financial authority.
- Added identity transport bypass/fallback behavior where appropriate.
- Kept official SEC CompanyFacts as the financial authority.
- Diagnosed SEC connectivity explicitly instead of treating access failure as a low-quality company.

### Why this architecture

Transport failure and fundamental quality are different domains. The scanner must not convert an HTTP problem into a business-quality score.

### What did not change

Candidate Quality, Leadership, Entry Quality, scanner gates, buckets and trade decisions remained frozen.

### Known limitation

External SEC transport behavior can still change; the engine must continue to fail visibly rather than silently substituting unverified data.

---

## 4.6 V1.2.2.2 — Fundamental Metric Integrity & Cross-Company Validation

**Status:** Accepted / Frozen  
**Decision confidence:** High for the tested SEC integrity rules.

### Objective

Before allowing Fundamental Quality to influence Composite Quality, prove that revenue and earnings calculations are based on structurally valid SEC concept/unit/period pairs across different issuer reporting structures.

### Problem discovered

A metric labelled “Latest Quarter YoY” could previously fall back to an older quarter if the true latest quarter lacked a valid YoY comparator. That creates false freshness.

### Architecture / solution

Every latest-quarter and latest-FY calculation exposes:

- SEC taxonomy/concept;
- unit;
- current period;
- prior-year/prior-FY period;
- YoY end-date gap;
- period durations;
- filing form;
- filing date;
- accession number.

Structural integrity states were formalized:

- **PASS:** the pair actually used is structurally sound.
- **REVIEW:** missing/domain-specific coverage or incomplete provenance.
- **FAIL:** a suspicious pair was actually used.

Additional rules:

- non-calendar fiscal years are valid;
- 52/53-week annual periods are allowed within tolerance;
- YTD facts are excluded from quarter calculations;
- turnaround/profit-to-loss/loss states remain non-mathematical rather than fabricated growth percentages;
- the true latest quarter stays the reference; if no valid comparator exists, YoY becomes N/A/REVIEW rather than falling back to an older quarter.

### Validation set

- AMZN — calendar-year growth megacap
- MSFT — June fiscal year
- NVDA — January / 52–53-week fiscal year
- UBER — earnings-transition semantics
- JPM — financial-sector concept/domain stress test

### Why this architecture

Fundamental scoring must be based on **provenance-aware metrics**, not merely populated cells. REVIEW is intentionally a valid outcome when the generic concept map is incomplete.

### Rejected alternative

**Rejected:** treat every missing generic revenue concept as a failure or invent a substitute value.  
**Reason:** domain coverage gaps are not the same as extraction corruption.

### What did not change

Persistent Quality, Candidate Quality, Leadership, Entry Quality, anti-chase logic, buckets and trade decisions remained frozen.

### Known limitation

Financial-sector/domain-specific concept mapping remains a future enhancement. JPM demonstrated that an explainable REVIEW can be correct.

---

## 4.7 V1.2.2.2a — SEC Concept Continuity & Latest-Period Integrity

**Status:** Accepted / Frozen

### Trigger

UBER live validation exposed a severe semantic issue: a **2019 revenue concept** could be selected while 2026 earnings facts were current.

### Root cause

Concept declaration order could outrank freshness/current-period coverage.

### Hard rule introduced

> A metric labelled **Latest Quarter/FY** may never fall back to an older reporting period.

### Architecture

- Approved SEC revenue concepts are ranked by current-period coverage before declaration order.
- Quarter and FY may use different approved concepts during taxonomy transitions.
- When that happens, the engine explicitly reports **SPLIT CURRENT SOURCES**.
- If no approved current concept exists, the metric is suppressed to **N/A — CONCEPT REVIEW REQUIRED**.
- Future facts are excluded from latest-period reference selection.

### Why this architecture

Current-period truth outranks taxonomy convenience. A stale metric with a clean numeric value is more dangerous than an explicit N/A.

### What did not change

Fundamental remained shadow; official scanner classification logic stayed frozen.

---

## 4.8 V1.2.2.2a1 — Annual Horizon & Filing-Form Integrity

**Status:** Accepted / Frozen

### Trigger

Cross-company validation showed that duration alone was not sufficient to prove that an annual reference was authoritative.

### Root cause

Later interim/TTM/comparative facts could resemble annual-duration observations and displace authoritative annual filing provenance.

### Fix

Annual reference horizons now require **annual SEC filing forms in addition to duration**. Later interim TTM/comparative facts cannot displace the authoritative annual filing source.

### Regression protection

The UBER concept-continuity/latest-period rules remained frozen and were not allowed to regress.

### Live freeze target

- AMZN / MSFT / NVDA / UBER: PASS
- JPM: explainable REVIEW-or-better
- hard FAIL: 0

### What did not change

Fundamental Quality remained shadow; scanner classifications and trade decisions remained unchanged.

---

## 4.9 V1.2.2.3 — Fundamental Universe Coverage & Cache Validation

**Status:** Accepted / Frozen

### Objective

Prove that the single-ticker SEC Fundamental Quality engine can scale to a bounded candidate sample without contaminating scanner state or selecting its own validation sample.

### Architecture

- Fundamental batch sizes: 10 / 25 / 50.
- Fetch only already persistent-quality-qualified candidates.
- Selection order uses frozen official Candidate Quality, Leadership and Legacy RS.
- Fundamental Quality cannot influence the sample used to validate Fundamental Quality.
- Existing SEC identity/CompanyFacts caches are reused.
- New scanner runs invalidate stale batch results.
- Batch view exposes CompanyFacts status, metric integrity, confidence, metric coverage and readable diagnostics.

### Promotion gate

- CompanyFacts failures = 0
- hard FAIL = 0
- usable coverage ≥ 90%
- REVIEW allowed only when explainable and fail-visible

### Why this architecture

Jumping directly from single-ticker validation to production Composite Quality would violate data-integrity-first discipline. The engine needed a bounded cross-sectional reference first.

### What did not change

Persistent Quality, official Candidate Quality/ranking, Leadership definition, Entry Quality, anti-chase gates, buckets, trade decisions and event-date handling remained unchanged.

---

## 4.10 V1.2.3 — Composite Candidate Quality Integration — Shadow Calibration

**Status:** Calibration captured; not final production architecture

### Objective

Study how Candidate Quality, Leadership and Fundamental Quality should work together without hiding the underlying components and without contaminating Entry Quality.

### Shadow architecture

**No-Fund reference**

`70% Candidate Quality + 30% Leadership`

**Fundamental scenarios**

- F10 = `63% CQ + 27% L + 10% F`
- F20 = `56% CQ + 24% L + 20% F`
- F30 = `49% CQ + 21% L + 30% F`

F20 was a calibration reference, not a production commitment.

### Rules

- REVIEW/FAIL/unavailable fundamentals receive no full composite.
- No neutral/average Fundamental score is substituted.
- Measure Top-10 overlap, Spearman correlation, rank shifts, score impact and scenario sensitivity.

### Why shadow mode

A blended score can change ranking materially. The project therefore required multi-universe evidence and an explicit weighting decision before any official promotion.

### What did not change

Official Candidate Quality, scanner ranking, buckets, Entry Quality and trade decisions remained frozen.

---

## 4.11 V1.2.3a — Composite Attribution & Incremental Fundamental Impact

**Status:** Accepted / Frozen

### Problem

Initial composite analysis blurred two separate effects:

1. the effect of Leadership versus official Candidate Quality; and
2. the incremental effect of Fundamental Quality after Leadership is already included.

BRZE was an important interpretive example: Leadership could strongly promote a technically attractive name while weaker fundamentals demoted it, yet the net result could still be positive. A single “rank change” label did not tell the user which layer caused what.

### Architecture

Attribution chain:

`Official Candidate Quality → No-Fund Reference → F10/F20/F30`

Definitions:

- **Leadership rank impact:** Official CQ rank → No-Fund rank
- **Fundamental rank impact:** No-Fund rank → F10/F20/F30 rank
- **Net F20 rank change:** Official CQ rank → F20 rank

Fundamental mover panels use F20 versus No-Fund, never F20 versus Official CQ.

### Why this architecture

Leadership and Fundamentals answer different questions and must remain separately explainable even when Composite Quality combines them.

### What did not change

F10/F20/F30 weights, Candidate Quality, Leadership definition, Fundamental Quality engine, Entry Quality, buckets, event gates and trade decisions remained unchanged.

---

## 4.12 V1.2.3b — Composite Weight Robustness & Guardrail Calibration

**Status:** Research stage completed after b1/b2 fixes; original b build itself exposed a precision defect.

### Objective

Stress-test whether the composite ranking is robust to Fundamental weight selection and whether a hard impact cap is necessary to protect legitimate technical leaders.

### Weight grid

`Composite(w) = (1-w) × No-Fund Reference + w × Fundamental Quality`

Weights tested:

- F05
- F10
- F15
- F20
- F25
- F30

F10/F20/F30 remained the accepted V1.2.3a anchors. F05/F15/F25 were interpolation points.

### Diagnostics

- Top-10 overlap vs No-Fund
- Spearman rank correlation vs No-Fund
- median Fundamental rank impact
- mean/max Fundamental score impact
- per-stock rank range F10→F30
- stable Top-10 membership across full/center bands

### Guardrail simulation

Raw F20 remained uncapped. The research layer simulated symmetric incremental Fundamental-impact caps at:

- ±4 points
- ±6 points
- ±8 points

No cap was enforced in production.

### Explicit architecture-risk watch

Track **TECHNICAL-LED / WEAK FUNDAMENTALS** names to determine whether continuous Fundamental weighting mechanically erases legitimate technical/leadership strength.

---

## 4.13 V1.2.3b1 — Full-Precision Robustness Integrity Fix

**Status:** Accepted / Frozen  
**Decision confidence:** High.

### Trigger

The S&P 500 50-name robustness run showed tiny F10/F20/F30 Spearman discrepancies between accepted 3D attribution and 3E robustness, even though the formulas were supposed to be identical.

### Root cause

3E reconstructed scenarios from the **displayed one-decimal No-Fund reference**, allowing display rounding to contaminate ranking calculations.

### Architecture / fix

- F10/F20/F30 scores/ranks are reused directly from accepted V1.2.3a anchors.
- Their exact formulas are recomputed only as an integrity check.
- F05/F15/F25 use unrounded internal No-Fund/composite values.
- New rankings use full-precision internal values.
- Guardrail triggers/rankings use exact F20 incremental Fundamental impact.
- Display values remain rounded only for readability.

### Why this architecture

Display precision and model precision are separate concerns. A user-friendly rounded number must never alter the internal rank ordering.

### Acceptance — S&P 500 50-name sample

**Rankable:** 49/50  
**Stable Top-10 F10→F30:** 7/10  
**Stable center Top-10 F15/F20/F25:** 9/10  
**Median rank range:** 7.0  
**High-sensitivity names:** 29  
**F20 ±6 triggers:** 16

#### S&P weight grid

| F weight | Top-10 overlap | Spearman vs No-Fund | Median |fund rank impact| | Mean |fund score impact| | Max |fund score impact| |
|---:|---:|---:|---:|---:|---:|
| 5% | 9/10 | 0.966 | 2 | 1.3 | 3.2 |
| 10% | 7/10 | 0.882 | 4 | 2.6 | 6.5 |
| 15% | 7/10 | 0.783 | 6 | 3.8 | 9.7 |
| 20% | 7/10 | 0.590 | 8 | 5.1 | 12.9 |
| 25% | 6/10 | 0.488 | 9 | 6.4 | 16.1 |
| 30% | 5/10 | 0.383 | 9 | 7.7 | 19.4 |

#### S&P F20 guardrail simulation

| Cap | Triggered | Direction | Top-10 vs raw F20 | Spearman vs raw F20 | Median |rank change| | Max |rank change| |
|---:|---:|---|---:|---:|---:|---:|
| ±4 | 29/49 | all downside | 8/10 | 0.775 | 6 | 22 |
| ±6 | 16/49 | all downside | 9/10 | 0.906 | 4 | 18 |
| ±8 | 10/49 | all downside | 10/10 | 0.977 | 1 | 13 |

### Technical-led preservation examples — S&P

| Symbol | CQ | Leadership | Fundamental | No-Fund ref | Raw F20 | F20 fund impact | Raw F20 rank | ±6 rank | Triggered |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NOW | 98.6 | 84.7 | 55.8 | 94.4 | 86.7 | -7.7 | 5 | 6 | Yes |
| IT | 97.2 | 91.0 | 52.0 | 95.3 | 86.7 | -8.6 | 5 | 4 | Yes |
| BDX | 95.8 | 84.3 | 40.2 | 92.4 | 81.9 | -10.5 | 23 | 10 | Yes |
| GPC | 94.2 | 86.1 | 37.2 | 91.8 | 80.9 | -10.9 | 30 | 12 | Yes |
| CAG | 93.8 | 80.0 | 42.4 | 89.7 | 80.2 | -9.5 | 36 | 18 | Yes |
| NWS | 93.2 | 80.9 | 43.4 | 89.5 | 80.3 | -9.2 | 33 | 19 | Yes |
| DASH | 90.1 | 80.9 | 59.6 | 87.3 | 81.8 | -5.5 | 25 | 29 | No |

### Interpretation

The precision defect was fixed. The S&P evidence also showed that hard caps can materially rescue technical leaders, which is not automatically desirable. Guardrails therefore remained research-only pending broader-universe evidence.

---

## 4.14 V1.2.3b2 — Pre-Revenue / Zero-Revenue Domain Integrity

**Status:** Accepted / Frozen  
**Decision confidence:** High for the domain rule tested.

### Trigger

The Russell 2000 50-name Fundamental sample produced one hard FAIL:

`SRRK — Structurally suspicious SEC period pairing: Revenue annual`

### Root cause

Annual YoY logic had paired the last two annual observations merely because they were adjacent rows. Sparse revenue history could therefore create a non-consecutive pair such as 2024 vs 2022.

### Architecture / fix

- The actual latest annual fact remains the required current endpoint.
- The prior comparator must be a genuine prior-year fact with a **320–410 day gap**.
- If no valid comparator exists, annual YoY is **N/A** and the metric becomes explainable **REVIEW**.
- Non-consecutive/stale historical revenue is never substituted.
- If latest annual revenue = 0 and no valid comparator exists, use explicit state **NO CURRENT REVENUE**.
- Genuine current structural defects — future periods, filing before period end, etc. — remain **FAIL**.
- No SRRK-specific hardcode exists; the rule is generic.

### Rejected alternatives

- **Ticker-specific SRRK exception:** rejected; not generalizable.
- **Pair any two available annual facts:** rejected; creates false YoY semantics.
- **Convert all annual anomalies to REVIEW:** rejected; genuine structural defects must still FAIL.

### Regression tests

1. sparse zero-revenue case → REVIEW, not FAIL;
2. non-consecutive history blocked;
3. zero-revenue state explicitly `NO CURRENT REVENUE`;
4. normal consecutive annual pair remains PASS and computes correctly;
5. genuine filing chronology defect remains FAIL.

### Live Russell acceptance

**Sample requested:** 50  
**CompanyFacts PASS:** 50  
**Integrity PASS:** 45  
**REVIEW:** 5  
**FAIL:** 0  
**Usable coverage:** 90.0%  
**Median Fundamental Quality:** 60.1/100  
**A/A+ fundamentals:** 5  
**Low/unknown data confidence:** 5

SRRK moved from hard FAIL to explainable REVIEW with Revenue Q YoY = N/A and no fabricated Fundamental score.

### What did not change

Candidate Quality, Leadership, Fundamental scoring weights, Composite weights/guardrails, Entry Quality, official ranking, buckets, event gates and trade decisions remained unchanged.

---

# 5. Cross-Universe Composite Calibration Evidence

## 5.1 Russell 2000 — V1.2.3a attribution

**Composite rankable:** 45/50  
**Official→F20 Top-10:** 7/10  
**No-Fund→F20 Top-10:** 8/10  
**Median |Leadership rank impact|:** 6.0  
**Median |F20 Fundamental rank impact|:** 5.0  
**Mean |F20 Fundamental score impact|:** 5.5 pts

### Scenario attribution

| Scenario | No-Fund Top-10 overlap | Spearman vs No-Fund | Median |fund rank impact| | Mean |fund score impact| |
|---|---:|---:|---:|---:|
| F10 | 9/10 | 0.881 | 4 | 2.7 |
| F20 | 8/10 | 0.723 | 5 | 5.5 |
| F30 | 8/10 | 0.579 | 8 | 8.2 |

Largest observed F20 Fundamental promotions included WT (+28 ranks), NESR (+16), CDNA (+16), SSRM (+14) and QTWO (+11). Largest demotions included PSNL (-18), PRGO (-17), ANF (-16), SRPT (-15) and WGS (-14).

## 5.2 Russell 2000 — full-precision robustness

**FULL-PRECISION INTEGRITY:** PASS  
**Rankable:** 45/50  
**Stable Top-10 F10→F30:** 9/10  
**Stable center Top-10 F15/F20/F25:** 9/10  
**Median rank range:** 4.0  
**High-sensitivity names:** 20  
**F20 ±6 triggers:** 20

### Russell weight grid

| F weight | Top-10 overlap | Spearman vs No-Fund | Median |fund rank impact| | Mean |fund score impact| | Max |fund score impact| |
|---:|---:|---:|---:|---:|---:|
| 5% | 10/10 | 0.948 | 2 | 1.4 | 3.8 |
| 10% | 9/10 | 0.881 | 4 | 2.7 | 7.6 |
| 15% | 8/10 | 0.790 | 5 | 4.1 | 11.4 |
| 20% | 8/10 | 0.723 | 5 | 5.5 | 15.2 |
| 25% | 8/10 | 0.655 | 7 | 6.9 | 19.0 |
| 30% | 8/10 | 0.579 | 8 | 8.2 | 22.8 |

### Russell F20 guardrail simulation

| Cap | Triggered | Direction | Top-10 vs raw F20 | Spearman vs raw F20 | Median |rank change| | Max |rank change| |
|---:|---:|---|---:|---:|---:|---:|
| ±4 | 28/45 | all downside | 8/10 | 0.886 | 3 | 16 |
| ±6 | 20/45 | all downside | 9/10 | 0.945 | 2 | 12 |
| ±8 | 9/45 | all downside | 10/10 | 0.986 | 1 | 9 |

### Technical-led / weak-fundamental preservation watch — Russell

| Symbol | CQ | Leadership | Fundamental | TL reference | Raw F20 | F20 fund impact | Raw F20 rank | ±6 rank |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HTFL | 96.5 | 92.3 | 59.9 | 95.2 | 88.2 | -7.0 | 5 | 4 |
| PRGO | 96.0 | 84.9 | 37.3 | 92.7 | 81.6 | -11.1 | 22 | 10 |
| WGS | 95.8 | 80.4 | 44.9 | 91.2 | 81.9 | -9.3 | 20 | 12 |
| BRZE | 90.4 | 83.7 | 55.3 | 88.4 | 81.8 | -6.6 | 21 | 22 |
| ANF | 90.2 | 81.3 | 41.3 | 87.5 | 78.3 | -9.2 | 32 | 24 |

The BRZE result is informative: capping one stock's downside contribution does not guarantee promotion because the whole cross-section moves.

---

# 6. V1.2.3c — Composite Architecture Selection

**Status:** ARCHITECTURE SELECTED / IMPLEMENTATION NEXT  
**Decision confidence:** Medium-High  
**ADR:** `docs/architecture/ADR-001-composite-quality-f15.md`

## 6.1 Decision

Select **F15** as the primary Composite Quality architecture candidate:

> **59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality**

Keep F20 as a shadow sensitivity benchmark.

Do **not** implement a hard Fundamental-impact cap at this stage.

Instead, expose the Fundamental contribution as an explainable impact state:

- NORMAL: `|impact| < 4`
- MATERIAL: `4 ≤ |impact| ≤ 6`
- HIGH IMPACT: `|impact| > 6`

## 6.2 Why F15 instead of F20

### Cross-universe evidence

| Metric | S&P F15 | S&P F20 | Russell F15 | Russell F20 |
|---|---:|---:|---:|---:|
| Top-10 overlap | 7/10 | 7/10 | 8/10 | 8/10 |
| Spearman vs No-Fund | **0.783** | 0.590 | **0.790** | 0.723 |
| Median |fund rank impact| | **6** | 8 | **5** | 5 |
| Mean |fund score impact| | **3.8** | 5.1 | **4.1** | 5.5 |
| Max |fund score impact| | **9.7** | 12.9 | **11.4** | 15.2 |

### Interpretation

F15 produced essentially the **same Top-10 discrimination** as F20 while reducing collateral rank churn.

The strongest cross-universe result is stability:

- F15 Spearman: **0.783 S&P / 0.790 Russell**
- F20 Spearman: **0.590 S&P / 0.723 Russell**

F15 therefore behaved far more consistently across two very different universes.

## 6.3 Why no hard ±6/±8 cap

The F20 guardrail study showed:

- ±4 is too interventionist;
- ±8 is light-touch;
- ±6 is the meaningful middle protection.

However, moving from F20 to F15 already reduces the Fundamental contribution by 25%. For example, a -12 point F20 impact is approximately -9 at F15. F15 therefore acts as a first-order structural restraint.

Adding a hard cap immediately on top of F15 would create another non-linear rule before forward-outcome evidence proves that such intervention improves expectancy.

### Selected approach

Keep the arithmetic transparent. Do not secretly rescue or punish the score. Instead show when Fundamentals materially drive the Composite result.

Example presentation:

`CQ A+ | Leadership A | Fundamental D | Composite B+ | Fundamental impact HIGH | Entry A`

The user can see the conflict instead of receiving a manipulated composite.

## 6.4 Rejected/not-selected alternatives

| Alternative | Decision | Reason |
|---|---|---|
| F10 | Not selected | Too little Fundamental influence for the intended higher-level quality layer. |
| F20 | Not selected as primary | Same Top-10 discrimination as F15 but materially more rank disruption and weaker cross-universe stability. |
| F25 | Not selected | More aggressive Fundamental dominance without evidence of better discrimination. |
| F30 | Rejected for primary use | Excessive rank sensitivity and largest score impacts. |
| ±4 hard cap | Rejected | Too interventionist in both universes. |
| ±6 hard cap | Not selected now | Useful calibration middle ground, but unnecessary complexity after F15 reduction without outcome proof. |
| ±8 hard cap | Not selected now | Minimal intervention but little demonstrated need after F15 selection. |
| Neutral Fundamental imputation | Rejected | Violates data-integrity-first and hides uncertainty. |

## 6.5 What V1.2.3c must not change

Until separately accepted:

- official Candidate Quality;
- Leadership score definition;
- Fundamental Quality engine;
- Entry Quality;
- anti-chase rules;
- candidate buckets;
- event gates;
- trade decisions;
- official scanner ordering.

## 6.6 Acceptance requirements for the implementation patch

1. F15 internal formula is exactly `59.5 / 25.5 / 15`.
2. F20 remains available as a shadow sensitivity reference.
3. No hard impact cap is applied to the score.
4. NORMAL / MATERIAL / HIGH IMPACT labels are derived from the incremental Fundamental contribution.
5. REVIEW/FAIL/unavailable fundamentals produce no full Composite score/rank.
6. CQ, Leadership, FQ, Composite and Entry remain separately visible.
7. Existing V1.2.3a/b1 anchor integrity continues to pass.
8. No official ranking, bucket or trade-decision changes occur in the first V1.2.3c implementation.

---

# 7. Validation Ledger

| Case | Observed issue | Repair / decision | Validation outcome |
|---|---|---|---|
| V1.2.1 Leadership | Blended technical quality could hide leadership deterioration/stress weakness | Separate Leadership composite and explainability | Frozen reference architecture |
| Ticker Inspector | Single-ticker percentile authority could be ambiguous without a reference | Read-only reference engine; block reference-dependent conclusions if reference unusable | V1.2.1.3c frozen |
| SEC 403 / identity | SEC access failure could prevent fundamental validation | Fair Access identity/connectivity handling; transport separated from financial authority | Accepted/Frozen |
| AMZN | Calendar-year/annual reference integrity | Provenance + annual-form rules | PASS in validation target |
| MSFT | Non-calendar fiscal year | Explicitly allow valid non-calendar fiscal year | PASS |
| NVDA | 52/53-week annual year | Allow within annual tolerance | PASS |
| UBER | Stale 2019 revenue concept selected while current earnings data existed | Latest-period concept continuity; current coverage outranks declaration order | Accepted/Frozen |
| JPM | Generic concept map incomplete for financial-sector structure | Explainable REVIEW rather than fabricated revenue | Correct fail-visible behavior |
| Latest quarter fallback | Older comparable quarter could masquerade as latest YoY | True latest period remains reference; N/A/REVIEW if comparator missing | Fixed in V1.2.2.2 |
| Full-precision | Rounded No-Fund display value altered robustness calculations | Use unrounded internals; reuse V1.2.3a anchors | FULL-PRECISION INTEGRITY PASS |
| BRZE attribution | Leadership promotion and Fundamental demotion could be conflated | Separate Leadership impact from incremental Fundamental impact | V1.2.3a accepted |
| SRRK | Sparse annual revenue history created non-consecutive annual pair and hard FAIL | Require 320–410 day prior-year comparator; otherwise N/A/REVIEW; explicit NO CURRENT REVENUE | Russell batch FAIL 1→0; accepted |

---

# 8. Known Limitations & Open Risks

1. **No forward-expectancy proof yet.** Composite selection is based on ranking robustness and architecture quality, not realized future trade outcomes.
2. **Sample breadth is bounded.** Current architecture decision relies on 50-name S&P 500 and 50-name Russell 2000 calibration samples, not full-universe historical backtests.
3. **Sector/domain specialization remains incomplete.** Generic SEC concepts may remain insufficient for some banks/financials or unusual reporting structures.
4. **Fundamental impact is asymmetric in observed samples.** Guardrail triggers were entirely downside in both S&P and Russell F20 runs, suggesting Fundamentals often acted more as a penalty mechanism than a promoter in these samples.
5. **F15 is selected, not production-authorized.** The first V1.2.3c build must remain shadow-only until acceptance.
6. **Entry Quality remains independent.** A high Composite score does not imply an actionable entry.
7. **Event-date reliability is not Fundamental Quality.** Earnings timing/proximity belongs to a separate later event-reliability layer.
8. **Architecture may need recalibration after backtesting.** F15 should be revisited only if broader historical/forward evidence materially contradicts the current robustness findings.

---

# 9. Decision Ledger

| Decision | Status | Rationale |
|---|---|---|
| Candidate Quality remains technical | Frozen principle | Preserve the truth of technical candidate quality; do not let weak fundamentals erase it. |
| Leadership remains separate | Frozen principle | Leadership/resilience is distinct from generic technical quality. |
| Fundamental Quality remains separate | Frozen principle | Business quality answers a different question from technical quality. |
| Composite Quality is higher-level, not a replacement score | Selected architecture | Preserve component transparency and attribution. |
| Entry Quality excluded from Composite | Frozen principle | Timing/actionability is not candidate desirability. |
| No imputation for REVIEW/FAIL FQ | Frozen principle | Missing/ambiguous data cannot create false precision. |
| F15 primary Composite candidate | Architecture selected | Same Top-10 discrimination as F20 with lower churn and far better cross-universe stability. |
| F20 retained as shadow sensitivity benchmark | Architecture selected | Provides useful stress/sensitivity information without becoming production formula. |
| No hard Fundamental-impact cap | Architecture selected | F15 already reduces impact; hard cap adds complexity before outcome evidence. |
| Explain Fundamental impact explicitly | Architecture selected | Transparency is preferable to hidden score manipulation. |

---

# 10. Frozen Design Principles — Do Not Violate

1. Data integrity before intelligence.
2. Candidate Quality ≠ Leadership ≠ Fundamental Quality ≠ Composite Quality ≠ Entry Quality.
3. Component scores remain separately visible.
4. REVIEW/FAIL/unavailable Fundamental Quality is never silently imputed.
5. Latest-period labels must refer to the actual latest eligible period.
6. Stale historical facts may not substitute for missing current-period facts.
7. Annual YoY requires a genuine prior-year comparator; sparse history is REVIEW, not fabricated growth.
8. Genuine structural SEC defects remain FAIL.
9. Rounded display values must never drive ranking calculations.
10. Shadow calibration cannot silently alter official ranking, buckets or trade decisions.
11. No production weight change without evidence.
12. NO TRADE remains valid.
13. A frozen baseline is not modified in place.
14. Any patch touching these principles must identify the affected principle, justify the change, add regression protection, and receive a new version number.

---

# Appendix A — Version Ledger

| Version | Theme | Key contribution | Status |
|---|---|---|---|
| V1.2.1 | Leadership & resilience | Separate leadership composite | Frozen |
| V1.2.1.1 | Explainability | Leadership score/grade/confidence visible | Frozen |
| V1.2.1.2–1.2.1.3c | Ticker Inspector | Read-only self-contained reference engine; explicit-action UX | Frozen |
| V1.2.2.1 | Fundamental growth | Initial revenue/earnings shadow model | Superseded |
| V1.2.2.1a–1b1 | SEC access | Fair Access, identity/connectivity integrity | Frozen |
| V1.2.2.2 | Metric integrity | Provenance + PASS/REVIEW/FAIL + latest-quarter protection | Frozen |
| V1.2.2.2a | Concept continuity | Current-period coverage outranks stale concept order | Frozen |
| V1.2.2.2a1 | Annual form integrity | Annual form + duration provenance | Frozen |
| V1.2.2.3 | Universe coverage | Bounded audited Fundamental sample, ≥90% gate | Frozen |
| V1.2.3 | Composite calibration | No-Fund/F10/F20/F30 shadow scenarios | Calibration only |
| V1.2.3a | Attribution | Leadership vs incremental Fundamental attribution | Frozen |
| V1.2.3b | Robustness | F05–F30 + ±4/±6/±8 simulations | Research |
| V1.2.3b1 | Precision integrity | Full-precision ranking; anchor reuse | Frozen |
| V1.2.3b2 | Pre-revenue integrity | Genuine annual comparator / REVIEW semantics | Frozen |
| V1.2.3c | Composite architecture | F15 selected; explainable impact; no hard cap | Architecture selected / implementation next |

---

# Appendix B — Current Composite Formulas

**No-Fund Reference**  
`0.70 × CQ + 0.30 × Leadership`

**General formula**  
`Composite(w) = (1-w) × No-Fund + w × Fundamental`

| Scenario | Expanded formula |
|---|---|
| F05 | 66.5% CQ + 28.5% Leadership + 5% Fundamental |
| F10 | 63.0% CQ + 27.0% Leadership + 10% Fundamental |
| **F15** | **59.5% CQ + 25.5% Leadership + 15% Fundamental** |
| F20 | 56.0% CQ + 24.0% Leadership + 20% Fundamental |
| F25 | 52.5% CQ + 22.5% Leadership + 25% Fundamental |
| F30 | 49.0% CQ + 21.0% Leadership + 30% Fundamental |

---

# Appendix C — Documentation Standard for Future Phases

Every future major phase record should include:

1. Version / stage
2. Objective
3. Problem / trigger
4. Evidence / symptom
5. Root cause
6. Architecture / solution
7. Why this architecture
8. Alternatives considered/rejected
9. Architecture delta — BEFORE vs AFTER
10. Files/modules affected
11. What did **not** change
12. Validation performed
13. Acceptance criteria
14. Acceptance result
15. Known limitations
16. Decision confidence
17. Frozen-principle impact
18. Future dependency

This structure is mandatory for major frozen milestones from V1.2.3c onward.
