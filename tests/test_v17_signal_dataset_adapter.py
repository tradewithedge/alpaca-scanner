import pandas as pd
import pytest

from scanner.v17_signal_dataset_adapter import (
    ADAPTER_OUTPUT_COLUMNS,
    combine_v13f_captures,
    normalize_v13f_capture,
    validate_v13f_capture_schema,
)


def _capture():
    return pd.DataFrame([
        {
            "capture_id": "BATCH1_ABC",
            "signal_timestamp_utc": "2026-09-16T19:00:00Z",
            "universe": "S&P 500",
            "symbol": "abc",
            "official_bucket": "A-QUALITY — WAIT",
            "trade_quality_state": "TRADE-QUALITY ELIGIBLE",
            "trade_quality_eligible": True,
            "official_candidate_quality": 94,
            "official_entry_quality": 61,
            "official_setup": "CONFIRMED BREAKOUT",
            "official_decision": "WAIT",
            "decision_state": "WATCH",
            "decision_reason": "wait for trigger",
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
            "trigger_timestamp_utc": "",
            "fill_status": "UNRECORDED",
            "fill_timestamp_utc": "",
            "fill_price": "",
            "slippage_pct": "",
            "invalidation_timestamp_utc": "",
            "invalidation_reason": "",
            "mae_pct": "",
            "mfe_pct": "",
            "exit_timestamp_utc": "",
            "exit_price": "",
            "realized_r": "",
            "missed_opportunity_r": "",
            "notes": "prospective",
        }
    ])


def test_schema_matches_v13f_capture_columns():
    result = validate_v13f_capture_schema(_capture())
    assert result["schema_valid"] is True


def test_normalization_preserves_frozen_fields_and_outcome_blanks():
    src = _capture()
    out = normalize_v13f_capture(src)
    assert list(out.columns) == ADAPTER_OUTPUT_COLUMNS
    assert out.loc[0, "symbol"] == "ABC"
    assert out.loc[0, "official_bucket"] == src.loc[0, "official_bucket"]
    assert out.loc[0, "official_setup"] == src.loc[0, "official_setup"]
    assert out.loc[0, "fill_status"] == "UNRECORDED"
    assert out.loc[0, "fill_price"] != out.loc[0, "fill_price"]  # NaN after numeric normalization
    assert out.loc[0, "realized_r"] != out.loc[0, "realized_r"]
    assert out.loc[0, "outcome_state_normalized"] == "UNRECORDED"
    assert bool(out.loc[0, "outcome_recorded"]) is False


def test_no_outcome_is_fabricated_from_price():
    src = _capture()
    src.loc[0, "current_price_at_capture"] = 999
    src.loc[0, "max_acceptable_fill"] = 100
    out = normalize_v13f_capture(src)
    assert out.loc[0, "fill_status"] == "UNRECORDED"
    assert out.loc[0, "outcome_state_normalized"] == "UNRECORDED"


def test_explicit_no_fill_is_preserved_as_recorded_source_status():
    src = _capture()
    src.loc[0, "fill_status"] = "NO_FILL"
    out = normalize_v13f_capture(src)
    assert out.loc[0, "fill_status"] == "NO_FILL"
    assert out.loc[0, "outcome_state_normalized"] == "NO_FILL_RECORDED"
    assert bool(out.loc[0, "outcome_recorded"]) is True


def test_incomplete_filled_outcome_is_not_treated_as_realized():
    src = _capture()
    src.loc[0, "fill_status"] = "FILLED"
    src.loc[0, "fill_price"] = 101
    out = normalize_v13f_capture(src)
    assert out.loc[0, "outcome_state_normalized"] == "FILLED_OUTCOME_INCOMPLETE"


def test_duplicate_capture_id_fails():
    src = pd.concat([_capture(), _capture()], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate capture_id"):
        validate_v13f_capture_schema(src)


def test_invalid_signal_timestamp_fails():
    src = _capture()
    src.loc[0, "signal_timestamp_utc"] = "bad"
    with pytest.raises(ValueError, match="invalid signal timestamps"):
        validate_v13f_capture_schema(src)


def test_combine_preserves_distinct_signal_keys():
    a = _capture()
    b = _capture()
    b.loc[0, "capture_id"] = "BATCH2_ABC"
    b.loc[0, "signal_timestamp_utc"] = "2026-09-17T19:00:00Z"
    out = combine_v13f_captures([a, b])
    assert len(out) == 2
    assert out["signal_key"].is_unique
    assert out["capture_id"].is_unique


def test_source_fingerprint_is_deterministic():
    a = normalize_v13f_capture(_capture())
    b = normalize_v13f_capture(_capture())
    assert a.loc[0, "source_row_fingerprint"] == b.loc[0, "source_row_fingerprint"]


def test_source_mutation_changes_fingerprint_but_not_signal_key():
    a = _capture()
    b = _capture()
    b.loc[0, "notes"] = "changed note only"
    na = normalize_v13f_capture(a)
    nb = normalize_v13f_capture(b)
    assert na.loc[0, "signal_key"] == nb.loc[0, "signal_key"]
    assert na.loc[0, "source_row_fingerprint"] != nb.loc[0, "source_row_fingerprint"]
