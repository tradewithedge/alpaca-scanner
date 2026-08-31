import unittest
from datetime import date

import pandas as pd

from scanner.fundamentals import build_fundamental_snapshot
from scanner.fundamental_validation import (
    classify_validation_snapshot,
    summarize_validation_rows,
    validation_row,
)


def fact(start, end, filed, value, form="10-Q", fy=2026, fp="Q2", accn="000-test"):
    return {
        "start": start,
        "end": end,
        "filed": filed,
        "val": value,
        "form": form,
        "fy": fy,
        "fp": fp,
        "accn": accn,
    }


def payload(rev, eps, name="Example Corp"):
    return {
        "entityName": name,
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {"USD": rev}
                },
                "EarningsPerShareDiluted": {
                    "units": {"USD/shares": eps}
                },
            }
        },
    }


def calendar_fixture():
    rev = [
        fact("2024-01-01", "2024-03-31", "2024-05-01", 90, fy=2024, fp="Q1"),
        fact("2024-04-01", "2024-06-30", "2024-08-01", 100, fy=2024, fp="Q2"),
        fact("2025-01-01", "2025-03-31", "2025-05-01", 108, fy=2025, fp="Q1"),
        fact("2025-04-01", "2025-06-30", "2025-08-01", 120, fy=2025, fp="Q2"),
        fact("2026-01-01", "2026-03-31", "2026-05-01", 129.6, fy=2026, fp="Q1"),
        fact("2026-04-01", "2026-06-30", "2026-08-01", 156, fy=2026, fp="Q2"),
        fact("2024-01-01", "2024-12-31", "2025-02-15", 390, form="10-K", fy=2024, fp="FY"),
        fact("2025-01-01", "2025-12-31", "2026-02-15", 480, form="10-K", fy=2025, fp="FY"),
    ]
    eps = [
        fact("2024-01-01", "2024-03-31", "2024-05-01", 1.0, fy=2024, fp="Q1"),
        fact("2024-04-01", "2024-06-30", "2024-08-01", 1.2, fy=2024, fp="Q2"),
        fact("2025-01-01", "2025-03-31", "2025-05-01", 1.5, fy=2025, fp="Q1"),
        fact("2025-04-01", "2025-06-30", "2025-08-01", 1.8, fy=2025, fp="Q2"),
        fact("2026-01-01", "2026-03-31", "2026-05-01", 2.1, fy=2026, fp="Q1"),
        fact("2026-04-01", "2026-06-30", "2026-08-01", 2.7, fy=2026, fp="Q2"),
        fact("2024-01-01", "2024-12-31", "2025-02-15", 5.0, form="10-K", fy=2024, fp="FY"),
        fact("2025-01-01", "2025-12-31", "2026-02-15", 7.5, form="10-K", fy=2025, fp="FY"),
    ]
    return payload(rev, eps)


