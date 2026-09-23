from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from scanner.backtest_engine import BACKTEST_OUTCOME_COLUMNS, BacktestConfig, evaluate_signal
from scanner.historical_replay import ReplayIntegrityError, build_replay_slice


FIXTURE_KIND = "SYNTHETIC_ENGINE_FIXTURE_ONLY"


@dataclass(frozen=True)
class FixtureCase:
    case_id: str
    signal: pd.Series
    bars: pd.DataFrame
    expected_outcome: str
    horizon_bars: int = 20


def _signal(case_id: str, *, timestamp: str = "2026-01-05T00:00:00Z") -> pd.Series:
    return pd.Series(
        {
            "case_id": case_id,
            "symbol": "ABC",
            "signal_timestamp_utc": timestamp,
            "trigger_price": 101.0,
            "entry_zone_low": 101.0,
            "entry_zone_high": 101.5,
            "max_acceptable_fill": 102.0,
            "stop_price": 99.0,
            "t1_price": 104.0,
            "t2_price": 105.0,
        }
    )


def _bars(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def build_synthetic_fixture() -> list[FixtureCase]:
    """Return a small deterministic engineering fixture.

    This fixture is intentionally synthetic. It is suitable for pipeline tests only
    and must never be treated as historical market evidence or expectancy data.
    """
    signal_bar = {
        "symbol": "ABC",
        "timestamp": "2026-01-05T00:00:00Z",
        "open": 100.0,
        "high": 100.5,
        "low": 99.5,
        "close": 100.0,
    }

    return [
        FixtureCase(
            case_id="TARGET2",
            signal=_signal("TARGET2"),
            bars=_bars(
                [
                    signal_bar,
                    {"symbol": "ABC", "timestamp": "2026-01-06T00:00:00Z", "open": 101.0, "high": 101.5, "low": 100.5, "close": 101.2},
                    {"symbol": "ABC", "timestamp": "2026-01-07T00:00:00Z", "open": 101.2, "high": 105.0, "low": 100.9, "close": 104.5},
                ]
            ),
            expected_outcome="FILLED_TARGET2",
        ),
        FixtureCase(
            case_id="STOP",
            signal=_signal("STOP"),
            bars=_bars(
                [
                    signal_bar,
                    {"symbol": "ABC", "timestamp": "2026-01-06T00:00:00Z", "open": 101.0, "high": 102.0, "low": 98.0, "close": 99.0},
                ]
            ),
            expected_outcome="FILLED_STOP",
        ),
        FixtureCase(
            case_id="GAP_ABOVE_MAX",
            signal=_signal("GAP_ABOVE_MAX"),
            bars=_bars(
                [
                    signal_bar,
                    {"symbol": "ABC", "timestamp": "2026-01-06T00:00:00Z", "open": 103.0, "high": 106.0, "low": 102.5, "close": 105.0},
                ]
            ),
            expected_outcome="NO_FILL_GAP_ABOVE_MAX",
        ),
        FixtureCase(
            case_id="INVALIDATED",
            signal=_signal("INVALIDATED"),
            bars=_bars(
                [
                    signal_bar,
                    {"symbol": "ABC", "timestamp": "2026-01-06T00:00:00Z", "open": 100.0, "high": 100.5, "low": 98.5, "close": 99.0},
                ]
            ),
            expected_outcome="INVALIDATED_BEFORE_TRIGGER",
        ),
        FixtureCase(
            case_id="TIMEOUT",
            signal=_signal("TIMEOUT"),
            bars=_bars(
                [
                    signal_bar,
                    {"symbol": "ABC", "timestamp": "2026-01-06T00:00:00Z", "open": 101.0, "high": 102.0, "low": 100.5, "close": 101.5},
                    {"symbol": "ABC", "timestamp": "2026-01-07T00:00:00Z", "open": 101.5, "high": 103.0, "low": 101.0, "close": 102.5},
                ]
            ),
            expected_outcome="TIMEOUT",
            horizon_bars=2,
        ),
    ]


def _evaluate_replayed_case(case: FixtureCase, *, config: BacktestConfig) -> dict:
    replay = build_replay_slice(
        symbol=case.signal["symbol"],
        signal_timestamp_utc=case.signal["signal_timestamp_utc"],
        bars=case.bars,
    )

    # Stage 1 sees only future bars here. The replay harness is responsible for
    # proving that signal-time state and outcome-time bars remain separated.
    outcome = evaluate_signal(case.signal, replay.future_bars, config=config)
    result = outcome.to_dict()
    result.update(
        {
            "case_id": case.case_id,
            "fixture_kind": FIXTURE_KIND,
            "replay_asof_rows": replay.asof_row_count,
            "replay_future_rows": replay.future_row_count,
            "replay_latest_asof_timestamp_utc": replay.latest_asof_timestamp_utc.isoformat(),
            "replay_source_fingerprint": replay.source_fingerprint,
            "fixture_expected_outcome": case.expected_outcome,
        }
    )
    return result


def run_fixture_population(*, commission_per_side_cash: float = 0.0) -> pd.DataFrame:
    """Run the synthetic fixture through Replay -> Stage 1 Outcome Engine."""
    cases = build_synthetic_fixture()
    rows: list[dict] = []
    for case in cases:
        cfg = BacktestConfig(
            horizon_bars=case.horizon_bars,
            commission_per_side_cash=commission_per_side_cash,
            position_size=1.0,
        )
        rows.append(_evaluate_replayed_case(case, config=cfg))

    columns = [
        "case_id",
        "fixture_kind",
        "fixture_expected_outcome",
        "replay_asof_rows",
        "replay_future_rows",
        "replay_latest_asof_timestamp_utc",
        "replay_source_fingerprint",
        *BACKTEST_OUTCOME_COLUMNS,
    ]
    return pd.DataFrame(rows).reindex(columns=columns)


def validate_fixture_population(result: pd.DataFrame) -> dict:
    """Return deterministic engineering assertions without making expectancy claims."""
    if result is None or result.empty:
        raise ReplayIntegrityError("fixture result is empty")

    states_match = bool((result["outcome_state"] == result["fixture_expected_outcome"]).all())
    lookahead_ok = bool(result["audit_no_lookahead"].all())
    timestamp_ok = bool(result["audit_timestamps_strict"].all())
    deterministic_ok = bool(result["audit_deterministic"].all())

    return {
        "fixture_kind": FIXTURE_KIND,
        "cases": int(len(result)),
        "expected_states_match": states_match,
        "audit_no_lookahead_all": lookahead_ok,
        "audit_timestamps_strict_all": timestamp_ok,
        "audit_deterministic_all": deterministic_ok,
        "all_gates_pass": bool(states_match and lookahead_ok and timestamp_ok and deterministic_ok),
        "note": "Synthetic engineering fixture only; not historical market evidence.",
    }


__all__ = [
    "FIXTURE_KIND",
    "FixtureCase",
    "build_synthetic_fixture",
    "run_fixture_population",
    "validate_fixture_population",
]
