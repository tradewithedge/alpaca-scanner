# ALPACA Scanner - Development Chronicle & Architecture Record

**Revision:** Rev.5  
**Prepared:** 11 September 2026  
**Current accepted implementation checkpoint:** V1.3c - Trigger & Entry-Zone Architecture  
**V1.3c status:** **ACCEPTED / FROZEN (SHADOW)**  
**Official decision-layer authority:** unchanged by V1.3c  
**Next development checkpoint:** V1.3d - Risk/Reward & Stop-Distance Gate

> This is the authoritative living engineering-history record for the ALPACA Scanner. It preserves problems encountered, evidence observed, architecture selected, alternatives rejected, validation performed, frozen principles, open risks and the next permitted development move.

> **Rev.4 note:** this revision freezes V1.3b after machine-readable S&P 500 and Russell 2000 validation, records continuous entry-location pressure/headroom as a shadow architecture, preserves the existing hard NO CHASE ceilings unchanged, and formally opens V1.3c. Rev.3's V1.3a freeze, Validation Evidence Standard and V1.7 Expectancy / Backtest / Forward-Test clarification remain in force.

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

1. Development decisions, acceptance outcomes and frozen architecture records.
2. Retained source artifacts, automated tests, Roadmap and ADR files.
3. **Full machine-readable live/calibration evidence with programmatic reconciliation.**
4. Live Streamlit screenshots for deployment/settings/UI proof.
5. Current implementation behavior verified from code.

Screenshots remain useful acceptance evidence for UI/deployment state, but screenshots alone do not freeze a quantitative engine when full-population machine-readable evidence is available.

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

No new major phase opens until the **Roadmap Reconciliation Gate** is completed across Roadmap, Chronicle, ADRs, outstanding research, live-test/case-study lessons and frozen dependencies. Every unresolved item must be ASSIGNED, DEFERRED, REJECTED or explicitly RESOLVED/FROZEN.

### 0.5 Validation Evidence Standard

For quantitative acceptance, full machine-readable evidence is required whenever the system can produce it.

Programmatic checks should include as applicable:

- full-population row reconciliation;
- unique symbols / duplicates;
- missingness;
- frozen-layer equality;
- bucket/state reconciliation;
- confidence/data-quality coverage;
- session/timestamp alignment;
- cross-universe behavior;
- threshold/outlier/borderline cases.

A dashboard table may be capped for readability, but a capped display/export is not proof of a complete population. Use a full underlying export or full audit table.

---

# 1. Executive Summary

The ALPACA Scanner is a regime-aware U.S. swing-trading decision-support system governed by:

> **Trade With Edge. Strong stock != good entry. NO TRADE is a valid result.**

The architecture deliberately separates:

- **Candidate Quality (CQ):** technical candidate quality;
- **Leadership:** relative-strength persistence and market-stress resilience;
- **Fundamental Quality (FQ):** reported business-performance quality from SEC CompanyFacts;
- **Composite Quality:** higher-level combined candidate assessment;
- **Entry Quality:** separate timing/actionability truth;
- **Contextual Volume Quality:** setup-dependent participation evidence near Setup/Entry;
- **Entry Location:** continuous extension/headroom evidence near the frozen anti-chase boundary.

The V1.2 Candidate Quality program is architecture-complete through **V1.2.3c**. V1.3a is frozen as a **SHADOW contextual-volume diagnostic architecture**. V1.3b is frozen as a **SHADOW entry-location / anti-chase architecture**. V1.3c is now frozen as a **SHADOW trigger/entry-zone architecture**. The next permitted development move is **V1.3d - Risk/Reward & Stop-Distance Gate**.

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
| ENTRY-02 | A strong stock or high Entry Quality score cannot override a frozen hard NO CHASE breach |
| LOC-01 | Hard anti-chase ceilings are ceilings, not targets; sub-ceiling deterioration can be measured continuously without relaxing the ceiling |
| LOC-02 | Entry Location diagnostics remain separate from official Entry Quality until explicitly promoted by later evidence |
| VOL-01 | Liquidity Quality and Contextual Volume Quality are different domains |
| VOL-02 | Volume meaning is setup-dependent; breakout expansion and pullback/VCP contraction are not interchangeable |
| DATA-01 | Invalid/incomplete/ambiguous data cannot create false precision |
| DATA-02 | Session completeness must be explicit when comparing volume against full-session baselines |
| CAL-01 | Production weight/gate changes require evidence |
| VAL-01 | Quantitative acceptance requires machine-readable full-population evidence when available |
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

