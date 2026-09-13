# ADR-004 — V1.3c Trigger & Entry-Zone Architecture

**Status:** ACCEPTED / FROZEN (SHADOW)  
**Date:** 13 September 2026  
**Decision:** Separate observed price from structural trigger, confirmation, preferred entry zone and maximum acceptable fill without changing the frozen official decision path.

## Context

The frozen scanner still uses the current close as the practical `entry_px` reference. That is a valid snapshot but is not a complete execution plan. A swing trader needs to know what structural event would justify entry, where a planned entry remains acceptable, and where the opportunity has become too late to chase.

V1.3b established continuous entry-location pressure against the existing hard NO CHASE ceilings. V1.3c builds the next layer on top of that foundation.

## Decision

V1.3c creates a separate SHADOW planning layer:

`current price -> structural trigger -> confirmation -> preferred entry zone -> maximum acceptable fill -> frozen NO CHASE ceiling`

The current official `entry_px`, stop, T1, T2, Candidate Quality, F15 Composite, Entry Quality, ranking, buckets, event gates and trade decisions remain unchanged.

## Trigger architecture

The structural trigger is setup-aware:

| Setup/context | Shadow trigger reference |
|---|---|
| Breakout | Prior-20-session structure high plus a small confirmation buffer |
| EMA20 Pullback | EMA20 / prior-session-high reclaim structure |
| VCP / Tight Base | Prior-10-session structure high |
| MA20 Repair | Reclaim structure; diagnostic only, not automatic actionability |
| No clean setup / Broken | No structured plan |

The independent prior-20 reconstruction is compared against the frozen official `high20_prev` reference wherever both are available.

## Entry-zone architecture

Reference parameters:

- preferred entry zone: trigger through **trigger + 0.25 ATR**;
- raw maximum acceptable fill: trigger through **trigger + 0.50 ATR**;
- maximum acceptable fill is capped by the most restrictive frozen V1.3b hard ceiling.

These are **research references**, not production-optimal thresholds. No parameter is promoted solely because it looks intuitive or produces attractive examples.

If the structural trigger itself lies beyond the frozen hard ceiling, the plan is **BLOCKED**. The ceiling is never moved upward to accommodate the trade.

## Shadow states

- WAITING FOR TRIGGER
- TRIGGERED — IN ENTRY ZONE
- TRIGGERED — ABOVE ZONE / LATE
- MISSED / NO CHASE — ABOVE MAX FILL
- BLOCKED — TRIGGER BEYOND HARD CEILING
- NO STRUCTURED PLAN

These states describe execution location. They are not production trade gates.

## Why this architecture

It directly addresses the difference between:

> **good stock** → **good setup** → **good location** → **good execution**

It also formalizes the CF Case Study #001 lesson: once a planned trigger/entry region is missed, the system should record the missed opportunity rather than widening the acceptable range after the fact.

## Alternatives rejected

### 1. Replace official `entry_px` immediately
Rejected. It would mix research logic into the frozen decision layer before outcome evidence exists.

### 2. Use current close as the trigger
Rejected. Current price is an observation, not necessarily the structural event that validates the trade.

### 3. Move the NO CHASE ceiling to fit the trigger
Rejected. This would turn a risk boundary into a moving target and weaken the anti-chase principle.

### 4. Create a new 0–100 Entry Location score
Rejected. A numeric score would imply calibration/ordering authority that has not yet been validated by outcomes.

### 5. Optimize 0.25 / 0.50 ATR parameters from the first live samples
Rejected. Limited live samples can demonstrate architecture integrity but cannot establish expectancy-optimal parameters.

## Validation evidence

### S&P 500 / STRICT

Full machine-readable Swing Candidates and V1.3c Diagnostic CSVs:

- official candidates: **116**;
- diagnostic rows: **116**;
- exact symbol population match: **116/116**;
- duplicates: **0** in both files;
- official bucket/setup/Candidate Quality/Entry Quality/legacy `entry_px` mismatches: **0/116**;
- Plan Data Confidence: **116/116 HIGH**;
- prior-20 structure parity: **116/116 PASS**;
- state reconciliation: **116/116**;
- state counts: **63 WAITING / 12 IN ENTRY ZONE / 4 ABOVE ZONE-LATE / 2 MISSED-NO CHASE / 7 BLOCKED / 28 NO STRUCTURED PLAN**.

Current-price export detail: PFG differs by $0.005 between the two CSVs; this is treated as export/display rounding. All 116 are within $0.01.

### Russell 2000 (IWM proxy) / STRICT

- official candidates: **90**;
- diagnostic rows: **90**;
- exact symbol population match: **90/90**;
- duplicates: **0** in both files;
- official bucket/setup/Candidate Quality/Entry Quality/legacy `entry_px` mismatches: **0/90**;
- Plan Data Confidence: **90/90 HIGH**;
- prior-20 structure parity: **90/90 PASS**;
- state reconciliation: **90/90**;
- state counts: **42 WAITING / 2 IN ENTRY ZONE / 2 ABOVE ZONE-LATE / 1 MISSED-NO CHASE / 11 BLOCKED / 32 NO STRUCTURED PLAN**.

## Acceptance criteria

| Criterion | Result |
|---|---|
| Separate shadow layer | PASS |
| Official layer unchanged | PASS |
| Exact symbol reconciliation | PASS |
| Duplicate control | PASS |
| Official field parity | PASS |
| Prior-20 structure parity | PASS |
| High plan-data confidence | PASS |
| State reconciliation | PASS |
| Hard-ceiling blocking without relaxation | PASS |
| Cross-universe validation | PASS |

## Acceptance boundary

V1.3c acceptance proves architecture and data integrity. It does **not** prove:

- positive trading expectancy;
- optimal trigger buffer;
- optimal 0.25 ATR preferred-zone width;
- optimal 0.50 ATR maximum-fill width;
- superiority of one trigger type over another;
- production Entry Quality or bucket authority.

Those outcome questions remain assigned to **V1.7 Expectancy Validation / Backtest / Forward-Test Lab**.

## Frozen invariants

V1.3c must not modify:

- Candidate Quality;
- Leadership;
- Fundamental Quality;
- F15 Composite;
- V1.3a Contextual Volume Quality;
- V1.3b hard NO CHASE ceilings;
- official Entry Quality;
- official `entry_px`, stop, T1 or T2;
- ranking;
- candidate buckets;
- event gates;
- trade decisions.

## Next dependency

**V1.3d — Risk/Reward & Stop-Distance Gate**.

V1.3d should calculate prospective R:R using the V1.3c planned entry/trigger architecture while keeping the same shadow-only discipline. Outcome validation remains downstream in V1.7.
