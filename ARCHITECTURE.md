# Trade With Edge — Architecture

**Status date:** 2026-09-21  
**Formal repository baseline:** `v7.8.1-RETRIEVAL-RECOVERY-HOTFIX`  
**Scoring/data compatibility key:** `v7.4.5-P2C-FREEZE`

## 1. Architectural objective

> **Data Reliability → Market Regime → Candidate Quality → Entry Quality → Actionability → Trade Plan → Lifecycle → Portfolio Risk → Execution**

## 2. Decision layers

### Candidate Quality

Question:

> **Is this a high-quality swing candidate?**

Persistent traits should dominate.

### Entry Quality

Question:

> **Is this a good place to enter now?**

Tactical factors include setup maturity, contextual volume, extension, stop geometry and R:R.

### Actionability

Question:

> **Should the system act now?**

A strong candidate can still be WAIT.

The system must preserve:

> **Candidate Quality ≠ Entry Quality ≠ Actionability**

## 3. System #1 — Core Scanner

The Core Scanner is the large-universe discovery and decision surface.

Scanner-level entry readiness is intentionally cheaper than full ticker verification. A price-ready scanner row may require:

> **VERIFY EVENT + STOP**

This means price-ready, not fully actionable.

The scanner remains governed by the frozen scoring/data baseline until historical evidence supports calibration.

## 4. System #2 — Authoritative Decision Architecture

System #2 provides the authoritative evaluator and persistent monitoring/state infrastructure.

### Canonical evaluator

The authoritative decision model is:

> **C3.0 Candidate Quality + E2.0 Entry Quality**

The evaluator is treated as canonical for System #2. Foreground and shadow paths must preserve parity with it.

### Monitoring progression

```text
Canonical evaluator
      ↓
monitor_shadow_evaluation
      ↓
monitor_authoritative_state
      ↓
monitor_authoritative_history
      ↓
monitor_transition_proposal
      ↓
[future explicit promotion gate]
```

### Phase 3B.5F1

F1 establishes the current authoritative state in a dedicated table:

> `monitor_authoritative_state`

F1 intentionally suppresses transition generation.

### Phase 3B.5F2

F2 introduces immutable evaluation history and read-only transition proposals:

> `monitor_authoritative_history`  
> `monitor_transition_proposal`

The semantic comparison must use decision fields, not volatile provenance alone.

Therefore:

> `input_sha256` changed ≠ trading-state transition

A semantic change may yield a proposal, but F2 does not write to the existing `monitor_transition` table.

## 5. Price-data architecture

### Individual ticker fresh history

- Yahoo/yfinance — PRIMARY
- Yahoo `Ticker.history` — RECOVERY
- Stooq — individual-ticker recovery / repair
- fail closed if reliable fresh OHLCV is unavailable

### Scanner durable recovery

- GitHub durable snapshots — LAST-GOOD SCANNER SNAPSHOT RECOVERY

GitHub durable recovery restores persisted scanner-universe state. It is not a fourth arbitrary per-ticker historical-data API.

### Future provider candidate

- Alpaca historical SIP — SHADOW / VALIDATION first

If benchmark evidence supports a role change, update provider roles through a separate validated phase.

## 6. Session integrity

Normal path:

- XNYS calendar via `exchange_calendars`
- completed-session signal selection
- 120-minute post-close publication buffer
- stale/in-progress daily bars rejected
- ambiguous timestamps fail closed

Resilience fallback:

The current code contains a weekday / approximately 18:00 ET fallback if the XNYS calendar library is unavailable or errors. Treat this as resilience behavior, not exact exchange-calendar equivalence.

Before v3.0, explicitly decide whether this fallback should remain after validation or be replaced with strict fail-closed behavior.

## 7. Trade Plan and data-confidence enforcement

A fully actionable ticker trade plan requires:

1. Candidate gate passes
2. Entry gate passes
3. Event risk acceptable
4. Stop/R:R acceptable
5. Price Data Confidence acceptable

Stop hard cap:

> **10%**

Current user-visible behavior is fail-closed for low confidence. Before lifecycle/API/automation reuse, centralize the confidence gate so the safety rule is not UI-only.

## 8. Lifecycle and transition architecture

The roadmap lifecycle is:

> `DISCOVERED → WATCH → DEVELOPING → READY → TRIGGER → ACTIVE / INVALIDATED`

System #2 transition infrastructure must remain separate from the existing lifecycle state until explicit validation and promotion gates are passed.

F2 currently proposes changes; it does not promote them into `monitor_transition`.

## 9. Future RS Quality

> **RS Quality = RS Level + RS Direction + Stress Resilience**

Research only until validated.

## 10. Future Contextual Volume

> **Volume Quality = f(Setup Type, Price Structure, Volume Behavior)**

Research only until validated.

## 11. Portfolio / Risk / Execution architecture

IBKR remains the intended:

> **Portfolio + Risk + Execution**

Any production execution path requires separate validation, permission boundaries and explicit promotion.

System #2 monitoring phases do not imply an order endpoint.

## 12. Validation architecture

Before v3.0, repeatable regression and validation coverage must include at least:

- completed-session resolution
- Price Data Confidence
- event UNKNOWN handling
- extension / no-chase gates
- stop hard cap
- scanner/ticker actionability semantics
- recovery-state behavior
- System #2 canonical parity
- semantic transition comparison
- transition isolation

Historical and forward validation remain mandatory before claims of statistical trading edge.

## 13. Security

Never commit Alpaca secrets, IBKR credentials or GitHub PATs.

Use managed secrets / environment bindings and keep request-time credential material out of logs, durable D1 state and source control.
