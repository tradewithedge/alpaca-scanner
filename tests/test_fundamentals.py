import unittest
from datetime import date

import numpy as np
import pandas as pd

from scanner.fundamentals import (
    build_fundamental_snapshot,
    normalize_sec_ticker,
    unavailable_snapshot,
)


def fact(start, end, filed, value, form="10-Q", fy=2026, fp="Q2"):
    return {
        "start": start,
        "end": end,
        "filed": filed,
        "val": value,
        "form": form,
        "fy": fy,
        "fp": fp,
        "accn": "000-test",
    }


def fixture():
    rev = [
        fact("2024-01-01", "2024-03-31", "2024-05-01", 90.0, fy=2024, fp="Q1"),
        fact("2024-04-01", "2024-06-30", "2024-08-01", 100.0, fy=2024, fp="Q2"),
        fact("2025-01-01", "2025-03-31", "2025-05-01", 108.0, fy=2025, fp="Q1"),
        fact("2025-04-01", "2025-06-30", "2025-08-01", 120.0, fy=2025, fp="Q2"),
        fact("2026-01-01", "2026-03-31", "2026-05-01", 129.6, fy=2026, fp="Q1"),
        fact("2026-04-01", "2026-06-30", "2026-08-01", 156.0, fy=2026, fp="Q2"),
        fact("2024-01-01", "2024-12-31", "2025-02-15", 390.0, form="10-K", fy=2024, fp="FY"),
        fact("2025-01-01", "2025-12-31", "2026-02-15", 480.0, form="10-K", fy=2025, fp="FY"),
    ]

    eps = [
        fact("2024-01-01", "2024-03-31", "2024-05-01", 1.00, fy=2024, fp="Q1"),
        fact("2024-04-01", "2024-06-30", "2024-08-01", 1.20, fy=2024, fp="Q2"),
        fact("2025-01-01", "2025-03-31", "2025-05-01", 1.50, fy=2025, fp="Q1"),
        fact("2025-04-01", "2025-06-30", "2025-08-01", 1.80, fy=2025, fp="Q2"),
        fact("2026-01-01", "2026-03-31", "2026-05-01", 2.10, fy=2026, fp="Q1"),
        fact("2026-04-01", "2026-06-30", "2026-08-01", 2.70, fy=2026, fp="Q2"),
        fact("2024-01-01", "2024-12-31", "2025-02-15", 5.00, form="10-K", fy=2024, fp="FY"),
        fact("2025-01-01", "2025-12-31", "2026-02-15", 7.50, form="10-K", fy=2025, fp="FY"),
    ]

    return {
        "entityName": "Example Corp",
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


class FundamentalTests(unittest.TestCase):
    def test_ticker_normalization(self):
        self.assertEqual(normalize_sec_ticker("brk.b"), "BRK-B")
        self.assertEqual(normalize_sec_ticker(" amzn "), "AMZN")

    def test_growth_and_acceleration_are_explainable(self):
        snap = build_fundamental_snapshot(
            "TEST",
            fixture(),
            cik=123,
            company_name="Example Corp",
            as_of=date(2026, 8, 30),
        )

        # Revenue Q2 2026 vs Q2 2025 = +30%
        self.assertAlmostEqual(snap["revenue_q_yoy"], 0.30, places=6)
        # Prior Q1 2026 vs Q1 2025 = +20%
        self.assertAlmostEqual(snap["revenue_q_prior_yoy"], 0.20, places=6)
        self.assertAlmostEqual(snap["revenue_q_change"], 0.10, places=6)

        # EPS Q2 2026 vs Q2 2025 = +50%
        self.assertAlmostEqual(snap["earnings_q_yoy"], 0.50, places=6)
        # Prior Q1 = +40%
        self.assertAlmostEqual(snap["earnings_q_prior_yoy"], 0.40, places=6)
        self.assertAlmostEqual(snap["earnings_q_change"], 0.10, places=6)

        self.assertEqual(snap["earnings_metric"], "Diluted EPS")
        self.assertEqual(snap["fundamental_confidence"], "HIGH")
        self.assertTrue(np.isfinite(snap["fundamental_score"]))
        self.assertIn(snap["fundamental_grade"], {"A+", "A", "B+", "B", "C", "D"})

    def test_annual_growth_is_separate_long_term_confirmation(self):
        snap = build_fundamental_snapshot(
            "TEST",
            fixture(),
            cik=123,
            as_of=date(2026, 8, 30),
        )
        self.assertAlmostEqual(
            snap["revenue_annual_yoy"],
            480.0 / 390.0 - 1.0,
            places=6,
        )
        self.assertAlmostEqual(
            snap["earnings_annual_yoy"],
            7.5 / 5.0 - 1.0,
            places=6,
        )

    def test_turnaround_does_not_manufacture_percentage_growth(self):
        data = fixture()
        eps_items = data["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]["USD/shares"]
        # Q2 2025 becomes a loss; Q2 2026 is positive -> TURNAROUND.
        for item in eps_items:
            if item["end"] == "2025-06-30":
                item["val"] = -0.50

        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        self.assertTrue(pd.isna(snap["earnings_q_yoy"]))
        self.assertEqual(snap["earnings_q_state"], "TURNAROUND")
        self.assertIn("turned positive", snap["fundamental_reasons"])

    def test_missing_earnings_is_fail_visible(self):
        data = fixture()
        del data["facts"]["us-gaap"]["EarningsPerShareDiluted"]
        snap = build_fundamental_snapshot(
            "TEST",
            data,
            as_of=date(2026, 8, 30),
        )
        self.assertEqual(snap["fundamental_confidence"], "UNKNOWN")
        self.assertTrue(pd.isna(snap["fundamental_score"]))
        self.assertIn("Fundamental Data Confidence UNKNOWN", snap["fundamental_risks"])

    def test_stale_data_downgrades_confidence(self):
        snap = build_fundamental_snapshot(
            "TEST",
            fixture(),
            as_of=date(2027, 8, 30),
        )
        self.assertEqual(snap["fundamental_confidence"], "LOW")

    def test_unavailable_snapshot_never_manufactures_score(self):
        snap = unavailable_snapshot("XYZ", "SEC request failed")
        self.assertEqual(snap["fundamental_confidence"], "UNKNOWN")
        self.assertTrue(pd.isna(snap["fundamental_score"]))
        self.assertIn("SEC request failed", snap["fundamental_risks"])


if __name__ == "__main__":
    unittest.main()
