# ADR-003 - Entry Location & Anti-Chase V1.3b: Continuous Pressure Against Frozen Hard Ceilings

**Status:** ACCEPTED / FROZEN (SHADOW)  
**Implementation date:** 11 September 2026  
**Live acceptance / freeze date:** 11 September 2026  
**Decision confidence:** High for measurement integrity, hard-gate parity and official-layer isolation; band expectancy remains unproven  
**Scope:** Entry-location / anti-chase diagnostics near Entry only; no official Candidate Quality, F15, Entry Quality, ranking, bucket, event-gate or trade-decision authority

## Context

The pre-V1.3b scanner already protected against obvious chasing with three frozen hard limits:

- EMA8 extension > **5.0%**;
- EMA20 extension > **8.0%**;
- EMA20 extension > **2.0 ATR**.

Those hard limits are useful and remain valid, but they are binary. A stock just below a ceiling and a stock far from that ceiling are both technically "not chase" until the strict `>` breach occurs.

The project principle is:

> **Strong stock != good entry.**

Therefore, the system needs to expose **how much extension headroom remains before the frozen hard ceiling is crossed**, without weakening the ceiling itself.

## Decision

Freeze V1.3b as a **SHADOW Entry Location / Anti-Chase diagnostic architecture**.

### 1. Preserve the frozen hard NO CHASE ceilings

V1.3b does not change the existing production thresholds:

- EMA8: 5.0%;
- EMA20: 8.0%;
- EMA20 in ATR units: 2.0 ATR.

The frozen hard gate remains strict `>`.

Exactly at a ceiling is **not** a hard breach. It is a near-ceiling / VERY LATE condition.

### 2. Normalize each extension axis into transparent pressure

For positive extension only:

`EMA8 pressure = 100 x max(0, ext_ema8_pct) / 5.0`

`EMA20 pressure = 100 x max(0, ext_ema20_pct) / 8.0`

`ATR pressure = 100 x max(0, ext_atr) / 2.0`

The diagnostic layer then reports:

- EMA8 pressure;
- EMA20 pressure;
- ATR pressure;
- dominant extension axis;
- maximum chase pressure;
- normalized hard-ceiling headroom;
- axis-specific remaining headroom.

A 100% pressure reading means price is exactly at one frozen hard ceiling. A reading above 100% means that axis independently breaches the hard NO CHASE limit.

### 3. Reference shadow location states

The accepted V1.3b reference bands are:

- **REPAIR / BELOW EMA20:** EMA20 extension < -1.5%;
- **PRIME / CONTROLLED:** max pressure <= 40% and EMA20 extension <= 3.0%;
- **ACCEPTABLE:** max pressure <= 65%;
- **STRETCHED:** max pressure <= 85%;
- **VERY LATE / AT CEILING:** below hard breach but above the STRETCHED band, including exactly at a ceiling;
- **NO CHASE — HARD CEILING:** one or more frozen official ceilings exceeded;
- **NOT RANKED:** required extension inputs are incomplete.

These states are frozen as **shadow diagnostics only**. V1.3b does not claim that 40% / 65% / 85% are expectancy-optimal production thresholds.

### 4. REPAIR is not treated as a good location merely because positive extension is low

A price below the EMA20 repair band can show low positive-extension pressure. That must not be confused with an attractive entry location.

Therefore, EMA20 extension below -1.5% receives the separate state:

**REPAIR / BELOW EMA20**.

### 5. Independent hard-gate parity

V1.3b independently recomputes whether any frozen hard ceiling is exceeded and compares that result with the official frozen `chase_reasons` path.

This produces a live **HARD NO CHASE PARITY PASS/FAIL** integrity control.

### 6. Shadow isolation

The V1.3b table is built separately from the official scored frame.

It does not:

- alter Candidate Quality;
- alter F15 Composite;
- alter official Entry Quality;
- alter ranking;
- alter buckets;
- alter event gates;
- alter trade decisions;
- relax or replace the hard NO CHASE ceilings.

### 7. No production Entry Location score

V1.3b does not create a new 0-100 production Entry Location score.

The purpose is to **measure -> explain -> validate** continuous location deterioration before any future scoring/promotion decision.

## Why this architecture

The hard NO CHASE gate is a safety boundary, not an ideal entry target.

A binary architecture alone can create false equivalence:

- 20% of a ceiling consumed -> not chase;
- 99% of a ceiling consumed -> also not chase;
- 101% consumed -> NO CHASE.

V1.3b preserves the binary safety boundary while exposing the continuous deterioration that occurs before the breach.

This supports the project rule:

> **An A/A+ stock or setup does not justify chasing an extended entry.**

## Implementation integrity

V1.3b implementation validation:

- `py_compile`: PASS;
- targeted unit/regression/integration validation: **53/53 PASS**;
- independent hard-gate recomputation included;
- official scored frame remains unchanged while diagnostics are built;
- missing required inputs produce NOT RANKED / LOW confidence rather than neutral imputation.

Offline replay on earlier accepted machine-readable S&P and Russell populations achieved full hard-NO-CHASE parity and official-field reconciliation. Those replays were engineering smoke tests only; live acceptance remained mandatory.

