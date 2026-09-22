# Trade With Edge — Master Roadmap

**Status date:** 2026-09-21  
**Formal repository baseline:** `v7.8.1-RETRIEVAL-RECOVERY-HOTFIX`  
**Scoring/data compatibility key:** `v7.4.5-P2C-FREEZE`

## Roadmap principle

> **Find Edge → Execute Edge → Prove Edge → Improve Edge**

## 1. Master roadmap structure

Trade With Edge uses **one Master Roadmap** with two coordinated workstreams:

- **Workstream A — Core Scanner / Trading-System Track**: the original scanner, validation, calibration, risk and production roadmap.
- **Workstream B — System #2 Authority Track**: the authoritative evaluation, monitoring, semantic state and transition infrastructure required to make the decision engine continuously auditable and reliable.

These are **not two competing roadmaps**. Workstream B supports the lifecycle and automation capabilities in Workstream A and ultimately converges into the same v3.0 production objective.

---

# Workstream A — Core Scanner / Trading-System Track

## Phase 2E.3 — Final Market Scanner Decision UX

**Repository-documented status:** NEXT at the last formal documentation checkpoint.

Objective:

Turn the large-universe scanner into a decision-first surface.

Required hierarchy:

> **Ticker → Candidate Quality → Entry Status → Action → Main Reason**

Scanner-level entry readiness must remain distinct from fully verified ticker actionability.

> **VERIFY EVENT + STOP = price-ready candidate, not yet fully ACTIONABLE**

Freeze condition:

> **Freeze UX except defects.**

No scoring weights, thresholds, provider roles or frozen gates change during UX work.

## Phase 2F — Candidate Lifecycle / State Tracking

Before lifecycle logic reuses ticker diagnostics, centralize the Price Data Confidence hard block so actionability cannot depend on UI-only enforcement.

Proposed state machine:

> `DISCOVERED → WATCH → DEVELOPING → READY → TRIGGER → ACTIVE / INVALIDATED`

## P1 — Alpaca Data Reliability Benchmark

Current roles remain frozen during benchmark:

- Yahoo/yfinance = PRIMARY
- Stooq = RECOVERY
- GitHub = LAST-GOOD SCANNER SNAPSHOT RECOVERY
- Alpaca = SHADOW / VALIDATION

If the benchmark is accepted, the provider architecture can be revisited through evidence rather than assumption.

## Phase 2G — Historical Validation / Backtesting

Validate Candidate grade, Entry grade, regime, RS, stress resilience, contextual volume, extension, ATR, setup type, stop geometry, event proximity and data-confidence states.

Add repeatable repository-contained regression tests for frozen gates and reliability behavior.

## Forward Test Lab

> **Signal Quality ≠ Execution Capture**

Track signal capture rate, missed-opportunity R, slippage and trigger latency.

## Phase 2H — Calibration

Only after historical and forward evidence.

## Phase 2I — Portfolio / Risk Integration

Preferred broker layer:

> **IBKR**

## Phase 2J — Workflow Automation

Target:

> Market Regime → Scan → Rank → Lifecycle → READY/TRIGGER → Event Verification → Position Sizing → Portfolio Risk → Execution Plan

## v3.0 — Production Freeze

Requires validated data/scoring, calibrated thresholds, lifecycle, forward-test evidence, regression-test coverage, portfolio-risk integration, stable UX and reproducible deployment.

---

# Workstream B — System #2 Authority Track

This workstream is the controlled implementation path for the authoritative evaluator and its monitoring/state infrastructure. It does not replace the Core Scanner roadmap.

## Phase 3B.4 — Monitoring / Alerts foundation

Monitoring and owner-only alert infrastructure established without introducing trading-order execution.

## Phase 3B.5D — Canonical parity validation

Foreground and canonical authoritative evaluator parity established against the controlled shadow-test path.

## Phase 3B.5E — Real Cron shadow evaluation

Real scheduled canonical evaluations persisted to `monitor_shadow_run` / `monitor_shadow_evaluation` with repeated successful cycles and no transition side effects.

## Phase 3B.5F1 — Authoritative State

**Status: COMPLETE / FROZEN ✅**

The canonical evaluator now maintains a dedicated `monitor_authoritative_state` for the scoped target. Transition generation remains suppressed.

Validated properties:

- repeated successful Cron cycles
- stable decision semantics
- authoritative state persisted
- no new `monitor_transition` rows
- no new alert publication
- no account/order calls

## Phase 3B.5F2 — Semantic Transition Proposal Engine

**Status: CODE VERIFIED / PRODUCTION DEPLOYMENT GATE ⏸**

Purpose:

Compare authoritative evaluations by **semantic decision content**, not volatile provenance such as `input_sha256`.

F2 adds:

- `monitor_authoritative_history`
- `monitor_transition_proposal`
- semantic fingerprinting
- idempotent proposal tracking
- BASELINE / STABLE / PROPOSED / BLOCKED semantics

Hard boundary:

> F2 proposals do **not** write to `monitor_transition`, do **not** publish new alerts, and do **not** introduce trading endpoints.

## Future System #2 phases

Future promotion beyond F2 requires explicit validation gates. Transition publication, execution-capture architecture and any production action path must not be introduced implicitly by F2.

---

# 2. Overall project status

> **Pre-validation / Pre-production**

Trade With Edge is **not yet a statistically validated trading system**.

Current controlled position:

| Area | Status |
|---|---|
| Core scanner | Mature baseline |
| C3.0 / E2.0 decision architecture | Established / frozen rules preserved |
| System #2 parity | PASS |
| System #2 real Cron shadow | PASS |
| 3B.5F1 authoritative state | COMPLETE / FROZEN |
| 3B.5F2 D1 schema | PASS |
| 3B.5F2 code-level verification | PASS |
| 3B.5F2 production deployment | NOT YET |
| Historical statistical validation | Remaining major work |
| Forward validation | Remaining |
| Calibration | Remaining |
| Portfolio / risk integration | Remaining |
| Production freeze | Future |

## 3. How the two workstreams relate

Workstream A asks:

> **Does the trading system produce a validated and ultimately production-ready edge?**

Workstream B asks:

> **Can the system reliably evaluate, persist, compare and identify changes in its authoritative trading state?**

A robust production system requires both answers.

## 4. Documentation rule

There is one Master Roadmap and one Overall Status.

Whenever project status is reported, identify:

1. Core Scanner Track position
2. System #2 Authority Track position
3. Overall production / validation status

Do not describe the project as being simultaneously at two unrelated phases without identifying the workstream.

## 5. Freeze / change-control rule

Roadmap reconciliation does not authorize changes to:

- Candidate scoring
- Entry scoring
- frozen thresholds
- risk rules
- provider roles
- monitor transition behavior
- alert publication behavior
- production Worker behavior

Any runtime change requires its own phase-specific validation and acceptance.

## 6. Development principle

> **Observation → Hypothesis → Historical Test → Forward Test → Evidence → Calibration**

Do not change weights, thresholds or gates because of one ticker.
