from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .composite_robustness import (
    build_composite_robustness_table,
    summarize_composite_robustness,
)


COMPOSITE_ARCHITECTURE_VERSION = "V1.2.3c"

# V1.2.3c selected architecture. Keep exact internal weights; presentation may
# describe these approximately as 60% / 25% / 15% only for readability.
SELECTED_WEIGHTS = {
    "candidate_quality": 0.595,
    "leadership": 0.255,
    "fundamental": 0.150,
}
SELECTED_FUNDAMENTAL_WEIGHT = 0.15
SHADOW_SENSITIVITY_WEIGHT = 0.20

# Explainability guardrail only. These thresholds classify the magnitude of the
# incremental Fundamental contribution to F15. They DO NOT cap or alter scores.
MATERIAL_IMPACT_THRESHOLD = 4.0
HIGH_IMPACT_THRESHOLD = 6.0


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def _grade(score) -> str:
    if not _finite(score):
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


def fundamental_impact_state(impact_pts) -> str:
    """Classify F15 Fundamental influence without changing the score.

    NORMAL       : |impact| < 4 points
    MATERIAL     : 4 <= |impact| <= 6 points
    HIGH IMPACT  : |impact| > 6 points
    """
    if not _finite(impact_pts):
        return "N/A"
    magnitude = abs(float(impact_pts))
    if magnitude > HIGH_IMPACT_THRESHOLD:
        return "HIGH IMPACT"
    if magnitude >= MATERIAL_IMPACT_THRESHOLD:
        return "MATERIAL"
    return "NORMAL"


def fundamental_impact_direction(impact_pts) -> str:
    if not _finite(impact_pts):
        return "N/A"
    impact = float(impact_pts)
    if impact > 1e-12:
        return "PROMOTION"
    if impact < -1e-12:
        return "PENALTY"
    return "NEUTRAL"


def _formula_f15(cq, leadership, fundamental):
    if not (_finite(cq) and _finite(leadership) and _finite(fundamental)):
        return np.nan
    return (
        SELECTED_WEIGHTS["candidate_quality"] * float(cq)
        + SELECTED_WEIGHTS["leadership"] * float(leadership)
        + SELECTED_WEIGHTS["fundamental"] * float(fundamental)
    )


def build_selected_composite_table(batch_table: pd.DataFrame) -> pd.DataFrame:
    """Build V1.2.3c F15 selected-architecture shadow table.

    Design discipline
    -----------------
    * Reuse V1.2.3b1 full-precision F15 calculations and accepted F20 anchors.
    * F15 = 59.5% Candidate Quality + 25.5% Leadership + 15% Fundamental.
    * F20 remains a shadow sensitivity benchmark only.
    * No hard Fundamental-impact cap is applied.
    * REVIEW/FAIL/unavailable fundamentals remain unranked; no imputation.
    * This function does not modify scanner ranking, buckets, Entry Quality, or
      trade decisions.
    """
    robust = build_composite_robustness_table(batch_table)
    if robust is None or robust.empty:
        return pd.DataFrame()

    out = robust.copy(deep=True)

    cq = pd.to_numeric(out.get("official_candidate_quality"), errors="coerce")
    leadership = pd.to_numeric(out.get("leadership_score"), errors="coerce")
    fundamental = pd.to_numeric(out.get("fundamental_score"), errors="coerce")

    # V1.2.3b1 is the full-precision authority for F15 interpolation.
    out["composite_f15_exact"] = pd.to_numeric(
        out.get("score_f15_exact"), errors="coerce"
    )
    out["composite_f15"] = pd.to_numeric(
        out.get("score_f15"), errors="coerce"
    )
    out["composite_f15_rank"] = pd.to_numeric(
        out.get("rank_f15"), errors="coerce"
    )
    out["composite_f15_grade"] = out["composite_f15"].apply(_grade)

    # Accepted V1.2.3a F20 anchor remains the sensitivity benchmark.
    out["shadow_f20_reference"] = pd.to_numeric(
        out.get("shadow_f20"), errors="coerce"
    )
    out["shadow_f20_reference_rank"] = pd.to_numeric(
        out.get("f20_rank"), errors="coerce"
    )

    out["f15_fund_impact_exact_pts"] = pd.to_numeric(
        out.get("fund_score_impact_f15_exact_pts"), errors="coerce"
    )
    out["f15_fund_impact_pts"] = out["f15_fund_impact_exact_pts"].round(1)
    out["fundamental_impact_state"] = out["f15_fund_impact_exact_pts"].apply(
        fundamental_impact_state
    )
    out["fundamental_impact_direction"] = out[
        "f15_fund_impact_exact_pts"
    ].apply(fundamental_impact_direction)
    out["fundamental_impact_label"] = np.where(
        out["fundamental_impact_state"].eq("N/A"),
        "N/A",
        out["fundamental_impact_state"].astype(str)
        + " — "
        + out["fundamental_impact_direction"].astype(str),
    )

    rankable = out["composite_f15_exact"].notna()
    out["composite_status"] = np.where(
        rankable,
        "F15 SHADOW RANKABLE",
        "NO FULL COMPOSITE — FUNDAMENTAL REVIEW/UNAVAILABLE",
    )

    # Independent exact-formula audit. Never rank on this duplicate calculation;
    # it exists only to prove the selected formula matches the b1 F15 authority.
    out["f15_formula_audit_exact"] = [
        _formula_f15(c, l, f) for c, l, f in zip(cq, leadership, fundamental)
    ]
    audit_delta = (
        pd.to_numeric(out["composite_f15_exact"], errors="coerce")
        - pd.to_numeric(out["f15_formula_audit_exact"], errors="coerce")
    ).abs()
    out["f15_formula_match"] = np.where(
        rankable,
        audit_delta <= 1e-10,
        True,
    )

    # Sensitivity diagnostics only; positive means F20 ranks the name better
    # (smaller numeric rank) than F15. No score is changed by this diagnostic.
    out["f20_vs_f15_rank_shift"] = (
        out["composite_f15_rank"] - out["shadow_f20_reference_rank"]
    )

    return out


