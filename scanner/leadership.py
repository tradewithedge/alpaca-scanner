from __future__ import annotations

import numpy as np
import pandas as pd


LEADERSHIP_VERSION = "V1.2.1"


def _percentile_rank(series: pd.Series) -> pd.Series:
    """0-100 cross-sectional percentile with a neutral single-observation case."""
    s = pd.to_numeric(series, errors="coerce")
    valid = s.dropna()
    out = pd.Series(np.nan, index=s.index, dtype=float)
    n = len(valid)
    if n == 0:
        return out
    if n == 1:
        out.loc[valid.index] = 50.0
        return out

    ranks = valid.rank(method="average", ascending=True)
    out.loc[valid.index] = 100.0 * (ranks - 1.0) / (n - 1.0)
    return out.clip(0.0, 100.0)


def _safe_relative_return(ratio: pd.Series, periods: int) -> float:
    ratio = pd.to_numeric(ratio, errors="coerce").dropna()
    if len(ratio) <= periods:
        return np.nan
    base = float(ratio.iloc[-(periods + 1)])
    last = float(ratio.iloc[-1])
    if not np.isfinite(base) or not np.isfinite(last) or base <= 0:
        return np.nan
    return last / base - 1.0


def _symbol_leadership_features(
    symbol_bars: pd.DataFrame,
    benchmark_bars: pd.DataFrame,
    stress_threshold: float,
    stress_lookback: int,
    min_stress_days: int,
) -> dict:
    g = (
        symbol_bars[["timestamp", "close"]]
        .dropna()
        .sort_values("timestamp")
        .drop_duplicates("timestamp", keep="last")
        .rename(columns={"close": "stock_close"})
    )
    b = (
        benchmark_bars[["timestamp", "close"]]
        .dropna()
        .sort_values("timestamp")
        .drop_duplicates("timestamp", keep="last")
        .rename(columns={"close": "benchmark_close"})
    )

    z = g.merge(b, on="timestamp", how="inner")
    z = z[(z["stock_close"] > 0) & (z["benchmark_close"] > 0)].copy()

    if len(z) < 22:
        return {
            "leadership_aligned_bars": int(len(z)),
            "leadership_confidence": "LOW",
        }

    z["stock_ret1"] = z["stock_close"].pct_change()
    z["benchmark_ret1"] = z["benchmark_close"].pct_change()
    z["relative_line"] = z["stock_close"] / z["benchmark_close"]

    rel20 = _safe_relative_return(z["relative_line"], 20)
    rel50 = _safe_relative_return(z["relative_line"], 50)

    # Relative-strength acceleration compares the latest 20-session relative
    # move with the immediately preceding 20-session relative move.
    rel20_prev = np.nan
    ratio = z["relative_line"].dropna()
    if len(ratio) >= 41:
        start = float(ratio.iloc[-41])
        end = float(ratio.iloc[-21])
        if np.isfinite(start) and np.isfinite(end) and start > 0:
            rel20_prev = end / start - 1.0

    rs_accel = (
        rel20 - rel20_prev
        if np.isfinite(rel20) and np.isfinite(rel20_prev)
        else np.nan
    )

    # RS-line proximity to its recent high. This is deliberately relative-price
    # structure, not the stock's absolute-price 52-week-high distance.
    rs_window = ratio.tail(min(100, len(ratio)))
    if len(rs_window) and float(rs_window.max()) > 0:
        rs_high_gap = float(ratio.iloc[-1] / rs_window.max() - 1.0)
    else:
        rs_high_gap = np.nan

    # Market-pullback resilience: use genuine SPY stress sessions when there
    # are enough; otherwise use the worst benchmark sessions in the lookback
    # and disclose that fallback through stress_mode/confidence.
    stress_frame = z.tail(stress_lookback + 1).copy()
    stress_frame = stress_frame.dropna(
        subset=["stock_ret1", "benchmark_ret1"]
    )
    threshold_mask = stress_frame["benchmark_ret1"] <= stress_threshold
    threshold_count = int(threshold_mask.sum())

    if threshold_count >= min_stress_days:
        stress = stress_frame[threshold_mask].copy()
        stress_mode = "THRESHOLD"
    else:
        negative = stress_frame[stress_frame["benchmark_ret1"] < 0].copy()
        source = negative if len(negative) >= min_stress_days else stress_frame
        take = min(max(min_stress_days, 5), len(source))
        stress = source.nsmallest(take, "benchmark_ret1").copy()
        stress_mode = "WORST_DAYS_FALLBACK"

    if stress.empty:
        stress_excess_mean = np.nan
        stress_outperform = np.nan
        downside_capture = np.nan
        stress_count = 0
    else:
        stress["excess"] = stress["stock_ret1"] - stress["benchmark_ret1"]
        stress_excess_mean = float(stress["excess"].mean())
        stress_outperform = float((stress["excess"] > 0).mean())

        benchmark_down = float(
            (-stress["benchmark_ret1"].clip(upper=0)).sum()
        )
        stock_down = float((-stress["stock_ret1"].clip(upper=0)).sum())
        downside_capture = (
            stock_down / benchmark_down
            if benchmark_down > 0
            else np.nan
        )
        stress_count = int(len(stress))

    aligned = int(len(z))
    if aligned >= 100 and stress_mode == "THRESHOLD" and stress_count >= min_stress_days:
        confidence = "HIGH"
    elif aligned >= 55 and stress_count >= min_stress_days:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "leadership_aligned_bars": aligned,
        "rs_vs_spy_20": rel20,
        "rs_vs_spy_50": rel50,
        "rs_accel": rs_accel,
        "rs_line_high_gap": rs_high_gap,
        "stress_excess_mean": stress_excess_mean,
        "stress_outperform_rate": stress_outperform,
        "downside_capture": downside_capture,
        "stress_day_count": stress_count,
        "stress_mode": stress_mode,
        "leadership_confidence": confidence,
    }


