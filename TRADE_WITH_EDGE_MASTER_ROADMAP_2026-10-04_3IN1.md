# Trade With Edge — MASTER ROADMAP
## 3-in-1 System Master Control Board
**Revision:** 2026-10-04 — Current-State Reconciliation  
**Core principle:** Find Edge → Execute Edge → Prove Edge → Improve Edge

---

# 0. MASTER ARCHITECTURE — SOURCE OF TRUTH

Trade With Edge is a **3-in-1 operational system** consisting of two coordinated development workstreams plus a standalone execution-review layer.

```text
                         TRADE WITH EDGE
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
     ① CORE SCANNER       ② SYSTEM #2       ③ IBKR JOURNAL
     Trading-System       Authority /        Execution Review
     & Research Lab      Monitoring          / Proof Layer
              │                 │                 │
       FIND EDGE          AUTHORITATIVE       PROVE EDGE
       SCREEN             EVALUATION          ACTUAL TRADES
       RANK               MONITORING          P&L / R
       FORWARD TEST       STATE               RISK
       BACKTEST           TRANSITIONS         EXECUTION
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                         IMPROVE EDGE
```

## System ownership

### ① Core Scanner / Trading-System
**Repository:** `tradewithedge/alpaca-scanner`

Primary responsibilities:

- market-data acquisition / validation;
- universe scanning;
- Candidate Quality;
- Leadership / Relative Strength;
- Fundamental Quality;
- F15 Composite architecture;
- Entry Quality;
- anti-chase / entry-location diagnostics;
- trigger / entry-zone planning;
- R:R / stop diagnostics;
- EXECUTION READY / WATCH / WAIT / NO CHASE shadow state;
- prospective forward-test capture;
- historical backtest / replay;
- expectancy research;
- calibration only after evidence.

**Current identity:** V1.3f frozen scanner architecture + V1.7 validation lab.

### ② System #2 — Authority / Monitoring
**System:** `trade-with-edge-monitor`

Primary responsibilities:

- canonical evaluator;
- authoritative state;
- scheduled shadow evaluation;
- semantic state comparison;
- transition proposal infrastructure;
- owner-only monitoring / alert transport;
- future transition/action architecture only after explicit validation gates.

**Current identity:** Phase 3B.5F2 — Semantic Transition Proposal Engine.

### ③ Standalone IBKR Journal
**Artifact:** `edge_trader_ibkr_dashboard_v10.html`

Primary responsibilities:

- actual IBKR transaction history;
- realized P&L;
- realized R;
- execution review;
- risk review;
- trade autopsy;
- process lessons;
- comparison of scanner plan versus actual execution.

**Current identity:** Journal v10 recovered and live; treated as a separate execution-review system, not merged into either scanner or System #2.

Live page:

`https://tradewithedge.github.io/alpaca-scanner/`

---

# 1. MASTER DEVELOPMENT WORKSTREAMS

The operational system is 3-in-1, but development is controlled through two coordinated workstreams:

## Workstream A — Core Scanner / Trading-System
`tradewithedge/alpaca-scanner`

Lifecycle:

**FIND EDGE → VALIDATE EDGE → FORWARD TEST → BACKTEST → EXPECTANCY → CALIBRATE**

## Workstream B — System #2 Authority
`trade-with-edge-monitor`

Lifecycle:

**CANONICAL EVALUATION → AUTHORITATIVE STATE → SEMANTIC TRANSITION PROPOSAL → VALIDATED ACTION PATH**

## Standalone evidence layer
IBKR Journal v10

Lifecycle:

**EXECUTE → RECORD → REVIEW → PROVE → FEED EVIDENCE BACK**

These are coordinated but must not be merged into one codebase or one authority layer.

---

# 2. CURRENT MASTER STATUS — 2026-10-04

