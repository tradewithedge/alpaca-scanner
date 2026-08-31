from __future__ import annotations

import math

import numpy as np
import pandas as pd


COMPOSITE_VERSION = "V1.2.3"

REFERENCE_WEIGHTS = {
    "candidate_quality": 0.70,
    "leadership": 0.30,
}

COMPOSITE_SCENARIOS = {
    "F10": {
        "candidate_quality": 0.63,
        "leadership": 0.27,
        "fundamental": 0.10,
    },
    "F20": {
        "candidate_quality": 0.56,
        "leadership": 0.24,
        "fundamental": 0.20,
    },
    "F30": {
        "candidate_quality": 0.49,
        "leadership": 0.21,
        "fundamental": 0.30,
    },
}


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


def _usable_fundamental(row: pd.Series) -> bool:
    return (
        str(row.get("batch_status") or "").upper() == "PASS"
        and str(row.get("metric_integrity") or "").upper() == "PASS"
        and str(row.get("companyfacts") or "").upper() == "PASS"
        and str(row.get("fundamental_confidence") or "UNKNOWN").upper()
        in {"HIGH", "MEDIUM"}
        and _finite(row.get("fundamental_score"))
    )


def _quality_profile(row: pd.Series) -> str:
    if not _usable_fundamental(row):
        return "FUNDAMENTAL REVIEW — NO FULL COMPOSITE"

    cq = row.get("official_candidate_quality")
    leadership = row.get("leadership_score")
    fundamental = row.get("fundamental_score")

    if not (_finite(cq) and _finite(leadership) and _finite(fundamental)):
        return "INCOMPLETE QUALITY REFERENCE"

    cq = float(cq)
    leadership = float(leadership)
    fundamental = float(fundamental)

    if cq >= 90 and leadership >= 80 and fundamental >= 80:
        return "FULL ALIGNMENT"
    if cq >= 90 and leadership >= 80 and fundamental < 60:
        return "TECHNICAL-LED / WEAK FUNDAMENTALS"
    if cq >= 90 and leadership >= 80 and fundamental < 80:
        return "TECHNICAL-LED / MIXED FUNDAMENTALS"
    if cq >= 90 and fundamental >= 80 and leadership < 80:
        return "FUNDAMENTAL-CONFIRMED / LEADERSHIP MIXED"
    if leadership >= 80 and fundamental >= 80:
        return "QUALITY ALIGNMENT / TECHNICAL MIXED"
    return "MIXED QUALITY"


def _weighted_score(cq, leadership, fundamental, weights):
    if not (_finite(cq) and _finite(leadership) and _finite(fundamental)):
        return np.nan

    return (
        float(cq) * float(weights["candidate_quality"])
        + float(leadership) * float(weights["leadership"])
        + float(fundamental) * float(weights["fundamental"])
    )