def _grade(score: float | int | None) -> str:
    if score is None or pd.isna(score):
        return "N/A"
    score = float(score)
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def _explain(row: pd.Series) -> tuple[str, str]:
    reasons = []
    risks = []

    if row.get("leadership_score", 0) >= 90:
        reasons.append("elite cross-sectional leadership")
    elif row.get("leadership_score", 0) >= 80:
        reasons.append("strong cross-sectional leadership")

    if row.get("lead_rs20_pct", 0) >= 80:
        reasons.append("RS20 top quintile")
    if row.get("lead_rs50_pct", 0) >= 80:
        reasons.append("RS50 top quintile")

    stress_rate = row.get("stress_outperform_rate")
    if pd.notna(stress_rate):
        if stress_rate >= 0.65:
            reasons.append(
                f"outperformed SPY on {100 * stress_rate:.0f}% of stress days"
            )
        elif stress_rate < 0.40:
            risks.append(
                f"outperformed SPY on only {100 * stress_rate:.0f}% of stress days"
            )

    high_gap = row.get("rs_line_high_gap")
    if pd.notna(high_gap):
        if high_gap >= -0.02:
            reasons.append("RS line near 100D high")
        elif high_gap < -0.06:
            risks.append(f"RS line {100 * abs(high_gap):.1f}% below 100D high")

    accel = row.get("rs_accel")
    if pd.notna(accel):
        if accel > 0.01:
            reasons.append("relative momentum accelerating")
        elif accel < -0.01:
            risks.append("relative momentum decelerating")

    capture = row.get("downside_capture")
    if pd.notna(capture):
        if capture <= 0.70:
            reasons.append("low downside capture on SPY stress days")
        elif capture >= 1.20:
            risks.append("high downside capture on SPY stress days")

    if row.get("leadership_confidence") != "HIGH":
        risks.append(
            f"leadership data confidence {row.get('leadership_confidence', 'LOW')}"
        )

    return ", ".join(reasons), "; ".join(risks)


