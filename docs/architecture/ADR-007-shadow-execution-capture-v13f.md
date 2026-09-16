# ADR-007 — V1.3f Shadow Execution-Capture Logging

**Status:** **ACCEPTED / FROZEN (SHADOW)**  
**Date:** 16 September 2026

## Decision
Introduce and freeze a manual, prospective execution-capture log that records the scanner state available at signal time. The layer is diagnostic infrastructure for future Forward-Test and Expectancy work; it is not an execution engine.

## Context
V1.3e separates EXECUTION READY from trade-quality eligibility. The next failure mode is execution capture: a valid signal can be identified but not captured, while later hindsight can make the missed opportunity look obvious. V1.3f therefore records the signal before its outcome is known.

## Design
- `scanner/execution_capture.py` owns the schema and snapshot construction.
- The UI provides a manual **Capture this scan** action.
- Capture IDs are deterministic by scan batch and symbol, preventing repeated-click duplicates.
- Signal-time fields are populated from V1.3e/V1.3c/V1.3d; outcome fields remain `UNRECORDED` until independently observed.
- A/B/C staged-execution references use **30% Starter / 30% Add / 40% Full Trigger** only as shadow preparation, not as production sizing.
- Captures are stored in Streamlit session state and can be downloaded as CSV; durable storage is deferred.
- Current-scan metrics are explicitly separated from cumulative session-capture metrics in the UI so a selected-universe count cannot be confused with the cross-universe session total.

## Integrity boundaries
V1.3f must not mutate the official scored frame or alter Candidate Quality, F15 Composite, Entry Quality, ranking, buckets, event gates, legacy trade-plan fields or broker execution.

A non-trade-quality-eligible candidate must not receive an active A/B/C staged plan. No fill, slippage, MAE/MFE, exit or realized-R outcome may be inferred from price movement alone.

## Validation
Offline validation before deployment: **31/31 PASS** across the V1.3e focused tests plus V1.3f module/integration tests; `py_compile` PASS; official scoring input-isolation check PASS.

Live deployed validation after UI-scope refinement:

- S&P 500 current scan: **123 signal rows / 79 quality-eligible / 5 EXECUTION READY / 0 outcomes recorded**.
- Russell 2000 current scan: **88 signal rows / 55 quality-eligible / 1 EXECUTION READY / 0 outcomes recorded**.
- After capturing both scans, cumulative session log: **211 captured rows / 134 quality-eligible / 6 EXECUTION READY / 0 outcomes recorded**.
- The cumulative reconciliation is exact: **123 + 88 = 211**, **79 + 55 = 134**, and **5 + 1 = 6**.
- Repeated capture did not create duplicate capture IDs in the supplied forward-test datasets.
- Captured outcome fields remained explicitly unrecorded; no realized result was fabricated.
- The UI correctly distinguishes **CURRENT SCAN — selected universe** from **SESSION CAPTURE LOG — cumulative across captured universes**.

## Acceptance
The V1.3f acceptance target was satisfied: module/integration validation passed, the deployed shadow workflow was exercised on both S&P 500 and Russell 2000, and prospective capture/download evidence was supplied for both universes.

**Decision:** **V1.3f ACCEPTED / FROZEN (SHADOW).**

## Consequences
The project can now accumulate prospective signal/outcome evidence without reconstructing signal state from hindsight. The frozen V1.3f architecture remains diagnostic and does not authorize production order placement or production position sizing.

V1.7 remains responsible for Backtest, Forward-Test, expectancy, transaction costs, slippage and missed-opportunity validation. Outcome collection may continue without changing the frozen scanner architecture.

## Known limitations
- The current capture store is session-state based; durable persistence is deferred.
- The A/B/C 30/30/40 structure is a research-preparation reference and has not been expectancy-proven.
- The present evidence proves capture integrity and prospective logging behavior, not trading profitability or expectancy.
