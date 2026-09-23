from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from scanner.v17_signal_dataset_adapter import (
    ADAPTER_OUTPUT_COLUMNS,
    combine_v13f_captures,
    normalize_v13f_capture,
)


AUDIT_OUTPUT_COLUMNS = [
    "dataset_role",
    "rows",
    "symbols",
    "universes",
    "date_min_utc",
    "date_max_utc",
    "quality_eligible",
    "unrecorded_outcomes",
    "explicit_no_fill",
    "filled_incomplete",
    "realized_outcomes",
    "duplicate_signal_keys",
    "duplicate_capture_ids",
]


def _sources(source: str | Path | pd.DataFrame | Iterable[str | Path | pd.DataFrame]):
    if isinstance(source, (str, Path, pd.DataFrame)):
        return [source]
    return list(source)


def audit_v13f_forward_test_dataset(
    source: str | Path | pd.DataFrame | Iterable[str | Path | pd.DataFrame],
) -> tuple[pd.DataFrame, dict]:
    """Normalize and audit preserved V1.3f prospective captures.

    This is an intake gate only. It does not infer historical fills, exits,
    realized R, slippage, MAE/MFE, or missed-opportunity R from market prices.
    """
    items = _sources(source)
    if not items:
        empty = pd.DataFrame(columns=ADAPTER_OUTPUT_COLUMNS)
        return empty, {
            "status": "NO_DATA",
            "rows": 0,
            "symbols": 0,
            "universes": 0,
            "realized_outcomes": 0,
            "unrecorded_outcomes": 0,
            "audit_pass": False,
            "note": "No V1.3f capture evidence supplied.",
        }

    frame = combine_v13f_captures(items)
    if frame.empty:
        return frame, {
            "status": "NO_DATA",
            "rows": 0,
            "symbols": 0,
            "universes": 0,
            "realized_outcomes": 0,
            "unrecorded_outcomes": 0,
            "audit_pass": False,
            "note": "Input captures normalized to an empty dataset.",
        }

    timestamps = pd.to_datetime(frame["signal_timestamp_parsed"], utc=True, errors="coerce")
    outcome_state = frame["outcome_state_normalized"].astype(str)
    realized = outcome_state.eq("FILLED_OUTCOME_RECORDED")
    incomplete = outcome_state.eq("FILLED_OUTCOME_INCOMPLETE")
    no_fill = outcome_state.eq("NO_FILL_RECORDED")
    unrecorded = outcome_state.eq("UNRECORDED")

    report = {
        "status": "READY_FOR_OUTCOME_PROCESSING",
        "rows": int(len(frame)),
        "symbols": int(frame["symbol"].nunique()),
        "universes": int(frame["universe"].astype(str).nunique()),
        "date_min_utc": timestamps.min().isoformat() if timestamps.notna().any() else "",
        "date_max_utc": timestamps.max().isoformat() if timestamps.notna().any() else "",
        "quality_eligible": int(frame["trade_quality_eligible"].sum()),
        "unrecorded_outcomes": int(unrecorded.sum()),
        "explicit_no_fill": int(no_fill.sum()),
        "filled_incomplete": int(incomplete.sum()),
        "realized_outcomes": int(realized.sum()),
        "duplicate_signal_keys": int(frame["signal_key"].duplicated().sum()),
        "duplicate_capture_ids": int(frame["capture_id"].duplicated().sum()),
        "audit_pass": bool(
            frame["signal_key"].is_unique
            and frame["capture_id"].is_unique
            and timestamps.notna().all()
        ),
        "note": "Intake/audit only; no outcome is inferred from current market prices.",
    }
    return frame, report


def audit_report_row(report: dict) -> pd.DataFrame:
    return pd.DataFrame([report]).reindex(columns=AUDIT_OUTPUT_COLUMNS)


def load_forward_test_capture_files(paths: Iterable[str | Path]) -> tuple[pd.DataFrame, dict]:
    """Load one or more preserved V1.3f CSV files from disk."""
    files = [Path(p) for p in paths]
    if not files:
        return audit_v13f_forward_test_dataset([])
    return audit_v13f_forward_test_dataset(files)


__all__ = [
    "AUDIT_OUTPUT_COLUMNS",
    "audit_report_row",
    "audit_v13f_forward_test_dataset",
    "load_forward_test_capture_files",
]
