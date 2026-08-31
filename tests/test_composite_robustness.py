import unittest

import numpy as np
import pandas as pd

from scanner.composite_quality import build_shadow_composite_table
from scanner.composite_robustness import (
    build_composite_robustness_table,
    summarize_composite_robustness,
)


class CompositeRobustnessTests(unittest.TestCase):
    def sample(self):
        return pd.DataFrame(
            [
                {
                    "symbol": "A",
                    "official_candidate_quality": 98.0,
                    "leadership_score": 90.0,
                    "fundamental_score": 95.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "B",
                    "official_candidate_quality": 97.0,
                    "leadership_score": 91.0,
                    "fundamental_score": 30.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "C",
                    "official_candidate_quality": 95.0,
                    "leadership_score": 75.0,
                    "fundamental_score": 100.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "D",
                    "official_candidate_quality": 94.0,
                    "leadership_score": 85.0,
                    "fundamental_score": 65.0,
                    "fundamental_confidence": "MEDIUM",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "E",
                    "official_candidate_quality": 93.0,
                    "leadership_score": 88.0,
                    "fundamental_score": np.nan,
                    "fundamental_confidence": "UNKNOWN",
                    "metric_integrity": "REVIEW",
                    "companyfacts": "PASS",
                    "batch_status": "REVIEW",
                },
            ]
        )

    def test_f10_f20_f30_match_accepted_v123a_exactly(self):
        source = self.sample()
        accepted = build_shadow_composite_table(source)
        robust = build_composite_robustness_table(source)

        for symbol in ("A", "B", "C", "D"):
            a = accepted[accepted["symbol"] == symbol].iloc[0]
            r = robust[robust["symbol"] == symbol].iloc[0]
            self.assertAlmostEqual(a["shadow_f10"], r["score_f10"], places=1)
            self.assertAlmostEqual(a["shadow_f20"], r["score_f20"], places=1)
            self.assertAlmostEqual(a["shadow_f30"], r["score_f30"], places=1)

    def test_interpolation_formula_f15_and_f25(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "A"].iloc[0]
        no_fund = row["technical_leadership_reference"]
        fund = row["fundamental_score"]

        self.assertAlmostEqual(
            row["score_f15"],
            0.85 * no_fund + 0.15 * fund,
            places=1,
        )
        self.assertAlmostEqual(
            row["score_f25"],
            0.75 * no_fund + 0.25 * fund,
            places=1,
        )

    def test_review_row_never_receives_weighted_scores_or_ranks(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "E"].iloc[0]

        self.assertTrue(np.isnan(row["score_f20"]))
        self.assertTrue(np.isnan(row["rank_f20"]))
        self.assertFalse(bool(row["cap6_triggered"]))

    def test_weight_sensitivity_is_measured(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "B"].iloc[0]

        self.assertGreaterEqual(row["rank_range_f10_f30"], 0)
        self.assertGreaterEqual(row["top10_weight_count"], 0)

    def test_cap6_clamps_large_negative_f20_impact(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "B"].iloc[0]

        self.assertLess(row["f20_fund_score_impact_pts"], -6.0)
        self.assertTrue(bool(row["cap6_triggered"]))
        self.assertEqual(row["cap6_direction"], "DOWNSIDE CAP")
        self.assertAlmostEqual(
            row["guard_f20_cap6"],
            row["technical_leadership_reference"] - 6.0,
            places=1,
        )

    def test_cap6_clamps_large_positive_f20_impact(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "C"].iloc[0]

        if row["f20_fund_score_impact_pts"] > 6.0:
            self.assertTrue(bool(row["cap6_triggered"]))
            self.assertEqual(row["cap6_direction"], "UPSIDE CAP")
            self.assertAlmostEqual(
                row["guard_f20_cap6"],
                row["technical_leadership_reference"] + 6.0,
                places=1,
            )

    def test_cap_does_not_change_score_when_inside_threshold(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "D"].iloc[0]

        if abs(row["f20_fund_score_impact_pts"]) <= 6.0:
            self.assertFalse(bool(row["cap6_triggered"]))
            self.assertAlmostEqual(
                row["guard_f20_cap6"],
                row["shadow_f20"],
                places=1,
            )

    def test_guardrail_simulation_does_not_modify_underlying_scores(self):
        source = self.sample()
        original = source.copy(deep=True)
        robust = build_composite_robustness_table(source)

        pd.testing.assert_frame_equal(source, original)
        for symbol in ("A", "B", "C", "D", "E"):
            src = source[source["symbol"] == symbol].iloc[0]
            row = robust[robust["symbol"] == symbol].iloc[0]
            self.assertEqual(
                src["official_candidate_quality"],
                row["official_candidate_quality"],
            )
            self.assertEqual(
                src["leadership_score"],
                row["leadership_score"],
            )

    def test_summary_reports_weight_and_guardrail_grids(self):
        out = build_composite_robustness_table(self.sample())
        summary = summarize_composite_robustness(out)

        self.assertEqual(summary["total"], 5)
        self.assertEqual(summary["rankable"], 4)
        self.assertEqual(len(summary["weight_summary"]), 6)
        self.assertEqual(len(summary["guardrail_summary"]), 3)
        self.assertTrue(summary["integrity_match"])

    def test_weight_summary_contains_5_to_30_percent(self):
        out = build_composite_robustness_table(self.sample())
        summary = summarize_composite_robustness(out)
        labels = [row["Fund weight"] for row in summary["weight_summary"]]

        self.assertEqual(
            labels,
            ["5%", "10%", "15%", "20%", "25%", "30%"],
        )

    def test_guardrail_summary_contains_expected_caps(self):
        out = build_composite_robustness_table(self.sample())
        summary = summarize_composite_robustness(out)
        labels = [
            row["F20 impact cap"]
            for row in summary["guardrail_summary"]
        ]
        self.assertEqual(labels, ["±4 pts", "±6 pts", "±8 pts"])


if __name__ == "__main__":
    unittest.main()
