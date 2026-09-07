from __future__ import annotations

from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from .indicators import add_indicators


ET = ZoneInfo("America/New_York")
SESSION_FINAL_TIME_ET = time(16, 30)
MIN_HIGH_CONF_BARS = 60
MIN_MEDIUM_CONF_BARS = 35


VOLUME_DIAGNOSTIC_COLUMNS = [
    "symbol",
    "official_bucket",
    "official_setup",
    "official_candidate_quality",
    "official_entry_quality",
    "price_context",
    "eval_session",
    "partial_session_excluded",
    "completed_bars",
    "rvol_20",
    "vol5_vs_prior20",
    "vol10_vs_prior20",
    "up_down_vol_ratio_10",
    "up_volume_share_10_pct",
    "accumulation_days_10",
    "distribution_days_10",
    "volume_trend_5",
    "volume_trend_10",
    "contextual_volume_state",
    "volume_data_confidence",
    "volume_notes",
]


def _asof_utc(asof_utc: datetime | pd.Timestamp | None) -> pd.Timestamp:
    if asof_utc is None:
        return pd.Timestamp(datetime.now(timezone.utc))
    ts = pd.Timestamp(asof_utc)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def completed_session_bars(
    bars: pd.DataFrame,
    *,
    asof_utc: datetime | pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, bool]:
    """Return only sessions safe to treat as completed for daily-volume analysis.

    Alpaca 1Day history can expose the current regular-session daily bar once the
    query end passes the Basic-plan delay window. V1.3a deliberately excludes a
    same-day bar until 16:30 ET so a partial daily volume bar cannot be compared
    with full historical sessions.
    """
    if bars is None or bars.empty:
        return pd.DataFrame(columns=getattr(bars, "columns", None)), False

    g = bars.copy(deep=True)
    g["timestamp"] = pd.to_datetime(g["timestamp"], utc=True, errors="coerce")
    g = g[g["timestamp"].notna()].sort_values("timestamp").reset_index(drop=True)
    if g.empty:
        return g, False

    asof = _asof_utc(asof_utc)
    asof_et = asof.tz_convert(ET)
    last_et = g.iloc[-1]["timestamp"].tz_convert(ET)
    same_calendar_session = last_et.date() == asof_et.date()
    before_safe_close = asof_et.time().replace(tzinfo=None) < SESSION_FINAL_TIME_ET

    excluded = bool(same_calendar_session and before_safe_close)
    if excluded:
        g = g.iloc[:-1].copy().reset_index(drop=True)
    return g, excluded


def _safe_ratio(numerator: float | int | None, denominator: float | int | None):
    if numerator is None or denominator is None:
        return np.nan
    if pd.isna(numerator) or pd.isna(denominator) or float(denominator) <= 0:
        return np.nan
    return float(numerator) / float(denominator)