Added scanner-funnel accounting and bucket reconciliation so every persistent-quality candidate must be accounted for in exactly one decision bucket. This became a core acceptance invariant used again in later phases.

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

F20 remains a shadow sensitivity benchmark. No hard Fundamental-impact cap is applied. REVIEW/FAIL/unavailable FQ remains unscored/unranked. F15 remains shadow-only and does not gain production ordering authority through this freeze.

### Validation summary

Offline regression: **22/22 PASS** across retained V1.2.3b1, V1.2.3b2 and V1.2.3c tests.

Final S&P 500 and Russell 2000 live acceptance passed formula/precision integrity, Fundamental coverage, official bucket reconciliation and official-decision-path isolation. V1.2.3c is frozen as an auditable shadow Composite architecture, not as a proven trading edge and not as production ranking authority.

---

# 4. Process Gap Review - Contextual Volume Quality Omission

## 4.1 Symptom

Contextual Volume Quality had been retained as an outstanding research item, but it was not promoted into the formal GitHub roadmap as a named stage. After V1.2.3c acceptance, development followed the formal roadmap mechanically and decomposed V1.3 around entry location/trigger/R:R without first reconciling unresolved research items.

## 4.2 Root cause

Two planning layers were not formally reconciled: research/backlog decisions retained from development discussions and the formal GitHub roadmap.

## 4.3 Corrective action

A mandatory **Roadmap Reconciliation Gate** now precedes every new major phase. Roadmap, Chronicle, ADRs, outstanding research, case-study/live-test lessons and frozen dependencies must be reconciled.

## 4.4 Prevention rule

Every open item must be ASSIGNED, DEFERRED, REJECTED or RESOLVED/FROZEN. No unresolved design dependency may remain only in conversational memory.

## 4.5 Architecture correction

V1.3 is decomposed as:

1. V1.3a - Contextual Volume Quality Diagnostics;
2. V1.3b - Entry Location & Anti-Chase;
3. V1.3c - Trigger & Entry-Zone;
4. V1.3d - Risk/Reward & Stop-Distance Gate;
5. V1.3e - READY / WATCH / WAIT / NO CHASE decisions;
6. V1.3f - Shadow Execution-Capture Logging / staged-execution preparation.

---

# 5. V1.3a - Contextual Volume Quality Diagnostics

**Status:** **ACCEPTED / FROZEN (SHADOW) - 11 Sep 2026**  
**ADR:** `docs/architecture/ADR-002-contextual-volume-quality-v13a.md`

## 5.1 Objective

Create a setup-aware volume evidence layer that distinguishes breakout participation/expansion, pullback/VCP/tight-base contraction, accumulation versus distribution, constructive versus conflicting price-volume behavior, and trustworthy versus insufficient volume data.

## 5.2 Implemented architecture

The accepted V1.3a layer:

- classifies price context before interpreting new volume diagnostics;
- uses completed consolidated SIP daily sessions;
- excludes the same-day daily bar before **16:30 ET**;
- uses explicit HIGH / MEDIUM / LOW Volume Data Confidence;
- makes LOW confidence **NOT RANKED**, not neutral;
- calculates completed-session RVOL versus prior 20 sessions and non-overlapping 5D/10D volume trends;
- measures up/down-volume participation, up-volume share, accumulation and distribution sessions;
- interprets breakout expansion differently from pullback/VCP contraction;
- prevents favorable volume from rescuing broken price structure;
- returns a separate shadow table and creates no 0-100 Volume Quality score.

## 5.3 Validation

- `py_compile`: PASS.
- Dedicated V1.3a unit/integration suite: **22/22 PASS**.
- S&P 500 machine-readable reconciliation: **127/127 exact population**, duplicates 0, official bucket/setup/CQ/EQ mismatches 0, 127/127 HIGH confidence.
- Russell controlled same-session reconciliation: **85/85 exact population**, duplicates 0, official bucket/setup/CQ/EQ mismatches 0, 85/85 HIGH confidence.

