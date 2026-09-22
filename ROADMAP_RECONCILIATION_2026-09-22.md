# Roadmap Reconciliation Gate — 2026-09-22

## Status

**Gate:** PASS — documentation reconciliation prepared  
**Repository:** `tradewithedge/alpaca-scanner`  
**Baseline:** restored `ROADMAP.md` SHA `a730a075fce675949e9834015e3fac1363f9650b`  
**Scope:** documentation only; no scanner/runtime/scoring changes

## 1. Authority

`ROADMAP.md` remains the single Master Roadmap.

The current authoritative scanner path is:

**V1.0 → V1.3f → V1.7 Expectancy / Backtest / Forward-Test → V1.8 Paper → V2.0**

System #2 / Authority Track is a coordinated workstream. It is **not** a competing master roadmap and does not replace the V1.x scanner roadmap.

## 2. Six-source reconciliation

| Control source | Reconciliation result |
|---|---|
| `ROADMAP.md` | Restored original V1.x baseline |
| `ALPACA_SCANNER_DEVELOPMENT_CHRONICLE.md` | V1.3f accepted/frozen; next permitted work is V1.7 |
| `docs/architecture/ADR-001..007` | Frozen V1.2.3c–V1.3f architecture remains authoritative |
| Outstanding Research / Dependency Register | V1.7 owns expectancy, outcome validation and threshold calibration |
| Accepted live tests / case-study lessons | Preserve execution-capture architecture; do not loosen quality standards |
| Frozen architecture dependencies | No changes to Candidate Quality, F15, Entry Quality, anti-chase, event gates or broker execution |

## 3. Scanner Master Roadmap status

### Completed / frozen

- V1.0 — scanner foundation
- V1.1 — universes / persistent quality
- V1.1.1 — consolidated SIP integrity
- V1.1.2 — scanner audit integrity
- V1.2.1 — leadership / resilience
- V1.2.1.1–V1.2.1.3c — leadership explainability / inspector
- V1.2.2 — Fundamental Quality
- V1.2.2.x — SEC / metric / coverage integrity
- V1.2.3c — F15 architecture
- V1.3a — contextual volume diagnostics
- V1.3b — entry location / anti-chase
- V1.3c — trigger / entry-zone
- V1.3d — risk/reward / stop-distance
- V1.3e — execution-state architecture
- V1.3f — shadow execution capture

All V1.3a–V1.3f layers remain **SHADOW** and do not gain production authority from this reconciliation.

### Current next scanner stage

**V1.7 — Expectancy Validation / Backtest / Forward-Test Lab**

Purpose:

1. collect prospective V1.3f outcomes;
2. build historical backtests without look-ahead leakage;
3. measure signal, entry/trigger, captured, realized, missed-opportunity and net expectancy;
4. include transaction costs and realistic slippage;
5. test robustness across time, regime, setup and universe;
6. validate whether any shadow diagnostic deserves production authority.

## 4. System #2 Authority Track

System #2 remains a separate authority/monitoring workstream.

Validated sequence:

**3B.4 → 3B.5D → 3B.5E → 3B.5F1 COMPLETE/FROZEN → 3B.5F2 CODE VERIFIED / DEPLOYMENT GATE**

Current state:

- 3B.5F1 authoritative state: **COMPLETE / FROZEN**
- 3B.5F2 semantic Transition Proposal Engine: **CODE VERIFIED**
- 3B.5F2 deployment: **NOT YET AUTHORIZED**
- `monitor_transition`: must remain untouched
- `/alerts`: no new publication authority
- trading/order endpoints: unchanged and absent
- account/equity/buying-power calls: prohibited for this track
- initial scope: SCHW only
- semantic comparison must ignore volatile provenance such as `input_sha256`

## 5. System #2 relationship to V1.7

System #2 does not modify the scanner's frozen scoring architecture.

Its role is to provide authoritative state monitoring and semantic transition evidence around the separately validated canonical evaluator.

Therefore:

- V1.7 validates **trading expectancy**.
- System #2 validates **state authority / transition integrity**.
- Neither workstream silently promotes the other's diagnostics into production trading authority.

## 6. Research / dependency dispositions

| Item | Disposition | Destination |
|---|---|---|
| Contextual Volume Quality | RESOLVED / FROZEN SHADOW | V1.3a; expectancy later |
| Entry Location / Anti-Chase | RESOLVED / FROZEN SHADOW | V1.3b; expectancy later |
| Trigger / Entry Zone | RESOLVED / FROZEN SHADOW | V1.3c; expectancy later |
| R:R / Stop Distance | RESOLVED / FROZEN SHADOW | V1.3d; expectancy later |
| READY / WATCH / WAIT / NO CHASE | RESOLVED / FROZEN SHADOW | V1.3e |
| Shadow execution capture | RESOLVED / FROZEN SHADOW | V1.3f |
| Trading expectancy | ASSIGNED | V1.7 |
| Backtest | ASSIGNED | V1.7 |
| Forward-test outcomes | ASSIGNED | V1.7 |
| F15 production authority | DEFERRED | V1.7+ evidence |
| Entry-location band production authority | DEFERRED | V1.7 evidence |
| Event-date reliability | ASSIGNED | V1.5 |
| Paper execution / journal | ASSIGNED | V1.8 |

## 7. Frozen boundaries

This reconciliation does **not** authorize:

- scoring changes;
- threshold changes;
- Candidate Quality changes;
- F15 production ranking;
- Entry Quality changes;
- anti-chase relaxation;
- event-gate changes;
- broker order execution;
- position sizing changes;
- `monitor_transition` writes;
- new alert publication;
- account/buying-power calls.

## 8. Decision

**Roadmap Reconciliation Gate: PASS.**

The project is now permitted to proceed under the restored Master Roadmap.

### Next permitted work

**V1.7 Expectancy Validation / Backtest / Forward-Test Lab**

while preserving all frozen V1.3a–V1.3f architecture.

System #2 3B.5F2 remains at its separate **deployment gate** and must not be deployed as part of V1.7.

---