| Component | Current status | Control |
|---|---|---|
| Core Scanner V1.3f | ACCEPTED / FROZEN | Do not modify frozen decision logic casually |
| V1.7 Stage 0 | RESOLVED | Complete |
| V1.7 Stage 1 deterministic evaluator | ACCEPTED / FROZEN | Validation dependency |
| V1.7 Stage 2 historical replay | PREPARED | **Next formal gate** |
| Forward Test | ACTIVE | Continue evidence collection |
| 27-Sep / 28-Sep forward captures | QUARANTINED | Retain audit evidence, exclude from clean performance series |
| Clean Forward Test | Starts 29-Sep-2026 | Continue prospectively |
| System #2 3B.5D | PASS | Frozen |
| System #2 3B.5E | PASS | Real Cron shadow |
| System #2 3B.5F1 | COMPLETE / FROZEN | Authoritative state |
| System #2 3B.5F2 | CODE VERIFIED / DEPLOYMENT GATE | Do not promote implicitly |
| IBKR Journal v10 | RECOVERED / LIVE / SEPARATE | Freeze until evidence justifies v11 |
| Production expectancy | NOT PROVEN | No production claim |
| Production trading | NOT AUTHORIZED | No implicit broker action |
| Overall project | PRE-PRODUCTION / VALIDATION | Evidence before calibration |

---

# 3. CORE SCANNER — FROZEN ARCHITECTURE

The following layers remain frozen unless a separately accepted phase explicitly changes them:

- Candidate Quality;
- Leadership / Relative Strength architecture;
- Fundamental Quality;
- F15 Composite architecture;
- V1.3a Contextual Volume diagnostics;
- V1.3b Entry Location / Anti-Chase diagnostics;
- V1.3c Trigger / Entry-Zone architecture;
- V1.3d R:R / Stop diagnostics;
- V1.3e EXECUTION READY / WATCH / WAIT / NO CHASE;
- V1.3f Shadow Execution Capture;
- existing event gates;
- existing official ranking / bucket semantics;
- existing hard anti-chase ceilings.

**Important:** Shadow diagnostics do not automatically become production scoring or trade gates.

---

# 4. V1.7 EXPECTANCY VALIDATION LAB

## Governing question

> Does the system produce positive, repeatable trading expectancy after realistic execution friction and missed opportunities?

Backtesting and forward testing are both mandatory.

## Expectancy hierarchy

1. Signal Expectancy
2. Entry / Trigger Expectancy
3. Captured Expectancy
4. Realized Expectancy
5. Missed Opportunity Expectancy
6. Net Expectancy after friction

## Stage 0 — Expectancy Preflight
**Status: RESOLVED**

Rules:

- do not change scanner logic merely to improve observed results;
- define outcome semantics before measuring;
- preserve frozen architecture;
- distinguish signal quality from execution capture.

## Stage 1 — Deterministic Backtest Engine
**Status: ACCEPTED / FROZEN**

Required semantics include:

- signal bar excluded from future evaluation;
- no look-ahead;
- pre-trigger invalidation;
- gap-through-trigger handling;
- maximum acceptable fill;
- same-bar STOP priority where defined;
- timeout;
- commission / friction handling;
- MAE / MFE;
- missed opportunity R;
- deterministic duplicate/timestamp handling.

## Stage 2 — Historical Replay
**Status: PREPARED / NEXT FORMAL GATE**

Objective:

> Reconstruct historical signal state using only information available at the decision timestamp, then pass the reconstructed signal into the frozen Stage 1 evaluator.

Acceptance must verify:

- as-of correctness;
- no look-ahead;
- deterministic reconstruction;
- frozen scanner-field integrity;
- complete signal population;
- duplicate handling;
- outcome reproducibility;
- cross-universe coverage;
- audit trail.

**No Stage 2 acceptance/freeze is claimed until machine-readable evidence passes the defined gate.**

---

# 5. FORWARD-TEST CONTROL

## Canonical clean-series rule

