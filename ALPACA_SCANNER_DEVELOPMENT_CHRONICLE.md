# ALPACA Scanner - Development Chronicle & Architecture Record

**Revision:** Rev.2  
**Prepared:** 7 September 2026  
**Current accepted implementation baseline:** V1.2.3c - Composite Architecture Selection & Explainable Guardrail Layer  
**V1.2.3c status:** **ACCEPTED / FROZEN**  
**Current development checkpoint:** V1.3a - Contextual Volume Quality Engine  
**Current development status:** OPEN / DESIGN - no V1.3 code authorized before reconciliation and freeze documentation

> This is the authoritative living engineering-history record for the ALPACA Scanner. It preserves problems encountered, evidence observed, architecture selected, alternatives rejected, validation performed, frozen principles, open risks and the next permitted development move.

> **Rev.2 consolidation note:** this revision intentionally consolidates repetitive wording from Rev.1 while preserving the verified development lineage, key defects, architecture decisions and acceptance evidence. The previous detailed Rev.1 remains permanently recoverable in Git commit history; this consolidation must not be interpreted as erasing a prior frozen decision.

---

## 0. Document Control

### 0.1 Purpose

This chronicle answers, for every meaningful phase:

- What problem were we trying to solve?
- What evidence exposed the problem?
- What was the root cause?
- What architecture/rule was selected?
- Why was it preferred?
- Which alternatives were rejected?
- What changed and what explicitly did not change?
- What validation justified acceptance?
- What remains provisional?

### 0.2 Evidence hierarchy

1. Development decisions and acceptance outcomes.
2. Retained source artifacts, tests and roadmap/ADR files.
3. Live Streamlit validation evidence, including screenshots.
4. Calibration datasets/results.
5. Current implementation behavior verified from code.

Historical uncertainty must be marked, not repaired with invented detail.

### 0.3 Status vocabulary

| Status | Meaning |
|---|---|
| WORKING | Active implementation/test stage |
| SHADOW | Calculated/displayed for research; no official decision authority |
| ACCEPTED | Acceptance criteria passed |
| FROZEN | Accepted reference baseline; later change requires a new version |
| SUPERSEDED | Historical stage replaced by a later accepted design |
| DEFERRED | Explicitly postponed with a destination/reason |

### 0.4 Change-control rules

No major stage is fully frozen until behavior passes acceptance, this chronicle is updated, relevant ADRs are updated, known limitations are documented and frozen-principle impact is stated.

No new major phase opens until the **Roadmap Reconciliation Gate** is completed across Roadmap, Chronicle, ADRs, outstanding research, live-test/case-study lessons and frozen dependencies. Every unresolved item must be ASSIGNED, DEFERRED or REJECTED.

---

# 1. Executive Summary

The ALPACA Scanner is a regime-aware U.S. swing-trading decision-support system governed by:

> **Trade With Edge. Strong stock != good entry. NO TRADE is a valid result.**

The architecture deliberately separates:

- **Candidate Quality (CQ):** technical candidate quality;
- **Leadership:** relative-strength persistence and market-stress resilience;
- **Fundamental Quality (FQ):** reported business-performance quality from SEC CompanyFacts;
- **Composite Quality:** higher-level combined candidate assessment;
- **Entry Quality:** separate timing/actionability truth.

The V1.2 Candidate Quality program is now architecture-complete through **V1.2.3c**, which froze F15 as the accepted Composite architecture while leaving it shadow-only. The next program is V1.3 Entry Quality, beginning with the previously outstanding **Contextual Volume Quality Engine**.

---

# 2. Non-Negotiable Architecture Invariants