class FundamentalMetricIntegrityTests(unittest.TestCase):
    def test_calendar_fixture_integrity_passes(self):
        snap = build_fundamental_snapshot(
            "TEST",
            calendar_fixture(),
            as_of=date(2026, 8, 30),
        )
        self.assertEqual(snap["metric_integrity_status"], "PASS")
        self.assertEqual(
            snap["fiscal_calendar"],
            "DECEMBER FY / CALENDAR-LIKE",
        )
        self.assertEqual(len(snap["metric_integrity_rows"]), 4)
        self.assertTrue(
            all(r["integrity"] == "PASS" for r in snap["metric_integrity_rows"])
        )

    def test_non_calendar_fiscal_year_is_not_treated_as_error(self):
        data = calendar_fixture()
        rev = data["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        eps = data["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]["USD/shares"]
        # Replace annual periods with June fiscal years.
        rev[-2:] = [
            fact("2023-07-01", "2024-06-30", "2024-08-01", 390, form="10-K", fy=2024, fp="FY"),
            fact("2024-07-01", "2025-06-30", "2025-08-01", 480, form="10-K", fy=2025, fp="FY"),
        ]
        eps[-2:] = [
            fact("2023-07-01", "2024-06-30", "2024-08-01", 5.0, form="10-K", fy=2024, fp="FY"),
            fact("2024-07-01", "2025-06-30", "2025-08-01", 7.5, form="10-K", fy=2025, fp="FY"),
        ]
        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        self.assertEqual(snap["metric_integrity_status"], "PASS")
        self.assertIn("JUNE FY", snap["fiscal_calendar"])

    def test_52_53_week_annual_gap_passes(self):
        data = calendar_fixture()
        rev = data["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        eps = data["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]["USD/shares"]
        rev[-2:] = [
            fact("2023-01-30", "2024-01-28", "2024-03-01", 390, form="10-K", fy=2024, fp="FY"),
            fact("2024-01-29", "2025-02-02", "2025-03-01", 480, form="10-K", fy=2025, fp="FY"),
        ]
        eps[-2:] = [
            fact("2023-01-30", "2024-01-28", "2024-03-01", 5.0, form="10-K", fy=2024, fp="FY"),
            fact("2024-01-29", "2025-02-02", "2025-03-01", 7.5, form="10-K", fy=2025, fp="FY"),
        ]
        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        self.assertNotEqual(snap["metric_integrity_status"], "FAIL")

    def test_turnaround_state_is_preserved_without_bogus_growth(self):
        data = calendar_fixture()
        eps = data["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]["USD/shares"]
        for item in eps:
            if item["end"] == "2025-06-30":
                item["val"] = -0.5
        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        self.assertTrue(pd.isna(snap["earnings_q_yoy"]))
        self.assertEqual(snap["earnings_q_state"], "TURNAROUND")
        self.assertNotEqual(snap["metric_integrity_status"], "FAIL")

    def test_ytd_duration_is_not_used_as_quarter(self):
        data = calendar_fixture()
        rev = data["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        # Add a newer 6-month YTD item with the same end date. It must not replace
        # the true ~90-day quarter in the quarter series.
        rev.append(
            fact(
                "2026-01-01",
                "2026-06-30",
                "2026-08-05",
                999.0,
                form="10-Q",
                fy=2026,
                fp="Q2",
                accn="000-ytd",
            )
        )
        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        self.assertAlmostEqual(snap["revenue_q_yoy"], 0.30, places=6)
        qrow = snap["revenue_q_pair"]["current_meta"]
        self.assertLessEqual(qrow["duration_days"], 120)

    def test_structurally_bad_used_pair_fails_integrity(self):
        data = calendar_fixture()
        rev = data["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        # Move prior-year Q2 far enough away that the latest current Q2 pairs to
        # an invalid YoY end-date gap only if it is actually used.
        for item in rev:
            if item["end"] == "2025-06-30":
                item["end"] = "2025-04-01"
                item["start"] = "2025-01-01"
        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        # No comparable prior pair is preferable to silently presenting an
        # older quarter as the latest quarter YoY.
        self.assertTrue(pd.isna(snap["revenue_q_yoy"]))
        self.assertEqual(snap["revenue_q_end"], date(2026, 6, 30))
        self.assertEqual(snap["metric_integrity_status"], "REVIEW")
        self.assertIn(
            "Revenue quarter",
            snap["metric_integrity_summary"],
        )

    def test_validation_classifier_distinguishes_review_from_fail(self):
        pass_snap = build_fundamental_snapshot(
            "TEST",
            calendar_fixture(),
            as_of=date(2026, 8, 30),
        )
        pass_snap["companyfacts_access_status"] = "PASS"
        result, _ = classify_validation_snapshot(pass_snap)
        self.assertEqual(result, "PASS")

        review_snap = dict(pass_snap)
        review_snap["metric_integrity_status"] = "REVIEW"
        review_snap["metric_integrity_summary"] = "sector concept review"
        result, _ = classify_validation_snapshot(review_snap)
        self.assertEqual(result, "REVIEW")

        fail_snap = dict(pass_snap)
        fail_snap["companyfacts_access_status"] = "FAILED"
        result, _ = classify_validation_snapshot(fail_snap)
        self.assertTrue(result.startswith("FAIL"))

    def test_validation_summary(self):
        rows = [
            {"Result": "PASS"},
            {"Result": "REVIEW"},
            {"Result": "FAIL — ACCESS"},
        ]
        summary = summarize_validation_rows(rows)
        self.assertEqual(summary["overall"], "FAIL")
        self.assertEqual(summary["pass"], 1)
        self.assertEqual(summary["review"], 1)
        self.assertEqual(summary["fail"], 1)


if __name__ == "__main__":
    unittest.main()