def build_shadow_composite_table(batch_table: pd.DataFrame) -> pd.DataFrame:
    """Build V1.2.3 shadow scores while preserving all official fields.

    Fundamental REVIEW/FAIL/unavailable rows never receive an imputed score.
    """
    if batch_table is None or batch_table.empty:
        return pd.DataFrame()

    out = batch_table.copy(deep=True)

    for col in (
        "official_candidate_quality",
        "leadership_score",
        "fundamental_score",
    ):
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")

    if "symbol" not in out.columns:
        out["symbol"] = ""
    out["symbol"] = out["symbol"].astype(str).str.upper()

    out["technical_leadership_reference"] = np.where(
        out["official_candidate_quality"].notna()
        & out["leadership_score"].notna(),
        (
            REFERENCE_WEIGHTS["candidate_quality"]
            * out["official_candidate_quality"]
            + REFERENCE_WEIGHTS["leadership"]
            * out["leadership_score"]
        ),
        np.nan,
    )
    out["technical_leadership_reference"] = pd.to_numeric(
        out["technical_leadership_reference"],
        errors="coerce",
    ).round(1)

    usable = out.apply(_usable_fundamental, axis=1)

    for scenario, weights in COMPOSITE_SCENARIOS.items():
        col = f"shadow_{scenario.lower()}"
        out[col] = np.nan
        out.loc[usable, col] = out.loc[usable].apply(
            lambda row: _weighted_score(
                row.get("official_candidate_quality"),
                row.get("leadership_score"),
                row.get("fundamental_score"),
                weights,
            ),
            axis=1,
        )
        out[col] = pd.to_numeric(out[col], errors="coerce").round(1)

    out["shadow_f20_grade"] = out["shadow_f20"].apply(_grade)
    out["f20_impact_pts"] = (
        out["shadow_f20"] - out["technical_leadership_reference"]
    ).round(1)

    out["scenario_spread_pts"] = (
        out[["shadow_f10", "shadow_f20", "shadow_f30"]].max(
            axis=1,
            skipna=False,
        )
        - out[["shadow_f10", "shadow_f20", "shadow_f30"]].min(
            axis=1,
            skipna=False,
        )
    ).round(1)

    out["quality_profile"] = out.apply(_quality_profile, axis=1)

    out["official_rank"] = np.nan
    out["shadow_f20_rank"] = np.nan
    out["rank_change"] = np.nan

    rankable = out["shadow_f20"].notna()
    if rankable.any():
        out.loc[rankable, "official_rank"] = (
            out.loc[rankable, "official_candidate_quality"]
            .rank(method="min", ascending=False)
        )
        out.loc[rankable, "shadow_f20_rank"] = (
            out.loc[rankable, "shadow_f20"]
            .rank(method="min", ascending=False)
        )
        # Positive = promoted by the shadow F20 ranking.
        out.loc[rankable, "rank_change"] = (
            out.loc[rankable, "official_rank"]
            - out.loc[rankable, "shadow_f20_rank"]
        )

    return out


def summarize_shadow_composite(composite: pd.DataFrame) -> dict:
    if composite is None or composite.empty:
        return {
            "total": 0,
            "rankable": 0,
            "top_n": 0,
            "top10_overlap": 0,
            "spearman_corr": None,
            "median_abs_rank_shift": None,
            "mean_abs_f20_impact": None,
            "full_alignment": 0,
            "unranked_fundamental_review": 0,
        }

    total = int(len(composite))
    rankable = composite[
        pd.to_numeric(composite["shadow_f20"], errors="coerce").notna()
    ].copy()
    n = int(len(rankable))
    top_n = min(10, n)

    if top_n:
        official_top = set(
            rankable.nlargest(top_n, "official_candidate_quality")["symbol"]
        )
        shadow_top = set(
            rankable.nlargest(top_n, "shadow_f20")["symbol"]
        )
        top_overlap = int(len(official_top & shadow_top))
    else:
        top_overlap = 0

    if n >= 2:
        corr = rankable[
            ["official_candidate_quality", "shadow_f20"]
        ].corr(method="spearman").iloc[0, 1]
        spearman = float(corr) if _finite(corr) else None
    else:
        spearman = None

    shifts = pd.to_numeric(
        rankable["rank_change"],
        errors="coerce",
    ).dropna()
    impacts = pd.to_numeric(
        rankable["f20_impact_pts"],
        errors="coerce",
    ).dropna()

    return {
        "total": total,
        "rankable": n,
        "top_n": top_n,
        "top10_overlap": top_overlap,
        "spearman_corr": round(spearman, 3) if spearman is not None else None,
        "median_abs_rank_shift": (
            round(float(shifts.abs().median()), 1)
            if not shifts.empty
            else None
        ),
        "mean_abs_f20_impact": (
            round(float(impacts.abs().mean()), 1)
            if not impacts.empty
            else None
        ),
        "full_alignment": int(
            (composite["quality_profile"] == "FULL ALIGNMENT").sum()
        ),
        "unranked_fundamental_review": int(total - n),
    }