| ID | Frozen principle |
|---|---|
| CQ-01 | Candidate Quality remains the technical candidate-quality layer |
| CQ-02 | Candidate Quality is not silently overwritten by Composite Quality |
| L-01 | Leadership remains separate and explainable |
| FQ-01 | Fundamental Quality remains a separate business-performance layer |
| FQ-02 | REVIEW/FAIL/unavailable fundamentals are never neutrally imputed |
| COMP-01 | Composite is a higher-level assessment, not a replacement for its inputs |
| ENTRY-01 | Entry Quality remains separate from candidate desirability |
| VOL-01 | Liquidity Quality and Contextual Volume Quality are different domains |
| DATA-01 | Invalid/incomplete/ambiguous data cannot create false precision |
| CAL-01 | Production weight/gate changes require evidence |
| FREEZE-01 | Frozen behavior is not modified in place |
| ACT-01 | NO TRADE remains a valid outcome |

---

# 3. Chronological Development Ledger

## 3.1 V1.0 - Working Alpaca + Streamlit Scanner

**Status:** Complete / Frozen

Established the basic Alpaca market-data + Streamlit scanner architecture and the working path from universe data to candidate output.

## 3.2 V1.1 - Universes + Persistent Quality Screening

**Status:** Complete / Frozen

Introduced explicit stock universes and persistent-quality screening. The scanner began separating universe membership/liquidity from deeper technical scoring rather than treating every tradable symbol equally.

## 3.3 V1.1.1 - Consolidated SIP Data Integrity

**Status:** Complete / Frozen

Established consolidated SIP discipline for previous-day liquidity and historical daily data. Critical liquidity decisions must not silently fall back to partial IEX-only volume. Data-source problems are surfaced explicitly.

## 3.4 V1.1.2 - Scanner Audit Integrity

**Status:** Complete / Frozen

Added scanner-funnel accounting and bucket reconciliation so every persistent-quality candidate must be accounted for in exactly one decision bucket. This became a core acceptance invariant used again in V1.2.3c.

## 3.5 V1.2.1 - Relative Leadership & Market-Stress Resilience

**Status:** Complete / Frozen

Leadership was created as a separate dimension instead of hiding relative-strength behavior inside one technical score. The accepted reference model includes:

- 30% RS20;
- 25% RS50;
- 15% RS acceleration;
- 20% SPY-pullback resilience;
- 10% RS-line proximity to its 100D high.

Persistent-quality eligibility, buckets, Entry Quality and trade decisions remained unchanged while Leadership was validated.

## 3.6 V1.2.1.1 - Leadership Explainability

**Status:** Complete / Frozen

Added Leadership score, grade, confidence and component-level interpretation. The goal was to make later Composite attribution auditable rather than opaque.

## 3.7 V1.2.1.2-V1.2.1.3c - Ticker Inspector / Reference Engine

**Status:** Complete / Frozen at V1.2.1.3c

Built an audit-safe read-only single-ticker diagnostic. Cross-sectional percentile conclusions require a valid reference distribution. The final explicit-action UX established:

> Run Scanner must never create/reactivate Inspector implicitly; Inspector is user-requested and read-only.

## 3.8 V1.2.2 - Fundamental Quality Engine

**Status:** Complete / Frozen as a layer

Fundamental Quality was kept separate from Candidate Quality and Entry Quality. It answers whether reported business performance is supportive; it does not answer whether the stock is buyable now.

## 3.9 V1.2.2.1a-V1.2.2.1b1 - SEC Access, Identity & Fair Access Integrity

**Status:** Complete / Frozen

Live cloud deployment exposed SEC access/identity transport problems. The architecture separated transport failure from financial quality, added Fair Access declaration/diagnostics and kept official SEC CompanyFacts as the financial authority.

Transport failure must never be converted into a low Fundamental score.

## 3.10 V1.2.2.2 - Fundamental Metric Integrity & Cross-Company Validation

**Status:** Accepted / Frozen

Revenue/earnings calculations became provenance-aware. The engine validates concept, unit, period pairing, filing chronology/forms and supports PASS / REVIEW / FAIL states. REVIEW is a valid result when a domain/concept gap is explainable; the engine must not manufacture a value.

Representative validation included AMZN, MSFT, NVDA, UBER and JPM.

## 3.11 V1.2.2.2a - SEC Concept Continuity & Latest-Period Integrity

