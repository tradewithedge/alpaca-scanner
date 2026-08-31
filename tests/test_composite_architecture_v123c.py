import unittest

import numpy as np
import pandas as pd

from scanner.composite_architecture import (
    SELECTED_WEIGHTS,
    build_selected_composite_table,
    fundamental_impact_state,
    summarize_selected_composite,
)
from scanner.composite_quality import build_shadow_composite_table


class CompositeArchitectureV123cTests(unittest.TestCase):
    def sample(self):
        return pd.DataFrame(
            [
                {
                    "symbol": "STRONG",
                    "official_candidate_quality": 98.0,
                    "leadership_score": 90.0,
                    "fundamental_score": 85.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "WEAKF",
                    "official_candidate_quality": 100.0,
                    "leadership_score": 100.0,
                    "fundamental_score": 0.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "MID",
                    "official_candidate_quality": 92.0,
                    "leadership_score": 82.0,
                    "fundamental_score": 65.0,
                    "fundamental_confidence": "MEDIUM",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "BOOST",
                    "official_candidate_quality": 80.0,
                    "leadership_score": 75.0,
                    "fundamental_score": 98.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "REVIEW",
                    "official_candidate_quality": 99.0,
                    "leadership_score": 95.0,
                    "fundamental_score": np.nan,
                    "fundamental_confidence": "LOW",
                    "metric_integrity": "REVIEW",
                    "companyfacts": "PASS",
                    "batch_status": "REVIEW",
                },
            ]
        )

    def test_selected_weights_are_exact_f15_architecture(self):
        self.assertEqual(SELECTED_WEIGHTS["candidate_quality"], 0.595)
        self.assertEqual(SELECTED_WEIGHTS["leadership"], 0.255)
        self.assertEqual(SELECTED_WEIGHTS["fundamental"], 0.15)
        self.assertAlmostEqual(sum(SELECTED_WEIGHTS.values()), 1.0, places=12)

    def test_f15_formula_exact_and_integrity_pass(self):
        out = build_selected_composite_table(self.sample())
        row = out[out["symbol"] == "STRONG"].iloc[0]
        expected = 0.595 * 98.0 + 0.255 * 90.0 + 0.15 * 85.0
        self.assertAlmostEqual(row["composite_f15_exact"], expected, places=12)
        self.assertAlmostEqual(row["f15_formula_audit_exact"], expected, places=12)
        self.assertTrue(bool(row["f15_formula_match"]))

        summary = summarize_selected_composite(out)
        self.assertTrue(summary["f15_formula_integrity_pass"])
        self.assertTrue(summary["anchor_integrity_pass"])

    def test_f20_shadow_reference_reuses_accepted_anchor(self):
        accepted = build_shadow_composite_table(self.sample())
        out = build_selected_composite_table(self.sample())

        for symbol in ("STRONG", "WEAKF", "MID", "BOOST"):
            a = accepted[accepted["symbol"] == symbol].iloc[0]
            r = out[out["symbol"] == symbol].iloc[0]
            self.assertEqual(r["shadow_f20_reference"], a["shadow_f20"])
            self.assertEqual(r["shadow_f20_reference_rank"], a["f20_rank"])

    def test_explainable_impact_thresholds(self):
        self.assertEqual(fundamental_impact_state(0.0), "NORMAL")
        self.assertEqual(fundamental_impact_state(3.999), "NORMAL")
        self.assertEqual(fundamental_impact_state(4.0), "MATERIAL")
        self.assertEqual(fundamental_impact_state(-6.0), "MATERIAL")
        self.assertEqual(fundamental_impact_state(6.0001), "HIGH IMPACT")
        self.assertEqual(fundamental_impact_state(-12.0), "HIGH IMPACT")
        self.assertEqual(fundamental_impact_state(np.nan), "N/A")

    def test_no_hard_cap_is_applied(self):
        out = build_selected_composite_table(self.sample())
        row = out[out["symbol"] == "WEAKF"].iloc[0]

        # No-Fund = 100. F15 raw = 85, so Fundamental impact = -15 points.
        # V1.2.3c must explain this impact, not cap/rescue it to -6 or -8.
        self.assertAlmostEqual(row["no_fund_exact"], 100.0, places=12)
        self.assertAlmostEqual(row["composite_f15_exact"], 85.0, places=12)
        self.assertAlmostEqual(row["f15_fund_impact_exact_pts"], -15.0, places=12)
        self.assertEqual(row["fundamental_impact_state"], "HIGH IMPACT")
        self.assertEqual(row["fundamental_impact_direction"], "PENALTY")

        summary = summarize_selected_composite(out)
        self.assertTrue(summary["no_hard_cap"])

    def test_review_fundamental_remains_unimputed_and_unranked(self):
        out = build_selected_composite_table(self.sample())
        row = out[out["symbol"] == "REVIEW"].iloc[0]

        self.assertTrue(np.isnan(row["composite_f15_exact"]))
        self.assertTrue(np.isnan(row["composite_f15_rank"]))
        self.assertEqual(row["fundamental_impact_state"], "N/A")
        self.assertIn("NO FULL COMPOSITE", row["composite_status"])

    def test_source_dataframe_is_not_mutated(self):
        source = self.sample()
        original = source.copy(deep=True)
        build_selected_composite_table(source)
        pd.testing.assert_frame_equal(source, original)


if __name__ == "__main__":
    unittest.main()
