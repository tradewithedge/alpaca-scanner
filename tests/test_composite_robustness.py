import unittest

import numpy as np
import pandas as pd

from scanner.composite_quality import (
    build_shadow_composite_table,
    summarize_shadow_composite,
)
from scanner.composite_robustness import (
    build_composite_robustness_table,
    summarize_composite_robustness,
)


class CompositeRobustnessPrecisionTests(unittest.TestCase):
    def sample(self):
        return pd.DataFrame(
            [
                {
                    "symbol": "A",
                    "official_candidate_quality": 98.7,
                    "leadership_score": 83.4,
                    "fundamental_score": 95.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "B",
                    "official_candidate_quality": 97.2,
                    "leadership_score": 91.1,
                    "fundamental_score": 30.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "C",
                    "official_candidate_quality": 95.4,
                    "leadership_score": 75.7,
                    "fundamental_score": 100.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "D",
                    "official_candidate_quality": 94.3,
                    "leadership_score": 85.2,
                    "fundamental_score": 65.0,
                    "fundamental_confidence": "MEDIUM",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "THRESH",
                    "official_candidate_quality": 60.0,
                    "leadership_score": 60.0,
                    "fundamental_score": 90.2,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "REVIEW",
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

    def test_anchor_scores_and_ranks_are_exactly_reused(self):
        accepted = build_shadow_composite_table(self.sample())
        robust = build_composite_robustness_table(self.sample())

        for symbol in ("A", "B", "C", "D", "THRESH"):
            a = accepted[accepted["symbol"] == symbol].iloc[0]
            r = robust[robust["symbol"] == symbol].iloc[0]

            for tag in ("f10", "f20", "f30"):
                self.assertEqual(r[f"score_{tag}"], a[f"shadow_{tag}"])
                self.assertEqual(r[f"rank_{tag}"], a[f"{tag}_rank"])

    def test_anchor_summary_metrics_match_v123a(self):
        accepted = build_shadow_composite_table(self.sample())
        a_summary = summarize_shadow_composite(accepted)

        robust = build_composite_robustness_table(self.sample())
        r_summary = summarize_composite_robustness(robust)

        weight_rows = {
            row["Fund weight"]: row
            for row in r_summary["weight_summary"]
        }

        self.assertEqual(
            weight_rows["20%"]["No-Fund Top-10 overlap"],
            f"{a_summary['nofund_f20_top10_overlap']}/{a_summary['top_n']}",
        )
        self.assertEqual(
            weight_rows["20%"]["Spearman vs No-Fund"],
            a_summary["nofund_f20_spearman"],
        )

    def test_interpolation_uses_unrounded_no_fund_exact(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "A"].iloc[0]

        no_fund_exact = 0.70 * 98.7 + 0.30 * 83.4
        expected_f15_exact = 0.85 * no_fund_exact + 0.15 * 95.0

        self.assertAlmostEqual(row["no_fund_exact"], no_fund_exact, places=10)
        self.assertAlmostEqual(
            row["score_f15_exact"],
            expected_f15_exact,
            places=10,
        )
        self.assertEqual(
            row["score_f15"],
            round(expected_f15_exact, 1),
        )

    def test_interpolation_rank_uses_exact_score(self):
        out = build_composite_robustness_table(self.sample())
        rankable = out[out["score_f15_exact"].notna()].copy()

        expected = (
            rankable["score_f15_exact"]
            .rank(method="min", ascending=False)
        )
        pd.testing.assert_series_equal(
            rankable["rank_f15"],
            expected,
            check_names=False,
        )

    def test_exact_guardrail_trigger_is_not_defeated_by_display_rounding(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "THRESH"].iloc[0]

        # Exact F20 impact = 0.20 * (90.2 - 60.0) = +6.04,
        # while the accepted displayed impact rounds to +6.0.
        self.assertAlmostEqual(
            row["f20_fund_score_impact_exact_pts"],
            6.04,
            places=10,
        )
        self.assertAlmostEqual(
            row["f20_fund_score_impact_pts"],
            6.0,
            places=1,
        )
        self.assertTrue(bool(row["cap6_triggered"]))
        self.assertEqual(row["cap6_direction"], "UPSIDE CAP")

    def test_guardrail_score_uses_exact_no_fund_plus_exact_cap(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "THRESH"].iloc[0]

        self.assertAlmostEqual(
            row["guard_f20_cap6_exact"],
            66.0,
            places=10,
        )
        self.assertEqual(row["guard_f20_cap6"], 66.0)

    def test_review_row_remains_unimputed(self):
        out = build_composite_robustness_table(self.sample())
        row = out[out["symbol"] == "REVIEW"].iloc[0]

        self.assertTrue(np.isnan(row["score_f15_exact"]))
        self.assertTrue(np.isnan(row["rank_f15"]))
        self.assertFalse(bool(row["cap6_triggered"]))

    def test_anchor_integrity_summary_passes(self):
        out = build_composite_robustness_table(self.sample())
        summary = summarize_composite_robustness(out)

        self.assertTrue(summary["anchor_integrity_pass"])
        self.assertEqual(len(summary["weight_summary"]), 6)
        self.assertEqual(len(summary["guardrail_summary"]), 3)

    def test_source_dataframe_is_not_mutated(self):
        source = self.sample()
        original = source.copy(deep=True)
        build_composite_robustness_table(source)
        pd.testing.assert_frame_equal(source, original)

    def test_guardrail_rank_change_compares_to_accepted_f20_rank(self):
        out = build_composite_robustness_table(self.sample())
        rankable = out[out["shadow_f20"].notna()]

        for _, row in rankable.iterrows():
            expected = row["f20_rank"] - row["guard_rank_cap6"]
            self.assertEqual(
                row["guard_rank_change_cap6_vs_raw"],
                expected,
            )


if __name__ == "__main__":
    unittest.main()
