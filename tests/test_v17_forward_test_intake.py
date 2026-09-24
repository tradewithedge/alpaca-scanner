import pandas as pd
import pytest

from scanner.v17_forward_test_intake import audit_cumulative_capture_delta


def _capture(*, capture_id="B1_ABC", note="prospective", outcome=None):
    fill_status = "UNRECORDED" if outcome is None else "FILLED"
    exit_price = "" if outcome is None else 105
    realized_r = "" if outcome is None else 2
    return pd.DataFrame([{
        "capture_id": capture_id,
        "signal_timestamp_utc": "2026-09-24T12:00:00Z",
        "universe": "S&P 500",
        "symbol": "ABC",
        "official_bucket": "A-QUALITY — WAIT",
        "trade_quality_state": "TRADE-QUALITY ELIGIBLE",
        "trade_quality_eligible": True,
        "official_candidate_quality": 94,
        "official_entry_quality": 61,
        "official_setup": "CONFIRMED BREAKOUT",
        "official_decision": "WAIT",
        "decision_state": "WATCH",
        "decision_reason": "wait",
        "plan_state": "WAITING FOR TRIGGER",
        "plan_data_confidence": "HIGH",
        "current_price_at_capture": 100,
        "trigger_price": 101,
        "entry_zone_low": 101,
        "entry_zone_high": 101.5,
        "max_acceptable_fill": 102,
        "max_fill_rr": 2,
        "stage_a_status": "WAIT",
        "stage_a_reference": "ref",
        "stage_b_status": "WAIT",
        "stage_b_reference": "ref",
        "stage_c_status": "WAIT",
        "stage_c_reference": "ref",
        "capture_event": "SIGNAL OBSERVED",
        "trigger_timestamp_utc": "" if outcome is None else "2026-09-25T14:31:00Z",
        "fill_status": fill_status,
        "fill_timestamp_utc": "" if outcome is None else "2026-09-25T14:31:00Z",
        "fill_price": "" if outcome is None else 101.1,
        "slippage_pct": "" if outcome is None else 0.1,
        "invalidation_timestamp_utc": "",
        "invalidation_reason": "",
        "mae_pct": "" if outcome is None else -0.2,
        "mfe_pct": "" if outcome is None else 4.0,
        "exit_timestamp_utc": "" if outcome is None else "2026-09-30T14:31:00Z",
        "exit_price": exit_price,
        "realized_r": realized_r,
        "missed_opportunity_r": "" if outcome is None else 0,
        "notes": note,
    }])


def test_new_cumulative_row_is_new_signal():
    accepted, audit, report = audit_cumulative_capture_delta(_capture())
    assert len(accepted) == 1
    assert audit.loc[0, "intake_state"] == "NEW_SIGNAL"
    assert report["new_signals"] == 1
    assert report["audit_pass"] is True


def test_unchanged_cumulative_row_does_not_duplicate():
    prior = _capture()
    current = _capture()
    accepted, audit, report = audit_cumulative_capture_delta(current, prior)
    assert len(accepted) == 1
    assert audit.loc[0, "intake_state"] == "UNCHANGED"
    assert report["accepted_rows"] == 1


def test_outcome_update_is_allowed_when_signal_fields_are_immutable():
    prior = _capture()
    current = _capture(outcome="recorded")
    accepted, audit, report = audit_cumulative_capture_delta(current, prior)
    assert len(accepted) == 1
    assert audit.loc[0, "intake_state"] == "OUTCOME_UPDATE"
    assert bool(accepted.loc[0, "outcome_recorded"]) is True
    assert report["outcome_updates"] == 1


def test_signal_time_mutation_is_blocked():
    prior = _capture()
    current = _capture()
    current.loc[0, "trigger_price"] = 999
    accepted, audit, report = audit_cumulative_capture_delta(current, prior)
    assert audit.loc[0, "intake_state"] == "SIGNAL_MUTATION"
    assert report["signal_mutations_blocked"] == 1
    assert report["audit_pass"] is False
    assert float(accepted.loc[0, "trigger_price"]) == 101.0


def test_distinct_capture_ids_append():
    prior = _capture(capture_id="B1_ABC")
    current = pd.concat([prior, _capture(capture_id="B2_DEF")], ignore_index=True)
    current.loc[1, "symbol"] = "DEF"
    accepted, audit, report = audit_cumulative_capture_delta(current, prior)
    assert len(accepted) == 2
    assert set(audit["intake_state"]) == {"UNCHANGED", "NEW_SIGNAL"}
    assert report["new_signals"] == 1


def test_duplicate_capture_id_in_current_source_fails_upstream():
    current = pd.concat([_capture(), _capture()], ignore_index=True)
    # normalize_v13f_capture is called by the intake gate and must reject duplicates.
    with pytest.raises(ValueError, match="duplicate capture_id"):
        audit_cumulative_capture_delta(current)
