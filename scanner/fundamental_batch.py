from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd


BATCH_VERSION = "V1.2.2.3"


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def _fmt_growth(value) -> str:
    if not _finite(value):
        return "N/A"
    return f"{100.0 * float(value):+.1f}%"


def _earnings_display(snapshot: dict) -> str:
    value = snapshot.get("earnings_q_yoy")
    if _finite(value):
        return _fmt_growth(value)
    state = str(snapshot.get("earnings_q_state") or "N/A")
    return state


def select_batch_candidates(
    scored: pd.DataFrame,
    limit: int = 25,
) -> pd.DataFrame:
    """Select a bounded SHADOW sample without using fundamentals to rank it.

    Selection is intentionally based only on already-official scanner fields:
    Candidate Quality, Leadership, and Legacy RS. This prevents circularity
    while Fundamental Quality is still being validated.
    """
    if scored is None or scored.empty:
        return pd.DataFrame()

    limit = max(1, int(limit))
    out = scored.copy()

    for col in ("quality_score", "leadership_score", "rs_score"):
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")

    if "symbol" not in out.columns:
        return pd.DataFrame()

    out["symbol"] = out["symbol"].astype(str).str.upper()
    out = out.drop_duplicates("symbol", keep="first")

    return (
        out.sort_values(
            ["quality_score", "leadership_score", "rs_score", "symbol"],
            ascending=[False, False, False, True],
            na_position="last",
        )
        .head(limit)
        .reset_index(drop=True)
    )


def classify_batch_snapshot(snapshot: dict) -> tuple[str, str]:
    """Classify one bounded batch result without altering scanner decisions."""
    companyfacts = str(
        snapshot.get("companyfacts_access_status") or "UNKNOWN"
    ).upper()
    if companyfacts != "PASS":
        return (
            "FAIL",
            "Official SEC CompanyFacts did not pass for this ticker.",
        )

    integrity = str(
        snapshot.get("metric_integrity_status") or "NOT AVAILABLE"
    ).upper()
    coverage = float(snapshot.get("available_weight_pct") or 0.0)
    confidence = str(
        snapshot.get("fundamental_confidence") or "UNKNOWN"
    ).upper()
    score = snapshot.get("fundamental_score")

    if integrity == "FAIL":
        return (
            "FAIL",
            str(
                snapshot.get("metric_integrity_summary")
                or "Metric integrity failed."
            ),
        )

    review_reasons = []
    if integrity in {"REVIEW", "NOT AVAILABLE"}:
        review_reasons.append(
            str(
                snapshot.get("metric_integrity_summary")
                or f"Metric integrity {integrity}"
            )
        )
    if coverage < 80.0:
        review_reasons.append(f"metric coverage {coverage:.0f}% < 80%")
    if confidence in {"LOW", "UNKNOWN"}:
        review_reasons.append(
            f"Fundamental Data Confidence {confidence}"
        )
    if not _finite(score):
        review_reasons.append("Fundamental Quality score unavailable")

    if review_reasons:
        return "REVIEW", "; ".join(dict.fromkeys(review_reasons))

    return (
        "PASS",
        "Official SEC CompanyFacts, coverage and metric integrity are usable.",
    )


def batch_row(scanner_row: dict, snapshot: dict) -> dict:
    status, interpretation = classify_batch_snapshot(snapshot)

    return {
        "symbol": str(scanner_row.get("symbol") or "").upper(),
        "official_candidate_quality": (
            round(float(scanner_row["quality_score"]), 1)
            if _finite(scanner_row.get("quality_score"))
            else np.nan
        ),
        "leadership_score": (
            round(float(scanner_row["leadership_score"]), 1)
            if _finite(scanner_row.get("leadership_score"))
            else np.nan
        ),
        "legacy_rs": (
            round(float(scanner_row["rs_score"]), 1)
            if _finite(scanner_row.get("rs_score"))
            else np.nan
        ),
        "fundamental_score": (
            round(float(snapshot["fundamental_score"]), 1)
            if _finite(snapshot.get("fundamental_score"))
            else np.nan
        ),
        "fundamental_grade": snapshot.get("fundamental_grade", "N/A"),
        "fundamental_confidence": snapshot.get(
            "fundamental_confidence", "UNKNOWN"
        ),
        "metric_coverage_pct": round(
            float(snapshot.get("available_weight_pct") or 0.0),
            1,
        ),
        "metric_integrity": snapshot.get(
            "metric_integrity_status", "NOT AVAILABLE"
        ),
        "companyfacts": snapshot.get(
            "companyfacts_access_status", "UNKNOWN"
        ),
        "revenue_q_yoy": _fmt_growth(snapshot.get("revenue_q_yoy")),
        "earnings_q_yoy_state": _earnings_display(snapshot),
        "latest_filing": snapshot.get("latest_filed"),
        "batch_status": status,
        "interpretation": interpretation,
    }


def summarize_batch_rows(rows: Iterable[dict]) -> dict:
    rows = list(rows)
    total = len(rows)

    companyfacts_pass = sum(
        str(r.get("companyfacts") or "").upper() == "PASS"
        for r in rows
    )
    integrity_pass = sum(
        str(r.get("metric_integrity") or "").upper() == "PASS"
        for r in rows
    )
    review = sum(
        str(r.get("batch_status") or "").upper() == "REVIEW"
        for r in rows
    )
    fail = sum(
        str(r.get("batch_status") or "").upper() == "FAIL"
        for r in rows
    )
    usable = sum(
        str(r.get("batch_status") or "").upper() == "PASS"
        for r in rows
    )

    fund_scores = [
        float(r["fundamental_score"])
        for r in rows
        if _finite(r.get("fundamental_score"))
    ]
    median_score = (
        float(np.median(fund_scores))
        if fund_scores
        else None
    )
    a_or_better = sum(
        _finite(r.get("fundamental_score"))
        and float(r["fundamental_score"]) >= 80.0
        for r in rows
    )
    low_unknown = sum(
        str(r.get("fundamental_confidence") or "UNKNOWN").upper()
        in {"LOW", "UNKNOWN"}
        for r in rows
    )

    return {
        "total": total,
        "companyfacts_pass": int(companyfacts_pass),
        "integrity_pass": int(integrity_pass),
        "review": int(review),
        "fail": int(fail),
        "usable": int(usable),
        "usable_coverage_pct": (
            100.0 * usable / total
            if total
            else 0.0
        ),
        "median_fundamental_score": (
            round(median_score, 1)
            if median_score is not None
            else None
        ),
        "a_or_better": int(a_or_better),
        "low_unknown_confidence": int(low_unknown),
    }
