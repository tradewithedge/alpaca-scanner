from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd


EXECUTION_CAPTURE_COLUMNS = [
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

# Shadow-only preparation defaults. These are deliberately not production
# sizing rules and do not connect to any broker execution endpoint.
STAGE_A_PCT = 30
STAGE_B_PCT = 30
STAGE_C_PCT = 40


def _clean(value):
    return value if value is not None else ""


def _stage_plan(row: pd.Series) -> dict:
    eligible = bool(row.get("trade_quality_eligible", False))
    state = str(row.get("decision_state", "")).strip().upper()
    current = row.get("current_price", "")
    zone_low = row.get("entry_zone_low", "")
    zone_high = row.get("entry_zone_high", "")
    trigger = row.get("trigger_price", "")
    max_fill = row.get("max_acceptable_fill", "")

    if not eligible:
        return {
            "stage_a_status": "NOT ELIGIBLE",
            "stage_a_reference": "Official bucket is outside A-quality trade-quality layer.",
            "stage_b_status": "NOT ELIGIBLE",
            "stage_b_reference": "Official bucket is outside A-quality trade-quality layer.",
            "stage_c_status": "NOT ELIGIBLE",
            "stage_c_reference": "Official bucket is outside A-quality trade-quality layer.",
        }

    if state == "EXECUTION READY":
        a_status = "READY TO PLAN"
        a_ref = f"Preferred zone {zone_low}–{zone_high}; shadow tranche {STAGE_A_PCT}%."
        b_status = "CONDITIONAL"
        b_ref = f"Trigger acceptance at {trigger}; shadow add {STAGE_B_PCT}%, without exceeding max fill {max_fill}."
        c_status = "CONDITIONAL"
        c_ref = f"Full-trigger continuation/retest confirmation; shadow final {STAGE_C_PCT}%, subject to max-fill boundary {max_fill}."
    elif state == "WATCH":
        a_status = "WAIT"
        a_ref = f"Wait for trigger {trigger}; do not anticipate. Preferred zone {zone_low}–{zone_high}."
        b_status = "WAIT"
        b_ref = f"Add only after trigger acceptance; max fill boundary {max_fill}."
        c_status = "WAIT"
        c_ref = "Full-trigger/retest confirmation is not yet observable."
    else:
        a_status = b_status = c_status = "NOT ACTIVE"
        a_ref = f"Decision state {state}; no staged execution preparation activated."
        b_ref = "No staged execution action is activated in this state."
        c_ref = "No staged execution action is activated in this state."

    return {
        "stage_a_status": a_status,
        "stage_a_reference": a_ref,
        "stage_b_status": b_status,
        "stage_b_reference": b_ref,
        "stage_c_status": c_status,
        "stage_c_reference": c_ref,
    }


def build_execution_capture_log(
    decision_table: pd.DataFrame,
    *,
    universe: str = "",
    signal_timestamp_utc: datetime | None = None,
    capture_event: str = "SIGNAL OBSERVED",
    capture_batch_id: str | None = None,
) -> pd.DataFrame:
    """Create a prospective, shadow-only execution-capture snapshot.

    This records what was knowable at scan time. It never sends orders, reads
    fills, or changes the official scanner decision layer.
    """
    if decision_table is None or decision_table.empty:
        return pd.DataFrame(columns=EXECUTION_CAPTURE_COLUMNS)

    ts = signal_timestamp_utc or datetime.now(timezone.utc)
    ts_text = ts.astimezone(timezone.utc).isoformat()
    rows: list[dict] = []
    for _, row in decision_table.iterrows():
        stage = _stage_plan(row)
        symbol = str(row.get("symbol", "")).upper().strip()
        batch = capture_batch_id or ts.strftime("%Y%m%dT%H%M%SZ")
        capture_id = f"{batch}_{symbol}"
        rows.append({
            "capture_id": capture_id,
            "signal_timestamp_utc": ts_text,
            "universe": universe,
            "symbol": symbol,
            "official_bucket": _clean(row.get("official_bucket")),
            "trade_quality_state": _clean(row.get("trade_quality_state")),
            "trade_quality_eligible": bool(row.get("trade_quality_eligible", False)),
            "official_candidate_quality": _clean(row.get("official_candidate_quality")),
            "official_entry_quality": _clean(row.get("official_entry_quality")),
            "official_setup": _clean(row.get("official_setup")),
            "official_decision": _clean(row.get("official_decision")),
            "decision_state": _clean(row.get("decision_state")),
            "decision_reason": _clean(row.get("decision_reason")),
            "plan_state": _clean(row.get("plan_state")),
            "plan_data_confidence": _clean(row.get("plan_data_confidence")),
            "current_price_at_capture": _clean(row.get("current_price")),
            "trigger_price": _clean(row.get("trigger_price")),
            "entry_zone_low": _clean(row.get("entry_zone_low")),
            "entry_zone_high": _clean(row.get("entry_zone_high")),
            "max_acceptable_fill": _clean(row.get("max_acceptable_fill")),
            "max_fill_rr": _clean(row.get("max_fill_rr")),
            **stage,
            "capture_event": capture_event,
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
            "notes": "Prospective shadow capture; outcome fields intentionally blank at signal time.",
        })

    return pd.DataFrame(rows, columns=EXECUTION_CAPTURE_COLUMNS)


def append_execution_capture(
    existing: pd.DataFrame | None,
    snapshot: pd.DataFrame,
) -> pd.DataFrame:
    """Append a snapshot with exact capture_id de-duplication."""
    base = existing.copy(deep=True) if existing is not None else pd.DataFrame(columns=EXECUTION_CAPTURE_COLUMNS)
    if snapshot is None or snapshot.empty:
        return base.reindex(columns=EXECUTION_CAPTURE_COLUMNS)
    combined = pd.concat([base, snapshot], ignore_index=True)
    if "capture_id" in combined.columns:
        combined = combined.drop_duplicates(subset=["capture_id"], keep="first")
    return combined.reindex(columns=EXECUTION_CAPTURE_COLUMNS)


def summarize_execution_capture(log: pd.DataFrame | None) -> dict:
    if log is None or log.empty:
        return {"rows": 0, "symbols": 0, "eligible": 0, "execution_ready": 0, "watch": 0, "outcome_recorded": 0}
    state = log["decision_state"].astype(str).str.upper()
    eligible = log["trade_quality_eligible"].fillna(False).astype(bool)
    fills = log["fill_status"].astype(str).str.upper().ne("UNRECORDED")
    return {
        "rows": int(len(log)),
        "symbols": int(log["symbol"].nunique()),
        "eligible": int(eligible.sum()),
        "execution_ready": int((state == "EXECUTION READY").sum()),
        "watch": int((state == "WATCH").sum()),
        "outcome_recorded": int(fills.sum()),
    }