## 5.4 Session-comparability finding

### Symptom

During an intraday Russell run, frozen official `vol_ratio` and V1.3a `rvol_20` differed dramatically for some stocks.

### Root cause

The two metrics were sometimes observing different session completeness: the frozen metric could use the latest partial daily bar, while V1.3a deliberately excluded a same-day bar before 16:30 ET.

### Corrective action / evidence

A controlled same-completed-session sample produced Pearson **0.999966**, Spearman **0.999790**, and **85/85 two-decimal matches**.

### Prevention rule

Session completeness must be explicit in future volume validation. Any future intraday participation metric must compare like-for-like time-of-day participation.

## 5.5 Acceptance decision

V1.3a is **ACCEPTED / FROZEN as a SHADOW diagnostic architecture**. Trading expectancy and threshold optimality remain unproven and belong to V1.7.

---

# 6. V1.3b - Entry Location & Anti-Chase Foundation

**Status:** **ACCEPTED / FROZEN (SHADOW) - 11 Sep 2026**  
**ADR:** `docs/architecture/ADR-003-entry-location-anti-chase-v13b.md`

## 6.1 Objective

Expose continuous deterioration in entry location **before** the existing frozen binary NO CHASE gate is crossed, while preserving the hard ceiling itself.

The design answers a different question from Candidate Quality:

> **How much anti-chase headroom is left at the current location?**

A strong stock can still be a poor entry when extension has consumed most of the available headroom.

## 6.2 Problem / trigger

The pre-V1.3b anti-chase gate already used three hard ceilings:

- EMA8 extension > **5.0%**;
- EMA20 extension > **8.0%**;
- EMA20 extension > **2.0 ATR**.

This is effective for rejecting a clear chase, but it is binary. A stock at 99% of a ceiling and a stock at 20% of a ceiling are both technically "not chase" until the strict `>` breach occurs.

### Root cause

The production architecture contained a hard safety gate but no transparent continuous location measure tied to that gate.

### Corrective action

V1.3b adds a separate SHADOW diagnostic table that converts each positive extension axis into percentage pressure against the existing frozen ceiling and reports remaining headroom.

### Prevention rule

A hard ceiling must not be interpreted as an ideal target. Future entry architecture should preserve the hard NO CHASE ceiling while separately measuring deterioration before the ceiling.

## 6.3 Implemented architecture

The accepted V1.3b calculations are:

- `EMA8 pressure = 100 x max(0, ext_ema8_pct) / 5.0`;
- `EMA20 pressure = 100 x max(0, ext_ema20_pct) / 8.0`;
- `ATR pressure = 100 x max(0, ext_atr) / 2.0`;
- `max_chase_pressure_pct = max(EMA8 pressure, EMA20 pressure, ATR pressure)`;
- `hard_ceiling_headroom_pct = 100 - max_chase_pressure_pct`.

The dominant extension axis is explicitly shown.

**100% pressure is exactly at a frozen ceiling.** The official hard gate remains strict `>`, so exactly at a ceiling is not a breach. Any axis above 100% independently constitutes hard NO CHASE.

## 6.4 Shadow states

The reference diagnostic states are:

- **REPAIR / BELOW EMA20:** EMA20 extension < -1.5%;
- **PRIME / CONTROLLED:** max pressure <= 40% and EMA20 extension <= 3.0%;
- **ACCEPTABLE:** max pressure <= 65%;
- **STRETCHED:** max pressure <= 85%;
- **VERY LATE / AT CEILING:** non-hard condition above the STRETCHED band, including exactly at a ceiling;
- **NO CHASE — HARD CEILING:** one or more frozen official ceilings exceeded;
- **NOT RANKED:** required extension inputs are incomplete.

These bands are frozen only as the **V1.3b shadow reference architecture**. They are not claimed to be expectancy-optimal production thresholds.

## 6.5 Integrity / isolation design

