# Trade With Edge — Project Status

**Status date:** 2026-09-21  
**Repository:** `tradewithedge/swing-momentum-scanner`  
**Formal repository baseline:** `v7.8.1-RETRIEVAL-RECOVERY-HOTFIX`  
**Scoring/data compatibility key:** `v7.4.5-P2C-FREEZE`

## Executive status

Trade With Edge has a mature reliable-scanner foundation and an established decision-engine architecture. It is **not yet a statistically validated trading system**.

The project is now tracked through one Master Roadmap with two coordinated workstreams:

> **Core Scanner / Trading-System Track**  
> **System #2 Authority Track**

## Current master status

| Area | Status | Notes |
|---|---|---|
| Core scanner | Mature | Large-universe scanner baseline established |
| Market regime | Implemented | Regime-first architecture |
| Candidate Quality | Implemented | Decision-layer separation established; feature-level separation remains a P1 research item |
| Entry Quality | Implemented | Full ticker-level decision engine; scanner-level entry readiness remains intentionally partial |
| Actionability | Implemented | Full ticker-level LONG / WAIT / blocked logic |
| Trade Plan | Implemented | Entry, stop, targets, R multiples |
| Completed-session protection | Strong | XNYS is normal source; fallback is documented resilience behavior |
| Price Data Confidence | Strong | User-visible actionability is fail-closed |
| Fundamental/Event Confidence | Good | UNKNOWN remains distinct from safe |
| Provider health | Implemented | CORE / RECOVERY / UNIVERSE / ANCILLARY |
| Circuit breakers | Implemented | Route-scoped containment |
| Durable recovery | Implemented | GitHub last-good scanner snapshot recovery |
| Responsive UX | Completed | Phase 2E.1 |
| Decision-first ticker UX | Completed | Phase 2E.2 |
| Core Scanner Track | 2E.3 documented next milestone | Preserve existing repository sequence until separately revalidated |
| System #2 parity | PASS | Canonical evaluator parity established |
| System #2 real Cron shadow | PASS | Repeated scheduled evaluations successful |
| 3B.5F1 authoritative state | COMPLETE / FROZEN | Dedicated authoritative state maintained |
| 3B.5F2 D1 schema | PASS | History + proposal tables and indexes verified |
| 3B.5F2 code-level verification | PASS | Draft verified before deployment |
| 3B.5F2 Production | NOT YET | Controlled deployment gate |
| Historical validation | Major work remaining | Phase 2G |
| Automated regression suite | Partial / remaining | Expand during validation and production hardening |
| Calibration | Planned | Phase 2H |
| Portfolio risk | Planned | Phase 2I |
| Workflow automation | Planned | Phase 2J |
| Production freeze | Future | v3.0 |

## System #2 current checkpoint

### Phase 3B.5F1 — COMPLETE / FROZEN

The canonical evaluator runs on the real Cron path and maintains a dedicated `monitor_authoritative_state` for the scoped target.

Validated:

- Worker identity and health = PASS
- D1 authoritative table and indexes = PASS
- repeated real Cron completion = PASS
- successful SCHW canonical evaluations = PASS
- authoritative baseline = PASS
- stable decision semantics across repeated cycles = PASS
- new transition generation suppressed = PASS
- existing historical transition untouched = PASS
- no order/account/buying-power calls = PASS

### Phase 3B.5F2 — CODE VERIFIED / DEPLOYMENT GATE

F2 introduces a semantic comparison and proposal layer without promoting proposals into real transitions.

D1 objects:

- `monitor_authoritative_history`
- `monitor_transition_proposal`

F2 comparison rule:

> **Volatile provenance changes are not, by themselves, trading-state transitions.**

For example, a changed `input_sha256` with unchanged decision semantics remains `STABLE`.

A genuine semantic change can produce a `PROPOSED` result, while F2 still leaves `monitor_transition` untouched.

## Frozen rules

Do not change these during documentation reconciliation or F2 deployment preparation:

- `MIN_ACTIONABLE_CANDIDATE_GRADES = {"A+", "A", "B+"}`
- Extended if >8% above EMA20 or RSI >= 75
- Oversold if >8% below EMA20 or RSI <= 25
- Earnings hard block: 3 days
- Earnings caution: 14 days
- Stop hard cap: 10%
- Completed-session signals are the operating rule
- XNYS calendar is the normal session source
- 120-minute post-close publication buffer
- Scan reuse up to 15 minutes
- stale/in-progress/ambiguous price data fails closed

## Reliability architecture

### Individual ticker fresh OHLCV recovery

1. Yahoo/yfinance primary
2. Yahoo `Ticker.history` recovery
3. Stooq individual-ticker fallback / repair
4. Fail closed if reliable fresh ticker history cannot be obtained

### System-level scanner recovery

GitHub durable storage is a **last-good scanner snapshot recovery mechanism**, not an arbitrary individual-ticker OHLCV API.

## Candidate / Entry / Action clarification

### Ticker decision engine

The fullest ticker workflow performs:

> Event → Candidate Quality → Directional Structure → Location → Stop/R:R → Data Confidence override

### Scanner

The universe scanner intentionally avoids expensive full event/stop verification for every ticker.

Therefore:

> **VERIFY EVENT + STOP = price-ready candidate, not yet fully ACTIONABLE**

## Feature-separation research seam

The decision layer separates Candidate Quality, Entry Quality and Actionability.

Feature-level separation is not yet complete. Candidate scoring still contains some tactical inputs such as entry location, volume, short-term momentum/acceleration, ATR/risk and regime fit.

This remains a **P1 research hypothesis** and must not be changed before evidence from historical validation.

## Validation principle

> **Signal Quality ≠ Execution Capture**

Historical validation, forward testing and execution-capture measurement remain required before production claims.

## Overall development rule

> **Observation → Hypothesis → Historical Test → Forward Test → Evidence → Calibration**

Do not change weights, thresholds or gates because of one ticker.
