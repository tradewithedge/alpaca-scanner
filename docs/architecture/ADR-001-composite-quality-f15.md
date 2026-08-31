# ADR-001 — Composite Quality Architecture: F15 Primary, F20 Shadow, No Hard Cap

**Status:** Architecture Selected — V1.2.3c shadow implementation ready for live acceptance  
**Date:** 31 August 2026  
**Decision confidence:** Medium-High  
**Scope:** Candidate desirability architecture only; not Entry Quality or trade actionability

## Context

The ALPACA Scanner has three separately validated candidate-quality dimensions:

- Candidate Quality (technical quality)
- Leadership (relative-strength persistence/resilience)
- Fundamental Quality (reported business-performance quality)

V1.2.3 introduced shadow composite scenarios. V1.2.3a separated Leadership attribution from incremental Fundamental attribution. V1.2.3b/b1 stress-tested Fundamental weights from 5% to 30% with full-precision ranking and simulated ±4/±6/±8 Fundamental-impact caps. V1.2.3b2 repaired a pre-revenue/zero-revenue SEC domain edge case before the Russell 2000 calibration was completed.

The architecture decision must preserve the separate meaning of Candidate Quality, Leadership and Fundamental Quality while selecting a combined ranking signal that is influential enough to matter but not so aggressive that Fundamental Quality dominates the technical/leadership engine.

## Decision

Select **F15** as the primary Composite Quality architecture candidate:

`Composite = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental Quality`

Equivalent construction:

`Composite = 85% × (70% CQ + 30% Leadership) + 15% Fundamental`

Additional decisions:

1. Keep **F20** as a shadow sensitivity benchmark.
2. Do **not** enforce a hard Fundamental-impact cap in the initial V1.2.3c implementation.
3. Expose incremental Fundamental impact explicitly as:
   - NORMAL: absolute impact < 4 points
   - MATERIAL: 4–6 points
   - HIGH IMPACT: > 6 points
4. REVIEW/FAIL/unavailable Fundamental Quality receives no full Composite score/rank; no imputation.
5. Candidate Quality, Leadership, Fundamental Quality, Composite Quality and Entry Quality remain separately visible.
6. Initial V1.2.3c remains shadow-only and does not change official scanner ranking, buckets or trade decisions.

## Evidence

### S&P 500 50-name sample

| Weight | Top-10 | Spearman | Median rank impact | Mean score impact | Max score impact |
|---:|---:|---:|---:|---:|---:|
| F15 | 7/10 | 0.783 | 6 | 3.8 | 9.7 |
| F20 | 7/10 | 0.590 | 8 | 5.1 | 12.9 |

### Russell 2000 50-name sample

| Weight | Top-10 | Spearman | Median rank impact | Mean score impact | Max score impact |
|---:|---:|---:|---:|---:|---:|
| F15 | 8/10 | 0.790 | 5 | 4.1 | 11.4 |
| F20 | 8/10 | 0.723 | 5 | 5.5 | 15.2 |

F15 preserved the same Top-10 overlap as F20 in both samples while reducing score/rank disruption. Its Spearman stability was also nearly identical across universes: 0.783 S&P versus 0.790 Russell. F20 was materially more universe-sensitive: 0.590 versus 0.723.

## Guardrail evidence

F20 guardrail simulations showed:

- ±4: too interventionist;
- ±6: meaningful middle protection;
- ±8: light-touch.

However, moving from F20 to F15 already reduces the Fundamental contribution by 25%. A hard cap on top of F15 would add a second non-linear intervention before forward-outcome evidence proves that it improves expectancy.

Therefore the initial architecture uses **explainability rather than hidden score manipulation**.

## Alternatives considered

### F10

Not selected. It provides less Fundamental influence than desired for a higher-level combined-quality layer.

### F20

Not selected as primary. It provides no better Top-10 discrimination in the tested samples but causes more rank churn and weaker cross-universe stability.

### F25 / F30

Not selected. Fundamental influence becomes increasingly dominant, with larger score impacts and lower rank stability.

### Hard ±4 cap

Rejected. Too many names are affected; the cap materially rewrites the raw ranking.

### Hard ±6 cap

Not selected now. It is the best middle guardrail at F20, but its incremental value after selecting F15 is unproven.

### Hard ±8 cap

Not selected now. It is low-intervention but adds architecture complexity without a demonstrated need after F15 selection.

### Neutral Fundamental imputation

Rejected. It violates data-integrity-first principles and hides uncertainty.

## Consequences

### Positive

- Technical Candidate Quality remains dominant.
- Leadership remains materially influential.
- Fundamentals matter without controlling the ranking.
- Cross-universe stability improves versus F20.
- Score conflicts remain interpretable.
- Architecture remains linear and auditable.

### Negative / trade-offs

- Weak fundamentals can still materially demote a technical leader.
- No hard cap means extreme Fundamental impact is not mechanically constrained.
- The architecture is selected from robustness evidence, not forward-return evidence.

## Known limitations

1. Calibration uses bounded 50-name S&P 500 and Russell 2000 samples.
2. No historical expectancy/backtest proof yet.
3. Some sectors may require future domain-specific Fundamental concept maps.
4. Observed F20 guardrail triggers were entirely downside in both samples; the asymmetry requires future study.
5. F15 may be recalibrated later only if broader empirical evidence justifies change.

## Frozen-principle impact

This ADR does **not** alter:

- official Candidate Quality;
- Leadership definition;
- Fundamental Quality calculation;
- Entry Quality;
- anti-chase rules;
- event gates;
- candidate buckets;
- trade decisions.

## V1.2.3c shadow implementation

The first implementation of this ADR is complete in shadow mode:

- `scanner/composite_architecture.py` is the selected-architecture layer.
- It reuses V1.2.3b1 full-precision `score_f15_exact` / `rank_f15` rather than reconstructing F15 from rounded display values.
- It reuses the accepted V1.2.3a F20 score/rank as the sensitivity benchmark.
- It independently audits `0.595 × CQ + 0.255 × Leadership + 0.15 × Fundamental` against the b1 F15 exact score.
- NORMAL / MATERIAL / HIGH IMPACT labels use the exact incremental F15 Fundamental contribution.
- PROMOTION / PENALTY / NEUTRAL is shown separately for direction.
- No hard impact cap is applied.
- REVIEW/FAIL/unavailable fundamentals remain without a full Composite score/rank.
- `app.py` presents this as Section 3F and explicitly states that official ranking, buckets, Entry Quality and trade decisions are unchanged.

Offline regression result: **22/22 PASS** across retained V1.2.3b1, V1.2.3b2 and new V1.2.3c tests.

## Live acceptance gate

V1.2.3c remains shadow-only until a live Russell 2000 STRICT / Fundamental sample 50 run confirms:

1. V1.2.3b1 anchor integrity still passes;
2. V1.2.3c F15 formula integrity passes;
3. F20 remains shadow-only;
4. no hard cap is applied;
5. REVIEW rows remain unranked; and
6. official scanner ordering/actionability is unchanged.

Production ranking influence requires a separate post-acceptance decision and is outside this ADR implementation gate.