**Status:** Accepted / Frozen

**Trigger:** UBER exposed a stale 2019 revenue concept being selected while current earnings data existed.

**Hard rule:** a metric labelled Latest Quarter/FY may never fall back to an older reporting period.

Current-period coverage outranks concept declaration order. If no approved current concept exists, the metric is suppressed to N/A / REVIEW rather than substituted with stale history.

## 3.12 V1.2.2.2a1 - Annual Horizon & Filing-Form Integrity

**Status:** Accepted / Frozen

Annual references require annual filing forms in addition to duration. Later interim/TTM/comparative facts cannot displace authoritative annual filing provenance.

## 3.13 V1.2.2.3 - Fundamental Universe Coverage & Cache Validation

**Status:** Accepted / Frozen

Scaled SEC Fundamental Quality to bounded persistent-quality samples (10/25/50) without allowing FQ to select its own validation population. Promotion gate: CompanyFacts hard failures 0, metric-integrity hard FAIL 0, usable coverage >=90%, REVIEW only when explainable/fail-visible.

## 3.14 V1.2.3 - Composite Candidate Quality Shadow Calibration

**Status:** Calibration captured / superseded by later refinements

Created:

- No-Fund = 70% CQ + 30% Leadership;
- F10 = 63% CQ + 27% L + 10% F;
- F20 = 56% CQ + 24% L + 20% F;
- F30 = 49% CQ + 21% L + 30% F.

F20 was a calibration reference, never a production commitment.

## 3.15 V1.2.3a - Composite Attribution & Incremental Fundamental Impact

**Status:** Accepted / Frozen

Separated Leadership impact from incremental Fundamental impact:

`Official CQ -> No-Fund -> F10/F20/F30`

This prevented Leadership promotion and Fundamental demotion from being conflated in a single rank-change number.

## 3.16 V1.2.3b - Weight Robustness & Guardrail Calibration

**Status:** Research completed

Tested F05/F10/F15/F20/F25/F30 and simulated symmetric F20 Fundamental-impact caps at +/-4, +/-6 and +/-8 points. Raw F20 remained uncapped. Technical-led / weak-fundamental names were explicitly watched to determine whether a continuous Fundamental weight could excessively suppress legitimate technical leadership.

## 3.17 V1.2.3b1 - Full-Precision Robustness Integrity Fix

**Status:** Accepted / Frozen

**Trigger:** tiny F10/F20/F30 rank-correlation mismatches between accepted attribution and robustness views.

**Root cause:** robustness reconstructed scenarios from a rounded display No-Fund value.

**Fix:** accepted F10/F20/F30 anchors are reused; new interpolation/guardrail calculations use unrounded internals; display rounding never drives ranking.

## 3.18 V1.2.3b2 - Pre-Revenue / Zero-Revenue Domain Integrity

**Status:** Accepted / Frozen

**Trigger:** Russell 2000 sample exposed SRRK as a hard FAIL due to non-consecutive annual revenue pairing.

**Fix:** annual YoY requires a genuine prior-year comparator (320-410 day gap). If unavailable, annual YoY is N/A and the state is explainable REVIEW; no stale/non-consecutive substitution. Genuine structural defects remain FAIL. The rule is generic, not ticker-specific.

## 3.19 V1.2.3c - F15 Composite Architecture & Explainable Guardrail

**Status:** **ACCEPTED / FROZEN - 7 Sep 2026**  
**ADR:** `docs/architecture/ADR-001-composite-quality-f15.md`

### Decision

Freeze the reference Composite architecture as:

> **F15 = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality**

F20 remains a shadow sensitivity benchmark. No hard Fundamental-impact cap is applied. Instead expose:

- NORMAL: `|impact| < 4 pts`;
- MATERIAL: `4-6 pts`;
- HIGH IMPACT: `>6 pts`.

REVIEW/FAIL/unavailable FQ remains unscored/unranked. F15 remains shadow-only and does not gain production ordering authority through this freeze.