def _volume_trend_label(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if value <= 0.75:
        return "STRONG DRY-UP"
    if value <= 0.90:
        return "DRYING UP"
    if value < 1.10:
        return "STABLE"
    if value < 1.30:
        return "EXPANDING"
    return "STRONG EXPANSION"


def _price_context(ind: pd.DataFrame) -> str:
    """Classify price structure without using the new volume diagnostics."""
    if ind is None or ind.empty:
        return "NO CLEAN SETUP"
    r = ind.iloc[-1]

    close = r.get("close")
    ema20 = r.get("ema20")
    ma50 = r.get("ma50")
    high20_prev = r.get("high20_prev")
    range5 = r.get("range5")
    range20 = r.get("range20")
    atr5 = r.get("atr5")
    atr20 = r.get("atr20")
    slope20 = r.get("ma20_slope5")

    if pd.isna(close):
        return "NO CLEAN SETUP"

    above20 = pd.notna(ema20) and close > ema20
    above50 = pd.notna(ma50) and close > ma50
    ext20 = 100.0 * (close / ema20 - 1.0) if pd.notna(ema20) and ema20 else np.nan

    if not above50:
        return "BROKEN / BELOW MA50"

    breakout = (
        pd.notna(high20_prev)
        and close > float(high20_prev) * 1.001
        and above20
        and above50
    )
    if breakout:
        return "BREAKOUT"

    near20 = pd.notna(ext20) and -1.5 <= ext20 <= 3.5
    if near20 and (float(slope20) if pd.notna(slope20) else 0.0) > 0:
        return "EMA20 PULLBACK"

    contraction = (
        pd.notna(atr5)
        and pd.notna(atr20)
        and float(atr20) > 0
        and float(atr5) / float(atr20) < 0.78
        and pd.notna(range5)
        and pd.notna(range20)
        and float(range20) > 0
        and float(range5) / float(range20) < 0.78
    )
    if contraction and above20:
        return "VCP / TIGHTENING"

    if above20 and pd.notna(range20) and float(range20) < 0.10:
        return "TIGHT BASE"

    if not above20:
        return "MA20 REPAIR WINDOW"

    return "NO CLEAN SETUP"


def _confidence(g: pd.DataFrame) -> str:
    if g is None or g.empty or "volume" not in g.columns:
        return "LOW"
    recent = pd.to_numeric(g["volume"].tail(30), errors="coerce")
    valid = recent.notna() & (recent > 0)
    valid_pct = float(valid.mean()) if len(recent) else 0.0
    n = int(len(g))

    if n >= MIN_HIGH_CONF_BARS and len(recent) >= 30 and valid_pct >= 0.97:
        return "HIGH"
    if n >= MIN_MEDIUM_CONF_BARS and len(recent) >= 25 and valid_pct >= 0.90:
        return "MEDIUM"
    return "LOW"


def _participation_metrics(ind: pd.DataFrame) -> dict:
    volume = pd.to_numeric(ind["volume"], errors="coerce")
    close = pd.to_numeric(ind["close"], errors="coerce")

    current = volume.iloc[-1] if len(volume) else np.nan
    prior20 = volume.iloc[-21:-1] if len(volume) >= 21 else pd.Series(dtype=float)
    rvol20 = _safe_ratio(current, prior20.mean() if len(prior20) == 20 else np.nan)

    recent5 = volume.iloc[-5:] if len(volume) >= 5 else pd.Series(dtype=float)
    base5 = volume.iloc[-25:-5] if len(volume) >= 25 else pd.Series(dtype=float)
    vol5 = _safe_ratio(
        recent5.mean() if len(recent5) == 5 else np.nan,
        base5.mean() if len(base5) == 20 else np.nan,
    )

    recent10 = volume.iloc[-10:] if len(volume) >= 10 else pd.Series(dtype=float)
    base10 = volume.iloc[-30:-10] if len(volume) >= 30 else pd.Series(dtype=float)
    vol10 = _safe_ratio(
        recent10.mean() if len(recent10) == 10 else np.nan,
        base10.mean() if len(base10) == 20 else np.nan,
    )

    ret1 = close.pct_change()
    last10 = ind.tail(10).copy()
    last10["ret1"] = ret1.tail(10).values
    last10["volume_num"] = pd.to_numeric(last10["volume"], errors="coerce")
    up_volume = last10.loc[last10["ret1"] > 0, "volume_num"].sum(min_count=1)
    down_volume = last10.loc[last10["ret1"] < 0, "volume_num"].sum(min_count=1)
    up_down = _safe_ratio(up_volume, down_volume)
    total_directional = (
        (0.0 if pd.isna(up_volume) else float(up_volume))
        + (0.0 if pd.isna(down_volume) else float(down_volume))
    )
    up_share = (
        100.0 * float(up_volume) / total_directional
        if total_directional > 0 and pd.notna(up_volume)
        else np.nan
    )

    prior_avg20 = volume.shift(1).rolling(20).mean()
    accumulation = (
        (ret1 >= 0.005)
        & (volume >= 1.20 * prior_avg20)
        & prior_avg20.notna()
    )
    distribution = (
        (ret1 <= -0.005)
        & (volume >= 1.20 * prior_avg20)
        & prior_avg20.notna()
    )

    return {
        "rvol_20": rvol20,
        "vol5_vs_prior20": vol5,
        "vol10_vs_prior20": vol10,
        "up_down_vol_ratio_10": up_down,
        "up_volume_share_10_pct": up_share,
        "accumulation_days_10": int(accumulation.tail(10).sum()),
        "distribution_days_10": int(distribution.tail(10).sum()),
        "volume_trend_5": _volume_trend_label(vol5),
        "volume_trend_10": _volume_trend_label(vol10),
    }


def _interpret(context: str, metrics: dict, confidence: str) -> tuple[str, str]:
    if confidence == "LOW":
        return (
            "NOT RANKED",
            "Insufficient completed-session volume history for a trusted contextual conclusion.",
        )

    rvol = metrics.get("rvol_20")
    vol5 = metrics.get("vol5_vs_prior20")
    up_down = metrics.get("up_down_vol_ratio_10")
    accum = int(metrics.get("accumulation_days_10", 0) or 0)
    dist = int(metrics.get("distribution_days_10", 0) or 0)

    dist_warning = dist >= 2 and dist > accum

    if context == "BREAKOUT":
        if pd.notna(rvol) and rvol >= 1.20 and not dist_warning:
            return "CONFIRMING", f"Breakout participation expanded to {rvol:.2f}x prior-20D volume."
        if pd.notna(rvol) and rvol >= 1.00 and not dist_warning:
            return "MIXED", f"Breakout participation is only moderate at {rvol:.2f}x prior-20D volume."
        note = "Breakout lacks convincing volume expansion"
        if pd.notna(rvol):
            note += f" ({rvol:.2f}x)"
        if dist_warning:
            note += "; recent distribution is elevated"
        return "CONFLICT / WATCH", note + "."

    if context in {"EMA20 PULLBACK", "VCP / TIGHTENING", "TIGHT BASE"}:
        dry = pd.notna(vol5) and vol5 <= 0.90
        latest_controlled = pd.notna(rvol) and rvol <= 1.05
        if dry and latest_controlled and not dist_warning:
            return (
                "CONFIRMING",
                f"Volume is contracting constructively: 5D/prior20={vol5:.2f}x, latest RVOL={rvol:.2f}x.",
            )
        if not dist_warning and (
            (pd.notna(vol5) and vol5 <= 1.05)
            or (pd.notna(rvol) and rvol <= 1.10)
        ):
            return "MIXED", "Volume is controlled but not yet a strong dry-up signal."
        note = "Volume is not contracting cleanly for this structure"
        if dist_warning:
            note += "; recent distribution is elevated"
        return "CONFLICT / WATCH", note + "."

    if context == "MA20 REPAIR WINDOW":
        if dist_warning:
            return "CONFLICT / WATCH", "Repair structure is accompanied by elevated distribution volume."
        return "DIAGNOSTIC ONLY", "Repair context: volume is displayed for evidence, not treated as confirmation."

    if context == "BROKEN / BELOW MA50":
        return "DIAGNOSTIC ONLY", "Broken price structure cannot be rescued by favorable volume diagnostics."

    if dist_warning:
        return "CONFLICT / WATCH", "No clean price setup and recent distribution volume is elevated."
    if pd.notna(up_down) and up_down >= 1.25 and accum >= dist:
        return "DIAGNOSTIC ONLY", "Constructive participation exists, but price structure is not yet a clean setup."
    return "DIAGNOSTIC ONLY", "No clean setup; retain raw volume diagnostics without a positive confirmation label."


def _official_map(scored: pd.DataFrame | None) -> dict[str, dict]:
    if scored is None or scored.empty or "symbol" not in scored.columns:
        return {}
    out = {}
    for _, r in scored.iterrows():
        symbol = str(r.get("symbol", "")).upper()
        if not symbol:
            continue
        out[symbol] = {
            "official_bucket": r.get("bucket"),
            "official_setup": r.get("setup"),
            "official_candidate_quality": r.get("quality_score"),
            "official_entry_quality": r.get("entry_score"),
        }
    return out


def build_contextual_volume_quality(
    scored: pd.DataFrame,
    bars: pd.DataFrame,
    *,
    asof_utc: datetime | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Build V1.3a contextual volume diagnostics without mutating official data.

    The function intentionally returns a separate table. It never writes volume
    features back into `scored`, so Candidate Quality, Entry Quality, buckets and
    trade decisions remain frozen.
    """
    if scored is None or scored.empty:
        return pd.DataFrame(columns=VOLUME_DIAGNOSTIC_COLUMNS)
    if bars is None or bars.empty or "symbol" not in bars.columns:
        return pd.DataFrame(columns=VOLUME_DIAGNOSTIC_COLUMNS)

    official = _official_map(scored.copy(deep=True))
    source_bars = bars.copy(deep=True)
    rows = []

    for symbol in scored["symbol"].astype(str).str.upper().tolist():
        g0 = source_bars[source_bars["symbol"].astype(str).str.upper() == symbol].copy()
        completed, partial_excluded = completed_session_bars(g0, asof_utc=asof_utc)

        base = {
            "symbol": symbol,
            **official.get(symbol, {}),
            "partial_session_excluded": partial_excluded,
            "completed_bars": int(len(completed)),
        }

        if completed.empty:
            base.update(
                {
                    "price_context": "NO CLEAN SETUP",
                    "eval_session": None,
                    "rvol_20": np.nan,
                    "vol5_vs_prior20": np.nan,
                    "vol10_vs_prior20": np.nan,
                    "up_down_vol_ratio_10": np.nan,
                    "up_volume_share_10_pct": np.nan,
                    "accumulation_days_10": 0,
                    "distribution_days_10": 0,
                    "volume_trend_5": "N/A",
                    "volume_trend_10": "N/A",
                    "contextual_volume_state": "NOT RANKED",
                    "volume_data_confidence": "LOW",
                    "volume_notes": "No completed-session bars available.",
                }
            )
            rows.append(base)
            continue

        ind = add_indicators(completed)
        context = _price_context(ind)
        confidence = _confidence(ind)
        metrics = _participation_metrics(ind)
        state, notes = _interpret(context, metrics, confidence)
        eval_ts = ind.iloc[-1]["timestamp"]
        eval_session = eval_ts.tz_convert(ET).date().isoformat() if pd.notna(eval_ts) else None

        base.update(
            {
                "price_context": context,
                "eval_session": eval_session,
                **metrics,
                "contextual_volume_state": state,
                "volume_data_confidence": confidence,
                "volume_notes": notes,
            }
        )
        rows.append(base)

    table = pd.DataFrame(rows)
    for col in VOLUME_DIAGNOSTIC_COLUMNS:
        if col not in table.columns:
            table[col] = np.nan
    return table[VOLUME_DIAGNOSTIC_COLUMNS].copy()


def summarize_contextual_volume_quality(table: pd.DataFrame) -> dict:
    if table is None or table.empty:
        return {
            "evaluated": 0,
            "high_confidence": 0,
            "breakout_contexts": 0,
            "pullback_base_contexts": 0,
            "confirming": 0,
            "conflict_watch": 0,
            "distribution_watch": 0,
            "partial_excluded": 0,
        }

    context = table["price_context"].astype(str)
    state = table["contextual_volume_state"].astype(str)
    dist = pd.to_numeric(table["distribution_days_10"], errors="coerce").fillna(0)
    return {
        "evaluated": int(len(table)),
        "high_confidence": int((table["volume_data_confidence"] == "HIGH").sum()),
        "breakout_contexts": int((context == "BREAKOUT").sum()),
        "pullback_base_contexts": int(
            context.isin(["EMA20 PULLBACK", "VCP / TIGHTENING", "TIGHT BASE"]).sum()
        ),
        "confirming": int((state == "CONFIRMING").sum()),
        "conflict_watch": int((state == "CONFLICT / WATCH").sum()),
        "distribution_watch": int((dist >= 2).sum()),
        "partial_excluded": int(table["partial_session_excluded"].fillna(False).astype(bool).sum()),
    }
