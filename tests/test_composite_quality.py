import unittest

import numpy as np
import pandas as pd

from scanner.composite_quality import (
    build_shadow_composite_table,
    summarize_shadow_composite,
)


class CompositeQualityTests(unittest.TestCase):
    def sample(self):
        return pd.DataFrame(
            [
                {
                    "symbol": "AAA",
                    "official_candidate_quality": 96.0,
                    "leadership_score": 90.0,
                    "fundamental_score": 90.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "BBB",
                    "official_candidate_quality": 95.0,
                    "leadership_score": 88.0,
                    "fundamental_score": 40.0,
                    "fundamental_confidence": "HIGH",
                    "metric_integrity": "PASS",
                    "companyfacts": "PASS",
                    "batch_status": "PASS",
                },
                {
                    "symbol": "CCC",
                    "official_candidate_quality": 94.0,
                    "leadership_score": 85.0,
                    "fundamental_score": np.nan,
                    "fundamental_confidence": "UNKNOWN",
                    "metric_integrity": "REVIEW",
                    "companyfacts": "PASS",
                    "batch_status": "REVIEW",
                },
            ]
        )

    def test_no_fund_reference_is_70_30(self):
        out = build_shadow_composite_table(self.sample())
        aaa = out[out["symbol"] == "AAA"].iloc[0]
        self.assertAlmostEqual(
            aaa["technical_leadership_reference"],
            0.70 * 96.0 + 0.30 * 90.0,
            places=1,
        )

    def test_f20_is_56_24_20(self):
        out = build_shadow_composite_table(self.sample())
        aaa = out[out["symbol"] == "AAA"].iloc[0]
        expected = 0.56 * 96.0 + 0.24 * 90.0 + 0.20 * 90.0
        self.assertAlmostEqual(aaa["shadow_f20"], expected, places=1)

    def test_weak_fundamentals_demote_without_overwriting_official_quality(self):
        source = self.sample()
        original = source.copy(deep=True)
        out = build_shadow_composite_table(source)
        bbb = out[out["symbol"] == "BBB"].iloc[0]
        self.assertEqual(bbb["official_candidate_quality"], 95.0)
        self.assertLess(
            bbb["shadow_f20"],
            bbb["technical_leadership_reference"],
        )
        pd.testing.assert_frame_equal(source, original)

    def test_review_fundamentals_are_not_imputed(self):
        out = build_shadow_composite_table(self.sample())
        ccc = out[out["symbol"] == "CCC"].iloc[0]
        self.assertTrue(np.isnan(ccc["shadow_f10"]))
        self.assertTrue(np.isnan(ccc["shadow_f20"]))
        self.assertTrue(np.isnan(ccc["shadow_f30"]))
        self.assertIn("REVIEW", ccc["quality_profile"])

    def test_full_alignment_profile(self):
        out = build_shadow_composite_table(self.sample())
        aaa = out[out["symbol"] == "AAA"].iloc[0]
        self.assertEqual(aaa["quality_profile"], "FULL ALIGNMENT")

    def test_technical_led_weak_fundamentals_profile(self):
        out = build_shadow_composite_table(self.sample())
        bbb = out[out["symbol"] == "BBB"].iloc[0]
        self.assertEqual(
            bbb["quality_profile"],
            "TECHNICAL-LED / WEAK FUNDAMENTALS",
        )

    def test_summary_excludes_review_from_full_rank(self):
        out = build_shadow_composite_table(self.sample())
        summary = summarize_shadow_composite(out)
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["rankable"], 2)
        self.assertEqual(summary["unranked_fundamental_review"], 1)
        self.assertEqual(summary["full_alignment"], 1)

    def test_fundamental_sensitivity_increases_for_weak_fundamentals(self):
        out = build_shadow_composite_table(self.sample())
        bbb = out[out["symbol"] == "BBB"].iloc[0]
        self.assertGreater(bbb["shadow_f10"], bbb["shadow_f20"])
        self.assertGreater(bbb["shadow_f20"], bbb["shadow_f30"])
        self.assertGreater(bbb["scenario_spread_pts"], 0)


if __name__ == "__main__":
    unittest.main()
