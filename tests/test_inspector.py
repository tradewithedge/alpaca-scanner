import unittest

import numpy as np

from scanner.inspector import (
    in_selected_universe,
    inspector_authority,
    liquidity_diagnostic,
    normalize_ticker,
    pct_rank_against_reference,
    resolve_asset,
    zero_to_100_rank_against_reference,
)


class TickerInspectorTests(unittest.TestCase):
    def test_normalize_and_resolve(self):
        assets = [
            {"symbol": "AMZN", "tradable": True},
            {"symbol": "BF.B", "tradable": True},
        ]
        self.assertEqual(normalize_ticker(" amzn "), "AMZN")
        self.assertEqual(resolve_asset(assets, "AMZN")["symbol"], "AMZN")
        self.assertEqual(resolve_asset(assets, "BFB")["symbol"], "BF.B")
        self.assertEqual(normalize_ticker("BAD/TICKER"), "")

    def test_membership(self):
        self.assertTrue(in_selected_universe("AMZN", ["AAPL", "AMZN"]))
        self.assertFalse(in_selected_universe("MSFT", ["AAPL", "AMZN"]))
        self.assertIsNone(in_selected_universe("AMZN", None))

    def test_rank_helpers(self):
        ref = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(pct_rank_against_reference(4.0, ref), 100.0)
        self.assertAlmostEqual(zero_to_100_rank_against_reference(4.0, ref), 100.0)
        self.assertLess(pct_rank_against_reference(0.0, ref), 30.0)
        self.assertLess(zero_to_100_rank_against_reference(0.0, ref), 10.0)

    def test_liquidity_diagnostic(self):
        passing = liquidity_diagnostic(
            {"c": 100.0, "v": 300_000, "t": "x"},
            min_price=5.0,
            min_dollar_volume=20_000_000,
        )
        self.assertEqual(passing["status"], "PASS")
        self.assertEqual(passing["prev_dollar_volume"], 30_000_000)

        failing = liquidity_diagnostic(
            {"c": 10.0, "v": 1_000_000, "t": "x"},
            min_price=5.0,
            min_dollar_volume=20_000_000,
        )
        self.assertEqual(failing["status"], "FAIL")
        self.assertIn("dollar volume", failing["reason"])

    def test_no_reference_never_claims_official_quality(self):
        state = inspector_authority(
            has_reference=False,
            persistent_pass=True,
            liquidity_status="PASS",
            bucket="TECH ACTIONABLE — EVENT CHECK",
        )
        self.assertEqual(state["persistent_quality"], "REF REQUIRED")
        self.assertFalse(state["candidate_quality_authoritative"])
        self.assertFalse(state["leadership_authoritative"])
        self.assertFalse(state["legacy_rs_authoritative"])
        self.assertEqual(state["official_status"], "NOT RANKED")
        self.assertEqual(state["conclusion"], "DIRECT DIAGNOSTICS")

    def test_reference_fail_is_not_eligible(self):
        state = inspector_authority(
            has_reference=True,
            persistent_pass=False,
            liquidity_status="PASS",
            bucket="A-QUALITY — WAIT",
        )
        self.assertEqual(state["persistent_quality"], "FAIL")
        self.assertEqual(state["official_status"], "NOT ELIGIBLE")

    def test_reference_pass_can_show_bucket(self):
        state = inspector_authority(
            has_reference=True,
            persistent_pass=True,
            liquidity_status="PASS",
            bucket="A-QUALITY — WAIT",
        )
        self.assertEqual(state["persistent_quality"], "PASS")
        self.assertEqual(state["official_status"], "A-QUALITY — WAIT")
        self.assertTrue(state["candidate_quality_authoritative"])


if __name__ == "__main__":
    unittest.main()
