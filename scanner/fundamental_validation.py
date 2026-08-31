from __future__ import annotations

import math


VALIDATION_VERSION = "V1.2.2.2"

# Deliberately different reporting profiles. These are not "best stocks";
# they are structural test cases for the extraction engine.
VALIDATION_CASES = (
    {
        "ticker": "AMZN",
        "profile": "Calendar-year growth megacap",
        "focus": "Baseline GAAP revenue + diluted EPS extraction",
    },
    {
        "ticker": "MSFT",
        "profile": "June fiscal year",
        "focus": "Non-calendar fiscal-year alignment",
    },
    {
        "ticker": "NVDA",
        "profile": "Jan / 52–53-week fiscal year",
        "focus": "52–53-week period/date tolerance",
    },
    {
        "ticker": "UBER",
        "profile": "Earnings-transition issuer",
        "focus": "Turnaround/loss-state semantics without bogus percentages",
    },
    {
        "ticker": "JPM",
        "profile": "Financial-sector schema stress",
        "focus": "Concept/domain coverage — missing generic revenue must be REVIEW, not fabricated",
    },
)


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def classify_validation_snapshot(snapshot: dict) -> tuple[str, str]:
    """Classify validation outcome without altering any scanner decision."""
    if snapshot.get("companyfacts_access_status") != "PASS":
        return (
            "FAIL — ACCESS",
            str(
                snapshot.get("companyfacts_transport_diagnosis")
                or snapshot.get("access_detail")
                or "CompanyFacts unavailable"
            ),
        )

    integrity = str(snapshot.get("metric_integrity_status") or "NOT AVAILABLE")
    if integrity == "FAIL":
        return (
            "FAIL — EXTRACTION",
            str(snapshot.get("metric_integrity_summary") or "Integrity failure"),
        )
    if integrity in {"REVIEW", "NOT AVAILABLE"}:
        return (
            "REVIEW",
            str(snapshot.get("metric_integrity_summary") or "Manual review required"),
        )

    coverage = float(snapshot.get("available_weight_pct") or 0.0)
    confidence = str(snapshot.get("fundamental_confidence") or "UNKNOWN")
    if coverage < 80.0 or confidence in {"LOW", "UNKNOWN"}:
        return (
            "REVIEW",
            f"Coverage {coverage:.0f}% / confidence {confidence}",
        )

    return (
        "PASS",
        "SEC access and used period pairs passed structural integrity checks.",
    )


def validation_row(case: dict, snapshot: dict) -> dict:
    result, note = classify_validation_snapshot(snapshot)
    earnings_yoy = snapshot.get("earnings_q_yoy")
    earnings_display = (
        f"{100.0 * float(earnings_yoy):+.1f}%"
        if _finite(earnings_yoy)
        else str(snapshot.get("earnings_q_state") or "N/A")
    )
    revenue_yoy = snapshot.get("revenue_q_yoy")
    revenue_display = (
        f"{100.0 * float(revenue_yoy):+.1f}%"
        if _finite(revenue_yoy)
        else "N/A"
    )

    return {
        "Ticker": case["ticker"],
        "Reporting profile": case["profile"],
        "Validation focus": case["focus"],
        "CompanyFacts": snapshot.get("companyfacts_access_status", "UNKNOWN"),
        "Metric integrity": snapshot.get("metric_integrity_status", "NOT AVAILABLE"),
        "Data confidence": snapshot.get("fundamental_confidence", "UNKNOWN"),
        "Coverage": f"{float(snapshot.get('available_weight_pct') or 0):.0f}%",
        "Fiscal calendar": snapshot.get("fiscal_calendar", "UNKNOWN"),
        "Revenue Q YoY": revenue_display,
        "Earnings Q YoY/state": earnings_display,
        "Earnings metric": snapshot.get("earnings_metric", "Unavailable"),
        "Revenue concept": snapshot.get("revenue_concept") or "—",
        "Result": result,
        "Interpretation": note,
    }


def summarize_validation_rows(rows: list[dict]) -> dict:
    counts = {"PASS": 0, "REVIEW": 0, "FAIL": 0}
    for row in rows:
        result = str(row.get("Result") or "")
        if result.startswith("PASS"):
            counts["PASS"] += 1
        elif result.startswith("FAIL"):
            counts["FAIL"] += 1
        else:
            counts["REVIEW"] += 1

    if counts["FAIL"]:
        overall = "FAIL"
    elif counts["REVIEW"]:
        overall = "REVIEW"
    else:
        overall = "PASS"

    return {
        "overall": overall,
        "total": len(rows),
        "pass": counts["PASS"],
        "review": counts["REVIEW"],
        "fail": counts["FAIL"],
    }
