import unittest

import numpy as np
import pandas as pd

from scanner.fundamental_batch import (
    batch_row,
    classify_batch_snapshot,
    select_batch_candidates,
    summarize_batch_rows,
)


class FundamentalBatchTests(unittest.TestCase):
    def test_selection_uses_official_quality_not_fundamentals(self):
        scored = pd.DataFrame(
            [
                {
                    "symbol": "BBB",
                    "quality_score": 90,
                    "leadership_score": 80,
                    "rs_score": 75,
                },
                {
                    "symbol": "AAA",
                    "quality_score": 95,
                    "leadership_score": 70,
                    "rs_score": 70,
                },
                {
                    "symbol": "CCC",
                    "quality_score": 90,
                    "leadership_score": 85,
                    "rs_score": 80,
                },
            ]
        )
        selected = select_batch_candidates(scored, 2)
        self.assertEqual(selected["symbol"].tolist(), ["AAA", "CCC"])

    def test_pass_requires_usable_companyfacts_and_integrity(self):
        snap = {
            "companyfacts_access_status": "PASS",
            "metric_integrity_status": "PASS",
            "available_weight_pct": 100.0,
            "fundamental_confidence": "HIGH",
            "fundamental_score": 86.0,
        }
        status, _ = classify_batch_snapshot(snap)
        self.assertEqual(status, "PASS")

    def test_review_is_fail_visible_not_hard_failure(self):
        snap = {
            "companyfacts_access_status": "PASS",
            "metric_integrity_status": "REVIEW",
            "metric_integrity_summary": "Revenue quarter concept review",
            "available_weight_pct": 60.0,
            "fundamental_confidence": "MEDIUM",
            "fundamental_score": 70.0,
        }
        status, text = classify_batch_snapshot(snap)
        self.assertEqual(status, "REVIEW")
        self.assertIn("Revenue quarter", text)

    def test_companyfacts_failure_is_hard_fail(self):
        snap = {
            "companyfacts_access_status": "FAILED",
            "metric_integrity_status": "NOT AVAILABLE",
        }
        status, _ = classify_batch_snapshot(snap)
        self.assertEqual(status, "FAIL")

    def test_batch_row_keeps_official_quality_separate(self):
        scanner = {
            "symbol": "AMZN",
            "quality_score": 94.5,
            "leadership_score": 78.0,
            "rs_score": 90.0,
        }
        snap = {
            "companyfacts_access_status": "PASS",
            "metric_integrity_status": "PASS",
            "available_weight_pct": 100.0,
            "fundamental_confidence": "HIGH",
            "fundamental_score": 86.4,
            "fundamental_grade": "A",
            "revenue_q_yoy": 0.196,
            "earnings_q_yoy": 2.423,
            "earnings_q_state": "POSITIVE",
            "latest_filed": "2026-07-31",
        }
        row = batch_row(scanner, snap)
        self.assertEqual(row["official_candidate_quality"], 94.5)
        self.assertEqual(row["fundamental_score"], 86.4)
        self.assertEqual(row["batch_status"], "PASS")

    def test_summary_coverage(self):
        rows = [
            {
                "batch_status": "PASS",
                "companyfacts": "PASS",
                "metric_integrity": "PASS",
                "fundamental_score": 90.0,
                "fundamental_confidence": "HIGH",
            },
            {
                "batch_status": "PASS",
                "companyfacts": "PASS",
                "metric_integrity": "PASS",
                "fundamental_score": 80.0,
                "fundamental_confidence": "HIGH",
            },
            {
                "batch_status": "REVIEW",
                "companyfacts": "PASS",
                "metric_integrity": "REVIEW",
                "fundamental_score": 70.0,
                "fundamental_confidence": "MEDIUM",
            },
        ]
        summary = summarize_batch_rows(rows)
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["usable"], 2)
        self.assertAlmostEqual(summary["usable_coverage_pct"], 66.6666667)
        self.assertEqual(summary["a_or_better"], 2)


if __name__ == "__main__":
    unittest.main()
