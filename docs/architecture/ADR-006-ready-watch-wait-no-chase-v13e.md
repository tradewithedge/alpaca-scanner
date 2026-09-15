# ADR-006 — V1.3e EXECUTION READY / WATCH / WAIT / NO CHASE Decision Architecture

**Status:** **ACCEPTED / FROZEN (SHADOW)**  
**Date:** 16 September 2026  
**Depends on:** V1.3c Trigger & Entry-Zone Architecture; V1.3d Risk/Reward & Stop-Distance Diagnostics

## Context
V1.3a–V1.3d established independent evidence layers for volume context, entry location, trigger/entry zone and risk geometry. Operators still have to mentally reconcile those diagnostics. V1.3e adds a compact decision-first shadow state without collapsing the underlying evidence.

## Decision
Implement a separate `scanner/decision_architecture.py` module. It consumes frozen V1.3c planning states and V1.3d max-fill R:R. It produces four shadow states:

- **EXECUTION READY:** structured + HIGH-confidence plan, current price inside preferred entry zone, and max-fill R:R >= provisional 1.5R floor. This is execution-state readiness, not Trade With Edge trade approval.
- **WATCH:** structured + HIGH-confidence plan below trigger; wait for trigger acceptance.
- **WAIT:** incomplete, non-structured, marginal, unknown or otherwise non-ready state.
- **NO CHASE:** V1.3c late, missed-above-max-fill, or blocked-beyond-ceiling state.

## Quality-separation refinement
Live reconciliation identified a semantic risk: an official `DEVELOPING` candidate could satisfy execution conditions. The user-facing state is therefore explicitly **EXECUTION READY**, and the shadow output exposes `trade_quality_state` and `trade_quality_eligible` derived from the unchanged official bucket. This is a diagnostic separation, not a new production gate.

## Non-negotiable constraints
1. Shadow only; no production gate.
2. Never mutate the official `scored` frame.
3. Never rewrite official decision, Candidate Quality, Entry Quality, ranking, buckets, event gates or legacy trade-plan fields.
4. Never invent or widen a trigger/entry zone.
5. Never tighten a stop or move a target to create EXECUTION READY.
6. Missing/low-confidence planning data cannot become EXECUTION READY.
7. V1.3c NO CHASE boundaries remain authoritative.
8. The 1.5R max-fill criterion is provisional research, not proven expectancy.
9. EXECUTION READY outside the official A-quality layer must remain visibly marked NOT TRADE-QUALITY ELIGIBLE.

## Validation and live acceptance
- Targeted V1.3e refinement validation: **16/16 PASS**.
- Original V1.3e focused/regression validation before refinement: **28/28 PASS**.
- `py_compile`: PASS.
- Official-layer deep-copy equality guard: PASS.
- Fresh deployed S&P 500 and Russell 2000 scans reconciled to the refined decision-state architecture.

### Live evidence
- S&P 500: 110 persistent-quality candidates; **5 EXECUTION READY / 55 WATCH / 29 WAIT / 21 NO CHASE**.
- Russell 2000 (IWM proxy): 29 persistent-quality candidates; **0 EXECUTION READY / 6 WATCH / 18 WAIT / 5 NO CHASE**.
- MO remained a visible semantic exception: execution-ready but **NOT TRADE-QUALITY ELIGIBLE**.

## Acceptance boundary
V1.3e is a frozen shadow architecture, not a proven trading edge. It does not authorize production changes to scoring, ranking, Entry Quality, buckets, event gates or trade decisions. Expectancy validation remains assigned to Backtest + Forward Test + V1.7.

**Next permitted development move:** V1.3f Shadow Execution-Capture Logging / staged-execution preparation, only after this freeze checkpoint is committed.