- V1.3b deep-copies/reads the official scored population and builds a separate diagnostic table.
- It does not alter Candidate Quality, F15, official Entry Quality, ranking, buckets, event gates or trade decisions.
- It independently recomputes hard NO CHASE and compares it with the frozen official `chase_reasons` result.
- Required missing inputs produce **NOT RANKED / LOW confidence** rather than neutral imputation.
- No 0-100 production Entry Location score exists.

## 6.6 Offline validation

- `py_compile`: PASS.
- Targeted V1.3b unit/regression/integration validation: **53/53 PASS**.
- Offline replay on prior accepted machine-readable S&P and Russell samples achieved complete hard-NO-CHASE parity and official-field reconciliation. The replay was used as engineering smoke evidence only, not as live acceptance.

## 6.7 S&P 500 live validation

**Controls:** S&P 500 / STRICT / min $5 / prev-day $vol $20M / max deep scan 2000.

Full Swing Candidates and full Entry Location CSVs were reconciled programmatically:

- **119 official candidates / 119 Entry Location rows**;
- **119/119 exact symbol population match**;
- duplicate symbols **0**;
- official bucket mismatches **0**;
- official setup mismatches **0**;
- Candidate Quality mismatches **0**;
- Entry Quality mismatches **0**;
- Location Data Confidence **119/119 HIGH**;
- independent hard NO CHASE parity **119/119 PASS**;
- states: **68 PRIME/CONTROLLED + 11 ACCEPTABLE + 6 STRETCHED + 4 VERY LATE + 25 REPAIR + 5 HARD NO CHASE = 119**;
- near-ceiling non-hard watch (75%-<100% pressure): **5**;
- official ACTIONABLE/TECH ACTIONABLE names already STRETCHED/VERY LATE: **0 - not observed**.

Representative near-ceiling cases:

| Symbol | Max pressure | State |
|---|---:|---|
| DVN | 95.62% | VERY LATE |
| CVX | 94.81% | VERY LATE |
| HPQ | 94.77% | VERY LATE |
| COP | 93.03% | VERY LATE |
| ELV | 79.80% | STRETCHED |

Hard NO CHASE names in this sample were SWKS, VLO, META, PSX and MPC, each independently breaching at least one frozen ceiling.

## 6.8 Russell 2000 live validation

**Controls:** Russell 2000 (IWM proxy) / STRICT / min $5 / prev-day $vol $20M / max deep scan 2000 / strict earnings-event gate ON.

Machine-readable reconciliation:

- **85 official candidates / 85 Entry Location rows**;
- **85/85 exact symbol population match**;
- duplicate symbols **0**;
- official bucket mismatches **0**;
- official setup mismatches **0**;
- Candidate Quality mismatches **0**;
- Entry Quality mismatches **0**;
- Location Data Confidence **85/85 HIGH**;
- independent hard NO CHASE parity **85/85 PASS**;
- states: **36 PRIME/CONTROLLED + 16 ACCEPTABLE + 10 STRETCHED + 5 VERY LATE + 12 REPAIR + 6 HARD NO CHASE = 85**;
- near-ceiling non-hard watch (75%-<100% pressure): **10**;
- official ACTIONABLE/TECH ACTIONABLE names already STRETCHED/VERY LATE: **0 - not observed**.

Representative near-ceiling cases:

| Symbol | Max pressure | State |
|---|---:|---|
| CRGY | **99.56%** | VERY LATE |
| TXG | 98.85% | VERY LATE |
| ANF | 94.70% | VERY LATE |
| CRC | 90.44% | VERY LATE |
| AVAH | 90.02% | VERY LATE |
| PTEN | 79.65% | STRETCHED |
| PBF | 78.52% | STRETCHED |
| TDS | 78.36% | STRETCHED |
| SM | 77.39% | STRETCHED |
| TARS | 75.35% | STRETCHED |

Hard NO CHASE names were ASO, CVI, SIG, CLMT, DHT and ATRC.

### CRGY canonical example

CRGY consumed **99.56%** of its most restrictive frozen ceiling, leaving only **0.44% normalized headroom**, yet the frozen binary gate correctly remained "not chase" because the ceiling had not actually been exceeded.

This is the architectural distinction V1.3b was designed to expose:

> **Not yet a hard breach does not mean good entry location.**

