from __future__ import annotations

import math

import numpy as np
import pandas as pd

RISK_REWARD_COLUMNS = [
    "symbol",
    "official_bucket",
    "official_setup",
    "official_candidate_quality",
    "official_entry_quality",
    "official_decision",
    "plan_state",
    "structured_plan",
    "plan_data_confidence",
    "trigger_price",
    "entry_zone_low",
    "entry_zone_high",
    "max_acceptable_fill",
    "ema20",
    "atr14",
    "prior_10_low",
    "prior_20_low",
    "structural_support",
    "stop_buffer_atr",
    "stop_price",
    "trigger_risk",
    "zone_high_risk",
    "max_fill_risk",
    "t1_price",
    "t2_price",
    "trigger_rr",
    "zone_high_rr",
    "max_fill_rr",
    "trigger_rr_band",
    "zone_high_rr_band",
    "max_fill_rr_band",
    "stop_distance_pct",
    "stop_distance_atr",
    "risk_geometry_state",
    "risk_reward_notes",
]

RR_STRONG = "STRONG"
RR_ACCEPTABLE = "ACCEPTABLE"
RR_WEAK = "WEAK"
RR_POOR = "POOR"
RR_NOT_RANKED = "NOT RANKED"


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _rr(reward: float, risk: float):
    if not _finite(reward) or not _finite(risk) or float(risk) <= 0:
        return np.nan
    return float(reward) / float(risk)


def _rr_band(value):
    if not _finite(value):
        return RR_NOT_RANKED
    value = float(value)
    if value >= 2.0:
        return RR_STRONG
    if value >= 1.5:
        return RR_ACCEPTABLE
    if value >= 1.0:
        return RR_WEAK
    return RR_POOR


