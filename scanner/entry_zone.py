from __future__ import annotations

import math

import numpy as np
import pandas as pd


ENTRY_ZONE_DIAGNOSTIC_COLUMNS = [
    "symbol",
    "official_bucket",
    "official_setup",
    "official_candidate_quality",
    "official_entry_quality",
    "official_decision",
    "official_entry_px",
    "current_price",
    "ema8",
    "ema20",
    "atr14",
    "prior_1_high",
    "prior_5_high",
    "prior_10_high",
    "prior_20_high",
    "official_high20_prev",
    "high20_structure_parity",
    "trigger_type",
    "trigger_price",
    "confirmation_condition",
    "entry_zone_low",
    "entry_zone_high",
    "entry_zone_width_atr",
    "raw_max_fill",
    "frozen_hard_ceiling_px",
    "max_acceptable_fill",
    "trigger_distance_pct",
    "max_fill_headroom_pct",
    "trigger_to_hard_ceiling_atr",
    "plan_state",
    "structured_plan",
    "trigger_beyond_hard_ceiling",
    "official_entry_ref_matches_current_price",
    "plan_data_confidence",
    "plan_notes",
]


BREAKOUT_SETUPS = {"CONFIRMED BREAKOUT", "LOW-CONFIDENCE BREAKOUT"}
PULLBACK_SETUPS = {"EMA20 PULLBACK"}
BASE_SETUPS = {"VCP / TIGHTENING", "TIGHT BASE / DEVELOPING"}
REPAIR_SETUPS = {"MA20 REPAIR WINDOW"}
NO_PLAN_SETUPS = {"TRENDING / NO CLEAN SETUP", "BROKEN / BELOW MA50"}


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _safe_pct(numerator, denominator):
    if not _finite(numerator) or not _finite(denominator) or float(denominator) == 0:
        return np.nan
    return 100.0 * float(numerator) / float(denominator)