## 6.9 Cross-universe result

The Russell sample showed greater extension pressure than the S&P sample:

| Measure | S&P 500 | Russell 2000 |
|---|---:|---:|
| Hard NO CHASE | 5/119 = 4.2% | 6/85 = 7.1% |
| Near ceiling 75%-<100% | 5/119 = 4.2% | 10/85 = 11.8% |
| Non-hard STRETCHED + VERY LATE | 10/119 = 8.4% | 15/85 = 17.6% |

The cross-universe difference is accepted as useful diagnostic information. It is not interpreted as proof of predictive return value.

## 6.10 Acceptance decision

V1.3b is **ACCEPTED / FROZEN as a SHADOW Entry Location / Anti-Chase architecture**.

Accepted:

- continuous EMA8 / EMA20 / ATR pressure measurement;
- dominant extension axis;
- explicit remaining headroom;
- separate REPAIR treatment;
- exact preservation of the existing strict hard NO CHASE semantics;
- independent hard-gate parity;
- official-layer isolation;
- fail-visible NOT RANKED behavior;
- cross-universe machine-readable validation.

Not authorized:

- relaxing/replacing frozen hard NO CHASE ceilings;
- modifying official Entry Quality;
- automatic official bucket downgrades from shadow bands;
- a new production Entry Location score;
- claiming PRIME/ACCEPTABLE/STRETCHED/VERY LATE bands are expectancy-optimal.

Trading outcome value and band calibration remain V1.7 dependencies.

---

# 7. Process Gap Review - Quantitative Validation Evidence

## 7.1 Symptom

Earlier live validation relied too heavily on screenshots, including wide diagnostic tables. Screenshots were useful for deployment proof but inefficient and insufficient for full row-level reconciliation.

A concrete V1.3a example occurred when the dashboard headline showed **41 CONFIRMING** while the displayed/exported confirming table contained **40 rows** because the UI intentionally used a display cap. The full diagnostic audit correctly contained all 41.

## 7.2 Root cause

Two evidence purposes were conflated: **UI/deployment acceptance** and **quantitative engine acceptance**.

## 7.3 Corrective action

The project uses the **Validation Evidence Standard**:

- screenshots: version/settings/banner/headline/UI proof;
- full CSV/machine-readable data: quantitative analysis and freeze evidence;
- programmatic reconciliation: row counts, population identity, frozen-layer equality, duplicates, nulls, states, confidence and session alignment.

## 7.4 Prevention rule

A quantitative engine cannot be frozen from screenshots alone when complete machine-readable evidence is available. Display caps must never be mistaken for population caps.

---

# 8. Outstanding Research / Dependency Register

The register is reconciled to one canonical ID set shared with `ROADMAP.md`.

| ID | Item | Disposition | Destination | Rule |
|---|---|---|---|---|
| R-001 | Contextual Volume Quality diagnostics architecture | **RESOLVED / FROZEN SHADOW** | **V1.3a** | Architecture accepted; outcome calibration remains V1.7 work |
| R-002 | Candidate-vs-Entry feature separation | ASSIGNED | V1.3b-V1.3e | Preserve separate truth layers |
| R-003 | Continuous EMA8/EMA20 extension/location quality | **RESOLVED / FROZEN SHADOW** | **V1.3b** | Continuous pressure/headroom accepted; production threshold value remains V1.7 work |
| R-004 | Trigger and entry-zone architecture | **RESOLVED / FROZEN SHADOW** | **V1.3c** | Trigger/zone/max-fill architecture accepted; parameter expectancy deferred to V1.7 |
| R-005 | Stop-distance / prospective R:R | ASSIGNED | V1.3d | Evaluate edge before actionability |
| R-006 | ACTIONABLE-A/B/C staged execution | DEFERRED / PREP | V1.3f -> V1.6/V1.8 | Fixed total portfolio risk |
| R-007 | Signal Capture Rate / Missed Opportunity R | ASSIGNED | V1.3f -> V1.7 | Start prospective logging; diagnostics underneath expectancy |
| R-008 | Earnings/event reliability | ASSIGNED | V1.5 | UNKNOWN must not equal safe |
| R-009 | F15 production ranking influence | DEFERRED | V1.7+ | Requires outcome evidence |
| R-010 | Stress-window sensitivity 6/10/12 sessions | DEFERRED | V1.7 | Validation research, not immediate redesign |
| R-011 | Volume-data confidence / completed-session reliability | **RESOLVED / FROZEN** | V1.3a | Completed SIP + fail-visible confidence accepted |
| R-012 | Relative-strength level/direction/resilience | RESOLVED / VALIDATE LATER | V1.2.1 + V1.7 | Architecture frozen; outcome validation later |
| **R-013** | **Trading expectancy / edge validation** | **ASSIGNED** | **V1.7** | **Central KPI using Backtest + Forward-Test evidence** |
| R-014 | READY / WATCH / WAIT / NO CHASE mapping | ASSIGNED | V1.3e | Decision-first output |
| R-015 | Entry Location band expectancy / calibration | DEFERRED / VALIDATE | V1.7 | Validate outcome separation before production authority |

