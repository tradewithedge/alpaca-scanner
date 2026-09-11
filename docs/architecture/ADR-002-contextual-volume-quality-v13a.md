# ADR-002 - Contextual Volume Quality V1.3a: Completed-Session, Setup-Aware Shadow Diagnostics

**Status:** ACCEPTED / FROZEN (SHADOW)  
**Implementation date:** 8 September 2026  
**Live acceptance / freeze date:** 11 September 2026  
**Decision confidence:** High for architecture/data integrity and official-layer isolation; threshold expectancy remains unproven  
**Scope:** Contextual volume diagnostics near Setup/Entry only; no official Candidate Quality, F15, Entry Quality, bucket or trade-decision authority

## Context

The existing scanner used volume in limited setup rules:

- breakout confirmation benefited from relative-volume expansion;
- pullback/VCP logic could benefit from low/contraction volume.

That logic was useful but incomplete. Volume meaning is setup-dependent:

- breakouts normally need demand/participation expansion;
- pullbacks and VCP/tightening can improve when supply dries up;
- heavy distribution can contradict attractive price structure;
- favorable volume must not rescue broken price structure.

A separate Contextual Volume Quality research layer was therefore added at V1.3a before Entry Location / Anti-Chase work.

## Decision

Freeze V1.3a as a **SHADOW contextual-volume diagnostic architecture** with the following decisions.

### 1. Price structure first

Classify price context independently of the new volume diagnostics. V1.3a does not use its own new volume evidence to manufacture the price setup it then evaluates.

Supported diagnostic contexts include:

- BREAKOUT;
- EMA20 PULLBACK;
- VCP / TIGHTENING;
- TIGHT BASE;
- MA20 REPAIR WINDOW;
- BROKEN / BELOW MA50;
- NO CLEAN SETUP.

### 2. Completed-session volume discipline

Use consolidated SIP daily bars and exclude a same-day daily bar before the conservative **16:30 ET** completion cutoff.

The purpose is to prevent a partial daily volume bar from being compared as if it were a completed session.

### 3. Explicit Volume Data Confidence

- HIGH: sufficient completed history and recent valid positive-volume coverage;
- MEDIUM: usable but weaker coverage;
- LOW: insufficient evidence.

LOW confidence is **NOT RANKED**. No neutral/average imputation is permitted.

### 4. Diagnostic features

The accepted shadow evidence includes:

- completed-session RVOL versus the prior 20 sessions;
- 5D volume versus a non-overlapping prior-20 baseline;
- 10D volume versus a non-overlapping prior-20 baseline;
- 10D up/down-volume ratio;
- 10D up-volume share;
- accumulation-day count;
- distribution-day count;
- 5D and 10D volume-trend labels.

### 5. Setup-aware interpretation

- BREAKOUT: seeks meaningful participation/expansion.
- EMA20 PULLBACK / VCP / TIGHT BASE: seeks controlled contraction/dry-up.
- MA20 REPAIR: diagnostic evidence only unless distribution is adverse.
- BROKEN / BELOW MA50: favorable volume cannot rescue the price structure.
- NO CLEAN SETUP: retain diagnostics without manufacturing a positive setup conclusion.

### 6. Shadow isolation

The V1.3a table is built separately from the official scored frame.

It does not:

- merge new volume fields into official scoring;
- alter Candidate Quality;
- alter F15;
- alter Entry Quality;
- alter ranking;
- alter buckets;
- alter event gates;
- alter trade decisions.

### 7. No numeric Volume Quality score

No 0-100 Contextual Volume Quality score or production weight is authorized by V1.3a.

## Why this architecture

The design follows the project rule:

> **measure -> explain -> validate -> then score**

A universal volume score would be premature because high volume can be constructive for a breakout and undesirable for a pullback. The setup context must therefore govern interpretation before any future scoring proposal.

Completed-session discipline is also required for data integrity. A partial-session daily volume bar and a completed daily volume bar are different observations and must not be compared without explicit normalization.

## Implementation integrity

Offline V1.3a validation:

- `py_compile`: PASS;
- dedicated unit/integration suite: **22/22 PASS**;
- tests covered session exclusion/inclusion, input immutability, prior-20 RVOL baseline, breakout and pullback behavior, LOW-confidence NOT RANKED, distribution accounting, app integration and official-layer isolation.

