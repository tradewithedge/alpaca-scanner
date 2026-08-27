from __future__ import annotations

import numpy as np
import pandas as pd


LEADERSHIP_VERSION = "V1.2.1.1"


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
    rel100 = _safe_relative_return(z["relative_line"], 100)

    # Interpretability view: compare today's 20-session RS with the same
    # 20-session RS calculation as of 10 trading sessions ago.
    ratio = z["relative_line"].dropna()
    rel20_10d_ago = np.nan
    if len(ratio) >= 31:
        old_base = float(ratio.iloc[-31])
        old_last = float(ratio.iloc[-11])
        if (
            np.isfinite(old_base)
            and np.isfinite(old_last)
            and old_base > 0
        ):
            rel20_10d_ago = old_last / old_base - 1.0

    rs20_change_10d = (
        rel20 - rel20_10d_ago
        if np.isfinite(rel20) and np.isfinite(rel20_10d_ago)
        else np.nan
    )

    # Legacy scoring acceleration is intentionally retained so V1.2.1.1 does
    # not change the already-validated shadow Leadership Score distribution.
    # It compares the latest 20-session relative move with the immediately
    # preceding 20-session relative move.
    rel20_prev = np.nan
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
        stress_win_count = 0
        downside_capture = np.nan
        stress_count = 0
    else:
        stress["excess"] = stress["stock_ret1"] - stress["benchmark_ret1"]
        stress_excess_mean = float(stress["excess"].mean())
        stress_win_count = int((stress["excess"] > 0).sum())
        stress_outperform = float(stress_win_count / len(stress))

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

    rs_line_index = (
        100.0 * (1.0 + rs_high_gap)
        if np.isfinite(rs_high_gap)
        else np.nan
    )

    if np.isfinite(downside_capture):
        capture_pct = 100.0 * downside_capture
        if capture_pct <= 70:
            capture_label = "EXCELLENT"
        elif capture_pct <= 90:
            capture_label = "GOOD"
        elif capture_pct <= 110:
            capture_label = "MARKET-LIKE"
        elif capture_pct <= 120:
            capture_label = "WEAKENING"
        else:
            capture_label = "POOR"
        capture_plain_english = (
            f"On selected SPY stress days, the stock lost about "
            f"{downside_capture:.2f}× as much as SPY in aggregate."
        )
    else:
        capture_label = "N/A"
        capture_plain_english = "Insufficient stress data for downside capture."

    return {
        "leadership_aligned_bars": aligned,
        "rs_vs_spy_20": rel20,
        "rs_vs_spy_50": rel50,
        "rs_vs_spy_100": rel100,
        "rs20_10d_ago": rel20_10d_ago,
        "rs20_change_10d": rs20_change_10d,
        "rs_accel": rs_accel,
        "rs_line_high_gap": rs_high_gap,
        "rs_line_index": rs_line_index,
        "stress_excess_mean": stress_excess_mean,
        "stress_outperform_rate": stress_outperform,
        "stress_win_count": stress_win_count,
        "downside_capture": downside_capture,
        "downside_capture_label": capture_label,
        "downside_capture_plain_english": capture_plain_english,
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


def _fmt_signed_pct(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{100.0 * float(value):+.1f}%"


def _fmt_signed_pp(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{100.0 * float(value):+.1f}pp"


def _explain(row: pd.Series) -> tuple[str, str]:
    reasons = []
    risks = []

    score = row.get("leadership_score")
    if pd.notna(score):
        if float(score) >= 90:
            reasons.append(f"elite leadership score {float(score):.1f}/100")
        elif float(score) >= 80:
            reasons.append(f"strong leadership score {float(score):.1f}/100")

    rel20 = row.get("rs_vs_spy_20")
    rel50 = row.get("rs_vs_spy_50")
    rel100 = row.get("rs_vs_spy_100")
    if pd.notna(rel20):
        reasons.append(f"20D vs SPY {_fmt_signed_pct(rel20)}")
    if pd.notna(rel50):
        reasons.append(f"50D vs SPY {_fmt_signed_pct(rel50)}")
    if pd.notna(rel100):
        reasons.append(f"100D vs SPY {_fmt_signed_pct(rel100)}")

    old_rs20 = row.get("rs20_10d_ago")
    now_rs20 = row.get("rs_vs_spy_20")
    rs20_change = row.get("rs20_change_10d")
    if pd.notna(old_rs20) and pd.notna(now_rs20) and pd.notna(rs20_change):
        phrase = (
            f"RS20 changed from {_fmt_signed_pct(old_rs20)} to "
            f"{_fmt_signed_pct(now_rs20)} over 10 sessions "
            f"({_fmt_signed_pp(rs20_change)})"
        )
        if float(rs20_change) >= 0.01:
            reasons.append("accelerating: " + phrase)
        elif float(rs20_change) <= -0.01:
            risks.append("decelerating: " + phrase)
        else:
            reasons.append("stable momentum: " + phrase)

    stress_count = int(row.get("stress_day_count", 0) or 0)
    stress_wins = int(row.get("stress_win_count", 0) or 0)
    stress_rate = row.get("stress_outperform_rate")
    stress_excess = row.get("stress_excess_mean")
    if stress_count > 0 and pd.notna(stress_rate):
        stress_text = (
            f"beat SPY on {stress_wins}/{stress_count} stress sessions "
            f"({100.0 * float(stress_rate):.0f}%)"
        )
        if pd.notna(stress_excess):
            stress_text += (
                f"; average excess return "
                f"{100.0 * float(stress_excess):+.2f}%"
            )

        if float(stress_rate) >= 0.65:
            reasons.append(stress_text)
        elif float(stress_rate) < 0.40:
            risks.append(stress_text)
        else:
            reasons.append("mixed stress resilience: " + stress_text)

    high_gap = row.get("rs_line_high_gap")
    rs_index = row.get("rs_line_index")
    if pd.notna(high_gap) and pd.notna(rs_index):
        rs_line_text = (
            f"RS-line index {float(rs_index):.1f}/100 "
            f"({100.0 * abs(float(high_gap)):.1f}% below its 100D peak)"
        )
        if float(high_gap) >= -0.02:
            reasons.append(rs_line_text)
        elif float(high_gap) < -0.06:
            risks.append(rs_line_text)
        else:
            reasons.append(rs_line_text)

    capture = row.get("downside_capture")
    capture_label = row.get("downside_capture_label", "N/A")
    if pd.notna(capture):
        capture_text = (
            f"downside capture {100.0 * float(capture):.0f}% "
            f"({capture_label}); stock lost about "
            f"{float(capture):.2f}× as much as SPY on stress days"
        )
        if float(capture) <= 0.70:
            reasons.append(capture_text)
        elif float(capture) >= 1.20:
            risks.append(capture_text)
        else:
            reasons.append(capture_text)

    if row.get("leadership_confidence") != "HIGH":
        risks.append(
            f"Leadership Data Confidence "
            f"{row.get('leadership_confidence', 'LOW')}"
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
        ("rs_vs_spy_100", "rs_vs_spy_100_pct"),
        ("rs20_10d_ago", "rs20_10d_ago_pct"),
        ("rs20_change_10d", "rs20_change_10d_pp"),
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