---

# 9. CF Case Study #001 - Execution Architecture Lesson

CF was found early, passed ACTIONABLE and the key resistance/trigger area around $133 was identified, but execution capture failed. The lesson is not to loosen standards. It is to convert hindsight regret into execution architecture:

**Find Edge -> Execute Edge -> Prove Edge -> Improve Edge**

Retained roadmap dependencies:

- ACTIONABLE-A Starter -> ACTIONABLE-B Add -> ACTIONABLE-C Full Trigger;
- pre-planned conditional breakout execution;
- maximum chase/fill limits;
- fixed total portfolio risk;
- separation of Signal Quality from Execution Capture;
- Signal Capture Rate and Missed Opportunity R;
- formal expectancy validation.

**Prove Edge** is explicitly defined as outcome validation using **Backtest + Forward-Test expectancy evidence**. Signal Capture Rate and Missed Opportunity R explain execution capture; they do not replace expectancy.

These dependencies remain staged into V1.3f/V1.6/V1.7/V1.8 rather than being forced into V1.3c.

---

# 10. V1.3c - Trigger & Entry-Zone Architecture

## 10.1 Governing problem

The current scanner still relies heavily on the current close as the practical entry reference. V1.3b tells us whether the current location is early or late, but it does not yet define **where a trade should actually be entered**.

V1.3c must separate:

- current observed price;
- planned entry zone;
- breakout/pullback trigger level;
- confirmation condition;
- maximum acceptable fill/chase boundary.

The goal is not to manufacture more trades. It is to make execution intent explicit before V1.3d evaluates stop distance and prospective R:R.

## 10.2 Frozen dependencies entering V1.3c

V1.3c must preserve:

- Candidate Quality / Composite separation;
- V1.3a Contextual Volume shadow architecture;
- V1.3b hard NO CHASE ceilings and shadow location pressure/headroom;
- official decision path unless/until a later phase explicitly promotes new logic;
- NO TRADE as a valid outcome.

V1.3c should begin in **SHADOW** and be validated with machine-readable exports before any production influence is considered.

---

## 10.3 Final V1.3c Acceptance Record

**Status:** **ACCEPTED / FROZEN (SHADOW) - 13 Sep 2026**  
**ADR:** `docs/architecture/ADR-004-trigger-entry-zone-v13c.md`

### Live machine-readable evidence

**S&P 500 / STRICT:**

- 116 official candidates and 116 diagnostic rows;
- exact symbol population match 116/116; duplicates 0;
- official bucket/setup/CQ/EQ/legacy `entry_px` mismatches 0;
- Plan Data Confidence 116/116 HIGH;
- prior-20 structure parity 116/116 PASS;
- states: 63 WAITING, 12 IN ENTRY ZONE, 4 ABOVE ZONE/LATE, 2 MISSED/NO CHASE, 7 BLOCKED, 28 NO STRUCTURED PLAN;
- 116/116 state reconciliation.

**Russell 2000 (IWM proxy) / STRICT:**

