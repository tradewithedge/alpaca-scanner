import unittest

import numpy as np
import pandas as pd

from scanner.composite_quality import (
    build_shadow_composite_table,
    summarize_shadow_composite,
)


class CompositeQualityAttributionTests(unittest.TestCase):
    def sample(self):
        # Designed so BRZE_LIKE demonstrates the exact real-world ambiguity:
        # Official rank 4 -> No-Fund rank 1 (Leadership promotion)
        # No-Fund rank 1 -> F20 rank 3 (Fundamental demotion)
        # Official rank 4 -> F20 rank 3 (net promotion still positive)
        return pd.DataFrame(
            [
                {
                    "symbol": "FULL",
                    "official_candidate_quality": 96.0,
                    "leadership_score": 80.0,
                    "fundamental_score": 90.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "TECH1",
                    "official_candidate_quality": 95.0,
                    "leadership_score": 70.0,
                    "fundamental_score": 70.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "TECH2",
                    "official_candidate_quality": 94.0,
                    "leadership_score": 72.0,
                    "fundamental_score": 70.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "BRZE_LIKE",
                    "official_candidate_quality": 92.0,
                    "leadership_score": 99.0,
                    "fundamental_score": 45.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "FUND_STRONG",
                    "official_candidate_quality": 91.0,
                    "leadership_score": 70.0,
                    "fundamental_score": 100.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "REVIEW",
                    "official_candidate_quality": 93.0,
                    "leadership_score": 85.0,
                    "fundamental_score": np.nan,
                    "fundamental_confidence": "UNKNOWN",
                    "metric_integrity": "REVIEW",
                    "companyfacts": "PASS",
                    "batch_status": "REVIEW",
                },
            ]
        )

    def test_formulas_are_unchanged_from_v123(self):
        out = build_shadow_composite_table(self.sample())
        row = out[out["symbol"] == "FULL"].iloc[0]

        self.assertAlmostEqual(
            row["technical_leadership_reference"],
            0.70 * 96.0 + 0.30 * 80.0,
            places=1,
        )
        self.assertAlmostEqual(
            row["shadow_f10"],
            0.63 * 96.0 + 0.27 * 80.0 + 0.10 * 90.0,
            places=1,
        )
        self.assertAlmostEqual(
            row["shadow_f20"],
            0.56 * 96.0 + 0.24 * 80.0 + 0.20 * 90.0,
            places=1,
        )
        self.assertAlmostEqual(
            row["shadow_f30"],
            0.49 * 96.0 + 0.21 * 80.0 + 0.30 * 90.0,
            places=1,
        )

    def test_review_fundamentals_remain_unranked_and_unimputed(self):
        out = build_shadow_composite_table(self.sample())
        row = out[out["symbol"] == "REVIEW"].iloc[0]

        self.assertTrue(np.isnan(row["shadow_f20"]))
        self.assertTrue(np.isnan(row["f20_rank"]))
        self.assertTrue(np.isnan(row["f20_fund_rank_impact"]))
        self.assertIn("REVIEW", row["quality_profile"])

    def test_leadership_and_fundamental_score_impacts_are_separate(self):
        out = build_shadow_composite_table(self.sample())
        row = out[out["symbol"] == "BRZE_LIKE"].iloc[0]

        self.assertGreater(row["leadership_score_impact_pts"], 0)
        self.assertLess(row["f20_fund_score_impact_pts"], 0)

    def test_brze_like_case_is_net_promoted_but_fundamentally_demoted(self):
        out = build_shadow_composite_table(self.sample())
        row = out[out["symbol"] == "BRZE_LIKE"].iloc[0]

        self.assertGreater(row["leadership_rank_impact"], 0)
        self.assertLess(row["f20_fund_rank_impact"], 0)
        self.assertGreater(row["net_f20_rank_change"], 0)

    def test_fundamental_strong_name_is_promoted_from_nofund(self):
        out = build_shadow_composite_table(self.sample())
        row = out[out["symbol"] == "FUND_STRONG"].iloc[0]

        self.assertGreater(row["f20_fund_score_impact_pts"], 0)
        self.assertGreater(row["f20_fund_rank_impact"], 0)

    def test_net_rank_change_equals_official_to_f20(self):
        out = build_shadow_composite_table(self.sample())
        rankable = out[out["shadow_f20"].notna()]

        for _, row in rankable.iterrows():
            self.assertEqual(
                row["net_f20_rank_change"],
                row["official_rank"] - row["f20_rank"],
            )

    def test_fundamental_rank_impact_equals_nofund_to_f20(self):
        out = build_shadow_composite_table(self.sample())
        rankable = out[out["shadow_f20"].notna()]

        for _, row in rankable.iterrows():
            self.assertEqual(
                row["f20_fund_rank_impact"],
                row["no_fund_rank"] - row["f20_rank"],
            )

    def test_summary_contains_incremental_scenario_attribution(self):
        out = build_shadow_composite_table(self.sample())
        summary = summarize_shadow_composite(out)

        self.assertEqual(summary["rankable"], 5)
        self.assertEqual(summary["unranked_fundamental_review"], 1)
        self.assertEqual(
            [r["scenario"] for r in summary["scenario_summary"]],
            ["F10", "F20", "F30"],
        )

        for row in summary["scenario_summary"]:
            self.assertIn("No-Fund Top-10 overlap", row)
            self.assertIn("Spearman vs No-Fund", row)
            self.assertIn("Median |fund rank impact|", row)
            self.assertIn("Mean |fund score impact|", row)

    def test_source_dataframe_is_not_mutated(self):
        source = self.sample()
        original = source.copy(deep=True)
        build_shadow_composite_table(source)
        pd.testing.assert_frame_equal(source, original)

    def test_backward_compatibility_aliases_remain_consistent(self):
        out = build_shadow_composite_table(self.sample())
        rankable = out[out["shadow_f20"].notna()]

        self.assertTrue(
            (
                rankable["rank_change"]
                == rankable["net_f20_rank_change"]
            ).all()
        )
        self.assertTrue(
            (
                rankable["shadow_f20_rank"]
                == rankable["f20_rank"]
            ).all()
        )


if __name__ == "__main__":
    unittest.main()
