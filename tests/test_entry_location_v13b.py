import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from scanner.entry_location import (
    build_entry_location_diagnostics,
    summarize_entry_location_diagnostics,
)


def row(
    symbol="TEST",
    ext8=1.0,
    ext20=1.0,
    extatr=0.5,
    chase_reasons="",
    bucket="TECH ACTIONABLE — EVENT CHECK",
    setup="EMA20 PULLBACK",
):
    return {
        "symbol": symbol,
        "bucket": bucket,
        "setup": setup,
        "quality_score": 88.0,
        "entry_score": 80.0,
        "decision": "TECHNICALLY ACTIONABLE — VERIFY EVENT DATE",
        "chase_reasons": chase_reasons,
        "close": 101.0,
        "ema8": 100.0,
        "ema20": 100.0,
        "atr14": 2.0,
        "ext_ema8_pct": ext8,
        "ext_ema20_pct": ext20,
        "ext_atr": extatr,
    }


class EntryLocationV13bTests(unittest.TestCase):
    def test_empty_input_returns_empty_schema(self):
        out = build_entry_location_diagnostics(pd.DataFrame())
        self.assertTrue(out.empty)
        self.assertIn("max_chase_pressure_pct", out.columns)
        self.assertIn("hard_no_chase_parity", out.columns)

    def test_input_frame_is_not_mutated(self):
        source = pd.DataFrame([row()])
        before = source.copy(deep=True)
        build_entry_location_diagnostics(source)
        assert_frame_equal(source, before)

    def test_prime_controlled_pressure_is_transparent(self):
        source = pd.DataFrame([row(ext8=2.0, ext20=2.0, extatr=0.5)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertAlmostEqual(out["ema8_pressure_pct"], 40.0)
        self.assertAlmostEqual(out["ema20_pressure_pct"], 25.0)
        self.assertAlmostEqual(out["atr_pressure_pct"], 25.0)
        self.assertAlmostEqual(out["max_chase_pressure_pct"], 40.0)
        self.assertAlmostEqual(out["hard_ceiling_headroom_pct"], 60.0)
        self.assertEqual(out["dominant_extension_axis"], "EMA8")
        self.assertEqual(out["entry_location_state"], "PRIME / CONTROLLED")

    def test_negative_extension_does_not_create_negative_pressure(self):
        source = pd.DataFrame([row(ext8=-1.0, ext20=-1.0, extatr=-0.4)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertEqual(out["ema8_pressure_pct"], 0.0)
        self.assertEqual(out["ema20_pressure_pct"], 0.0)
        self.assertEqual(out["atr_pressure_pct"], 0.0)
        self.assertEqual(out["max_chase_pressure_pct"], 0.0)
        self.assertEqual(out["entry_location_state"], "PRIME / CONTROLLED")

    def test_below_ema20_repair_is_not_mistaken_for_good_location(self):
        source = pd.DataFrame([row(ext8=-2.0, ext20=-2.0, extatr=-0.8)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertEqual(out["max_chase_pressure_pct"], 0.0)
        self.assertEqual(out["entry_location_state"], "REPAIR / BELOW EMA20")

    def test_acceptable_band(self):
        source = pd.DataFrame([row(ext8=3.0, ext20=3.2, extatr=1.0)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertEqual(out["max_chase_pressure_pct"], 60.0)
        self.assertEqual(out["entry_location_state"], "ACCEPTABLE")

    def test_stretched_band_before_hard_gate(self):
        source = pd.DataFrame([row(ext8=4.0, ext20=4.0, extatr=1.2)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertEqual(out["max_chase_pressure_pct"], 80.0)
        self.assertFalse(out["hard_no_chase"])
        self.assertEqual(out["entry_location_state"], "STRETCHED")

    def test_very_late_band_before_hard_gate(self):
        source = pd.DataFrame([row(ext8=4.6, ext20=6.8, extatr=1.7)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertAlmostEqual(out["max_chase_pressure_pct"], 92.0)
        self.assertFalse(out["hard_no_chase"])
        self.assertEqual(out["entry_location_state"], "VERY LATE / AT CEILING")

    def test_exact_hard_ceiling_preserves_strict_greater_than_semantics(self):
        source = pd.DataFrame([row(ext8=5.0, ext20=8.0, extatr=2.0)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertEqual(out["max_chase_pressure_pct"], 100.0)
        self.assertFalse(out["hard_no_chase"])
        self.assertEqual(out["entry_location_state"], "VERY LATE / AT CEILING")

    def test_ema8_hard_no_chase(self):
        source = pd.DataFrame([row(ext8=5.01, ext20=2.0, extatr=0.8, chase_reasons="5.0% above EMA8")])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertTrue(out["hard_no_chase"])
        self.assertIn("EMA8 extension", out["hard_no_chase_reasons"])
        self.assertEqual(out["entry_location_state"], "NO CHASE — HARD CEILING")
        self.assertTrue(out["hard_no_chase_parity"])

    def test_ema20_hard_no_chase(self):
        source = pd.DataFrame([row(ext8=2.0, ext20=8.01, extatr=1.0, chase_reasons="8.0% above EMA20")])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertTrue(out["hard_no_chase"])
        self.assertIn("EMA20 extension", out["hard_no_chase_reasons"])

    def test_atr_hard_no_chase(self):
        source = pd.DataFrame([row(ext8=2.0, ext20=4.0, extatr=2.01, chase_reasons="2.0 ATR above EMA20")])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertTrue(out["hard_no_chase"])
        self.assertIn("ATR ceiling", out["hard_no_chase_reasons"])

    def test_missing_extension_is_not_ranked_without_imputation(self):
        source = pd.DataFrame([row(ext8=np.nan, ext20=2.0, extatr=0.5)])
        out = build_entry_location_diagnostics(source).iloc[0]
        self.assertEqual(out["entry_location_state"], "NOT RANKED")
        self.assertEqual(out["location_data_confidence"], "LOW")
        self.assertTrue(pd.isna(out["max_chase_pressure_pct"]))

    def test_hard_gate_parity_mismatch_is_visible(self):
        source = pd.DataFrame([row(ext8=5.2, ext20=2.0, extatr=0.5, chase_reasons="")])
        table = build_entry_location_diagnostics(source)
        self.assertFalse(table.iloc[0]["hard_no_chase_parity"])
        summary = summarize_entry_location_diagnostics(table)
        self.assertEqual(summary["hard_ceiling_parity_mismatches"], 1)

    def test_summary_reconciles_states_and_late_actionable(self):
        source = pd.DataFrame(
            [
                row("P", ext8=2.0, ext20=2.0, extatr=0.5),
                row("A", ext8=3.0, ext20=3.2, extatr=1.0),
                row("S", ext8=4.0, ext20=4.0, extatr=1.2),
                row("L", ext8=4.6, ext20=6.8, extatr=1.7),
                row("R", ext8=-2.0, ext20=-2.0, extatr=-0.5, bucket="A-QUALITY — WAIT"),
                row("H", ext8=5.2, ext20=4.0, extatr=1.0, chase_reasons="5.2% above EMA8", bucket="A-QUALITY — WAIT"),
            ]
        )
        table = build_entry_location_diagnostics(source)
        summary = summarize_entry_location_diagnostics(table)
        self.assertEqual(summary["evaluated"], 6)
        self.assertEqual(summary["ranked"], 6)
        self.assertEqual(summary["prime_controlled"], 1)
        self.assertEqual(summary["acceptable"], 1)
        self.assertEqual(summary["stretched"], 1)
        self.assertEqual(summary["very_late"], 1)
        self.assertEqual(summary["repair_below_ema20"], 1)
        self.assertEqual(summary["hard_no_chase"], 1)
        self.assertEqual(summary["late_official_actionable"], 2)
        self.assertEqual(sum(summary[k] for k in [
            "prime_controlled", "acceptable", "stretched", "very_late",
            "repair_below_ema20", "hard_no_chase"
        ]), 6)


if __name__ == "__main__":
    unittest.main()