- 90 official candidates and 90 diagnostic rows;
- exact symbol population match 90/90; duplicates 0;
- official bucket/setup/CQ/EQ/legacy `entry_px` mismatches 0;
- Plan Data Confidence 90/90 HIGH;
- prior-20 structure parity 90/90 PASS;
- states: 42 WAITING, 2 IN ENTRY ZONE, 2 ABOVE ZONE/LATE, 1 MISSED/NO CHASE, 11 BLOCKED, 32 NO STRUCTURED PLAN;
- 90/90 state reconciliation.

One S&P current-price field differed from the diagnostic by $0.005 (PFG), consistent with export/display rounding; all 116 were within $0.01. This is recorded explicitly rather than calling it exact equality.

### Architecture decision

V1.3c successfully separates the **current observed price** from the **planned execution architecture**:

`current price -> structural trigger -> confirmation -> preferred entry zone -> maximum acceptable fill -> frozen NO CHASE ceiling`

The layer remains shadow-only. It must not rewrite official `entry_px`, stop/T1/T2, Entry Quality, Candidate Quality, Composite Quality, ranking, buckets, event gates or trade decisions.

### Parameter boundary

The current reference parameters are:

- preferred zone extension: **0.25 ATR**;
- raw maximum-fill extension: **0.50 ATR**;
- maximum fill capped by the frozen hard anti-chase ceiling.

These are **not frozen as production-optimal values**. Their outcome value must be tested later under historical and prospective data.

### CF Case Study #001 linkage

V1.3c formalizes the execution lesson from CF: identify the structural trigger before the move, define the acceptable execution region, and record a missed opportunity rather than widening the plan after price has escaped. This is an execution-architecture improvement, not a relaxation of entry standards.

### Acceptance boundary

V1.3c is accepted because the architecture is internally consistent, cross-universe, machine-readable and isolated from the official decision layer. **Trading expectancy remains unproven.** V1.3d should therefore address prospective R:R/stop-distance without bypassing the later V1.7 Backtest + Forward-Test + Expectancy validation requirement.

# 11. Planned V1.7 - Expectancy Validation / Backtest / Forward-Test Lab

## 11.1 Governing question

> **Does the system produce positive, repeatable trading expectancy after realistic execution friction and missed opportunities?**

Backtesting remains explicit and mandatory. Forward testing does not replace it.

Basic R-multiple reference:

`Expectancy = Win Rate x Average Win (R) - Loss Rate x Average Loss (R)`

## 11.2 Expectancy hierarchy

| Layer | Purpose |
|---|---|
| Signal Expectancy | Was the scanner signal itself positive-expectancy under the predefined plan? |
| Entry / Trigger Expectancy | Did the entry architecture improve or damage the underlying signal? |
| Captured Expectancy | How much available signal expectancy was captured? |
| Realized Expectancy | What R was realized after actual fills/stops/partials/slippage? |
| Missed Expectancy | How much identified positive opportunity was not captured? |
| Net Expectancy | What remains after realistic costs/friction? |

A high Signal Capture Rate of a negative-expectancy strategy is failure. Positive Signal Expectancy with weak capture points to execution leakage.

## 11.3 Backtest role

Backtesting should provide historical breadth and regime coverage while controlling for look-ahead leakage, timestamp correctness, unrealistic fills, slippage/transaction costs, in-sample overfitting, no-fill/gap-through/invalidation cases and regime/setup/universe concentration.

Use out-of-sample / walk-forward evidence and robustness/sensitivity analysis.

## 11.4 Forward-test role

V1.3f begins prospective logging before V1.7. Preserve at minimum signal timestamp, setup/context, Candidate Quality, relevant Leadership/Fundamental/Composite states, Entry Quality, Contextual Volume state, Entry Location pressure/state/headroom, planned entry/zone/trigger, stop/targets, event/regime state, trigger time, fill/no-fill, slippage, invalidated-before-entry, MAE/MFE, exit path, realized R and Missed Opportunity R.

## 11.5 Acceptance discipline

A positive point estimate alone is insufficient. Evaluate sample size, dispersion, confidence intervals/bootstrap ranges where practical, drawdown, stability across time/universes/regimes/setups and sensitivity to realistic execution assumptions.

Conditional expectancy should be evaluated by relevant system state to discover **where edge actually exists**.

---

# 12. Known Limitations & Open Risks

