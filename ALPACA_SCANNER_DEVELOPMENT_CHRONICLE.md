# ALPACA Scanner - Development Chronicle & Architecture Record

**Revision:** Rev.3  
**Prepared:** 11 September 2026  
**Current accepted implementation checkpoint:** V1.3a - Contextual Volume Quality Diagnostics  
**V1.3a status:** **ACCEPTED / FROZEN (SHADOW)**  
**Official decision-layer authority:** unchanged by V1.3a  
**Next development checkpoint:** V1.3b - Entry Location & Anti-Chase Foundation

> This is the authoritative living engineering-history record for the ALPACA Scanner. It preserves problems encountered, evidence observed, architecture selected, alternatives rejected, validation performed, frozen principles, open risks and the next permitted development move.

> **Rev.3 note:** this revision freezes V1.3a after machine-readable cross-universe validation, records the completed-session/partial-session volume finding, adopts a machine-readable Validation Evidence Standard, reconciles the research-register IDs, and clarifies V1.7 as **Expectancy Validation / Backtest / Forward-Test Lab**. Earlier frozen decisions remain preserved in Git history and are not silently rewritten.

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
- **Contextual Volume Quality:** setup-dependent participation evidence near Setup/Entry, not a replacement for the layers above.

The V1.2 Candidate Quality program is architecture-complete through **V1.2.3c**. V1.3a is now accepted/frozen as a **SHADOW contextual-volume diagnostic architecture**. The next permitted development move is **V1.3b - Entry Location & Anti-Chase Foundation**.

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

## 4.1 Symptom

Contextual Volume Quality had been retained as an outstanding research item, but it was not promoted into the formal GitHub roadmap as a named stage. After V1.2.3c acceptance, development followed the formal roadmap mechanically and decomposed V1.3 around entry location/trigger/R:R without first reconciling unresolved research items.

The existing code already contained rudimentary volume logic, which made the omission easier to miss: breakout confirmation used relative-volume expansion and pullback/VCP logic gave a small benefit for contraction. That was not equivalent to a complete Contextual Volume Quality engine.

## 4.2 Root cause

Two planning layers were not formally reconciled:

1. research/backlog decisions retained from development discussions;
2. the formal GitHub roadmap.

An item could therefore remain known but unmapped.

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

Create a setup-aware volume evidence layer that distinguishes:

- breakout participation/expansion;
- pullback/VCP/tight-base contraction;
- accumulation versus distribution;
- constructive versus conflicting price-volume behavior;
- trustworthy versus insufficient volume data.

The first accepted architecture remains **SHADOW ONLY**.

## 5.2 Architectural boundary

> **Liquidity Quality != Contextual Volume Quality.**

Liquidity answers whether a security is tradeable efficiently. Contextual Volume Quality asks whether participation confirms or contradicts the current setup/entry.

Volume Quality belongs downstream near Setup/Entry, not inside F15 Composite.

## 5.3 Implemented architecture

The accepted V1.3a layer:

- classifies price context before interpreting new volume diagnostics;
- uses completed consolidated SIP daily sessions;
- excludes the same-day daily bar before **16:30 ET**;
- uses explicit HIGH / MEDIUM / LOW Volume Data Confidence;
- makes LOW confidence **NOT RANKED**, not neutral;
- calculates completed-session RVOL versus the prior 20 sessions;
- calculates non-overlapping 5D and 10D volume trends;
- calculates 10D up/down-volume ratio and up-volume share;
- counts accumulation and distribution sessions;
- interprets breakout expansion differently from pullback/VCP contraction;
- prevents favorable volume from rescuing broken price structure;
- returns a separate shadow table;
- does not write new volume features back into the official scored frame;
- does not create a 0-100 Volume Quality score.

## 5.4 Offline implementation validation

- `py_compile`: PASS.
- Dedicated V1.3a unit/integration suite: **22/22 PASS**.
- Tests covered completed-session handling, immutability, prior-20 RVOL baseline, setup-specific interpretation, LOW-confidence behavior, distribution accounting, app integration and no-merge/official-layer isolation.
- The isolated packaging environment did **not** run the entire pre-existing repository regression suite; this is stated explicitly rather than implied.

## 5.5 S&P 500 live validation

**Controls:** S&P 500 / STRICT / min $5 / prev-day $vol $20M / max deep scan 2000 / strict event gate ON.

Full Swing Candidates and full Contextual Volume Diagnostic CSVs were reconciled programmatically:

- **127 official candidates / 127 contextual rows**;
- **127 unique symbols**, duplicates **0**;
- population match **127/127**;
- official bucket mismatches **0**;
- official setup mismatches **0**;
- Candidate Quality mismatches **0**;
- Entry Quality mismatches **0**;
- Volume Data Confidence **127/127 HIGH**;
- evaluation session **2026-09-04** for all rows;
- state reconciliation: **41 CONFIRMING + 38 MIXED + 34 DIAGNOSTIC ONLY + 14 CONFLICT/WATCH = 127**;
- context reconciliation: **83 EMA20 PULLBACK + 35 NO CLEAN SETUP + 4 BREAKOUT + 4 MA20 REPAIR + 1 TIGHT BASE = 127**.

