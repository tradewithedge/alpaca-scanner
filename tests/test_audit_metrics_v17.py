import pandas as pd

from scanner.audit_metrics import segment_audit_metrics, summarize_audit_metrics


def _outcomes():
    return pd.DataFrame([
        {
            "symbol": "AAA", "outcome_state": "FILLED_TARGET2", "fill_status": "FILLED",
            "trigger_timestamp_utc": "2026-01-06T00:00:00+00:00", "realized_r": 2.0,
            "net_realized_r": 1.9, "missed_opportunity_r": 0.0, "mae_r": -0.2,
            "mfe_r": 2.1, "fill_slippage_r": 0.1, "commission_cash": 0.2,
            "audit_no_lookahead": True, "audit_timestamps_strict": True, "audit_deterministic": True,
            "setup": "BREAKOUT",
        },
        {
            "symbol": "BBB", "outcome_state": "FILLED_STOP", "fill_status": "FILLED",
            "trigger_timestamp_utc": "2026-01-06T00:00:00+00:00", "realized_r": -1.0,
            "net_realized_r": -1.1, "missed_opportunity_r": 0.0, "mae_r": -1.0,
            "mfe_r": 0.3, "fill_slippage_r": 0.0, "commission_cash": 0.2,
            "audit_no_lookahead": True, "audit_timestamps_strict": True, "audit_deterministic": True,
            "setup": "PULLBACK",
        },
        {
            "symbol": "CCC", "outcome_state": "NO_FILL_GAP_ABOVE_MAX", "fill_status": "NO_FILL",
            "trigger_timestamp_utc": "2026-01-06T00:00:00+00:00", "realized_r": None,
            "net_realized_r": None, "missed_opportunity_r": 1.5, "mae_r": None,
            "mfe_r": None, "fill_slippage_r": None, "commission_cash": 0.0,
            "audit_no_lookahead": True, "audit_timestamps_strict": True, "audit_deterministic": True,
            "setup": "BREAKOUT",
        },
    ])


def test_core_metrics_are_descriptive_and_deterministic():
    summary = summarize_audit_metrics(_outcomes())
    assert summary["signals"] == 3
    assert summary["triggered"] == 3
    assert summary["filled"] == 2
    assert summary["realized"] == 2
    assert summary["missed"] == 1
    assert summary["entry_rate_pct"] == 100.0
    assert summary["capture_rate_pct"] == 100.0 * 2 / 3
    assert summary["realization_rate_pct"] == 100.0
    assert abs(summary["mean_net_realized_r"] - 0.4) < 1e-12
    assert abs(summary["signal_expectancy_r"] - (0.8 / 3)) < 1e-12
    assert summary["total_missed_opportunity_r"] == 1.5
    assert summary["win_rate_pct"] == 50.0
    assert summary["max_drawdown_r"] == -1.1
    assert summary["audit_all_no_lookahead"] is True


def test_empty_inputs_are_stable():
    summary = summarize_audit_metrics(pd.DataFrame())
    assert summary["signals"] == 0
    assert summary["signal_expectancy_r"] == 0.0


def test_segmentation_preserves_groups():
    segmented = segment_audit_metrics(_outcomes(), "setup")
    assert set(segmented["setup"]) == {"BREAKOUT", "PULLBACK"}
    breakout = segmented.loc[segmented["setup"] == "BREAKOUT"].iloc[0]
    assert breakout["signals"] == 2
    assert breakout["filled"] == 1
    assert breakout["missed"] == 1


def test_missing_required_column_fails_visibly():
    bad = _outcomes().drop(columns=["net_realized_r"])
    try:
        summarize_audit_metrics(bad)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("missing required column must fail")