def _prepare_symbol_bars(bars: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if bars is None or bars.empty or "symbol" not in bars.columns:
        return pd.DataFrame()
    g = bars[bars["symbol"].astype(str).str.upper() == str(symbol).upper()].copy()
    if g.empty:
        return g
    if "timestamp" in g.columns:
        g["_ts"] = pd.to_datetime(g["timestamp"], utc=True, errors="coerce")
        g = g[g["_ts"].notna()].sort_values("_ts")
    else:
        g = g.sort_index()
    return g.reset_index(drop=True)


def _prior_structure(g: pd.DataFrame) -> dict:
    """Return prior-session structure excluding the latest observed/evaluation bar."""
    if g is None or g.empty or len(g) < 2 or "high" not in g.columns:
        return {
            "prior_1_high": np.nan,
            "prior_5_high": np.nan,
            "prior_10_high": np.nan,
            "prior_20_high": np.nan,
        }

    prior = g.iloc[:-1].copy()
    highs = pd.to_numeric(prior["high"], errors="coerce")
    highs = highs[highs.notna()]
    if highs.empty:
        return {
            "prior_1_high": np.nan,
            "prior_5_high": np.nan,
            "prior_10_high": np.nan,
            "prior_20_high": np.nan,
        }

    return {
        "prior_1_high": float(highs.iloc[-1]),
        "prior_5_high": float(highs.tail(5).max()) if len(highs) >= 1 else np.nan,
        "prior_10_high": float(highs.tail(10).max()) if len(highs) >= 1 else np.nan,
        "prior_20_high": float(highs.tail(20).max()) if len(highs) >= 1 else np.nan,
    }


def _frozen_hard_ceiling_price(
    ema8: float,
    ema20: float,
    atr14: float,
    *,
    max_ext_ema8_pct: float,
    max_ext_ema20_pct: float,
    max_ext_atr: float,
):
    values = []
    if _finite(ema8) and _finite(max_ext_ema8_pct) and float(ema8) > 0:
        values.append(float(ema8) * (1.0 + float(max_ext_ema8_pct) / 100.0))
    if _finite(ema20) and _finite(max_ext_ema20_pct) and float(ema20) > 0:
        values.append(float(ema20) * (1.0 + float(max_ext_ema20_pct) / 100.0))
    if (
        _finite(ema20)
        and _finite(atr14)
        and _finite(max_ext_atr)
        and float(ema20) > 0
        and float(atr14) > 0
    ):
        values.append(float(ema20) + float(max_ext_atr) * float(atr14))
    return min(values) if values else np.nan


def _setup_trigger(setup: str, row: pd.Series, structure: dict):
    """Return (trigger_type, trigger_price, confirmation, plan_class)."""
    setup = str(setup or "")
    ema20 = row.get("ema20")

    if setup in BREAKOUT_SETUPS:
        reference = structure.get("prior_20_high")
        official = row.get("high20_prev")
        if _finite(official):
            reference = max(float(reference), float(official)) if _finite(reference) else float(official)
        if not _finite(reference):
            return "20D HIGH BREAK", np.nan, "Prior-20-session high unavailable.", "BREAKOUT"
        return (
            "20D HIGH BREAK",
            float(reference) * 1.001,
            "Clear the prior 20-session high by 0.10%; participation/volume confirmation remains a separate V1.3a diagnostic.",
            "BREAKOUT",
        )

    if setup in PULLBACK_SETUPS:
        p1 = structure.get("prior_1_high")
        if not _finite(p1) and not _finite(ema20):
            return "PULLBACK RECLAIM", np.nan, "Prior-session high and EMA20 unavailable.", "PULLBACK"
        base = max(
            float(p1) if _finite(p1) else -np.inf,
            float(ema20) if _finite(ema20) else -np.inf,
        )
        return (
            "PULLBACK RECLAIM",
            base * 1.001,
            "Hold/reclaim EMA20 and clear the prior-session high by 0.10% before treating the pullback as triggered.",
            "PULLBACK",
        )

    if setup in BASE_SETUPS:
        p10 = structure.get("prior_10_high")
        if not _finite(p10):
            return "10D STRUCTURE BREAK", np.nan, "Prior-10-session structure high unavailable.", "BASE"
        return (
            "10D STRUCTURE BREAK",
            float(p10) * 1.001,
            "Clear the prior 10-session structure high by 0.10%; the base/VCP contraction evidence remains separate from the trigger itself.",
            "BASE",
        )

    if setup in REPAIR_SETUPS:
        p1 = structure.get("prior_1_high")
        if not _finite(p1) and not _finite(ema20):
            return "EMA20 REPAIR RECLAIM", np.nan, "Prior-session high and EMA20 unavailable.", "REPAIR"
        base = max(
            float(p1) if _finite(p1) else -np.inf,
            float(ema20) if _finite(ema20) else -np.inf,
        )
        return (
            "EMA20 REPAIR RECLAIM",
            base * 1.001,
            "Reclaim EMA20 and the prior-session high by 0.10%. This is a repair trigger, not an automatic actionable entry.",
            "REPAIR",
        )

    return (
        "NONE",
        np.nan,
        "No structured V1.3c trigger is assigned to this official setup; the system does not invent an entry plan.",
        "NONE",
    )


def _plan_state(
    current_price: float,
    trigger: float,
    zone_high: float,
    max_fill: float,
    *,
    structured_plan: bool,
    trigger_beyond_hard_ceiling: bool,
    data_ok: bool,
):
    if not data_ok:
        return "NOT RANKED"
    if not structured_plan:
        return "NO STRUCTURED PLAN"
    if trigger_beyond_hard_ceiling:
        return "BLOCKED — TRIGGER BEYOND HARD CEILING"
    if not all(_finite(v) for v in [current_price, trigger, zone_high, max_fill]):
        return "NOT RANKED"
    if float(current_price) < float(trigger):
        return "WAITING FOR TRIGGER"
    if float(current_price) <= float(zone_high):
        return "TRIGGERED — IN ENTRY ZONE"
    if float(current_price) <= float(max_fill):
        return "TRIGGERED — ABOVE ZONE / LATE"
    return "MISSED / NO CHASE — ABOVE MAX FILL"


def build_entry_zone_diagnostics(
    scored: pd.DataFrame,
    bars: pd.DataFrame,
    *,
    max_ext_ema8_pct: float = 5.0,
    max_ext_ema20_pct: float = 8.0,
    max_ext_atr: float = 2.0,
    entry_zone_atr: float = 0.25,
    max_fill_atr: float = 0.50,
) -> pd.DataFrame:
    """Build V1.3c Trigger / Entry-Zone diagnostics as a separate SHADOW table.

    The official scanner still treats ``entry_px`` as the current close. V1.3c does
    not rewrite that field. Instead it builds a setup-aware structural trigger from
    *prior* daily-bar structure, then creates a provisional ATR-sized entry zone and
    a maximum acceptable fill capped by the existing frozen hard anti-chase ceilings.

    V1.3c is descriptive/research architecture only. The 0.25 ATR zone width and
    0.50 ATR raw max-fill allowance are provisional reference parameters, not proven
    expectancy-optimal production gates.
    """
    if scored is None or scored.empty:
        return pd.DataFrame(columns=ENTRY_ZONE_DIAGNOSTIC_COLUMNS)

    source = scored.copy(deep=True)
    rows: list[dict] = []

    for _, r in source.iterrows():
        symbol = str(r.get("symbol", "")).upper().strip()
        setup = str(r.get("setup", ""))
        current = r.get("close")
        atr = r.get("atr14")
        ema8 = r.get("ema8")
        ema20 = r.get("ema20")
        official_entry = r.get("entry_px")

        g = _prepare_symbol_bars(bars, symbol)
        structure = _prior_structure(g)

        official_h20 = r.get("high20_prev")
        computed_h20 = structure.get("prior_20_high")
        if _finite(official_h20) and _finite(computed_h20):
            h20_parity = bool(np.isclose(float(official_h20), float(computed_h20), rtol=1e-9, atol=1e-8))
        else:
            h20_parity = False

        trigger_type, trigger, confirmation, plan_class = _setup_trigger(setup, r, structure)
        structured = plan_class != "NONE"

        hard_ceiling = _frozen_hard_ceiling_price(
            ema8,
            ema20,
            atr,
            max_ext_ema8_pct=max_ext_ema8_pct,
            max_ext_ema20_pct=max_ext_ema20_pct,
            max_ext_atr=max_ext_atr,
        )

        core_inputs_ok = all(_finite(v) for v in [current, atr, ema8, ema20]) and float(atr) > 0
        trigger_ok = (not structured) or _finite(trigger)
        bars_ok = not g.empty and len(g) >= 2
        data_ok = bool(core_inputs_ok and trigger_ok and bars_ok)

        if structured and data_ok:
            raw_zone_high = float(trigger) + float(entry_zone_atr) * float(atr)
            raw_max_fill = float(trigger) + float(max_fill_atr) * float(atr)
            trigger_beyond = bool(_finite(hard_ceiling) and float(trigger) > float(hard_ceiling))
            max_fill = min(float(raw_max_fill), float(hard_ceiling)) if _finite(hard_ceiling) else float(raw_max_fill)
            zone_low = float(trigger)
            zone_high = min(float(raw_zone_high), float(max_fill))
            zone_width_atr = max(0.0, float(zone_high) - float(zone_low)) / float(atr)
            trigger_distance_pct = _safe_pct(float(trigger) - float(current), float(current))
            max_fill_headroom_pct = _safe_pct(float(max_fill) - float(current), float(current))
            trigger_to_hard_atr = (
                (float(hard_ceiling) - float(trigger)) / float(atr)
                if _finite(hard_ceiling)
                else np.nan
            )
        else:
            raw_zone_high = np.nan
            raw_max_fill = np.nan
            trigger_beyond = False
            max_fill = np.nan
            zone_low = np.nan
            zone_high = np.nan
            zone_width_atr = np.nan
            trigger_distance_pct = np.nan
            max_fill_headroom_pct = np.nan
            trigger_to_hard_atr = np.nan

        state = _plan_state(
            current,
            trigger,
            zone_high,
            max_fill,
            structured_plan=structured,
            trigger_beyond_hard_ceiling=trigger_beyond,
            data_ok=data_ok,
        )

        entry_ref_match = bool(
            _finite(official_entry)
            and _finite(current)
            and np.isclose(float(official_entry), float(current), rtol=0.0, atol=0.011)
        )

        if not data_ok:
            confidence = "LOW"
            notes = (
                "Required current-price/ATR/MA inputs, prior-bar structure, or trigger reference are incomplete. "
                "No neutral trigger/zone conclusion is imputed."
            )
        else:
            confidence = "HIGH"
            if not structured:
                notes = (
                    "The official setup does not receive a structured V1.3c plan. Current close remains observable, "
                    "but V1.3c refuses to invent a trigger or entry zone."
                )
            elif trigger_beyond:
                notes = (
                    "The structural trigger itself lies beyond the most restrictive frozen hard anti-chase ceiling. "
                    "The shadow plan is blocked rather than moving the ceiling or chasing the trigger."
                )
            elif state == "WAITING FOR TRIGGER":
                notes = (
                    "Current price is below the structural trigger. V1.3c keeps the plan conditional instead of "
                    "treating the current close as an automatic entry."
                )
            elif state == "TRIGGERED — IN ENTRY ZONE":
                notes = (
                    "The structural trigger has been cleared and current price remains inside the provisional entry zone. "
                    "This is shadow evidence only, not a production order instruction."
                )
            elif state == "TRIGGERED — ABOVE ZONE / LATE":
                notes = (
                    "The trigger has been cleared but price is already above the preferred entry zone. Remaining fill "
                    "headroom exists, but entry quality is deteriorating."
                )
            else:
                notes = (
                    "Price is above the maximum acceptable shadow fill. The architecture records a missed/NO CHASE state "
                    "rather than expanding the entry zone after the move."
                )

        rows.append(
            {
                "symbol": symbol,
                "official_bucket": r.get("bucket"),
                "official_setup": setup,
                "official_candidate_quality": r.get("quality_score"),
                "official_entry_quality": r.get("entry_score"),
                "official_decision": r.get("decision"),
                "official_entry_px": official_entry,
                "current_price": current,
                "ema8": ema8,
                "ema20": ema20,
                "atr14": atr,
                "prior_1_high": structure.get("prior_1_high"),
                "prior_5_high": structure.get("prior_5_high"),
                "prior_10_high": structure.get("prior_10_high"),
                "prior_20_high": structure.get("prior_20_high"),
                "official_high20_prev": official_h20,
                "high20_structure_parity": h20_parity,
                "trigger_type": trigger_type,
                "trigger_price": trigger,
                "confirmation_condition": confirmation,
                "entry_zone_low": zone_low,
                "entry_zone_high": zone_high,
                "entry_zone_width_atr": zone_width_atr,
                "raw_max_fill": raw_max_fill,
                "frozen_hard_ceiling_px": hard_ceiling,
                "max_acceptable_fill": max_fill,
                "trigger_distance_pct": trigger_distance_pct,
                "max_fill_headroom_pct": max_fill_headroom_pct,
                "trigger_to_hard_ceiling_atr": trigger_to_hard_atr,
                "plan_state": state,
                "structured_plan": structured,
                "trigger_beyond_hard_ceiling": trigger_beyond,
                "official_entry_ref_matches_current_price": entry_ref_match,
                "plan_data_confidence": confidence,
                "plan_notes": notes,
            }
        )

    return pd.DataFrame(rows, columns=ENTRY_ZONE_DIAGNOSTIC_COLUMNS)


def summarize_entry_zone_diagnostics(table: pd.DataFrame) -> dict:
    if table is None or table.empty:
        return {
            "evaluated": 0,
            "high_confidence": 0,
            "structured_plans": 0,
            "waiting_for_trigger": 0,
            "in_entry_zone": 0,
            "above_zone_late": 0,
            "missed_no_chase": 0,
            "trigger_blocked": 0,
            "no_structured_plan": 0,
            "not_ranked": 0,
            "official_entry_ref_current_matches": 0,
            "high20_structure_parity_checked": 0,
            "high20_structure_parity_mismatches": 0,
        }

    state = table["plan_state"].astype(str)
    confidence = table["plan_data_confidence"].astype(str)
    structured = table["structured_plan"].fillna(False).astype(bool)
    entry_match = table["official_entry_ref_matches_current_price"].fillna(False).astype(bool)
    parity = table["high20_structure_parity"].fillna(False).astype(bool)
    official_h20 = pd.to_numeric(table["official_high20_prev"], errors="coerce")
    prior_h20 = pd.to_numeric(table["prior_20_high"], errors="coerce")
    parity_rankable = official_h20.notna() & prior_h20.notna()

    return {
        "evaluated": int(len(table)),
        "high_confidence": int((confidence == "HIGH").sum()),
        "structured_plans": int(structured.sum()),
        "waiting_for_trigger": int((state == "WAITING FOR TRIGGER").sum()),
        "in_entry_zone": int((state == "TRIGGERED — IN ENTRY ZONE").sum()),
        "above_zone_late": int((state == "TRIGGERED — ABOVE ZONE / LATE").sum()),
        "missed_no_chase": int((state == "MISSED / NO CHASE — ABOVE MAX FILL").sum()),
        "trigger_blocked": int((state == "BLOCKED — TRIGGER BEYOND HARD CEILING").sum()),
        "no_structured_plan": int((state == "NO STRUCTURED PLAN").sum()),
        "not_ranked": int((state == "NOT RANKED").sum()),
        "official_entry_ref_current_matches": int(entry_match.sum()),
        "high20_structure_parity_checked": int(parity_rankable.sum()),
        "high20_structure_parity_mismatches": int((parity_rankable & ~parity).sum()),
    }