## Live Acceptance Evidence

### S&P 500 / STRICT

Machine-readable reconciliation:

- official candidates: **119**;
- Entry Location rows: **119**;
- exact symbol population match: **119/119**;
- duplicate symbols: **0**;
- official bucket mismatches: **0**;
- official setup mismatches: **0**;
- Candidate Quality mismatches: **0**;
- Entry Quality mismatches: **0**;
- Location Data Confidence: **119/119 HIGH**;
- hard NO CHASE parity: **119/119 PASS**;
- states: **68 PRIME/CONTROLLED / 11 ACCEPTABLE / 6 STRETCHED / 4 VERY LATE / 25 REPAIR / 5 HARD NO CHASE**;
- near-ceiling non-hard watch (75%-<100%): **5**;
- official ACTIONABLE/TECH ACTIONABLE already STRETCHED/VERY LATE: **0 - not observed**.

Representative pre-breach cases:

- DVN: 95.62% pressure;
- CVX: 94.81%;
- HPQ: 94.77%;
- COP: 93.03%;
- ELV: 79.80%.

Hard-breach examples included SWKS, VLO, META, PSX and MPC.

### Russell 2000 (IWM proxy) / STRICT

Strict earnings/event gate was ON.

Machine-readable reconciliation:

- official candidates: **85**;
- Entry Location rows: **85**;
- exact symbol population match: **85/85**;
- duplicate symbols: **0**;
- official bucket mismatches: **0**;
- official setup mismatches: **0**;
- Candidate Quality mismatches: **0**;
- Entry Quality mismatches: **0**;
- Location Data Confidence: **85/85 HIGH**;
- hard NO CHASE parity: **85/85 PASS**;
- states: **36 PRIME/CONTROLLED / 16 ACCEPTABLE / 10 STRETCHED / 5 VERY LATE / 12 REPAIR / 6 HARD NO CHASE**;
- near-ceiling non-hard watch (75%-<100%): **10**;
- official ACTIONABLE/TECH ACTIONABLE already STRETCHED/VERY LATE: **0 - not observed**.

Representative pre-breach cases:

- CRGY: **99.56%** pressure;
- TXG: 98.85%;
- ANF: 94.70%;
- CRC: 90.44%;
- AVAH: 90.02%;
- PTEN: 79.65%;
- PBF: 78.52%;
- TDS: 78.36%;
- SM: 77.39%;
- TARS: 75.35%.

Hard-breach examples were ASO, CVI, SIG, CLMT, DHT and ATRC.

## Canonical Research Example - CRGY

CRGY reached **99.56% of its most restrictive frozen ceiling**, leaving only **0.44% normalized headroom**.

The frozen official hard gate correctly remained "not chase" because no strict `>` breach occurred.

V1.3b simultaneously classified the location as **VERY LATE / AT CEILING**.

This is not a contradiction. It demonstrates the architecture:

> **A trade can still be below the hard ceiling while already having very poor entry-location headroom.**

## Cross-Universe Evidence

| Measure | S&P 500 | Russell 2000 |
|---|---:|---:|
| HARD NO CHASE | 5/119 = 4.2% | 6/85 = 7.1% |
| Near ceiling 75%-<100% | 5/119 = 4.2% | 10/85 = 11.8% |
| Non-hard STRETCHED + VERY LATE | 10/119 = 8.4% | 15/85 = 17.6% |

The Russell sample contained materially more extension pressure than the S&P sample. This cross-universe difference is useful diagnostic evidence, not proof of predictive expectancy.

## Acceptance Decision

V1.3b is **ACCEPTED / FROZEN as SHADOW Entry Location / Anti-Chase diagnostics**.

This acceptance proves:

- continuous extension-pressure calculation;
- transparent dominant-axis/headroom behavior;
- REPAIR separation;
- exact preservation of the frozen hard NO CHASE semantics;
- independent hard-gate parity;
- official-layer isolation;
- fail-visible data-confidence behavior;
- cross-universe machine-readable reconciliation.

It does **not** prove:

- positive trading expectancy;
- optimal PRIME/ACCEPTABLE/STRETCHED/VERY LATE bands;
- that shadow states should alter official Entry Quality;
- that shadow states should alter production buckets;
- a valid production Entry Location score.

## Frozen-Principle Impact

V1.3b does not modify:

- Candidate Quality;
- Leadership;
- Fundamental Quality;
- F15 Composite;
- Contextual Volume V1.3a architecture;
- official Entry Quality;
- frozen hard anti-chase ceilings;
- event gates;
- candidate buckets;
- trade decisions.

Future changes to hard ceilings, location bands, scoring or production authority require a new version/evidence record.

## Next Dependency

**V1.3c - Trigger & Entry-Zone Architecture** may open after this documentation checkpoint is committed.

V1.3c must stop treating the current close as the only practical entry reference and begin separating:

- observed current price;
- planned entry zone;
- trigger;
- confirmation condition;
- maximum acceptable fill/chase boundary.

Outcome value for V1.3b remains a dependency of **V1.7 - Expectancy Validation / Backtest / Forward-Test Lab**.