The 27-Sep and 28-Sep captures are retained as historical audit evidence but are **QUARANTINED / NON-CANONICAL** for clean performance measurement because capture date and represented completed U.S. session were not sufficiently separated.

The clean forward-test series starts:

**29-Sep-2026**

## Required date fields

Every future capture must distinguish:

1. capture timestamp/date;
2. latest completed U.S. market session date;
3. signal timestamp;
4. dataset role.

A later capture date does not automatically represent a new independent market session.

## Outcome rules

- `UNRECORDED` remains `UNRECORDED`;
- never infer fills from later price movement;
- never infer exits;
- never infer realized R;
- preserve explicit `NO_FILL`;
- incomplete fills are not completed outcomes;
- duplicate capture/signal keys must be rejected.

---

# 6. FORWARD-TEST → EXPECTANCY PIPELINE

```text
Scanner Signal
      ↓
Prospective Capture
      ↓
Open Execution-Ready Cohort
      ↓
Actual Outcome Evidence
      ↓
Fill / No-Fill / Invalidation
      ↓
MAE / MFE / Exit Path
      ↓
Realized R
      ↓
Missed Opportunity R
      ↓
Net Expectancy
      ↓
Statistical Audit
      ↓
Calibration
```

The ledger is evidence infrastructure. It does not itself change scanner thresholds.

---

# 7. SYSTEM #2 — AUTHORITY TRACK

## 3B.5D — Canonical Parity
**Status: PASS**

Canonical evaluator parity established.

## 3B.5E — Real Cron Shadow Evaluation
**Status: PASS**

Real scheduled canonical evaluations persist shadow results without transition side effects.

## 3B.5F1 — Authoritative State
**Status: COMPLETE / FROZEN**

Dedicated authoritative state persists across Cron cycles.

Rules:

- stable semantic state;
- no `monitor_transition` writes;
- no new alert publication;
- no account/order calls.

## 3B.5F2 — Semantic Transition Proposal Engine
**Status: CODE VERIFIED / PRODUCTION DEPLOYMENT GATE**

Purpose:

Compare authoritative evaluations using semantic decision content rather than volatile provenance.

Current architecture includes:

- authoritative history;
- semantic fingerprinting;
- transition proposals;
- idempotent proposal tracking;
- BASELINE / STABLE / PROPOSED / BLOCKED semantics.

Hard boundary:

- does not write production `monitor_transition`;
- does not publish new alerts from proposal logic;
- does not introduce trading endpoints;
- does not create broker execution authority.

### Next System #2 gate

Production deployment must be explicitly validated before any promotion from proposal to transition/action.

No implicit transition publication is permitted.

---

# 8. IBKR JOURNAL — STANDALONE EXECUTION REVIEW

## Journal v10

Status:

**RECOVERED / LIVE / SEPARATE**

Purpose:

- actual transaction evidence;
- P&L;
- realized R;
- execution quality;
- position sizing;
- stop discipline;
- entry quality;
- management;
- trade autopsy;
- process lessons.

Journal v10 is not a scanner authority and does not automatically modify scanner parameters.

## Feedback loop

```text
Scanner Plan
    ↓
Actual Execution
    ↓
IBKR Journal
    ↓
Autopsy / Evidence
    ↓
Hypothesis
    ↓
Historical Test
    ↓
Forward Test
    ↓
Calibration
```

### Journal v11

**DEFERRED**

Only open when enough new real trades/evidence justify a new version.

---

# 9. DATA PROVIDER / BENCHMARK TRACK

## Yahoo ↔ Alpaca SIP benchmark

Purpose:

Evaluate:

- OHLCV consistency;
- volume differences;
- missing/stale data;
- session completeness;
- source confidence;
- universe coverage.

Initial benchmark work found price-integrity concerns were not established merely from observed volume differences.

Provider-role changes must be evidence-driven and separately accepted.

**No provider-role change is authorized by this roadmap reconciliation alone.**

---

# 10. FULL UNIVERSE COVERAGE

