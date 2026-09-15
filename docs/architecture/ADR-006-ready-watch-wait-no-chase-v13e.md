# ADR-006 — V1.3e EXECUTION READY / WATCH / WAIT / NO CHASE Decision Architecture

**Status:** IN DEVELOPMENT / SHADOW  
**Date:** 13 September 2026  
**Depends on:** V1.3c Trigger & Entry-Zone Architecture; V1.3d Risk/Reward & Stop-Distance Diagnostics

## Context
V1.3a–V1.3d established independent evidence layers for volume context, entry location, trigger/entry zone and risk geometry. Operators still have to mentally reconcile those diagnostics. V1.3e adds a compact decision-first shadow state without collapsing the underlying evidence.

## Decision
Implement a separate `scanner/decision_architecture.py` module. It consumes frozen V1.3c planning states and V1.3d max-fill R:R. It produces four shadow states:

- **EXECUTION READY:** structured + HIGH-confidence plan, current price inside preferred entry zone, and max-fill R:R >= provisional 1.5R floor. This is execution-state readiness, not Trade With Edge trade approval.
- **WATCH:** structured + HIGH-confidence plan below trigger; wait for trigger acceptance.
- **WAIT:** incomplete, non-structured, marginal, unknown or otherwise non-ready state.
- **NO CHASE:** V1.3c late, missed-above-max-fill, or blocked-beyond-ceiling state.

## Non-negotiable constraints
1. Shadow only; no production gate.
2. Never mutate the official `scored` frame.
3. Never rewrite official decision, Candidate Quality, Entry Quality, ranking, buckets, event gates or legacy trade-plan fields.
4. Never invent or widen a trigger/entry zone.
5. Never tighten a stop or move a target to create READY.
6. Missing/low-confidence planning data cannot become READY.
7. V1.3c NO CHASE boundaries remain authoritative.
8. The 1.5R max-fill criterion is provisional research, not proven expectancy.

## Rationale
The architecture separates **execution-state readability** from **trade-quality authority**. EXECUTION READY is intentionally narrow; WATCH preserves the discipline of waiting for a trigger; WAIT prevents incomplete evidence from becoming an action; NO CHASE makes late execution explicit.

## Validation target
Application compilation, V1.3d regression tests, V1.3e unit/integration tests, official-layer equality, and live S&P 500/Russell 2000 reconciliation are required before acceptance/freeze.


## Live reconciliation refinement — 15 September 2026

S&P 500 and Russell 2000 live diagnostics exposed one important semantic risk: an official `DEVELOPING` candidate (MO, CQ 77.3) satisfied the V1.3c/V1.3d execution conditions and therefore appeared as READY. This did not violate the shadow logic, but the label could be misread as Trade With Edge trade approval.

Corrective architecture: rename the user-facing state to **EXECUTION READY** while preserving the execution logic, and add shadow-only `trade_quality_state` / `trade_quality_eligible` fields derived from the unchanged official bucket. This keeps Candidate Quality and Entry Quality authoritative and separate; it does not add a production trade gate. The UI explicitly warns when EXECUTION READY exists outside the A-quality layer.