### Offline regression

- V1.2.3b1 precision tests: 10/10 PASS;
- V1.2.3b2 domain tests: 5/5 PASS;
- V1.2.3c architecture tests: 7/7 PASS;
- combined: **22/22 PASS**.

### Final live acceptance - S&P 500

**Controls:** S&P 500 / STRICT / min $5 / prev-day $vol $20M / max deep scan 2000 / strict event gate ON / Fundamental sample 50.

**Scanner/audit:** 503 universe members; 495 matched; 495 completed SIP bars; 495 deep-scanned; 127 persistent-quality; **127/127 bucket reconciliation PASS**; usable SIP **100%**; missing SIP bars **0**.

**Fundamental batch:** 50 requested; CompanyFacts 50 PASS; Integrity **47 PASS / 3 REVIEW / 0 FAIL**; usable coverage **94.0%**; median FQ **60.8/100**.

**3E precision:** **FULL-PRECISION INTEGRITY PASS**; rankable 47/50; stable Top-10 F10-F30 9/10; stable center Top-10 F15/F20/F25 10/10; median rank range 4.0; high-sensitivity names 20; F20 +/-6 triggers 19.

**3F selected architecture:** **V1.2.3c INTEGRITY PASS**; F15 rankable 47/50; formula 59.5/25.5/15; F15<->F20 Top-10 10/10; Spearman **0.984**; 27 NORMAL / 10 MATERIAL / 10 HIGH IMPACT; median |F15 F impact| **3.76 pts**; hard score cap **NONE**.

**Official buckets:** 0 ACTIONABLE NOW + 57 TECH+EVENT CHECK + 42 A-QUALITY-WAIT + 2 WAIT/ENTRY NOT READY + 22 DEVELOPING + 4 AVOID/BROKEN = **127/127**.

### Final live acceptance - Russell 2000 (IWM proxy)

**Controls:** Russell 2000 proxy / STRICT / min $5 / prev-day $vol $20M / max deep scan 2000 / strict event gate ON / Fundamental sample 50.

**Scanner/audit:** 1,954 proxy-universe members; 1,945 matched; 602 deep-scanned; 74 persistent-quality; **74/74 bucket reconciliation PASS**; usable SIP **100%**; missing SIP bars **0**; unmatched symbols disclosed explicitly.

**Fundamental batch:** 50 requested; CompanyFacts 50 PASS; Integrity **47 PASS / 3 REVIEW / 0 FAIL**; usable coverage **94.0%**; median FQ **59.9/100**.

**3E precision:** **FULL-PRECISION INTEGRITY PASS**; rankable 47/50; stable Top-10 F10-F30 7/10; stable center Top-10 F15/F20/F25 8/10; median rank range 5.0; high-sensitivity names 25; F20 +/-6 triggers 21.

**3F selected architecture:** **V1.2.3c INTEGRITY PASS**; F15 rankable 47/50; formula 59.5/25.5/15; F15<->F20 Top-10 8/10; Spearman **0.986**; 23 NORMAL / 12 MATERIAL / 12 HIGH IMPACT; median |F15 F impact| **4.14 pts**; hard score cap **NONE**.

**Official buckets:** 0 ACTIONABLE NOW + 14 TECH+EVENT CHECK + 51 A-QUALITY-WAIT + 1 WAIT/ENTRY NOT READY + 5 DEVELOPING + 3 AVOID/BROKEN = **74/74**.

### Freeze conclusion

Both universes passed the live integrity and official-decision-path invariants. V1.2.3c is frozen as an auditable **shadow Composite architecture**, not as a proven trading edge and not as production ranking authority.

---

# 4. Process Gap Review - Contextual Volume Quality Omission

## 4.1 What happened

Contextual Volume Quality had been retained as an outstanding research item, but it was not promoted into the formal GitHub roadmap as a named stage. After V1.2.3c acceptance, development followed the formal roadmap mechanically and decomposed V1.3 around entry location/trigger/R:R without first reconciling unresolved research items.

