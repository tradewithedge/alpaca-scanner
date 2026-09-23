from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd


V13F_REQUIRED_COLUMNS = [
    "capture_id",
    "signal_timestamp_utc",
    "universe",
    "symbol",
    "official_bucket",
    "trade_quality_state",
    "trade_quality_eligible",
    "official_candidate_quality",
    "official_entry_quality",
    "official_setup",
    "official_decision",
    "decision_state",
    "decision_reason",
    "plan_state",
    "plan_data_confidence",
    "current_price_at_capture",
    "trigger_price",
    "entry_zone_low",
    "entry_zone_high",
    "max_acceptable_fill",
    "max_fill_rr",
    "stage_a_status",
    "stage_a_reference",
    "stage_b_status",
    "stage_b_reference",
    "stage_c_status",
    "stage_c_reference",
    "capture_event",
    "trigger_timestamp_utc",
    "fill_status",
    "fill_timestamp_utc",
    "fill_price",
    "slippage_pct",
    "invalidation_timestamp_utc",
    "invalidation_reason",
    "mae_pct",
    "mfe_pct",
    "exit_timestamp_utc",
    "exit_price",
    "realized_r",
    "missed_opportunity_r",
    "notes",
]

ADAPTER_OUTPUT_COLUMNS = [
    *V13F_REQUIRED_COLUMNS,
    "dataset_role",
    "signal_key",
    "signal_timestamp_parsed",
    "outcome_state_normalized",
    "outcome_recorded",
    "source_row_fingerprint",
]

NUMERIC_COLUMNS = [
    "official_candidate_quality",
    "official_entry_quality",
    "current_price_at_capture",
    "trigger_price",
    "entry_zone_low",
    "entry_zone_high",
    "max_acceptable_fill",
    "max_fill_rr",
    "fill_price",
    "slippage_pct",
    "mae_pct",
    "mfe_pct",
    "exit_price",
    "realized_r",
    "missed_opportunity_r",
]

OUTCOME_COLUMNS = [
    "trigger_timestamp_utc",
    "fill_status",
    "fill_timestamp_utc",
    "fill_price",
    "slippage_pct",
    "invalidation_timestamp_utc",
    "invalidation_reason",
    "mae_pct",
    "mfe_pct",
    "exit_timestamp_utc",
    "exit_price",
    "realized_r",
    "missed_opportunity_r",
]


def _text(value: object) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def _fingerprint_row(row: Mapping[str, object]) -> str:
    payload = "|".join(f"{c}={_text(row.get(c))}" for c in V13F_REQUIRED_COLUMNS)
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def _load_source(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"capture file not found: {path}")
    return pd.read_csv(path)


def validate_v13f_capture_schema(source: str | Path | pd.DataFrame) -> dict:
    """Validate that a prospective V1.3f capture has the required fields.

    Validation never fills missing outcome values from prices. Outcome fields are
    expected to remain blank/UNRECORDED until genuine execution evidence exists.
    """
    frame = _load_source(source)
    missing = [c for c in V13F_REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"V1.3f capture missing required columns: {missing}")

    if frame["capture_id"].astype(str).duplicated().any():
        raise ValueError("V1.3f capture contains duplicate capture_id values")

    timestamps = pd.to_datetime(frame["signal_timestamp_utc"], utc=True, errors="coerce")
    if timestamps.isna().any():
        raise ValueError("V1.3f capture contains invalid signal timestamps")

    symbols = frame["symbol"].map(_text).str.upper()
    if symbols.eq("").any():
        raise ValueError("V1.3f capture contains blank symbols")

    return {
        "rows": int(len(frame)),
        "symbols": int(symbols.nunique()),
        "duplicates": 0,
        "schema_valid": True,
    }