Future coverage work remains a validation priority.

Target:

> **Full Universe Coverage Integrity**

Must prove:

- complete universe retrieval;
- no silent pagination loss;
- symbol reconciliation;
- duplicate handling;
- completed-session integrity;
- deterministic population counts;
- full export/audit evidence.

This is validation work, not permission to loosen scanner standards.

---

# 11. MARKET REGIME CONTROL

Market Regime remains upstream of swing screening.

Operational sequence:

**REGIME FIRST → CASH-MARKET CONFIRMATION → SCAN → RANK → LIFECYCLE → ENTRY VALIDATION → EXECUTION → REVIEW**

The Regime Master Template remains a separate frozen control document and should not be merged into scanner scoring.

---

# 12. PRODUCTION FREEZE REQUIREMENTS

Trade With Edge does not enter full production merely because the scanner is technically functional.

Required evidence includes:

- validated market-data integrity;
- validated scanner decision semantics;
- Stage 2 historical replay acceptance;
- sufficient forward-test evidence;
- expectancy analysis;
- realistic friction;
- MAE/MFE;
- missed-opportunity analysis;
- regime segmentation;
- setup segmentation;
- robustness / sensitivity testing;
- portfolio-risk integration;
- stable System #2 authority;
- stable deployment;
- reproducible audit trail.

Only after these gates should production calibration/freeze be considered.

---

# 13. CHANGE-CONTROL RULE

No one observation, ticker, screenshot, or short forward-test run may justify changing:

- Candidate Quality weights;
- F15 weights;
- Entry Quality thresholds;
- anti-chase ceilings;
- R:R thresholds;
- event gates;
- provider roles;
- System #2 authority semantics;
- production alert behavior;
- broker execution behavior.

Required development sequence:

> **Observation → Hypothesis → Historical Test → Forward Test → Evidence → Calibration**

---

# 14. MASTER ROADMAP — NEXT ACTIONS

## P0 — Protect the baselines
- Core Scanner → FROZEN
- System #2 Authority semantics → FROZEN
- IBKR Journal v10 → FROZEN
- Market Regime Master Template → FROZEN

## P1 — Core Scanner / V1.7
### NEXT:
**V1.7 Stage 2 — Historical Replay**

At the same time:

- continue clean forward-test capture;
- maintain open Execution-Ready cohort;
- collect real outcome evidence;
- maintain dataset audit.

## P1 — System #2
### NEXT:
**3B.5F2 Production Deployment Gate**

Deploy only after the defined validation checks pass.

## P1 — Data
Continue Yahoo ↔ Alpaca SIP benchmark and coverage validation.

## P2 — Full Universe
Proceed to Full Universe Coverage Integrity after the current validation gates are stable.

## P2 — Journal
Do not create Journal v11 yet unless new execution evidence warrants it.

---

# 15. MASTER STATUS STATEMENT

As of **2026-10-04**:

> **Trade With Edge is on the correct technical path, but remains in validation / pre-production.**

The principal correction required is:

> **DOCUMENTATION + EVIDENCE SYNCHRONIZATION**

—not scanner redesign.

The three operational pillars are explicitly preserved:

1. **Core Scanner** — `tradewithedge/alpaca-scanner`
2. **System #2 Authority** — `trade-with-edge-monitor`
3. **Standalone IBKR Journal v10**

The next technical gate is:

> **V1.7 Stage 2 Historical Replay → Deterministic Acceptance**

while forward-test evidence continues in parallel.

---

# 16. NON-NEGOTIABLE MASTER PRINCIPLE

## BUILD LESS → MEASURE MORE → AUDIT HARDER

```text
FIND EDGE
    ↓
VALIDATE EDGE
    ↓
EXECUTE EDGE
    ↓
PROVE EDGE
    ↓
REVIEW EDGE
    ↓
IMPROVE EDGE
```

**No production authority is granted by this reconciliation alone.**

