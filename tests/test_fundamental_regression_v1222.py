import unittest
from datetime import date

import numpy as np
import pandas as pd

from scanner.fundamentals import build_fundamental_snapshot


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


class LegacyFundamentalRegressionTests(unittest.TestCase):
    def test_core_growth_math_unchanged(self):
        snap = build_fundamental_snapshot(
            "TEST",
            fixture(),
            cik=123,
            as_of=date(2026, 8, 30),
        )
        self.assertAlmostEqual(snap["revenue_q_yoy"], 0.30, places=6)
        self.assertAlmostEqual(snap["revenue_q_prior_yoy"], 0.20, places=6)
        self.assertAlmostEqual(snap["revenue_q_change"], 0.10, places=6)
        self.assertAlmostEqual(snap["earnings_q_yoy"], 0.50, places=6)
        self.assertAlmostEqual(snap["earnings_q_prior_yoy"], 0.40, places=6)
        self.assertAlmostEqual(snap["earnings_q_change"], 0.10, places=6)
        self.assertEqual(snap["earnings_metric"], "Diluted EPS")
        self.assertEqual(snap["fundamental_confidence"], "HIGH")
        self.assertTrue(np.isfinite(snap["fundamental_score"]))

    def test_turnaround_semantics_unchanged(self):
        data = fixture()
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


if __name__ == "__main__":
    unittest.main()
