from __future__ import annotations

import math

import numpy as np
import pandas as pd


ENTRY_LOCATION_DIAGNOSTIC_COLUMNS = [
    "symbol",
    "official_bucket",
    "official_setup",
    "official_candidate_quality",
    "official_entry_quality",
    "official_decision",
    "official_chase_reasons",
    "close",
    "ema8",
    "ema20",
    "atr14",
    "ext_ema8_pct",
    "ext_ema20_pct",
    "ext_atr",
    "ema8_pressure_pct",
    "ema20_pressure_pct",
    "atr_pressure_pct",
    "max_chase_pressure_pct",
    "hard_ceiling_headroom_pct",
    "ema8_ceiling_headroom_pct_pts",
    "ema20_ceiling_headroom_pct_pts",
    "atr_ceiling_headroom",
    "dominant_extension_axis",
    "entry_location_state",
    "hard_no_chase",
    "hard_no_chase_reasons",
    "official_hard_no_chase",
    "hard_no_chase_parity",
    "location_data_confidence",
    "location_notes",
]


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _pressure(extension, ceiling):
    if not _finite(extension) or not _finite(ceiling) or float(ceiling) <= 0:
        return np.nan
    return 100.0 * max(0.0, float(extension)) / float(ceiling)


def _official_hard_no_chase(row: pd.Series) -> bool:
    reasons = row.get("chase_reasons")
    if reasons is None or (isinstance(reasons, float) and pd.isna(reasons)):
        return False
    return bool(str(reasons).strip())


def _location_state(ext20: float, pressure: float, hard_no_chase: bool) -> str:
    """Classify location without changing the frozen official Entry decision path.

    The pressure bands are research diagnostics normalized to the existing frozen
    hard ceilings. They are intentionally not production gates in V1.3b.
    """
    if not _finite(ext20) or not _finite(pressure):
        return "NOT RANKED"
    if hard_no_chase:
        return "NO CHASE — HARD CEILING"
    if float(ext20) < -1.5:
        return "REPAIR / BELOW EMA20"
    if float(pressure) <= 40.0 and float(ext20) <= 3.0:
        return "PRIME / CONTROLLED"
    if float(pressure) <= 65.0:
        return "ACCEPTABLE"
    if float(pressure) <= 85.0:
        return "STRETCHED"
    return "VERY LATE / AT CEILING"


