# ADR-005 — V1.3d Risk/Reward & Stop-Distance Shadow Diagnostics

- **Status:** Accepted for development / SHADOW ONLY
- **Date:** 2026-09-13
- **Depends on:** V1.3c Trigger & Entry-Zone Architecture

## Context
V1.3c separates current price from structural trigger, preferred entry zone and maximum acceptable fill. The next missing execution dimension is downside geometry: structural support, stop distance, and available reward. A single R:R value at the current close is insufficient because R:R can deteriorate materially as price moves through the entry zone.

## Decision
Create a separate V1.3d diagnostic module that:

1. consumes V1.3c trigger/zone/max-fill fields;
2. derives structural support from available EMA20, prior-10 low and prior-20 low;
3. places a provisional stop 0.25 ATR below support;
4. calculates 1.5R and 2.5R target references from the trigger risk;
5. reports R:R separately at trigger, preferred-zone high and maximum fill;
6. labels R:R bands as STRONG / ACCEPTABLE / WEAK / POOR / NOT RANKED;
7. does not modify the official scoring or trade-plan fields.

## Rationale
The system should expose the geometry rather than manufacture a binary action. A setup can be attractive at trigger, marginal at zone high, and poor at maximum fill. This supports later outcome testing without prematurely granting production authority.

## Rejected alternatives
- **Rewrite official `stop`/`t1`/`t2`:** rejected; breaks frozen baseline and contaminates attribution.
- **Hard-code a 2R production gate now:** rejected; no expectancy evidence yet.
- **Use current close as the only entry reference:** rejected; V1.3c already demonstrated why execution location matters.
- **Tighten stops to improve R:R:** rejected; would manufacture edge rather than measure it.

## Safety / invariants
- SHADOW ONLY.
- `scored` deep-copy equality must pass.
- Missing/invalid critical risk inputs produce NOT RANKED, not neutral values.
- Blocked/missed/no-chase plans are not converted into entries by R:R.
- 0.25 ATR, 1.5R, 2.5R and 2.0R are provisional research references.

## Validation target
Focused V1.3b/V1.3c/V1.3d tests must pass before live validation. S&P 500 and Russell 2000 CSV validation is required before any V1.3d freeze decision. Outcome authority remains deferred to Backtest + Forward Test + Expectancy.