The current code already contains rudimentary volume logic, which made the omission easier to miss: breakout confirmation uses relative-volume expansion and pullback/VCP logic gives a small benefit for contraction. That is not equivalent to a complete Contextual Volume Quality engine.

## 4.2 Root cause

Two planning layers were not formally reconciled:

1. research/backlog decisions retained from development discussions;
2. the formal GitHub roadmap.

An item could therefore remain known but unmapped.

## 4.3 Control introduced

A mandatory **Roadmap Reconciliation Gate** now precedes every new major phase. Roadmap, Chronicle, ADRs, outstanding research, case-study/live-test lessons and frozen dependencies must be reconciled. Every open item must be ASSIGNED, DEFERRED or REJECTED.

## 4.4 Architecture correction

V1.3 is now decomposed as:

1. **V1.3a - Contextual Volume Quality Engine**;
2. V1.3b - Entry Location & Anti-Chase;
3. V1.3c - Trigger & Entry-Zone;
4. V1.3d - Risk/Reward & Stop-Distance Gate;
5. V1.3e - READY / WATCH / WAIT / NO CHASE decisions;
6. V1.3f - Shadow Execution-Capture Logging / staged-execution preparation.

This correction is made **before any V1.3 code patch**, so no frozen layer needs repair.

---

# 5. V1.3a - Contextual Volume Quality Engine

**Status:** OPEN / DESIGN  
**Initial mode:** SHADOW ONLY

## 5.1 Architectural boundary

> **Liquidity Quality != Contextual Volume Quality.**

Liquidity answers whether a security is tradeable efficiently. Contextual Volume Quality asks whether participation confirms or contradicts the current setup/entry.

Volume Quality belongs downstream near Setup/Entry, not inside F15 Composite.

## 5.2 Why the current volume logic is insufficient

Existing scoring uses limited volume conditions such as breakout relative-volume confirmation and low/contraction volume for pullback/VCP. It does not yet evaluate:

- volume trend across multiple sessions;
- setup-specific dry-up versus expansion;
- up-day/down-day participation asymmetry;
- abnormal distribution;
- price-volume disagreement;
- volume behavior during recent stress;
- explicit Volume Data Confidence.

## 5.3 Candidate research features

Before weights are selected, V1.3a should expose/validate:

- current RVOL versus 20D baseline;
- 5D/10D volume trend/dry-up;
- breakout participation quality;
- pullback volume contraction quality;
- VCP/tightening contraction quality;
- up-volume vs down-volume behavior;
- abnormal distribution/heavy selling count;
- price-volume confirmation/divergence;
- volume behavior during pullback/stress windows;
- consolidated-SIP Volume Data Confidence / coverage.

The first patch should emphasize feature integrity and explainability, not force a final score formula prematurely.

---

# 6. Outstanding Research / Dependency Register

| ID | Item | Disposition | Destination | Rule |
|---|---|---|---|---|
| R-001 | Contextual Volume Quality | ASSIGNED | **V1.3a** | First V1.3 work item |
| R-002 | Candidate-vs-Entry feature separation | ASSIGNED | V1.3b-V1.3e | Preserve separate truth layers |
| R-003 | Continuous EMA8/EMA20 extension/location quality | ASSIGNED | V1.3b | Hard NO CHASE remains a ceiling |
| R-004 | Trigger and entry-zone architecture | ASSIGNED | V1.3c | Do not assume current close is the planned entry |
| R-005 | Stop-distance / prospective R:R | ASSIGNED | V1.3d | Evaluate edge before actionability |
| R-006 | READY/WATCH/WAIT/NO CHASE mapping | ASSIGNED | V1.3e | Decision-first output |
| R-007 | ACTIONABLE-A/B/C staged execution | DEFERRED/PREP | V1.3f -> V1.6/V1.8 | Fixed total portfolio risk |
| R-008 | Signal Capture Rate / Missed Opportunity R | ASSIGNED | V1.3f -> V1.7 | Start logging before formal lab |
| R-009 | Earnings/event reliability | ASSIGNED | V1.5 | UNKNOWN must not equal safe |
| R-010 | F15 production ranking influence | DEFERRED | V1.7+ | Requires outcome evidence |
| R-011 | Stress-window sensitivity 6/10/12 sessions | DEFERRED | V1.7 | Validation research, not immediate redesign |
| R-012 | Volume-data confidence | ASSIGNED | V1.3a | Consolidated SIP, completed sessions, fail-visible |

