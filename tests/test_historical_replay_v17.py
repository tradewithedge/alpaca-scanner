import pandas as pd
import pytest

from scanner.historical_replay import (
    ReplayIntegrityError,
    build_replay_slice,
    replay_signal,
)


def _bars():
    return pd.DataFrame([
        {"symbol": "ABC", "timestamp": "2026-01-02T00:00:00Z", "open": 99, "high": 101, "low": 98, "close": 100},
        {"symbol": "ABC", "timestamp": "2026-01-05T00:00:00Z", "open": 100, "high": 103, "low": 99, "close": 102},
        {"symbol": "ABC", "timestamp": "2026-01-06T00:00:00Z", "open": 102, "high": 108, "low": 101, "close": 107},
        {"symbol": "ABC", "timestamp": "2026-01-07T00:00:00Z", "open": 107, "high": 109, "low": 106, "close": 108},
    ])


def test_asof_slice_excludes_future_bars():
    replay = build_replay_slice(
        symbol="ABC",
        signal_timestamp_utc="2026-01-05T00:00:00Z",
        bars=_bars(),
    )
    assert len(replay.asof_bars) == 2
    assert len(replay.future_bars) == 2
    assert replay.asof_bars["timestamp"].max() == pd.Timestamp("2026-01-05", tz="UTC")
    assert replay.future_bars["timestamp"].min() == pd.Timestamp("2026-01-06", tz="UTC")


def test_lookback_is_applied_after_asof_filter():
    replay = build_replay_slice(
        symbol="ABC",
        signal_timestamp_utc="2026-01-06T00:00:00Z",
        bars=_bars(),
        lookback_bars=2,
    )
    assert replay.asof_bars["timestamp"].tolist() == [
        pd.Timestamp("2026-01-05", tz="UTC"),
        pd.Timestamp("2026-01-06", tz="UTC"),
    ]


def test_future_bar_mutation_cannot_change_signal_time_result():
    bars = _bars()
    altered = bars.copy(deep=True)
    altered.loc[altered["timestamp"] == "2026-01-06T00:00:00Z", "high"] = 999
    altered.loc[altered["timestamp"] == "2026-01-07T00:00:00Z", "close"] = 777

    def evaluator(asof_bars, future_bars, signal_ts):
        return {
            "last_close": float(asof_bars.iloc[-1]["close"]),
            "asof_rows": int(len(asof_bars)),
            "signal_ts": signal_ts.isoformat(),
        }

    a = replay_signal(
        symbol="ABC",
        signal_timestamp_utc="2026-01-05T00:00:00Z",
        bars=bars,
        evaluator=evaluator,
    )
    b = replay_signal(
        symbol="ABC",
        signal_timestamp_utc="2026-01-05T00:00:00Z",
        bars=altered,
        evaluator=evaluator,
    )
    assert a.result == b.result
    assert a.source_fingerprint != b.source_fingerprint


def test_duplicate_timestamps_fail():
    bars = _bars().copy()
    bars.loc[len(bars)] = bars.iloc[1].to_dict()
    with pytest.raises(ReplayIntegrityError, match="duplicate timestamps"):
        build_replay_slice(
            symbol="ABC",
            signal_timestamp_utc="2026-01-05T00:00:00Z",
            bars=bars,
        )


def test_missing_asof_bar_fails():
    bars = _bars().loc[_bars()["timestamp"] > "2026-01-05T00:00:00Z"].copy()
    with pytest.raises(ReplayIntegrityError, match="no as-of bar"):
        build_replay_slice(
            symbol="ABC",
            signal_timestamp_utc="2026-01-05T00:00:00Z",
            bars=bars,
        )


def test_non_numeric_ohlc_fails():
    bars = _bars().copy()
    bars["high"] = bars["high"].astype(object)
    bars.loc[1, "high"] = "not-a-number"
    with pytest.raises(ReplayIntegrityError, match="non-numeric OHLC"):
        build_replay_slice(
            symbol="ABC",
            signal_timestamp_utc="2026-01-05T00:00:00Z",
            bars=bars,
        )


def test_signal_timestamp_itself_is_not_treated_as_future():
    replay = build_replay_slice(
        symbol="ABC",
        signal_timestamp_utc="2026-01-06T00:00:00Z",
        bars=_bars(),
    )
    assert replay.asof_bars["timestamp"].max() == pd.Timestamp("2026-01-06", tz="UTC")
    assert replay.future_bars["timestamp"].min() == pd.Timestamp("2026-01-07", tz="UTC")
