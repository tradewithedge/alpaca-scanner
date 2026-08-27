from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd


EXPECTED_BUCKETS = [
    "ACTIONABLE NOW",
    "TECH ACTIONABLE — EVENT CHECK",
    "A-QUALITY — WAIT",
    "WAIT",
    "DEVELOPING",
    "AVOID / BROKEN",
]


def _rate(numerator: int | float, denominator: int | float | None) -> float | None:
    if denominator is None or denominator <= 0:
        return None
    return round(100.0 * float(numerator) / float(denominator), 1)


def build_funnel(stages: Iterable[tuple[str, int]]) -> pd.DataFrame:
    """Build an auditable stage-by-stage scanner funnel.

    Each stage must be a non-negative integer count. Rates are intentionally
    computed against both the previous stage and the first stage so silent
    drop-offs are obvious in the UI.
    """
    rows = []
    first_count = None
    previous_count = None

    for stage, raw_count in stages:
        count = max(int(raw_count or 0), 0)
        if first_count is None:
            first_count = count

        rows.append(
            {
                "Stage": stage,
                "Count": count,
                "% of prior stage": _rate(count, previous_count),
                "% of starting universe": _rate(count, first_count),
            }
        )
        previous_count = count

    return pd.DataFrame(rows)


def bucket_integrity(scored: pd.DataFrame | None) -> dict:
    """Return bucket counts plus an explicit reconciliation result."""
    if scored is None or scored.empty or "bucket" not in scored.columns:
        counts = {bucket: 0 for bucket in EXPECTED_BUCKETS}
        return {
            "counts": counts,
            "classified_count": 0,
            "row_count": 0,
            "unknown_count": 0,
            "unknown_buckets": [],
            "reconciled": True,
        }

    raw_counts: Mapping[str, int] = scored["bucket"].value_counts(dropna=False).to_dict()
    counts = {bucket: int(raw_counts.get(bucket, 0)) for bucket in EXPECTED_BUCKETS}

    observed = set(str(x) for x in scored["bucket"].dropna().unique())
    unknown_buckets = sorted(observed - set(EXPECTED_BUCKETS))
    missing_bucket_count = int(scored["bucket"].isna().sum())
    unknown_count = int(
        sum(int(raw_counts.get(bucket, 0)) for bucket in unknown_buckets)
        + missing_bucket_count
    )
    if missing_bucket_count:
        unknown_buckets = [*unknown_buckets, "<MISSING>"]
    classified_count = int(sum(counts.values()))
    row_count = int(len(scored))

    return {
        "counts": counts,
        "classified_count": classified_count,
        "row_count": row_count,
        "unknown_count": unknown_count,
        "unknown_buckets": unknown_buckets,
        "reconciled": classified_count == row_count and unknown_count == 0,
    }


def liquidity_summary(observations: pd.DataFrame, threshold: float) -> dict:
    """Summarize consolidated previous-session dollar-volume observations."""
    if observations is None or observations.empty:
        return {
            "q25": None,
            "median": None,
            "q75": None,
            "cutoff_sample": pd.DataFrame(),
        }

    x = observations.copy()
    dv = pd.to_numeric(x["prev_dollar_volume"], errors="coerce").dropna()

    if dv.empty:
        q25 = median = q75 = None
    else:
        q25 = float(dv.quantile(0.25))
        median = float(dv.quantile(0.50))
        q75 = float(dv.quantile(0.75))

    x["distance_to_cutoff"] = (x["prev_dollar_volume"] - float(threshold)).abs()
    x["liquidity_status"] = x["passed_liquidity"].map({True: "PASS", False: "FAIL"})
    cutoff_sample = (
        x.sort_values(["distance_to_cutoff", "prev_dollar_volume"], ascending=[True, False])
        .head(12)
        .drop(columns=["distance_to_cutoff"], errors="ignore")
        .reset_index(drop=True)
    )

    return {
        "q25": q25,
        "median": median,
        "q75": q75,
        "cutoff_sample": cutoff_sample,
    }