---

# 7. CF Case Study #001 - Execution Architecture Lesson

CF was found early, passed ACTIONABLE and the key resistance/trigger area around $133 was identified, but execution capture failed. The lesson is not to loosen standards. It is to convert hindsight regret into execution architecture:

**Find Edge -> Execute Edge -> Prove Edge -> Improve Edge**

Retained roadmap dependencies:

- ACTIONABLE-A Starter -> ACTIONABLE-B Add -> ACTIONABLE-C Full Trigger;
- pre-planned conditional breakout execution;
- maximum chase/fill limits;
- fixed total portfolio risk;
- Forward Test Lab separation of Signal Quality from Execution Capture;
- Signal Capture Rate and Missed Opportunity R.

These are staged into V1.3f/V1.6/V1.7/V1.8 rather than being forced into V1.3a.

---

# 8. Known Limitations & Open Risks

1. F15 architecture mechanics are accepted, but no forward expectancy is proven.
2. F15 remains shadow-only; production ranking authority is deferred.
3. Fundamental concept coverage can still require sector/domain-specific work.
4. Event-date reliability remains immature and belongs to V1.5.
5. Entry Quality remains coarse relative to the planned V1.3 architecture.
6. Contextual Volume Quality is not yet a formal engine; current volume use is rudimentary.
7. Paper execution and trade journaling are not yet established.
8. Future recalibration of frozen layers requires explicit new evidence/versioning.

---

# 9. Version Ledger

| Version | Theme | Status |
|---|---|---|
| V1.0 | Core Alpaca/Streamlit scanner | Frozen |
| V1.1 | Universes/persistent quality | Frozen |
| V1.1.1 | Consolidated SIP integrity | Frozen |
| V1.1.2 | Scanner audit integrity | Frozen |
| V1.2.1 | Leadership/resilience | Frozen |
| V1.2.1.1 | Leadership explainability | Frozen |
| V1.2.1.2-1.2.1.3c | Ticker Inspector/reference UX | Frozen |
| V1.2.2 | Fundamental Quality | Frozen |
| V1.2.2.1a-1b1 | SEC access/identity/Fair Access | Frozen |
| V1.2.2.2 | Metric integrity | Frozen |
| V1.2.2.2a | Concept continuity | Frozen |
| V1.2.2.2a1 | Annual form/horizon integrity | Frozen |
| V1.2.2.3 | Fundamental batch coverage | Frozen |
| V1.2.3 | Composite calibration | Superseded/refined |
| V1.2.3a | Attribution | Frozen |
| V1.2.3b | Robustness/guardrails | Research completed |
| V1.2.3b1 | Full precision | Frozen |
| V1.2.3b2 | Pre-revenue integrity | Frozen |
| **V1.2.3c** | **F15 architecture / explainable impact** | **ACCEPTED / FROZEN** |
| **V1.3a** | **Contextual Volume Quality** | **OPEN / DESIGN** |

---

# 10. Documentation Standard for Future Phases

Every future major phase record must include:

1. version/stage;
2. objective;
3. problem/trigger;
4. evidence/symptom;
5. root cause;
6. architecture/solution;
7. why this architecture;
8. alternatives considered/rejected;
9. BEFORE vs AFTER delta;
10. files/modules affected;
11. what did not change;
12. validation performed;
13. acceptance criteria;
14. acceptance result;
15. known limitations;
16. decision confidence;
17. frozen-principle impact;
18. future dependency;
19. Roadmap Reconciliation disposition for outstanding research/case-study items.