1. F15 architecture mechanics are accepted, but production ranking authority remains shadow-only pending outcome evidence.
2. V1.3a contextual-volume architecture is accepted, but its thresholds are not proven to improve trading expectancy.
3. V1.3a has no authorized 0-100 score and no production Entry/Candidate weighting.
4. The frozen legacy `vol_ratio` can represent a partial latest daily bar intraday; a future intraday volume-pace metric requires like-for-like time-of-day evidence.
5. V1.3b Entry Location architecture is accepted, but PRIME/ACCEPTABLE/STRETCHED/VERY LATE are shadow reference bands, not proven expectancy-optimal production gates.
6. V1.3b does not alter official Entry Quality or buckets.
7. Official ACTIONABLE/TECH ACTIONABLE names that were already STRETCHED/VERY LATE were **not observed** in the two V1.3b live samples; absence of an example is recorded rather than fabricated.
8. V1.3c trigger/entry-zone architecture is accepted, but its 0.25 ATR / 0.50 ATR parameters remain unproven research references.
9. Fundamental concept coverage can still require sector/domain-specific work.
10. Event-date reliability remains immature and belongs to V1.5.
11. Paper execution and trade journaling are not yet established.
12. Formal Backtest / Forward-Test trading expectancy is not yet proven.
13. Future recalibration of frozen layers requires explicit new evidence/versioning.

---

# 13. Version Ledger

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
| **V1.3a** | **Contextual Volume Quality Diagnostics** | **ACCEPTED / FROZEN (SHADOW)** |
| **V1.3b** | **Entry Location & Anti-Chase Foundation** | **ACCEPTED / FROZEN (SHADOW)** |
| **V1.3c** | **Trigger & Entry-Zone Architecture** | **ACCEPTED / FROZEN (SHADOW)** |

---

# 14. Documentation Standard for Future Phases

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
13. machine-readable evidence/reconciliation where quantitative claims are made;
14. acceptance criteria;
15. acceptance result;
16. known limitations;
17. decision confidence;
18. frozen-principle impact;
19. future dependency;
20. Roadmap Reconciliation disposition for outstanding research/case-study items.

For defects/process gaps, use:

**symptom -> root cause -> corrective action -> prevention rule**.


## V1.3d Opening Record - Risk/Reward & Stop-Distance Shadow Diagnostics

**Date:** 13 September 2026
**Status:** IN DEVELOPMENT / SHADOW
**Dependency:** V1.3c Trigger & Entry-Zone Architecture accepted/frozen shadow

### Problem / trigger
V1.3c can define a structural trigger, preferred entry zone and maximum acceptable fill, but it does not yet show how the downside risk and available R change across those entry references. A single current-price R:R can therefore hide execution deterioration.

### Architecture
V1.3d adds a separate risk-geometry table. It consumes V1.3c planning fields and derives a transparent structural support reference from EMA20 and prior daily lows. A provisional 0.25 ATR stop buffer is applied below support. T1/T2 use 1.5R/2.5R shadow references. R:R is evaluated independently at trigger, zone high and max fill.

### What does not change
Official Candidate Quality, F15 Composite, Entry Quality, ranking, buckets, event gates, legacy `entry_px`, legacy `stop`, legacy `t1`, legacy `t2` and trade decisions remain untouched. The app checks `scored.equals(copy_before_shadow)` after the shadow build.

### Acceptance philosophy
The layer is diagnostic, not a new production gate. R:R bands are descriptive research labels. No missing risk input is imputed. Good R:R cannot rescue poor price structure, blocked/no-chase plans, or weak data.

### Test evidence
The focused V1.3b/V1.3c/V1.3d suites completed with **80/80 PASS** locally. The complete historical repository regression suite was not run in the isolated build workspace and is therefore not claimed.

### Research dependency
The 0.25 ATR stop buffer, 1.5R/2.5R target references and 2.0R STRONG band remain provisional. Their production authority requires Backtest + Forward Test + Expectancy evidence. Expectancy remains the central KPI; Signal Capture Rate and Missed Opportunity R are subordinate diagnostics.

### Prevention rule
**Never manufacture a trade by tightening the stop or moving the target until a desired R:R appears.** Risk geometry must describe the trade that structure actually permits.
