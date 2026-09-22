import pandas as pd

from scanner.backtest_engine import (
    BACKTEST_OUTCOME_COLUMNS,
    BacktestConfig,
    evaluate_signal,
    evaluate_signals,
    summarize_outcomes,
)


def _bars(rows):
    return pd.DataFrame(rows)


def _signal(**overrides):
    row = {
        "symbol": "ABC",
        "signal_timestamp_utc": "2026-01-05T00:00:00Z",
        "trigger_price": 101.0,
        "entry_zone_low": 101.0,
        "entry_zone_high": 101.5,
        "max_acceptable_fill": 102.0,
        "stop_price": 99.0,
        "t1_price": 104.0,
        "t2_price": 105.0,
    }
    row.update(overrides)
    return pd.Series(row)


def test_target2_path_is_deterministic():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 100.5, "high": 101.2, "low": 100.2, "close": 101.0},
        {"timestamp": "2026-01-07T00:00:00Z", "open": 101.0, "high": 105.0, "low": 100.8, "close": 104.5},
    ])
    a = evaluate_signal(_signal(), bars)
    b = evaluate_signal(_signal(), bars)
    assert a.to_dict() == b.to_dict()
    assert a.outcome_state == "FILLED_TARGET2"
    assert a.fill_price == 101.0
    assert a.realized_r == 2.0
    assert a.audit_no_lookahead is True
    assert a.audit_deterministic is True


def test_signal_bar_is_excluded_from_evaluation():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 110, "low": 95, "close": 109},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
    ])
    out = evaluate_signal(_signal(), bars)
    assert out.outcome_state == "TRIGGER_NOT_REACHED"


def test_same_bar_stop_and_target_uses_conservative_stop_priority():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 101.2, "high": 105.5, "low": 98.5, "close": 101},
    ])
    out = evaluate_signal(_signal(), bars)
    assert out.outcome_state == "FILLED_STOP"
    assert out.exit_reason == "STOP_AND_TARGET_SAME_BAR"
    assert out.realized_r == -1.0


def test_gap_above_max_fill_is_no_fill():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 103, "high": 106, "low": 102.5, "close": 105},
    ])
    out = evaluate_signal(_signal(), bars)
    assert out.outcome_state == "NO_FILL_GAP_ABOVE_MAX"
    assert out.fill_status == "NO_FILL"
    assert out.fill_price is None


def test_invalidation_before_trigger():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 100, "high": 100.5, "low": 98.9, "close": 99},
    ])
    out = evaluate_signal(_signal(), bars)
    assert out.outcome_state == "INVALIDATED_BEFORE_TRIGGER"
    assert out.fill_status == "NO_FILL"
    assert out.invalidation_timestamp_utc.endswith("00:00:00+00:00")


def test_timeout_exits_at_horizon_close():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.2, "low": 99.8, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 100.5, "high": 101.2, "low": 100.4, "close": 101.0},
        {"timestamp": "2026-01-07T00:00:00Z", "open": 101.0, "high": 103.0, "low": 100.8, "close": 103.0},
    ])
    out = evaluate_signal(_signal(), bars, config=BacktestConfig(horizon_bars=2))
    assert out.outcome_state == "TIMEOUT"
    assert out.exit_reason == "TIMEOUT"
    assert out.exit_price == 103.0


def test_outcome_schema_and_batch_summary():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 101, "high": 105, "low": 100.5, "close": 104},
    ])
    signals = pd.DataFrame([_signal()])
    result = evaluate_signals(signals, {"ABC": bars})
    assert list(result.columns) == BACKTEST_OUTCOME_COLUMNS
    summary = summarize_outcomes(result)
    assert summary["signals"] == 1
    assert summary["filled"] == 1
    assert summary["target2"] == 1


def test_commission_reduces_net_r():
    bars = _bars([
        {"timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 100.5, "low": 99.5, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 101, "high": 105, "low": 100.5, "close": 104},
    ])
    out = evaluate_signal(
        _signal(),
        bars,
        config=BacktestConfig(commission_per_side_cash=1.0, position_size=1.0),
    )
    assert out.realized_r == 2.0
    assert out.net_realized_r == 1.0


def test_duplicate_timestamps_are_rejected():
    bars = _bars([
        {"timestamp": "2026-01-06T00:00:00Z", "open": 100, "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-01-06T00:00:00Z", "open": 100, "high": 102, "low": 99, "close": 101},
    ])
    try:
        evaluate_signal(_signal(), bars)
    except ValueError as exc:
        assert "duplicate timestamps" in str(exc)
    else:
        raise AssertionError("duplicate timestamps must fail")