The sample demonstrated that the new layer is contextual rather than a simple high-volume reward. Pullback names could confirm through contraction, while breakouts demanded participation. Borderline cases were retained for later outcome calibration rather than used to loosen rules.

## 5.6 Russell 2000 live validation

The final controlled Russell run was taken before U.S. pre-market so both legacy and V1.3a volume metrics referenced the same completed session.

Full machine-readable reconciliation:

- **85 official candidates / 85 contextual rows**;
- **85 unique symbols**, duplicates **0**;
- population match **85/85**;
- official bucket mismatches **0**;
- official setup mismatches **0**;
- Candidate Quality mismatches **0**;
- Entry Quality mismatches **0**;
- Volume Data Confidence **85/85 HIGH**;
- evaluation session **2026-09-10** for all rows;
- state reconciliation: **24 CONFIRMING + 11 MIXED + 13 CONFLICT/WATCH + 37 DIAGNOSTIC ONLY = 85**;
- context reconciliation: **39 EMA20 PULLBACK + 24 NO CLEAN SETUP + 12 MA20 REPAIR + 5 BREAKOUT + 3 BROKEN/BELOW MA50 + 2 VCP/TIGHTENING = 85**.

## 5.7 Session-comparability finding

### Symptom

During an intraday Russell run, frozen official `vol_ratio` and V1.3a `rvol_20` differed dramatically for some stocks. The discrepancy could have been misread as a formula defect.

### Root cause

The two metrics were sometimes observing different session completeness:

- frozen `vol_ratio` uses the latest available daily-bar volume divided by the prior-20-session average;
- V1.3a deliberately excludes the same-day daily bar before 16:30 ET and evaluates the latest completed session.

Comparing partial-day volume with a completed-session baseline is not like-for-like.

### Corrective action / evidence

Three live timing samples were compared:

| Timing condition | Pearson correlation | Evidence |
|---|---:|---|
| Regular session / partial bar present | ~0.043 | severe session mismatch |
| Pre-market/session-mismatch sample | ~0.580 | partial alignment |
| **Controlled same-completed-session sample** | **0.999966** | metrics effectively reconcile |

For the controlled 85-stock run:

- Spearman: **0.999790**;
- mean official `vol_ratio`: **0.98847x**;
- mean V1.3a `rvol_20`: **0.98859x**;
- **85/85 matched at two-decimal precision**.

### Prevention rule

Session completeness must be explicit in all future volume validation. A future intraday participation metric must compare current time-of-day volume against historical time-of-day volume or another like-for-like pace baseline. V1.3a does **not** silently rewrite the frozen legacy metric.

## 5.8 Acceptance decision

V1.3a is **ACCEPTED / FROZEN as a SHADOW diagnostic architecture**.

Accepted:

- completed-session discipline;
- Volume Data Confidence;
- price-context-first design;
- contextual expansion versus contraction;
- accumulation/distribution diagnostics;
- separate shadow-table architecture;
- cross-universe official-layer isolation;
- fail-visible behavior.

Not authorized:

- 0-100 Volume Quality score;
- Candidate Quality/F15 weighting;
- official Entry Quality modification;
- production trade gate;
- threshold optimization based on limited live samples.

Trading expectancy remains unproven and belongs to V1.7.

---

# 6. Process Gap Review - Quantitative Validation Evidence

## 6.1 Symptom

Earlier live validation relied too heavily on screenshots, including wide diagnostic tables. Screenshots were useful for deployment proof but inefficient and insufficient for full row-level reconciliation.

A concrete example occurred when the dashboard headline showed **41 CONFIRMING** while the displayed/exported confirming table contained **40 rows** because the UI intentionally used a display cap. The full diagnostic audit correctly contained all 41.

## 6.2 Root cause

Two evidence purposes were conflated:

1. **UI/deployment acceptance**;
2. **quantitative engine acceptance**.

A screenshot can prove that a section rendered and a headline count appeared, but it cannot efficiently prove full-population equality, hidden columns, duplicates, nulls, threshold behavior or exact numeric reconciliation.

## 6.3 Corrective action

The project adopts the **Validation Evidence Standard**:

- screenshots: version/settings/banner/headline/UI proof;
- full CSV/machine-readable data: quantitative analysis and freeze evidence;
- programmatic reconciliation: row counts, population identity, frozen-layer equality, duplicates, nulls, states, confidence and session alignment.

## 6.4 Prevention rule

