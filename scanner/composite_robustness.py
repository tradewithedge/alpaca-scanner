from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .composite_quality import build_shadow_composite_table


ROBUSTNESS_VERSION = "V1.2.3b1"

WEIGHT_GRID = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
RANK_GRID = (0.10, 0.15, 0.20, 0.25, 0.30)
CENTER_WEIGHTS = (0.15, 0.20, 0.25)
GUARDRAIL_CAPS = (4.0, 6.0, 8.0)
ANCHOR_WEIGHTS = (0.10, 0.20, 0.30)


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def _weight_tag(weight: float) -> str:
    return f"f{int(round(weight * 100)):02d}"


def _rank_desc(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").rank(
        method="min",
        ascending=False,
    )


def _spearman(df: pd.DataFrame, left: str, right: str):
    if len(df) < 2:
        return None
    corr = df[[left, right]].corr(method="spearman").iloc[0, 1]
    return float(corr) if _finite(corr) else None


def _top_overlap(df: pd.DataFrame, left: str, right: str, top_n: int) -> int:
    if top_n <= 0:
        return 0
    a = set(df.nlargest(top_n, left)["symbol"])
    b = set(df.nlargest(top_n, right)["symbol"])
    return int(len(a & b))


def _top_set(df: pd.DataFrame, score_col: str, top_n: int) -> set[str]:
    if top_n <= 0:
        return set()
    return set(df.nlargest(top_n, score_col)["symbol"])


def _accepted_anchor_columns(weight: float) -> tuple[str, str]:
    tag = _weight_tag(weight)
    return f"shadow_{tag}", f"{tag}_rank"