The packaging environment did not run the entire pre-existing repository regression suite; no broader claim is made.

## Live Acceptance Evidence

### S&P 500 / STRICT

Full machine-readable reconciliation:

- 127 official candidates / 127 contextual rows;
- 127 unique symbols; duplicates 0;
- 127/127 exact population match;
- 0 official bucket mismatches;
- 0 official setup mismatches;
- 0 Candidate Quality mismatches;
- 0 Entry Quality mismatches;
- 127/127 HIGH Volume Data Confidence;
- states: 41 CONFIRMING / 38 MIXED / 34 DIAGNOSTIC ONLY / 14 CONFLICT-WATCH;
- contexts: 83 EMA20 PULLBACK / 35 NO CLEAN SETUP / 4 BREAKOUT / 4 MA20 REPAIR / 1 TIGHT BASE.

### Russell 2000 (IWM proxy) / STRICT - controlled same-session run

- 85 official candidates / 85 contextual rows;
- 85 unique symbols; duplicates 0;
- 85/85 exact population match;
- 0 official bucket mismatches;
- 0 official setup mismatches;
- 0 Candidate Quality mismatches;
- 0 Entry Quality mismatches;
- 85/85 HIGH Volume Data Confidence;
- evaluation session 2026-09-10 for all rows;
- states: 24 CONFIRMING / 11 MIXED / 13 CONFLICT-WATCH / 37 DIAGNOSTIC ONLY;
- contexts: 39 EMA20 PULLBACK / 24 NO CLEAN SETUP / 12 MA20 REPAIR / 5 BREAKOUT / 3 BROKEN-BELOW-MA50 / 2 VCP-TIGHTENING.

## Session-Comparability Investigation

### Symptom

During earlier intraday testing, frozen official `vol_ratio` and V1.3a `rvol_20` sometimes diverged sharply.

### Root cause

The legacy metric could reflect the latest partial daily bar, while V1.3a deliberately evaluated the latest completed session. The observations were not session-aligned.

### Evidence

Russell comparisons:

- regular-session/partial-bar sample: Pearson ~0.043;
- pre-market/session-mismatch sample: Pearson ~0.580;
- controlled same-completed-session sample: Pearson **0.999966**, Spearman **0.999790**.

In the final 85-stock controlled run:

- mean official `vol_ratio`: 0.98847x;
- mean V1.3a `rvol_20`: 0.98859x;
- 85/85 values matched when rounded to two decimals.

### Decision

The V1.3a completed-session safeguard is accepted. V1.3a does not silently rewrite frozen legacy `vol_ratio`.

If an intraday participation feature is added later, it must use a like-for-like intraday pace baseline (for example, current time-of-day versus historical time-of-day participation) and requires separate validation.

## Validation Evidence Control

V1.3a also establishes a process rule:

- screenshots prove version, settings, banners, headline counts and UI behavior;
- full CSV/machine-readable exports are the primary evidence for quantitative acceptance;
- full-population reconciliation must be programmatic when practical;
- capped display tables cannot stand in for full-population evidence.

## Acceptance Decision

V1.3a is **ACCEPTED / FROZEN as SHADOW diagnostics**.

This acceptance proves:

- completed-session handling;
- Volume Data Confidence behavior;
- setup-aware contextual interpretation;
- separate shadow-table architecture;
- cross-universe official-layer isolation;
- fail-visible/no-imputation behavior.

It does **not** prove:

- positive trading expectancy;
- optimal thresholds;
- a valid 0-100 Volume Quality score;
- production ranking or Entry Quality improvement.

## Frozen-Principle Impact

V1.3a does not modify:

- Candidate Quality;
- Leadership;
- Fundamental Quality;
- F15 Composite;
- official Entry Quality;
- anti-chase rules;
- event gates;
- candidate buckets;
- trade decisions.

Future changes to completed-session policy, confidence rules, contextual thresholds, scoring or production authority require a new version/evidence record.

## Next Dependency

**V1.3b - Entry Location & Anti-Chase Foundation** may open after this documentation checkpoint is committed.

Outcome value for V1.3a remains a dependency of **V1.7 - Expectancy Validation / Backtest / Forward-Test Lab**.