def add_leadership_features(
    cross_section: pd.DataFrame,
    bars: pd.DataFrame,
    benchmark_bars: pd.DataFrame,
    *,
    stress_threshold: float = -0.01,
    stress_lookback: int = 60,
    min_stress_days: int = 3,
) -> pd.DataFrame:
    """Attach V1.2.1 leadership/resilience features in SHADOW MODE.

    This function does NOT alter eligibility, buckets, entry scoring, or the
    existing candidate-quality score. It adds an independently auditable
    leadership subscore for validation before later promotion into the composite
    Candidate Quality Engine.
    """
    if cross_section is None or cross_section.empty:
        return cross_section.copy() if cross_section is not None else pd.DataFrame()

    required_bar_cols = {"symbol", "timestamp", "close"}
    if bars is None or bars.empty or not required_bar_cols.issubset(bars.columns):
        out = cross_section.copy()
        out["leadership_score"] = np.nan
        out["leadership_grade"] = "N/A"
        out["leadership_confidence"] = "LOW"
        out["leadership_reasons"] = ""
        out["leadership_risks"] = "missing stock history"
        return out

    if (
        benchmark_bars is None
        or benchmark_bars.empty
        or not {"timestamp", "close"}.issubset(benchmark_bars.columns)
    ):
        out = cross_section.copy()
        out["leadership_score"] = np.nan
        out["leadership_grade"] = "N/A"
        out["leadership_confidence"] = "LOW"
        out["leadership_reasons"] = ""
        out["leadership_risks"] = "missing SPY benchmark history"
        return out

    rows = []
    for symbol in cross_section["symbol"].astype(str):
        g = bars[bars["symbol"] == symbol]
        features = _symbol_leadership_features(
            g,
            benchmark_bars,
            stress_threshold,
            stress_lookback,
            min_stress_days,
        )
        features["symbol"] = symbol
        rows.append(features)

    feat = pd.DataFrame(rows)
    out = cross_section.merge(feat, on="symbol", how="left")

    # Cross-sectional percentile components. Keeping each component visible
    # makes the composite explainable and testable.
    out["lead_rs20_pct"] = _percentile_rank(out.get("rs_vs_spy_20"))
    out["lead_rs50_pct"] = _percentile_rank(out.get("rs_vs_spy_50"))
    out["lead_accel_pct"] = _percentile_rank(out.get("rs_accel"))
    out["lead_stress_excess_pct"] = _percentile_rank(
        out.get("stress_excess_mean")
    )
    out["lead_stress_win_pct"] = _percentile_rank(
        out.get("stress_outperform_rate")
    )
    out["lead_resilience_pct"] = (
        0.60 * out["lead_stress_excess_pct"]
        + 0.40 * out["lead_stress_win_pct"]
    )
    out["lead_rs_high_pct"] = _percentile_rank(out.get("rs_line_high_gap"))

    # V1.2.1 leadership composite:
    # 30% recent RS, 25% intermediate RS, 15% RS acceleration,
    # 20% market-pullback resilience, 10% RS-line high proximity.
    component_cols = [
        "lead_rs20_pct",
        "lead_rs50_pct",
        "lead_accel_pct",
        "lead_resilience_pct",
        "lead_rs_high_pct",
    ]
    weights = np.array([0.30, 0.25, 0.15, 0.20, 0.10], dtype=float)

    def weighted_score(row: pd.Series) -> float:
        vals = np.array(
            [pd.to_numeric(row.get(c), errors="coerce") for c in component_cols],
            dtype=float,
        )
        mask = np.isfinite(vals)
        if not mask.any():
            return np.nan
        w = weights[mask]
        return float(np.dot(vals[mask], w) / w.sum())

    out["leadership_score"] = out.apply(weighted_score, axis=1).clip(0, 100)
    out["leadership_grade"] = out["leadership_score"].map(_grade)

    explanations = out.apply(_explain, axis=1)
    out["leadership_reasons"] = [x[0] for x in explanations]
    out["leadership_risks"] = [x[1] for x in explanations]

    # User-facing percentage-point forms.
    for raw, display in [
        ("rs_vs_spy_20", "rs_vs_spy_20_pct"),
        ("rs_vs_spy_50", "rs_vs_spy_50_pct"),
        ("rs_accel", "rs_accel_pct"),
        ("rs_line_high_gap", "rs_line_high_gap_pct"),
        ("stress_excess_mean", "stress_excess_mean_pct"),
        ("stress_outperform_rate", "stress_outperform_pct"),
    ]:
        out[display] = 100.0 * pd.to_numeric(out.get(raw), errors="coerce")

    out["downside_capture_pct"] = (
        100.0 * pd.to_numeric(out.get("downside_capture"), errors="coerce")
    )

    return out
