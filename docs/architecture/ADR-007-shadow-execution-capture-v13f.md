# ADR-007 — V1.3f Shadow Execution-Capture Logging

**Status:** IN DEVELOPMENT / SHADOW
**Date:** 16 September 2026

## Decision
Introduce a manual, prospective execution-capture log that records the scanner state available at signal time. The layer is diagnostic infrastructure for future Forward-Test and Expectancy work; it is not an execution engine.

## Context
V1.3e separates EXECUTION READY from trade-quality eligibility. The next failure mode is execution capture: a valid signal can be identified but not captured, while later hindsight can make the missed opportunity look obvious. V1.3f therefore records the signal before its outcome is known.

## Design
- `scanner/execution_capture.py` owns the schema and snapshot construction.
- The UI provides a manual **Capture this scan** action.
- Capture IDs are deterministic by scan batch and symbol, preventing repeated-click duplicates.
- Signal-time fields are populated from V1.3e/V1.3c/V1.3d; outcome fields remain `UNRECORDED`.
- A/B/C staged-execution references use 30/30/40 only as shadow preparation, not as production sizing.
- Captures are stored in Streamlit session state and can be downloaded as CSV; durable storage is deferred.

## Integrity boundaries
V1.3f must not mutate the official scored frame or alter Candidate Quality, F15 Composite, Entry Quality, ranking, buckets, event gates, legacy trade-plan fields or broker execution.

## Validation
Offline validation: 10 original V1.3f module tests + 4 V1.3f app integration tests + 1 explicit input-isolation test, together with the existing 16 V1.3e focused tests = **31/31 PASS**; `py_compile` PASS.

## Consequences
The project can begin accumulating prospective signal/outcome evidence without reconstructing it from hindsight. V1.7 remains responsible for Backtest, Forward-Test, expectancy, transaction costs, slippage and missed-opportunity validation.