def _normalize_outcome_state(row: pd.Series) -> tuple[str, bool]:
    fill_status = _text(row.get("fill_status")).upper()
    exit_price = _text(row.get("exit_price"))
    realized_r = _text(row.get("realized_r"))

    if fill_status in {"", "UNRECORDED", "NONE", "NAN"}:
        return "UNRECORDED", False

    if fill_status == "NO_FILL":
        # No-fill status can be genuine evidence only when the source explicitly
        # recorded it. Do not infer a no-fill from blank prices or current market data.
        return "NO_FILL_RECORDED", bool(_text(row.get("capture_event")))

    if fill_status == "FILLED":
        return ("FILLED_OUTCOME_RECORDED" if exit_price != "" and realized_r != "" else "FILLED_OUTCOME_INCOMPLETE"), True

    return "SOURCE_STATUS_UNRECOGNIZED", True


def normalize_v13f_capture(
    source: str | Path | pd.DataFrame,
    *,
    dataset_role: str = "FORWARD_TEST_PROSPECTIVE",
) -> pd.DataFrame:
    """Normalize a V1.3f capture into the V1.7 signal-dataset contract.

    The adapter is intentionally conservative: it preserves source outcome values,
    marks blank outcome fields as UNRECORDED, and never derives fills/exits/results
    from prices. It also leaves frozen scanner decision fields untouched.
    """
    validate_v13f_capture_schema(source)
    frame = _load_source(source)
    frame = frame[V13F_REQUIRED_COLUMNS].copy(deep=True)

    frame["symbol"] = frame["symbol"].map(_text).str.upper()
    frame["signal_timestamp_parsed"] = pd.to_datetime(frame["signal_timestamp_utc"], utc=True, errors="raise")

    # Normalize explicit booleans without changing their meaning.
    frame["trade_quality_eligible"] = frame["trade_quality_eligible"].map(
        lambda v: bool(v) if isinstance(v, bool) else _text(v).lower() in {"true", "1", "yes"}
    )

    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    # Blank V1.3f outcome fields remain blank at source level. A derived state is
    # added separately so the adapter does not mutate the source semantics.
    normalized = frame.apply(_normalize_outcome_state, axis=1)
    frame["outcome_state_normalized"] = [item[0] for item in normalized]
    frame["outcome_recorded"] = [item[1] for item in normalized]

    frame["dataset_role"] = str(dataset_role)
    frame["signal_key"] = frame.apply(
        lambda row: f"{row['universe']}|{row['symbol']}|{row['signal_timestamp_parsed'].isoformat()}",
        axis=1,
    )
    frame["source_row_fingerprint"] = frame.apply(_fingerprint_row, axis=1)

    return frame.reindex(columns=ADAPTER_OUTPUT_COLUMNS)


def load_v13f_capture_csv(path: str | Path) -> pd.DataFrame:
    """Load and normalize one preserved V1.3f capture CSV."""
    return normalize_v13f_capture(path)


def combine_v13f_captures(
    sources: Iterable[str | Path | pd.DataFrame],
) -> pd.DataFrame:
    """Combine multiple V1.3f captures with deterministic duplicate protection."""
    normalized = [normalize_v13f_capture(source) for source in sources]
    if not normalized:
        return pd.DataFrame(columns=ADAPTER_OUTPUT_COLUMNS)

    combined = pd.concat(normalized, ignore_index=True)
    if combined["capture_id"].duplicated().any():
        raise ValueError("combined V1.3f captures contain duplicate capture_id values")
    if combined["signal_key"].duplicated().any():
        raise ValueError("combined V1.3f captures contain duplicate signal_key values")

    return combined.sort_values(["signal_timestamp_parsed", "symbol"]).reset_index(drop=True)


__all__ = [
    "ADAPTER_OUTPUT_COLUMNS",
    "OUTCOME_COLUMNS",
    "V13F_REQUIRED_COLUMNS",
    "combine_v13f_captures",
    "load_v13f_capture_csv",
    "normalize_v13f_capture",
    "validate_v13f_capture_schema",
]
