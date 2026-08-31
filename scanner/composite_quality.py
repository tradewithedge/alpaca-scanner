from __future__ import annotations

import math

import numpy as np
import pandas as pd


COMPOSITE_VERSION = "V1.2.3a"

REFERENCE_WEIGHTS = {
    "candidate_quality": 0.70,
    "leadership": 0.30,
}

# Unchanged from V1.2.3.
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


def _rank_desc(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").rank(
        method="min",
        ascending=False,
    )


def _top_overlap(df: pd.DataFrame, left: str, right: str, top_n: int) -> int:
    if top_n <= 0:
        return 0
    return int(
        len(
            set(df.nlargest(top_n, left)["symbol"])
            & set(df.nlargest(top_n, right)["symbol"])
        )
    )


def _spearman(df: pd.DataFrame, left: str, right: str):
    if len(df) < 2:
        return None
    corr = df[[left, right]].corr(method="spearman").iloc[0, 1]
    return float(corr) if _finite(corr) else None


def build_shadow_composite_table(batch_table: pd.DataFrame) -> pd.DataFrame:
    """V1.2.3a: separate Leadership effect from Fundamental incremental effect.

    Attribution chain:
        Official Candidate Quality
        -> No-Fund Reference (70% CQ + 30% Leadership)
        -> F10 / F20 / F30

    REVIEW/FAIL/unavailable Fundamental Quality is never imputed.
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
        score_col = f"shadow_{scenario.lower()}"
        out[score_col] = np.nan
        out.loc[usable, score_col] = out.loc[usable].apply(
            lambda row: _weighted_score(
                row.get("official_candidate_quality"),
                row.get("leadership_score"),
                row.get("fundamental_score"),
                weights,
            ),
            axis=1,
        )
        out[score_col] = pd.to_numeric(
            out[score_col],
            errors="coerce",
        ).round(1)

    out["shadow_f20_grade"] = out["shadow_f20"].apply(_grade)

    # Score attribution.
    out["leadership_score_impact_pts"] = (
        out["technical_leadership_reference"]
        - out["official_candidate_quality"]
    ).round(1)

    for scenario in ("f10", "f20", "f30"):
        out[f"{scenario}_fund_score_impact_pts"] = (
            out[f"shadow_{scenario}"]
            - out["technical_leadership_reference"]
        ).round(1)

    # Compatibility with V1.2.3.
    out["f20_impact_pts"] = out["f20_fund_score_impact_pts"]

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

    rank_cols = (
        "official_rank",
        "no_fund_rank",
        "f10_rank",
        "f20_rank",
        "f30_rank",
        "leadership_rank_impact",
        "f10_fund_rank_impact",
        "f20_fund_rank_impact",
        "f30_fund_rank_impact",
        "net_f20_rank_change",
    )
    for col in rank_cols:
        out[col] = np.nan

    # Rank all stages on the identical rankable subset for clean attribution.
    rankable = out["shadow_f20"].notna()
    if rankable.any():
        idx = out.index[rankable]

        out.loc[idx, "official_rank"] = _rank_desc(
            out.loc[idx, "official_candidate_quality"]
        )
        out.loc[idx, "no_fund_rank"] = _rank_desc(
            out.loc[idx, "technical_leadership_reference"]
        )
        out.loc[idx, "f10_rank"] = _rank_desc(
            out.loc[idx, "shadow_f10"]
        )
        out.loc[idx, "f20_rank"] = _rank_desc(
            out.loc[idx, "shadow_f20"]
        )
        out.loc[idx, "f30_rank"] = _rank_desc(
            out.loc[idx, "shadow_f30"]
        )

        # Positive = promotion, negative = demotion.
        out.loc[idx, "leadership_rank_impact"] = (
            out.loc[idx, "official_rank"]
            - out.loc[idx, "no_fund_rank"]
        )
        out.loc[idx, "f10_fund_rank_impact"] = (
            out.loc[idx, "no_fund_rank"]
            - out.loc[idx, "f10_rank"]
        )
        out.loc[idx, "f20_fund_rank_impact"] = (
            out.loc[idx, "no_fund_rank"]
            - out.loc[idx, "f20_rank"]
        )
        out.loc[idx, "f30_fund_rank_impact"] = (
            out.loc[idx, "no_fund_rank"]
            - out.loc[idx, "f30_rank"]
        )
        out.loc[idx, "net_f20_rank_change"] = (
            out.loc[idx, "official_rank"]
            - out.loc[idx, "f20_rank"]
        )

    # Compatibility aliases from V1.2.3.
    out["shadow_f20_rank"] = out["f20_rank"]
    out["rank_change"] = out["net_f20_rank_change"]

    return out


def _scenario_summary(rankable: pd.DataFrame) -> list[dict]:
    top_n = min(10, len(rankable))
    rows = []

    scenarios = (
        ("F10", "shadow_f10", "f10_fund_rank_impact", "f10_fund_score_impact_pts"),
        ("F20", "shadow_f20", "f20_fund_rank_impact", "f20_fund_score_impact_pts"),
        ("F30", "shadow_f30", "f30_fund_rank_impact", "f30_fund_score_impact_pts"),
    )

    for label, score_col, rank_impact_col, score_impact_col in scenarios:
        corr = _spearman(
            rankable,
            "technical_leadership_reference",
            score_col,
        )
        rank_impacts = pd.to_numeric(
            rankable[rank_impact_col],
            errors="coerce",
        ).dropna()
        score_impacts = pd.to_numeric(
            rankable[score_impact_col],
            errors="coerce",
        ).dropna()

        rows.append(
            {
                "scenario": label,
                "No-Fund Top-10 overlap": (
                    f"{_top_overlap(rankable, 'technical_leadership_reference', score_col, top_n)}/{top_n}"
                    if top_n
                    else "0/0"
                ),
                "Spearman vs No-Fund": (
                    None if corr is None else round(corr, 3)
                ),
                "Median |fund rank impact|": (
                    None
                    if rank_impacts.empty
                    else round(float(rank_impacts.abs().median()), 1)
                ),
                "Mean |fund score impact|": (
                    None
                    if score_impacts.empty
                    else round(float(score_impacts.abs().mean()), 1)
                ),
            }
        )

    return rows


def summarize_shadow_composite(composite: pd.DataFrame) -> dict:
    if composite is None or composite.empty:
        return {
            "total": 0,
            "rankable": 0,
            "top_n": 0,
            "official_f20_top10_overlap": 0,
            "nofund_f20_top10_overlap": 0,
            "official_f20_spearman": None,
            "nofund_f20_spearman": None,
            "median_abs_leadership_rank_impact": None,
            "median_abs_f20_fund_rank_impact": None,
            "mean_abs_f20_fund_score_impact": None,
            "full_alignment": 0,
            "unranked_fundamental_review": 0,
            "scenario_summary": [],
        }

    total = int(len(composite))
    rankable = composite[
        pd.to_numeric(composite["shadow_f20"], errors="coerce").notna()
    ].copy()
    n = int(len(rankable))
    top_n = min(10, n)

    leadership_impacts = pd.to_numeric(
        rankable["leadership_rank_impact"],
        errors="coerce",
    ).dropna()
    f20_rank_impacts = pd.to_numeric(
        rankable["f20_fund_rank_impact"],
        errors="coerce",
    ).dropna()
    f20_score_impacts = pd.to_numeric(
        rankable["f20_fund_score_impact_pts"],
        errors="coerce",
    ).dropna()

    official_corr = _spearman(
        rankable,
        "official_candidate_quality",
        "shadow_f20",
    )
    nofund_corr = _spearman(
        rankable,
        "technical_leadership_reference",
        "shadow_f20",
    )

    result = {
        "total": total,
        "rankable": n,
        "top_n": top_n,
        "official_f20_top10_overlap": _top_overlap(
            rankable,
            "official_candidate_quality",
            "shadow_f20",
            top_n,
        ),
        "nofund_f20_top10_overlap": _top_overlap(
            rankable,
            "technical_leadership_reference",
            "shadow_f20",
            top_n,
        ),
        "official_f20_spearman": (
            None if official_corr is None else round(official_corr, 3)
        ),
        "nofund_f20_spearman": (
            None if nofund_corr is None else round(nofund_corr, 3)
        ),
        "median_abs_leadership_rank_impact": (
            None
            if leadership_impacts.empty
            else round(float(leadership_impacts.abs().median()), 1)
        ),
        "median_abs_f20_fund_rank_impact": (
            None
            if f20_rank_impacts.empty
            else round(float(f20_rank_impacts.abs().median()), 1)
        ),
        "mean_abs_f20_fund_score_impact": (
            None
            if f20_score_impacts.empty
            else round(float(f20_score_impacts.abs().mean()), 1)
        ),
        "full_alignment": int(
            (composite["quality_profile"] == "FULL ALIGNMENT").sum()
        ),
        "unranked_fundamental_review": int(total - n),
        "scenario_summary": _scenario_summary(rankable),
    }

    # Backward-compatible V1.2.3 summary keys.
    result["top10_overlap"] = result["official_f20_top10_overlap"]
    result["spearman_corr"] = result["official_f20_spearman"]

    net = pd.to_numeric(
        rankable["net_f20_rank_change"],
        errors="coerce",
    ).dropna()
    result["median_abs_rank_shift"] = (
        None if net.empty else round(float(net.abs().median()), 1)
    )
    result["mean_abs_f20_impact"] = result[
        "mean_abs_f20_fund_score_impact"
    ]

    return result
