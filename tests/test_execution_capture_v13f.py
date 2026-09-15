import pandas as pd

from scanner.execution_capture import (
    EXECUTION_CAPTURE_COLUMNS,
    append_execution_capture,
    build_execution_capture_log,
    summarize_execution_capture,
)


def _decision(rows=None):
    rows = rows or [
        {
            "symbol": "ABC", "official_bucket": "A-QUALITY — WAIT",
            "trade_quality_state": "TRADE-QUALITY ELIGIBLE", "trade_quality_eligible": True,
            "official_candidate_quality": 95.0, "official_entry_quality": 60.0,
            "official_setup": "EMA20 PULLBACK", "official_decision": "WAIT",
            "decision_state": "WATCH", "decision_reason": "wait",
            "plan_state": "WAITING FOR TRIGGER", "plan_data_confidence": "HIGH",
            "current_price": 100.0, "trigger_price": 101.0, "entry_zone_low": 100.0,
            "entry_zone_high": 101.5, "max_acceptable_fill": 102.0, "max_fill_rr": 2.0,
        }
    ]
    return pd.DataFrame(rows)


def test_schema_is_stable():
    out = build_execution_capture_log(_decision(), universe="S&P 500")
    assert list(out.columns) == EXECUTION_CAPTURE_COLUMNS
    assert len(out) == 1


def test_signal_fields_are_prospective_and_outcomes_blank():
    out = build_execution_capture_log(_decision(), universe="S&P 500")
    row = out.iloc[0]
    assert row["capture_event"] == "SIGNAL OBSERVED"
    assert row["fill_status"] == "UNRECORDED"
    assert row["fill_price"] == ""
    assert row["realized_r"] == ""
    assert row["missed_opportunity_r"] == ""


def test_quality_ineligible_has_no_staged_execution_plan():
    d = _decision()
    d.loc[0, "official_bucket"] = "DEVELOPING"
    d.loc[0, "trade_quality_state"] = "NOT TRADE-QUALITY ELIGIBLE"
    d.loc[0, "trade_quality_eligible"] = False
    out = build_execution_capture_log(d)
    row = out.iloc[0]
    assert row["stage_a_status"] == "NOT ELIGIBLE"
    assert row["stage_b_status"] == "NOT ELIGIBLE"
    assert row["stage_c_status"] == "NOT ELIGIBLE"


def test_watch_quality_candidate_waits_for_trigger():
    out = build_execution_capture_log(_decision())
    row = out.iloc[0]
    assert row["stage_a_status"] == "WAIT"
    assert row["stage_b_status"] == "WAIT"
    assert row["stage_c_status"] == "WAIT"
    assert "trigger" in row["stage_a_reference"].lower()


def test_execution_ready_uses_30_30_40_shadow_references():
    d = _decision()
    d.loc[0, "decision_state"] = "EXECUTION READY"
    d.loc[0, "plan_state"] = "TRIGGERED — IN ENTRY ZONE"
    out = build_execution_capture_log(d)
    row = out.iloc[0]
    assert row["stage_a_status"] == "READY TO PLAN"
    assert "30%" in row["stage_a_reference"]
    assert "30%" in row["stage_b_reference"]
    assert "40%" in row["stage_c_reference"]


def test_append_deduplicates_capture_ids():
    snapshot = build_execution_capture_log(_decision(), capture_batch_id="BATCH1")
    combined = append_execution_capture(snapshot, snapshot.copy())
    assert len(combined) == 1


def test_append_preserves_distinct_batches():
    a = build_execution_capture_log(_decision(), capture_batch_id="BATCH1")
    b = build_execution_capture_log(_decision(), capture_batch_id="BATCH2")
    combined = append_execution_capture(a, b)
    assert len(combined) == 2


def test_summary_counts_quality_and_state():
    d = _decision()
    d.loc[0, "decision_state"] = "EXECUTION READY"
    log = build_execution_capture_log(d)
    summary = summarize_execution_capture(log)
    assert summary["rows"] == 1
    assert summary["symbols"] == 1
    assert summary["eligible"] == 1
    assert summary["execution_ready"] == 1
    assert summary["outcome_recorded"] == 0


def test_empty_input_returns_stable_schema():
    out = build_execution_capture_log(pd.DataFrame())
    assert list(out.columns) == EXECUTION_CAPTURE_COLUMNS
    assert out.empty


def test_capture_batch_id_is_deterministic_for_same_scan():
    a = build_execution_capture_log(_decision(), capture_batch_id="SAME")
    b = build_execution_capture_log(_decision(), capture_batch_id="SAME")
    assert a.loc[0, "capture_id"] == b.loc[0, "capture_id"]


def test_capture_does_not_mutate_decision_input():
    decision = _decision()
    before = decision.copy(deep=True)
    build_execution_capture_log(decision, universe="S&P 500")
    pd.testing.assert_frame_equal(decision, before)