def summarize_selected_composite(selected: pd.DataFrame) -> dict:
    if selected is None or selected.empty:
        return {
            "total": 0,
            "rankable": 0,
            "normal": 0,
            "material": 0,
            "high_impact": 0,
            "median_abs_f15_fund_impact": None,
            "mean_abs_f15_fund_impact": None,
            "f15_f20_top10_overlap": 0,
            "f15_f20_spearman": None,
            "f15_formula_integrity_pass": False,
            "anchor_integrity_pass": False,
            "no_hard_cap": True,
        }

    total = int(len(selected))
    rankable = selected[
        pd.to_numeric(selected.get("composite_f15_exact"), errors="coerce").notna()
    ].copy()
    n = int(len(rankable))

    impacts = pd.to_numeric(
        rankable.get("f15_fund_impact_exact_pts"), errors="coerce"
    ).abs().dropna()

    states = rankable.get(
        "fundamental_impact_state", pd.Series(dtype=str)
    ).astype(str)

    top_n = min(10, n)
    if top_n:
        f15_top = set(rankable.nsmallest(top_n, "composite_f15_rank")["symbol"])
        f20_top = set(
            rankable.nsmallest(top_n, "shadow_f20_reference_rank")["symbol"]
        )
        top_overlap = int(len(f15_top & f20_top))
    else:
        top_overlap = 0

    corr = None
    if n >= 2:
        value = rankable[
            ["composite_f15_exact", "shadow_f20_reference"]
        ].corr(method="spearman").iloc[0, 1]
        if _finite(value):
            corr = float(value)

    formula_integrity = bool(
        selected.get("f15_formula_match", pd.Series(dtype=bool))
        .fillna(False)
        .astype(bool)
        .all()
    )

    # Preserve the b1 anchor-integrity result as an explicit V1.2.3c gate.
    robust_summary = summarize_composite_robustness(selected)

    return {
        "total": total,
        "rankable": n,
        "normal": int(states.eq("NORMAL").sum()),
        "material": int(states.eq("MATERIAL").sum()),
        "high_impact": int(states.eq("HIGH IMPACT").sum()),
        "median_abs_f15_fund_impact": (
            None if impacts.empty else round(float(impacts.median()), 2)
        ),
        "mean_abs_f15_fund_impact": (
            None if impacts.empty else round(float(impacts.mean()), 2)
        ),
        "f15_f20_top10_overlap": top_overlap,
        "f15_f20_spearman": None if corr is None else round(corr, 3),
        "f15_formula_integrity_pass": formula_integrity,
        "anchor_integrity_pass": bool(
            robust_summary.get("anchor_integrity_pass", False)
        ),
        "no_hard_cap": True,
    }