def _prepare_symbol_bars(bars: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if bars is None or bars.empty or "symbol" not in bars.columns:
        return pd.DataFrame()
    g = bars[bars["symbol"].astype(str).str.upper() == str(symbol).upper()].copy()
    if g.empty:
        return g
    if "timestamp" in g.columns:
        g["_ts"] = pd.to_datetime(g["timestamp"], utc=True, errors="coerce")
        g = g[g["_ts"].notna()].sort_values("_ts")
    return g.reset_index(drop=True)


def _prior_lows(g: pd.DataFrame) -> tuple[float, float]:
    if g is None or g.empty or len(g) < 2 or "low" not in g.columns:
        return np.nan, np.nan
    prior = g.iloc[:-1].copy()
    lows = pd.to_numeric(prior["low"], errors="coerce").dropna()
    if lows.empty:
        return np.nan, np.nan
    return (
        float(lows.iloc[-1]) if len(lows) >= 1 else np.nan,
        float(lows.tail(20).min()) if len(lows) >= 1 else np.nan,
    )


def _support(ema20, prior_10_low, prior_20_low):
    values = [v for v in [ema20, prior_10_low, prior_20_low] if _finite(v) and float(v) > 0]
    if not values:
        return np.nan
    # The recent structural low is the primary downside reference; EMA20 is
    # retained as a trend-support reference. Using the lowest of the available
    # structural/trend references prevents manufacturing a tighter stop solely
    # to improve R:R.
    return min(values)


def build_risk_reward_diagnostics(
    scored: pd.DataFrame,
    bars: pd.DataFrame,
    *,
    entry_zone: pd.DataFrame | None = None,
    stop_buffer_atr: float = 0.25,
    t1_r: float = 1.5,
    t2_r: float = 2.5,
) -> pd.DataFrame:
    """Build V1.3d Risk/Reward and stop-distance diagnostics as SHADOW data.

    V1.3d consumes the frozen V1.3c trigger/zone plan. It derives a transparent
    structural support reference from EMA20 and prior-session lows, places a
    provisional stop ``stop_buffer_atr`` below that support, and calculates R
    geometry at trigger, preferred-zone-high and maximum acceptable fill.

    The 1.5R / 2.5R target references mirror the frozen legacy target multiples;
    they are diagnostic references, not a production target authority. No field
    in ``scored`` is mutated and no production decision is changed.
    """
    if scored is None or scored.empty:
        return pd.DataFrame(columns=RISK_REWARD_COLUMNS)

    source = scored.copy(deep=True)
    zone = entry_zone.copy(deep=True) if entry_zone is not None else pd.DataFrame()
    if not zone.empty and "symbol" in zone.columns:
        zone = zone.drop_duplicates("symbol").set_index("symbol")

    rows: list[dict] = []
    for _, r in source.iterrows():
        symbol = str(r.get("symbol", "")).upper().strip()
        z = zone.loc[symbol] if symbol in zone.index else pd.Series(dtype=object)
        setup = r.get("setup")
        plan_state = z.get("plan_state", "NOT RANKED")
        structured = bool(z.get("structured_plan", False))
        confidence = str(z.get("plan_data_confidence", "LOW"))
        trigger = z.get("trigger_price", np.nan)
        zone_low = z.get("entry_zone_low", np.nan)
        zone_high = z.get("entry_zone_high", np.nan)
        max_fill = z.get("max_acceptable_fill", np.nan)
        ema20 = r.get("ema20")
        atr = r.get("atr14")
        current = r.get("close")

        g = _prepare_symbol_bars(bars, symbol)
        prior_1_low, prior_20_low = _prior_lows(g)
        # Use a recent structural low, not the current in-progress bar.
        prior_10_low = (
            float(pd.to_numeric(g.iloc[:-1]["low"], errors="coerce").dropna().tail(10).min())
            if len(g) >= 2 and "low" in g.columns and not pd.to_numeric(g.iloc[:-1]["low"], errors="coerce").dropna().tail(10).empty
            else np.nan
        )
        support = _support(ema20, prior_10_low, prior_20_low)

        data_ok = (
            structured
            and confidence == "HIGH"
            and _finite(trigger)
            and _finite(zone_low)
            and _finite(zone_high)
            and _finite(max_fill)
            and _finite(atr)
            and float(atr) > 0
            and _finite(support)
        )

        if data_ok:
            stop = float(support) - float(stop_buffer_atr) * float(atr)
            # A structural stop must remain strictly below all planned entry refs.
            max_planned = max(float(trigger), float(zone_high), float(max_fill))
            if stop >= max_planned:
                data_ok = False
            else:
                trigger_risk = float(trigger) - stop
                zone_risk = float(zone_high) - stop
                max_risk = float(max_fill) - stop
                t1 = float(trigger) + float(t1_r) * trigger_risk
                t2 = float(trigger) + float(t2_r) * trigger_risk
                trigger_rr = _rr(t2 - float(trigger), trigger_risk)
                zone_rr = _rr(t2 - float(zone_high), zone_risk)
                max_rr = _rr(t2 - float(max_fill), max_risk)
                stop_distance_pct = 100.0 * (float(trigger) - stop) / float(trigger) if float(trigger) > 0 else np.nan
                stop_distance_atr = trigger_risk / float(atr)
                if plan_state.startswith("BLOCKED") or plan_state.startswith("MISSED"):
                    geometry_state = "DIAGNOSTIC — NO ENTRY"
                elif trigger_rr >= 2.0 and max_rr >= 1.5:
                    geometry_state = "FAVOURABLE THROUGH ZONE"
                elif trigger_rr >= 2.0 and max_rr >= 1.0:
                    geometry_state = "FAVOURABLE AT TRIGGER / DETERIORATES WITH FILL"
                elif trigger_rr >= 1.5:
                    geometry_state = "MARGINAL / WATCH FILL PRICE"
                else:
                    geometry_state = "R:R CONFLICT"
                notes = (
                    "Structural stop = minimum of available EMA20 / prior-10 low / prior-20 low, "
                    f"then {stop_buffer_atr:.2f} ATR below support. T1={t1_r:.1f}R and T2={t2_r:.1f}R "
                    "are shadow references only. R:R is evaluated separately at trigger, zone-high and max-fill."
                )
        if not data_ok:
            stop = trigger_risk = zone_risk = max_risk = t1 = t2 = np.nan
            trigger_rr = zone_rr = max_rr = np.nan
            stop_distance_pct = stop_distance_atr = np.nan
            geometry_state = "NOT RANKED"
            notes = (
                "Required V1.3c structured-plan data or structural stop inputs are incomplete/invalid. "
                "No neutral risk or R:R value is imputed."
            )

        rows.append({
            "symbol": symbol,
            "official_bucket": r.get("bucket"),
            "official_setup": setup,
            "official_candidate_quality": r.get("quality_score"),
            "official_entry_quality": r.get("entry_score"),
            "official_decision": r.get("decision"),
            "plan_state": plan_state,
            "structured_plan": structured,
            "plan_data_confidence": confidence,
            "trigger_price": trigger,
            "entry_zone_low": zone_low,
            "entry_zone_high": zone_high,
            "max_acceptable_fill": max_fill,
            "ema20": ema20,
            "atr14": atr,
            "prior_10_low": prior_10_low,
            "prior_20_low": prior_20_low,
            "structural_support": support,
            "stop_buffer_atr": float(stop_buffer_atr),
            "stop_price": stop,
            "trigger_risk": trigger_risk,
            "zone_high_risk": zone_risk,
            "max_fill_risk": max_risk,
            "t1_price": t1,
            "t2_price": t2,
            "trigger_rr": trigger_rr,
            "zone_high_rr": zone_rr,
            "max_fill_rr": max_rr,
            "trigger_rr_band": _rr_band(trigger_rr),
            "zone_high_rr_band": _rr_band(zone_rr),
            "max_fill_rr_band": _rr_band(max_rr),
            "stop_distance_pct": stop_distance_pct,
            "stop_distance_atr": stop_distance_atr,
            "risk_geometry_state": geometry_state,
            "risk_reward_notes": notes,
        })

    return pd.DataFrame(rows, columns=RISK_REWARD_COLUMNS)


def summarize_risk_reward_diagnostics(rr: pd.DataFrame) -> dict:
    if rr is None or rr.empty:
        return {
            "evaluated": 0,
            "high_confidence": 0,
            "structured": 0,
            "strong_trigger_rr": 0,
            "acceptable_trigger_rr": 0,
            "weak_trigger_rr": 0,
            "poor_trigger_rr": 0,
            "not_ranked": 0,
        }
    bands = rr["trigger_rr_band"]
    return {
        "evaluated": int(len(rr)),
        "high_confidence": int((rr["plan_data_confidence"] == "HIGH").sum()),
        "structured": int(rr["structured_plan"].fillna(False).astype(bool).sum()),
        "strong_trigger_rr": int((bands == RR_STRONG).sum()),
        "acceptable_trigger_rr": int((bands == RR_ACCEPTABLE).sum()),
        "weak_trigger_rr": int((bands == RR_WEAK).sum()),
        "poor_trigger_rr": int((bands == RR_POOR).sum()),
        "not_ranked": int((bands == RR_NOT_RANKED).sum()),
    }
