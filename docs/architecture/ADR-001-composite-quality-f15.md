# ADR-001 - Composite Quality Architecture: F15 Primary, F20 Shadow, No Hard Cap

**Status:** ACCEPTED / FROZEN  
**Original decision date:** 31 August 2026  
**Live acceptance / freeze date:** 7 September 2026  
**Decision confidence:** High for architecture mechanics; forward expectancy remains unproven  
**Scope:** Candidate desirability architecture only; not Entry Quality or trade actionability

## Context

The ALPACA Scanner maintains separate candidate-quality dimensions:

- Candidate Quality - technical candidate quality;
- Leadership - relative-strength persistence/resilience;
- Fundamental Quality - reported business-performance quality;
- Composite Quality - higher-level combined candidate assessment;
- Entry Quality - separate timing/actionability gate.

V1.2.3 introduced shadow composite scenarios. V1.2.3a separated Leadership attribution from incremental Fundamental attribution. V1.2.3b/b1 stress-tested Fundamental weights from 5% to 30% with full-precision ranking and simulated impact caps. V1.2.3b2 repaired pre-revenue/zero-revenue SEC domain integrity before final architecture acceptance.

## Decision

Select **F15** as the frozen Composite Quality architecture:

`Composite = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality`

Equivalent construction:

`Composite = 85% x (70% CQ + 30% Leadership) + 15% Fundamental`

Additional frozen decisions:

1. Keep **F20** as a shadow sensitivity benchmark.
2. Do **not** enforce a hard Fundamental-impact score cap.
3. Expose incremental Fundamental impact as:
   - NORMAL: absolute impact < 4 points;
   - MATERIAL: 4-6 points;
   - HIGH IMPACT: > 6 points.
4. REVIEW/FAIL/unavailable Fundamental Quality receives no full Composite score/rank; no imputation.
5. Candidate Quality, Leadership, Fundamental Quality, Composite Quality and Entry Quality remain separately visible.
6. F15 remains **shadow-only** after this freeze. Production ranking influence is a separate future decision requiring outcome evidence.

## Why F15

The architecture-selection calibration showed that F15 preserved useful Top-10 discrimination while reducing score/rank disruption versus F20 across both S&P 500 and Russell 2000 samples. F15 therefore provided a more stable middle architecture without adding a non-linear hard cap.

A hard cap was not selected because it would mechanically rescue/alter scores before forward evidence demonstrates that such intervention improves expectancy. Explainability is preferred to hidden score manipulation.

## Implementation integrity

The V1.2.3c selected-architecture layer:

- reuses the accepted full-precision F15 path;
- reuses the accepted F20 anchor as sensitivity benchmark;
- independently audits `0.595 x CQ + 0.255 x Leadership + 0.15 x Fundamental`;
- derives impact labels from the exact incremental F15 Fundamental contribution;
- applies no hard score cap;
- leaves REVIEW/FAIL/unavailable fundamentals unscored/unranked;
- leaves official Candidate Quality, buckets, Entry Quality and trade decisions untouched.

Offline regression before live acceptance: **22/22 PASS** across retained V1.2.3b1, V1.2.3b2 and V1.2.3c tests.

## Final Live Acceptance Evidence - 7 Sep 2026

### S&P 500 / STRICT / Fundamental sample 50

- CompanyFacts: **50/50 PASS**
- Fundamental integrity: **47 PASS / 3 REVIEW / 0 FAIL**
- Usable Fundamental coverage: **94.0%**
- V1.2.3b1 full-precision integrity: **PASS**
- V1.2.3c F15 integrity: **PASS**
- F15 rankable: **47/50**
- Selected formula: **59.5 / 25.5 / 15**
- F15<->F20 Top-10: **10/10**
- F15<->F20 Spearman: **0.984**
- Impact states: **27 NORMAL / 10 MATERIAL / 10 HIGH IMPACT**
- Median absolute F15 Fundamental impact: **3.76 pts**
- Hard score cap: **NONE**
- Official scanner bucket reconciliation: **127/127 PASS**
- Official decision path remained independent from F15 shadow output.

### Russell 2000 (IWM proxy) / STRICT / Fundamental sample 50

- CompanyFacts: **50/50 PASS**
- Fundamental integrity: **47 PASS / 3 REVIEW / 0 FAIL**
- Usable Fundamental coverage: **94.0%**
- V1.2.3b1 full-precision integrity: **PASS**
- V1.2.3c F15 integrity: **PASS**
- F15 rankable: **47/50**
- Selected formula: **59.5 / 25.5 / 15**
- F15<->F20 Top-10: **8/10**
- F15<->F20 Spearman: **0.986**
- Impact states: **23 NORMAL / 12 MATERIAL / 12 HIGH IMPACT**
- Median absolute F15 Fundamental impact: **4.14 pts**
- Hard score cap: **NONE**
- Official scanner bucket reconciliation: **74/74 PASS**
- Official decision path remained independent from F15 shadow output.

## Acceptance Decision

All V1.2.3c implementation gates passed. The architecture is therefore **ACCEPTED / FROZEN** as the reference Composite Quality design.

This acceptance proves:

- formula and anchor integrity;
- no-hard-cap behavior;
- fail-visible no-imputation behavior;
- explainable impact classification;
- preservation of the official Entry Quality / bucket / trade-decision path.

It does **not** prove forward-return edge and does **not** authorize F15 to control production ordering.

## Frozen-Principle Impact

V1.2.3c does not alter:

- official Candidate Quality;
- Leadership definition;
- Fundamental Quality calculation;
- Entry Quality;
- anti-chase rules;
- event gates;
- candidate buckets;
- trade decisions.

Future changes to F15 weights, cap policy, no-imputation behavior or production authority require a new ADR/version and new evidence.

## Next Dependency

V1.3 begins downstream of this frozen layer. Contextual Volume Quality and Entry Quality work must not modify F15 in place.
