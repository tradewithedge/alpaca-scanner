# Trade With Edge — Changelog

## 2026-09-21 — Master Roadmap Reconciliation v1 — PREPARED

Prepared a documentation-only reconciliation to establish one Master Roadmap with two coordinated workstreams:

- Core Scanner / Trading-System Track
- System #2 Authority Track

The reconciliation explicitly avoids maintaining two competing roadmaps.

### System #2 checkpoint recorded

- Phase 3B.5D — canonical parity = PASS
- Phase 3B.5E — real Cron shadow evaluation = PASS
- Phase 3B.5F1 — authoritative state = COMPLETE / FROZEN
- Phase 3B.5F2 — D1 schema = PASS
- Phase 3B.5F2 — code-level verification = PASS
- Phase 3B.5F2 — production deployment = NOT YET / deployment gate

### Change-control boundary

This reconciliation does not change:

- scoring logic
- Candidate / Entry thresholds
- risk rules
- provider runtime behavior
- `monitor_transition`
- `/alerts` publication behavior
- production Worker behavior
- frozen scanner baseline

This is a documentation alignment change only.

## Prior documented baseline — 2026-09-04

Cold-Start Continuity Audit — PASS / FREEZE.

Formal baseline:

> `v7.8.1-RETRIEVAL-RECOVERY-HOTFIX`

Scoring/data compatibility key:

> `v7.4.5-P2C-FREEZE`

Repository documentation at that checkpoint listed Phase 2E.3 as the next Core Scanner milestone.

## `v7.8.1-RETRIEVAL-RECOVERY-HOTFIX` — ACCEPTED & FROZEN

- Yahoo/yfinance remains primary
- strengthened ticker-history recovery
- retained Stooq fallback
- protected durable last-good scanner snapshots
- failed/empty fresh retrieval must not overwrite valid durable state
- scoring/data compatibility remains `v7.4.5-P2C-FREEZE`

## `v7.8.0-P2E2-DECISION-FIRST-UX` — ACCEPTED

- Candidate Quality first
- Entry Quality separated visibly
- Action surfaced prominently
- Price Data Confidence visible
- technical evidence below decision layer
