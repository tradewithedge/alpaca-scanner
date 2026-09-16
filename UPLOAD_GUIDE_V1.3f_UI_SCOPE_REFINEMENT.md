# Upload Guide — V1.3f UI Scope Refinement

## Files to upload to GitHub `main`

1. `app.py` → replace existing `app.py`
2. `tests/test_execution_capture_app_integration_v13f.py` → replace existing test file
3. `V1.3F_UI_SCOPE_REFINEMENT_REPORT.md` → add at repository root
4. `UPLOAD_GUIDE_V1.3f_UI_SCOPE_REFINEMENT.md` → add at repository root

Do not replace `scanner/execution_capture.py`; this refinement is UI-only.

## Exact Git commit message

`V1.3f UI refinement: separate current-scan and session-capture metrics`

## Validation completed before upload

- 17/17 V1.3f tests PASS
- Python compile PASS

## After upload

Run the deployed scanner once for S&P 500 and once for Russell 2000.

Expected behavior:

- The **CURRENT SCAN — selected universe** metrics change with the selected universe.
- The **SESSION CAPTURE LOG — cumulative across captured universes** metrics retain the cumulative session totals.
- The dashboard explicitly states that the two scopes must not be interpreted as the same population.

Do not formally freeze V1.3f from this UI change alone; continue prospective forward-test capture first.