A quantitative engine cannot be frozen from screenshots alone when complete machine-readable evidence is available. Display caps must never be mistaken for population caps.

---

# 7. Outstanding Research / Dependency Register

The register is now reconciled to one canonical ID set shared with `ROADMAP.md`.

| ID | Item | Disposition | Destination | Rule |
|---|---|---|---|---|
| R-001 | Contextual Volume Quality diagnostics architecture | **RESOLVED / FROZEN SHADOW** | **V1.3a** | Architecture accepted; outcome calibration remains V1.7 work |
| R-002 | Candidate-vs-Entry feature separation | ASSIGNED | V1.3b-V1.3e | Preserve separate truth layers |
| R-003 | Continuous EMA8/EMA20 extension/location quality | ASSIGNED | V1.3b | Hard NO CHASE remains a ceiling |
| R-004 | Trigger and entry-zone architecture | ASSIGNED | V1.3c | Do not assume current close is the planned entry |
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

---

# 8. CF Case Study #001 - Execution Architecture Lesson

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

**Prove Edge** is now explicitly defined as outcome validation using **Backtest + Forward-Test expectancy evidence**. Signal Capture Rate and Missed Opportunity R explain execution capture; they do not replace expectancy.

These dependencies remain staged into V1.3f/V1.6/V1.7/V1.8 rather than being forced into V1.3b.

---

# 9. Planned V1.7 - Expectancy Validation / Backtest / Forward-Test Lab

## 9.1 Governing question

> **Does the system produce positive, repeatable trading expectancy after realistic execution friction and missed opportunities?**

Backtesting remains explicit and mandatory. Forward testing does not replace it.

Basic R-multiple reference:

`Expectancy = Win Rate x Average Win (R) - Loss Rate x Average Loss (R)`

## 9.2 Expectancy hierarchy

| Layer | Purpose |
|---|---|
| Signal Expectancy | Was the scanner signal itself positive-expectancy under the predefined plan? |
| Entry / Trigger Expectancy | Did the entry architecture improve or damage the underlying signal? |
| Captured Expectancy | How much available signal expectancy was captured? |
| Realized Expectancy | What R was realized after actual fills/stops/partials/slippage? |
| Missed Expectancy | How much identified positive opportunity was not captured? |
| Net Expectancy | What remains after realistic costs/friction? |

A high Signal Capture Rate of a negative-expectancy strategy is failure. Positive Signal Expectancy with weak capture points to execution leakage.

## 9.3 Backtest role

Backtesting should provide historical breadth and regime coverage while controlling for:

- look-ahead leakage;
- timestamp-correct feature availability;
- unrealistic fill assumptions;
- slippage/transaction costs;
- in-sample overfitting;
- no-fill/gap-through/invalidation cases;
- regime/setup/universe concentration.

Use out-of-sample / walk-forward evidence and robustness/sensitivity analysis.

## 9.4 Forward-test role

V1.3f begins prospective logging before V1.7. Preserve at minimum:

- signal timestamp;
- setup/context;
- Candidate Quality;
- relevant Leadership/Fundamental/Composite states;
- Entry Quality;
- Contextual Volume state;
- planned entry/zone/trigger;
- stop and targets;
- event/regime state;
- trigger time;
- fill/no-fill;
- slippage;
- invalidated-before-entry;
- MAE/MFE;
- exit path;
- realized R;
- Missed Opportunity R.

## 9.5 Acceptance discipline

A positive point estimate alone is insufficient. Evaluate sample size, dispersion, confidence intervals/bootstrap ranges where practical, drawdown, stability across time/universes/regimes/setups and sensitivity to realistic execution assumptions.

Conditional expectancy should be evaluated by relevant system state to discover **where edge actually exists**.

---

# 10. Known Limitations & Open Risks

1. F15 architecture mechanics are accepted, but production ranking authority remains shadow-only pending outcome evidence.
2. V1.3a contextual-volume architecture is accepted, but its thresholds are not proven to improve trading expectancy.
3. V1.3a has no authorized 0-100 score and no production Entry/Candidate weighting.
4. The frozen legacy `vol_ratio` can represent a partial latest daily bar intraday; V1.3a deliberately avoids that comparison. A future intraday volume-pace metric requires like-for-like time-of-day evidence.
5. Fundamental concept coverage can still require sector/domain-specific work.
6. Event-date reliability remains immature and belongs to V1.5.
7. Entry Quality remains coarse relative to the planned V1.3b-V1.3e architecture.
8. Paper execution and trade journaling are not yet established.
9. Formal Backtest / Forward-Test trading expectancy is not yet proven.
10. Future recalibration of frozen layers requires explicit new evidence/versioning.

---

# 11. Version Ledger

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
| **V1.3b** | **Entry Location & Anti-Chase Foundation** | **NEXT / DESIGN** |

---

# 12. Documentation Standard for Future Phases

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
