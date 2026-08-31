from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .composite_quality import build_shadow_composite_table


ROBUSTNESS_VERSION = "V1.2.3b"

WEIGHT_GRID = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
RANK_GRID = (0.10, 0.15, 0.20, 0.25, 0.30)
CENTER_WEIGHTS = (0.15, 0.20, 0.25)
GUARDRAIL_CAPS = (4.0, 6.0, 8.0)


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


def build_composite_robustness_table(batch_table: pd.DataFrame) -> pd.DataFrame:
    """Build V1.2.3b robustness diagnostics from accepted V1.2.3a output.

    Nothing in this function changes official scanner scores or classifications.
    It adds interpolation weights and simulated F20 impact caps only.
    """
    base = build_shadow_composite_table(batch_table)
    if base is None or base.empty:
        return pd.DataFrame()

    out = base.copy(deep=True)

    no_fund = pd.to_numeric(
        out["technical_leadership_reference"],
        errors="coerce",
    )
    fundamental = pd.to_numeric(
        out["fundamental_score"],
        errors="coerce",
    )

    # Same rankable subset used by the accepted V1.2.3a full composite.
    rankable = pd.to_numeric(
        out["shadow_f20"],
        errors="coerce",
    ).notna()

    # Continuous weight family preserving the frozen 70:30 CQ:Leadership mix.
    for weight in WEIGHT_GRID:
        tag = _weight_tag(weight)
        score_col = f"score_{tag}"

        out[score_col] = np.nan
        out.loc[rankable, score_col] = (
            (1.0 - weight) * no_fund.loc[rankable]
            + weight * fundamental.loc[rankable]
        ).round(1)

        rank_col = f"rank_{tag}"
        out[rank_col] = np.nan
        out.loc[rankable, rank_col] = _rank_desc(
            out.loc[rankable, score_col]
        )

        impact_col = f"fund_score_impact_{tag}_pts"
        out[impact_col] = (
            out[score_col] - out["technical_leadership_reference"]
        ).round(1)

    # Integrity: F10 / F20 / F30 must match accepted V1.2.3a values.
    out["f10_match_v123a"] = np.isclose(
        pd.to_numeric(out["score_f10"], errors="coerce"),
        pd.to_numeric(out["shadow_f10"], errors="coerce"),
        atol=0.11,
        equal_nan=True,
    )
    out["f20_match_v123a"] = np.isclose(
        pd.to_numeric(out["score_f20"], errors="coerce"),
        pd.to_numeric(out["shadow_f20"], errors="coerce"),
        atol=0.11,
        equal_nan=True,
    )
    out["f30_match_v123a"] = np.isclose(
        pd.to_numeric(out["score_f30"], errors="coerce"),
        pd.to_numeric(out["shadow_f30"], errors="coerce"),
        atol=0.11,
        equal_nan=True,
    )

    # Weight sensitivity is evaluated F10→F30, avoiding the trivial near-No-Fund F05.
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
        if top_n:
            members = _top_set(
                out.loc[rankable],
                f"score_{tag}",
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

    # Raw accepted F20 Fundamental impact.
    raw_f20_impact = pd.to_numeric(
        out["f20_fund_score_impact_pts"],
        errors="coerce",
    )

    # Guardrail simulations: cap the incremental Fundamental contribution only.
    for cap in GUARDRAIL_CAPS:
        cap_tag = int(cap)
        clipped = raw_f20_impact.clip(lower=-cap, upper=cap)

        score_col = f"guard_f20_cap{cap_tag}"
        rank_col = f"guard_rank_cap{cap_tag}"
        trigger_col = f"cap{cap_tag}_triggered"
        direction_col = f"cap{cap_tag}_direction"
        rank_delta_col = f"guard_rank_change_cap{cap_tag}_vs_raw"

        out[score_col] = np.nan
        out.loc[rankable, score_col] = (
            no_fund.loc[rankable] + clipped.loc[rankable]
        ).round(1)

        out[rank_col] = np.nan
        out.loc[rankable, rank_col] = _rank_desc(
            out.loc[rankable, score_col]
        )

        out[trigger_col] = False
        out.loc[rankable, trigger_col] = (
            raw_f20_impact.loc[rankable].abs() > cap
        )

        out[direction_col] = ""
        out.loc[
            rankable & (raw_f20_impact > cap),
            direction_col,
        ] = "UPSIDE CAP"
        out.loc[
            rankable & (raw_f20_impact < -cap),
            direction_col,
        ] = "DOWNSIDE CAP"

        out[rank_delta_col] = np.nan
        out.loc[rankable, rank_delta_col] = (
            pd.to_numeric(out.loc[rankable, "rank_f20"], errors="coerce")
            - pd.to_numeric(out.loc[rankable, rank_col], errors="coerce")
        )

    return out


def _weight_summary(rankable: pd.DataFrame) -> list[dict]:
    rows = []
    top_n = min(10, len(rankable))

    for weight in WEIGHT_GRID:
        tag = _weight_tag(weight)
        score_col = f"score_{tag}"
        rank_col = f"rank_{tag}"
        impact_col = f"fund_score_impact_{tag}_pts"

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
            }
        )

    return rows


def _guardrail_summary(rankable: pd.DataFrame) -> list[dict]:
    rows = []
    top_n = min(10, len(rankable))

    for cap in GUARDRAIL_CAPS:
        cap_tag = int(cap)
        score_col = f"guard_f20_cap{cap_tag}"
        rank_col = f"guard_rank_cap{cap_tag}"
        trigger_col = f"cap{cap_tag}_triggered"

        triggered = rankable[trigger_col].astype(bool)
        corr = _spearman(rankable, "shadow_f20", score_col)
        rank_diff = (
            pd.to_numeric(rankable["rank_f20"], errors="coerce")
            - pd.to_numeric(rankable[rank_col], errors="coerce")
        ).abs()

        rows.append(
            {
                "F20 impact cap": f"±{cap_tag} pts",
                "Triggered": f"{int(triggered.sum())}/{len(rankable)}",
                "Downside triggers": int(
                    (
                        pd.to_numeric(
                            rankable["f20_fund_score_impact_pts"],
                            errors="coerce",
                        )
                        < -cap
                    ).sum()
                ),
                "Upside triggers": int(
                    (
                        pd.to_numeric(
                            rankable["f20_fund_score_impact_pts"],
                            errors="coerce",
                        )
                        > cap
                    ).sum()
                ),
                "Top-10 overlap vs raw F20": (
                    f"{_top_overlap(rankable, 'shadow_f20', score_col, top_n)}/{top_n}"
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
            "integrity_match": False,
        }

    total = int(len(robust))
    rankable = robust[
        pd.to_numeric(robust["shadow_f20"], errors="coerce").notna()
    ].copy()
    n = int(len(rankable))
    top_n = min(10, n)

    if top_n:
        all_sets = [
            _top_set(rankable, f"score_{_weight_tag(w)}", top_n)
            for w in RANK_GRID
        ]
        stable_all = len(set.intersection(*all_sets)) if all_sets else 0

        center_sets = [
            _top_set(rankable, f"score_{_weight_tag(w)}", top_n)
            for w in CENTER_WEIGHTS
        ]
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

    integrity_cols = (
        "f10_match_v123a",
        "f20_match_v123a",
        "f30_match_v123a",
    )
    integrity_match = bool(
        robust[list(integrity_cols)]
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
        "integrity_match": integrity_match,
    }
