from __future__ import annotations

import math

import numpy as np
import pandas as pd

DECISION_COLUMNS = [
    "symbol",
    "official_bucket",
    "official_setup",
    "official_candidate_quality",
    "official_entry_quality",
    "official_decision",
    "plan_state",
    "structured_plan",
    "plan_data_confidence",
    "current_price",
    "trigger_price",
    "entry_zone_low",
    "entry_zone_high",
    "max_acceptable_fill",
    "max_fill_rr",
    "risk_geometry_state",
    "decision_state",
    "decision_reason",
    "decision_ready",
]

READY = "READY"
WATCH = "WATCH"
WAIT = "WAIT"
NO_CHASE = "NO CHASE"


_HARD_NO_CHASE_STATES = {
    "MISSED / NO CHASE — ABOVE MAX FILL",
    "BLOCKED — TRIGGER BEYOND HARD CEILING",
}


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _as_bool(value) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _decision_for_row(row: pd.Series) -> tuple[str, str, bool]:
    plan_state = str(row.get("plan_state", "")).strip()
    structured = _as_bool(row.get("structured_plan", False))
    confidence = str(row.get("plan_data_confidence", "")).strip().upper()
    current = row.get("current_price", np.nan)
    trigger = row.get("trigger_price", np.nan)
    zone_low = row.get("entry_zone_low", np.nan)
    zone_high = row.get("entry_zone_high", np.nan)
    max_fill = row.get("max_acceptable_fill", np.nan)
    max_rr = row.get("max_fill_rr", np.nan)
    geometry = str(row.get("risk_geometry_state", "")).strip().upper()

    if plan_state in _HARD_NO_CHASE_STATES or "NO CHASE" in plan_state.upper():
        return NO_CHASE, "V1.3c plan is already beyond the permitted chase boundary.", False

    if plan_state == "TRIGGERED — ABOVE ZONE / LATE":
        return NO_CHASE, "Price triggered but is above the preferred entry zone; do not chase.", False

    if not structured or confidence != "HIGH":
        return WAIT, "Structured high-confidence entry plan is not available.", False

    if not all(_finite(v) for v in [current, trigger, zone_low, zone_high, max_fill]):
        return WAIT, "Required trigger/zone/max-fill reference is incomplete.", False

    if _finite(max_rr) and float(max_rr) < 1.5:
        return WAIT, "Maximum-fill R:R is below the provisional 1.5R research floor.", False

    if plan_state == "TRIGGERED — IN ENTRY ZONE":
        if _finite(max_rr) and float(max_rr) >= 1.5:
            return READY, "Current price is inside the preferred entry zone and risk geometry remains acceptable through max fill.", True
        return WAIT, "Current price is in the zone, but risk geometry does not remain acceptable through max fill.", False

    if plan_state == "WAITING FOR TRIGGER":
        if float(current) < float(trigger):
            return WATCH, "Structured plan is valid and waiting for the trigger; no entry before trigger acceptance.", False
        return WAIT, "Price is at/above the trigger but is not in a valid V1.3c entry state.", False

    if plan_state in {"NO STRUCTURED PLAN", "NOT RANKED"}:
        return WAIT, "No structured entry plan is available; remain outside the action set.", False

    # Defensive handling for future V1.3c states: unknown states never become READY.
    return WAIT, f"Unrecognized V1.3c plan state: {plan_state or 'blank'}.", False


def build_decision_architecture(
    scored: pd.DataFrame,
    entry_zone: pd.DataFrame | None = None,
    risk_reward: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build V1.3e READY/WATCH/WAIT/NO CHASE shadow decision states.

    This layer is decision UX only. It consumes frozen V1.3c planning references
    and V1.3d risk geometry, but never mutates the official ``scored`` frame and
    never rewrites the official trade decision.
    """
    if scored is None or scored.empty:
        return pd.DataFrame(columns=DECISION_COLUMNS)

    zone = entry_zone.copy(deep=True) if entry_zone is not None else pd.DataFrame()
    rr = risk_reward.copy(deep=True) if risk_reward is not None else pd.DataFrame()
    if not zone.empty and "symbol" in zone.columns:
        zone = zone.drop_duplicates("symbol").set_index("symbol")
    if not rr.empty and "symbol" in rr.columns:
        rr = rr.drop_duplicates("symbol").set_index("symbol")

    rows: list[dict] = []
    for _, r in scored.iterrows():
        symbol = str(r.get("symbol", "")).upper().strip()
        z = zone.loc[symbol] if symbol in zone.index else pd.Series(dtype=object)
        q = rr.loc[symbol] if symbol in rr.index else pd.Series(dtype=object)

        merged = pd.Series({
            "plan_state": z.get("plan_state", "NOT RANKED"),
            "structured_plan": z.get("structured_plan", False),
            "plan_data_confidence": z.get("plan_data_confidence", "LOW"),
            "current_price": r.get("close", np.nan),
            "trigger_price": z.get("trigger_price", np.nan),
            "entry_zone_low": z.get("entry_zone_low", np.nan),
            "entry_zone_high": z.get("entry_zone_high", np.nan),
            "max_acceptable_fill": z.get("max_acceptable_fill", np.nan),
            "max_fill_rr": q.get("max_fill_rr", np.nan),
            "risk_geometry_state": q.get("risk_geometry_state", "NOT RANKED"),
        })
        state, reason, ready = _decision_for_row(merged)
        rows.append({
            "symbol": symbol,
            "official_bucket": r.get("bucket"),
            "official_setup": r.get("setup"),
            "official_candidate_quality": r.get("quality_score"),
            "official_entry_quality": r.get("entry_score"),
            "official_decision": r.get("decision"),
            "plan_state": merged["plan_state"],
            "structured_plan": bool(merged["structured_plan"]),
            "plan_data_confidence": merged["plan_data_confidence"],
            "current_price": merged["current_price"],
            "trigger_price": merged["trigger_price"],
            "entry_zone_low": merged["entry_zone_low"],
            "entry_zone_high": merged["entry_zone_high"],
            "max_acceptable_fill": merged["max_acceptable_fill"],
            "max_fill_rr": merged["max_fill_rr"],
            "risk_geometry_state": merged["risk_geometry_state"],
            "decision_state": state,
            "decision_reason": reason,
            "decision_ready": ready,
        })

    return pd.DataFrame(rows, columns=DECISION_COLUMNS)


def summarize_decision_architecture(table: pd.DataFrame) -> dict:
    if table is None or table.empty:
        return {
            "evaluated": 0,
            "ready": 0,
            "watch": 0,
            "wait": 0,
            "no_chase": 0,
            "decision_ready": 0,
        }
    states = table["decision_state"].astype(str)
    return {
        "evaluated": int(len(table)),
        "ready": int((states == READY).sum()),
        "watch": int((states == WATCH).sum()),
        "wait": int((states == WAIT).sum()),
        "no_chase": int((states == NO_CHASE).sum()),
        "decision_ready": int(table["decision_ready"].fillna(False).astype(bool).sum()),
    }