def build_entry_location_diagnostics(
    scored: pd.DataFrame,
    *,
    max_ext_ema8_pct: float = 5.0,
    max_ext_ema20_pct: float = 8.0,
    max_ext_atr: float = 2.0,
) -> pd.DataFrame:
    """Build V1.3b Entry Location / Anti-Chase diagnostics as a separate shadow table.

    V1.3b deliberately reuses the *existing official hard NO CHASE ceilings* as
    reference anchors, but does not write anything back into ``scored`` and does
    not change Entry Quality, buckets, ranking, event gates or trade decisions.

    Continuous extension pressure is transparent rather than weighted:

    - EMA8 pressure = positive EMA8 extension / frozen EMA8 ceiling;
    - EMA20 pressure = positive EMA20 extension / frozen EMA20 ceiling;
    - ATR pressure = positive ATR extension / frozen ATR ceiling;
    - max pressure = the most restrictive of those three axes.

    100% pressure means the price is exactly at a frozen hard ceiling. The frozen
    gate itself remains strict ``>`` just as in the official scoring code, so a
    value exactly at the ceiling is VERY LATE but is not independently marked as
    hard NO CHASE until the ceiling is exceeded.
    """
    if scored is None or scored.empty:
        return pd.DataFrame(columns=ENTRY_LOCATION_DIAGNOSTIC_COLUMNS)

    source = scored.copy(deep=True)
    rows: list[dict] = []

    for _, r in source.iterrows():
        symbol = str(r.get("symbol", "")).upper().strip()
        ext8 = r.get("ext_ema8_pct")
        ext20 = r.get("ext_ema20_pct")
        extatr = r.get("ext_atr")

        p8 = _pressure(ext8, max_ext_ema8_pct)
        p20 = _pressure(ext20, max_ext_ema20_pct)
        patr = _pressure(extatr, max_ext_atr)

        all_valid = all(
            _finite(v)
            for v in [
                ext8,
                ext20,
                extatr,
                p8,
                p20,
                patr,
                max_ext_ema8_pct,
                max_ext_ema20_pct,
                max_ext_atr,
            ]
        ) and all(float(v) > 0 for v in [max_ext_ema8_pct, max_ext_ema20_pct, max_ext_atr])

        if all_valid:
            pressures = {
                "EMA8": float(p8),
                "EMA20": float(p20),
                "ATR": float(patr),
            }
            dominant_axis = max(pressures, key=pressures.get)
            max_pressure = float(pressures[dominant_axis])

            hard_reasons = []
            if float(ext8) > float(max_ext_ema8_pct):
                hard_reasons.append(
                    f"EMA8 extension {float(ext8):.2f}% > {float(max_ext_ema8_pct):.2f}% ceiling"
                )
            if float(ext20) > float(max_ext_ema20_pct):
                hard_reasons.append(
                    f"EMA20 extension {float(ext20):.2f}% > {float(max_ext_ema20_pct):.2f}% ceiling"
                )
            if float(extatr) > float(max_ext_atr):
                hard_reasons.append(
                    f"EMA20 extension {float(extatr):.2f} ATR > {float(max_ext_atr):.2f} ATR ceiling"
                )
            hard_no_chase = bool(hard_reasons)
            state = _location_state(float(ext20), max_pressure, hard_no_chase)
            confidence = "HIGH"
            hard_headroom = 100.0 - max_pressure
            h8 = float(max_ext_ema8_pct) - float(ext8)
            h20 = float(max_ext_ema20_pct) - float(ext20)
            hatr = float(max_ext_atr) - float(extatr)

            if hard_no_chase:
                notes = (
                    "Independent V1.3b recomputation exceeds at least one frozen hard "
                    "NO CHASE ceiling; shadow diagnostics do not alter the official gate."
                )
            elif state == "REPAIR / BELOW EMA20":
                notes = (
                    "Price is below the EMA20 repair band. Low positive-extension pressure "
                    "does not imply a good entry location."
                )
            elif state == "PRIME / CONTROLLED":
                notes = (
                    "Extension pressure is controlled relative to the frozen hard ceilings; "
                    "this is location evidence only, not an actionable signal."
                )
            elif state == "ACCEPTABLE":
                notes = (
                    "Location remains below the late-stage pressure bands but has less "
                    "anti-chase headroom than a prime/controlled entry."
                )
            elif state == "STRETCHED":
                notes = (
                    "Extension is materially consuming hard-ceiling headroom. Treat as a "
                    "shadow late-entry watch rather than lowering standards."
                )
            else:
                notes = (
                    "Price is very near a frozen hard ceiling. V1.3b flags the continuous "
                    "late-entry risk before the existing binary NO CHASE gate is crossed."
                )
        else:
            dominant_axis = "N/A"
            max_pressure = np.nan
            hard_reasons = []
            hard_no_chase = False
            state = "NOT RANKED"
            confidence = "LOW"
            hard_headroom = np.nan
            h8 = np.nan
            h20 = np.nan
            hatr = np.nan
            notes = (
                "Required extension inputs or hard-ceiling references are incomplete; "
                "no neutral location conclusion is imputed."
            )

        official_hard = _official_hard_no_chase(r)
        parity = bool(hard_no_chase == official_hard) if all_valid else False

        rows.append(
            {
                "symbol": symbol,
                "official_bucket": r.get("bucket"),
                "official_setup": r.get("setup"),
                "official_candidate_quality": r.get("quality_score"),
                "official_entry_quality": r.get("entry_score"),
                "official_decision": r.get("decision"),
                "official_chase_reasons": r.get("chase_reasons"),
                "close": r.get("close"),
                "ema8": r.get("ema8"),
                "ema20": r.get("ema20"),
                "atr14": r.get("atr14"),
                "ext_ema8_pct": ext8,
                "ext_ema20_pct": ext20,
                "ext_atr": extatr,
                "ema8_pressure_pct": p8,
                "ema20_pressure_pct": p20,
                "atr_pressure_pct": patr,
                "max_chase_pressure_pct": max_pressure,
                "hard_ceiling_headroom_pct": hard_headroom,
                "ema8_ceiling_headroom_pct_pts": h8,
                "ema20_ceiling_headroom_pct_pts": h20,
                "atr_ceiling_headroom": hatr,
                "dominant_extension_axis": dominant_axis,
                "entry_location_state": state,
                "hard_no_chase": hard_no_chase,
                "hard_no_chase_reasons": "; ".join(hard_reasons),
                "official_hard_no_chase": official_hard,
                "hard_no_chase_parity": parity,
                "location_data_confidence": confidence,
                "location_notes": notes,
            }
        )

    return pd.DataFrame(rows, columns=ENTRY_LOCATION_DIAGNOSTIC_COLUMNS)


def summarize_entry_location_diagnostics(table: pd.DataFrame) -> dict:
    if table is None or table.empty:
        return {
            "evaluated": 0,
            "ranked": 0,
            "prime_controlled": 0,
            "acceptable": 0,
            "stretched": 0,
            "very_late": 0,
            "repair_below_ema20": 0,
            "hard_no_chase": 0,
            "near_ceiling_watch": 0,
            "late_official_actionable": 0,
            "hard_ceiling_parity_mismatches": 0,
        }

    state = table["entry_location_state"].astype(str)
    hard = table["hard_no_chase"].fillna(False).astype(bool)
    pressure = pd.to_numeric(table["max_chase_pressure_pct"], errors="coerce")
    bucket = table["official_bucket"].astype(str)
    late_states = state.isin(["STRETCHED", "VERY LATE / AT CEILING"])
    actionable = bucket.isin(["ACTIONABLE NOW", "TECH ACTIONABLE — EVENT CHECK"])
    parity = table["hard_no_chase_parity"].fillna(False).astype(bool)
    ranked = state != "NOT RANKED"

    return {
        "evaluated": int(len(table)),
        "ranked": int(ranked.sum()),
        "prime_controlled": int((state == "PRIME / CONTROLLED").sum()),
        "acceptable": int((state == "ACCEPTABLE").sum()),
        "stretched": int((state == "STRETCHED").sum()),
        "very_late": int((state == "VERY LATE / AT CEILING").sum()),
        "repair_below_ema20": int((state == "REPAIR / BELOW EMA20").sum()),
        "hard_no_chase": int(hard.sum()),
        "near_ceiling_watch": int(((pressure >= 75.0) & (pressure < 100.0) & ~hard).sum()),
        "late_official_actionable": int((late_states & actionable & ~hard).sum()),
        "hard_ceiling_parity_mismatches": int((ranked & ~parity).sum()),
    }