def build_composite_robustness_table(batch_table: pd.DataFrame) -> pd.DataFrame:
    """V1.2.3b1 full-precision robustness diagnostics.

    Integrity rules
    ---------------
    1. F10/F20/F30 are immutable V1.2.3a anchors:
       displayed score and rank are reused directly from the accepted layer.
    2. New interpolation scenarios F05/F15/F25 are calculated from the
       unrounded internal No-Fund value and ranked on the unrounded score.
    3. Guardrail simulations use exact F20 incremental Fundamental impact.
    4. REVIEW/FAIL/unavailable Fundamental Quality is never imputed.
    """
    base = build_shadow_composite_table(batch_table)
    if base is None or base.empty:
        return pd.DataFrame()

    out = base.copy(deep=True)

    cq = pd.to_numeric(
        out["official_candidate_quality"],
        errors="coerce",
    )
    leadership = pd.to_numeric(
        out["leadership_score"],
        errors="coerce",
    )
    fundamental = pd.to_numeric(
        out["fundamental_score"],
        errors="coerce",
    )

    rankable = pd.to_numeric(
        out["shadow_f20"],
        errors="coerce",
    ).notna()

    # Full-precision No-Fund internal value.
    out["no_fund_exact"] = np.nan
    out.loc[rankable, "no_fund_exact"] = (
        0.70 * cq.loc[rankable]
        + 0.30 * leadership.loc[rankable]
    )

    # Accepted displayed No-Fund remains untouched for V1.2.3a attribution.
    # Build full-precision scores for every weight, but only NEW interpolation
    # weights use those exact scores for their ranking.
    for weight in WEIGHT_GRID:
        tag = _weight_tag(weight)
        exact_col = f"score_{tag}_exact"
        display_col = f"score_{tag}"
        rank_col = f"rank_{tag}"
        impact_exact_col = f"fund_score_impact_{tag}_exact_pts"
        impact_display_col = f"fund_score_impact_{tag}_pts"

        out[exact_col] = np.nan
        out.loc[rankable, exact_col] = (
            (1.0 - weight) * out.loc[rankable, "no_fund_exact"]
            + weight * fundamental.loc[rankable]
        )

        out[impact_exact_col] = (
            out[exact_col] - out["no_fund_exact"]
        )

        if weight in ANCHOR_WEIGHTS:
            accepted_score_col, accepted_rank_col = _accepted_anchor_columns(
                weight
            )

            # Critical b1 fix: reuse accepted V1.2.3a anchor values exactly.
            out[display_col] = pd.to_numeric(
                out[accepted_score_col],
                errors="coerce",
            )
            out[rank_col] = pd.to_numeric(
                out[accepted_rank_col],
                errors="coerce",
            )
        else:
            out[display_col] = pd.to_numeric(
                out[exact_col],
                errors="coerce",
            ).round(1)

            out[rank_col] = np.nan
            out.loc[rankable, rank_col] = _rank_desc(
                out.loc[rankable, exact_col]
            )

        out[impact_display_col] = pd.to_numeric(
            out[impact_exact_col],
            errors="coerce",
        ).round(1)

    # Anchor score integrity: exact formulas rounded to display precision must
    # reproduce the accepted V1.2.3a displayed scores.
    for weight in ANCHOR_WEIGHTS:
        tag = _weight_tag(weight)
        accepted_score_col, accepted_rank_col = _accepted_anchor_columns(weight)

        out[f"{tag}_score_match_v123a"] = np.isclose(
            pd.to_numeric(
                out[f"score_{tag}_exact"],
                errors="coerce",
            ).round(1),
            pd.to_numeric(
                out[accepted_score_col],
                errors="coerce",
            ),
            atol=1e-12,
            equal_nan=True,
        )

        out[f"{tag}_rank_match_v123a"] = (
            pd.to_numeric(
                out[f"rank_{tag}"],
                errors="coerce",
            )
            .fillna(-999999)
            .eq(
                pd.to_numeric(
                    out[accepted_rank_col],
                    errors="coerce",
                ).fillna(-999999)
            )
        )

    # Weight sensitivity F10→F30.
    # F10/F20/F30 ranks are frozen anchors; F15/F25 use exact internal ranks.
    rank_cols = [f"rank_{_weight_tag(w)}" for w in RANK_GRID]
    out["rank_best_f10_f30"] = out[rank_cols].min(axis=1, skipna=False)
    out["rank_worst_f10_f30"] = out[rank_cols].max(axis=1, skipna=False)
    out["rank_range_f10_f30"] = (
        out["rank_worst_f10_f30"] - out["rank_best_f10_f30"]
    )

    top_n = min(10, int(rankable.sum()))
    for weight in RANK_GRID:
        tag = _weight_tag(weight)
        out[f"top10_{tag}"] = False

        if not top_n:
            continue

        if weight in ANCHOR_WEIGHTS:
            score_col = f"score_{tag}"
        else:
            score_col = f"score_{tag}_exact"

        members = _top_set(
            out.loc[rankable],
            score_col,
            top_n,
        )
        out.loc[rankable, f"top10_{tag}"] = (
            out.loc[rankable, "symbol"].isin(members)
        )

    out["top10_weight_count"] = out[
        [f"top10_{_weight_tag(w)}" for w in RANK_GRID]
    ].sum(axis=1)

    out["center_top10_count"] = out[
        [f"top10_{_weight_tag(w)}" for w in CENTER_WEIGHTS]
    ].sum(axis=1)

    # Full-precision raw F20 incremental Fundamental impact.
    out["f20_fund_score_impact_exact_pts"] = pd.to_numeric(
        out["score_f20_exact"] - out["no_fund_exact"],
        errors="coerce",
    )

    # Keep accepted V1.2.3a rounded impact visible for continuity.
    # Guardrail triggers and calculations use the exact value above.
    raw_f20_impact_exact = pd.to_numeric(
        out["f20_fund_score_impact_exact_pts"],
        errors="coerce",
    )

    for cap in GUARDRAIL_CAPS:
        cap_tag = int(cap)
        clipped = raw_f20_impact_exact.clip(lower=-cap, upper=cap)

        exact_score_col = f"guard_f20_cap{cap_tag}_exact"
        display_score_col = f"guard_f20_cap{cap_tag}"
        rank_col = f"guard_rank_cap{cap_tag}"
        trigger_col = f"cap{cap_tag}_triggered"
        direction_col = f"cap{cap_tag}_direction"
        rank_delta_col = f"guard_rank_change_cap{cap_tag}_vs_raw"

        out[exact_score_col] = np.nan
        out.loc[rankable, exact_score_col] = (
            out.loc[rankable, "no_fund_exact"]
            + clipped.loc[rankable]
        )

        out[display_score_col] = pd.to_numeric(
            out[exact_score_col],
            errors="coerce",
        ).round(1)

        out[rank_col] = np.nan
        out.loc[rankable, rank_col] = _rank_desc(
            out.loc[rankable, exact_score_col]
        )

        out[trigger_col] = False
        out.loc[rankable, trigger_col] = (
            raw_f20_impact_exact.loc[rankable].abs() > cap
        )

        out[direction_col] = ""
        out.loc[
            rankable & (raw_f20_impact_exact > cap),
            direction_col,
        ] = "UPSIDE CAP"
        out.loc[
            rankable & (raw_f20_impact_exact < -cap),
            direction_col,
        ] = "DOWNSIDE CAP"

        out[rank_delta_col] = np.nan
        out.loc[rankable, rank_delta_col] = (
            pd.to_numeric(
                out.loc[rankable, "f20_rank"],
                errors="coerce",
            )
            - pd.to_numeric(
                out.loc[rankable, rank_col],
                errors="coerce",
            )
        )

    return out


