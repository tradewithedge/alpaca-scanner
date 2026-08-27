import unittest

import pandas as pd

from scanner.audit import EXPECTED_BUCKETS, bucket_integrity, build_funnel, liquidity_summary


class AuditIntegrityTests(unittest.TestCase):
    def test_funnel_rates(self):
        f = build_funnel([
            ("Universe", 1000),
            ("Matched", 900),
            ("Liquidity", 450),
            ("Quality", 90),
        ])
        self.assertEqual(f.loc[0, "Count"], 1000)
        self.assertEqual(f.loc[1, "% of prior stage"], 90.0)
        self.assertEqual(f.loc[2, "% of starting universe"], 45.0)
        self.assertEqual(f.loc[3, "% of prior stage"], 20.0)

    def test_bucket_reconciliation_includes_wait(self):
        rows = []
        for bucket in EXPECTED_BUCKETS:
            rows.append({"bucket": bucket})
        rows.extend([{"bucket": "WAIT"}, {"bucket": "A-QUALITY — WAIT"}])
        audit = bucket_integrity(pd.DataFrame(rows))
        self.assertTrue(audit["reconciled"])
        self.assertEqual(audit["row_count"], 8)
        self.assertEqual(audit["counts"]["WAIT"], 2)
        self.assertEqual(audit["counts"]["A-QUALITY — WAIT"], 2)

    def test_unknown_bucket_fails_reconciliation(self):
        audit = bucket_integrity(pd.DataFrame([
            {"bucket": "ACTIONABLE NOW"},
            {"bucket": "MYSTERY"},
            {"bucket": None},
        ]))
        self.assertFalse(audit["reconciled"])
        self.assertEqual(audit["unknown_count"], 2)
        self.assertIn("MYSTERY", audit["unknown_buckets"])
        self.assertIn("<MISSING>", audit["unknown_buckets"])

    def test_liquidity_summary_cutoff(self):
        df = pd.DataFrame([
            {"symbol": "A", "prev_dollar_volume": 10_000_000, "passed_liquidity": False},
            {"symbol": "B", "prev_dollar_volume": 19_500_000, "passed_liquidity": False},
            {"symbol": "C", "prev_dollar_volume": 20_500_000, "passed_liquidity": True},
            {"symbol": "D", "prev_dollar_volume": 40_000_000, "passed_liquidity": True},
        ])
        s = liquidity_summary(df, 20_000_000)
        self.assertEqual(list(s["cutoff_sample"]["symbol"][:2]), ["C", "B"])
        self.assertGreater(s["median"], 0)


if __name__ == "__main__":
    unittest.main()