def _weight_summary(rankable: pd.DataFrame) -> list[dict]:
    """Report weight-grid metrics against the accepted V1.2.3a No-Fund anchor."""
    rows = []
    top_n = min(10, len(rankable))

    for weight in WEIGHT_GRID:
        tag = _weight_tag(weight)

        # Anchor scenarios use accepted score/rank exactly. Interpolation
        # scenarios use unrounded exact score/rank.
        if weight in ANCHOR_WEIGHTS:
            score_col = f"score_{tag}"
        else:
            score_col = f"score_{tag}_exact"

        rank_col = f"rank_{tag}"
        impact_col = f"fund_score_impact_{tag}_exact_pts"

        corr = _spearman(
            rankable,
            "technical_leadership_reference",
            score_col,
        )

        rank_impact = (
            pd.to_numeric(
                rankable["no_fund_rank"],
                errors="coerce",
            )
            - pd.to_numeric(
                rankable[rank_col],
                errors="coerce",
            )
        )

        score_impact = pd.to_numeric(
            rankable[impact_col],
            errors="coerce",
        )

        rows.append(
            {
                "Fund weight": f"{int(weight * 100)}%",
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
                    if rank_impact.dropna().empty
                    else round(float(rank_impact.abs().median()), 1)
                ),
                "Mean |fund score impact|": (
                    None
                    if score_impact.dropna().empty
                    else round(float(score_impact.abs().mean()), 1)
                ),
                "Max |fund score impact|": (
                    None
                    if score_impact.dropna().empty
                    else round(float(score_impact.abs().max()), 1)
                ),
                "Mode": (
                    "V1.2.3a ANCHOR"
                    if weight in ANCHOR_WEIGHTS
                    else "FULL-PRECISION INTERPOLATION"
                ),
            }
        )

    return rows


def _guardrail_summary(rankable: pd.DataFrame) -> list[dict]:
    rows = []
    top_n = min(10, len(rankable))

    for cap in GUARDRAIL_CAPS:
        cap_tag = int(cap)
        exact_score_col = f"guard_f20_cap{cap_tag}_exact"
        rank_col = f"guard_rank_cap{cap_tag}"
        trigger_col = f"cap{cap_tag}_triggered"

        triggered = rankable[trigger_col].astype(bool)
        corr = _spearman(rankable, "shadow_f20", exact_score_col)

        rank_diff = (
            pd.to_numeric(rankable["f20_rank"], errors="coerce")
            - pd.to_numeric(rankable[rank_col], errors="coerce")
        ).abs()

        exact_impact = pd.to_numeric(
            rankable["f20_fund_score_impact_exact_pts"],
            errors="coerce",
        )

        rows.append(
            {
                "F20 impact cap": f"±{cap_tag} pts",
                "Triggered": f"{int(triggered.sum())}/{len(rankable)}",
                "Downside triggers": int((exact_impact < -cap).sum()),
                "Upside triggers": int((exact_impact > cap).sum()),
                "Top-10 overlap vs raw F20": (
                    f"{_top_overlap(rankable, 'shadow_f20', exact_score_col, top_n)}/{top_n}"
                    if top_n
                    else "0/0"
                ),
                "Spearman vs raw F20": (
                    None if corr is None else round(corr, 3)
                ),
                "Median |rank change vs raw|": (
                    None
                    if rank_diff.dropna().empty
                    else round(float(rank_diff.median()), 1)
                ),
                "Max |rank change vs raw|": (
                    None
                    if rank_diff.dropna().empty
                    else round(float(rank_diff.max()), 1)
                ),
            }
        )

    return rows


def summarize_composite_robustness(robust: pd.DataFrame) -> dict:
    if robust is None or robust.empty:
        return {
            "total": 0,
            "rankable": 0,
            "stable_top10_all_weights": 0,
            "stable_top10_center_weights": 0,
            "median_rank_range": None,
            "high_sensitivity_count": 0,
            "cap6_trigger_count": 0,
            "weight_summary": [],
            "guardrail_summary": [],
            "anchor_integrity_pass": False,
        }

    total = int(len(robust))
    rankable = robust[
        pd.to_numeric(robust["shadow_f20"], errors="coerce").notna()
    ].copy()
    n = int(len(rankable))
    top_n = min(10, n)

    if top_n:
        all_sets = []
        for weight in RANK_GRID:
            tag = _weight_tag(weight)
            score_col = (
                f"score_{tag}"
                if weight in ANCHOR_WEIGHTS
                else f"score_{tag}_exact"
            )
            all_sets.append(_top_set(rankable, score_col, top_n))

        stable_all = len(set.intersection(*all_sets)) if all_sets else 0

        center_sets = []
        for weight in CENTER_WEIGHTS:
            tag = _weight_tag(weight)
            score_col = (
                f"score_{tag}"
                if weight in ANCHOR_WEIGHTS
                else f"score_{tag}_exact"
            )
            center_sets.append(_top_set(rankable, score_col, top_n))

        stable_center = (
            len(set.intersection(*center_sets))
            if center_sets
            else 0
        )
    else:
        stable_all = 0
        stable_center = 0

    rank_range = pd.to_numeric(
        rankable["rank_range_f10_f30"],
        errors="coerce",
    ).dropna()

    integrity_cols = []
    for weight in ANCHOR_WEIGHTS:
        tag = _weight_tag(weight)
        integrity_cols.extend(
            [
                f"{tag}_score_match_v123a",
                f"{tag}_rank_match_v123a",
            ]
        )

    anchor_integrity_pass = bool(
        robust[integrity_cols]
        .fillna(False)
        .all(axis=1)
        .all()
    )

    return {
        "total": total,
        "rankable": n,
        "stable_top10_all_weights": stable_all,
        "stable_top10_center_weights": stable_center,
        "median_rank_range": (
            None
            if rank_range.empty
            else round(float(rank_range.median()), 1)
        ),
        "high_sensitivity_count": int((rank_range >= 5).sum()),
        "cap6_trigger_count": int(
            rankable.get("cap6_triggered", pd.Series(dtype=bool))
            .fillna(False)
            .astype(bool)
            .sum()
        ),
        "weight_summary": _weight_summary(rankable),
        "guardrail_summary": _guardrail_summary(rankable),
        "anchor_integrity_pass": anchor_integrity_pass,
    }
