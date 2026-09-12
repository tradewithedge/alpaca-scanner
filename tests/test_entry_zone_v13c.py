import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from scanner.entry_zone import (
    build_entry_zone_diagnostics,
    summarize_entry_zone_diagnostics,
)


def make_bars(symbol="TEST", last_close=99.0, prior_highs=None):
    if prior_highs is None:
        prior_highs = [90.0 + i * 0.5 for i in range(20)]
        prior_highs[-1] = 100.0
    rows = []
    start = pd.Timestamp("2026-08-01", tz="UTC")
    for i, high in enumerate(prior_highs):
        close = high - 0.5
        rows.append(
            {
                "symbol": symbol,
                "timestamp": start + pd.Timedelta(days=i),
                "open": close - 0.2,
                "high": high,
                "low": close - 1.0,
                "close": close,
                "volume": 1_000_000,
            }
        )
    rows.append(
        {
            "symbol": symbol,
            "timestamp": start + pd.Timedelta(days=len(prior_highs)),
            "open": last_close - 0.2,
            "high": last_close + 0.4,
            "low": last_close - 0.8,
            "close": last_close,
            "volume": 1_100_000,
        }
    )
    return pd.DataFrame(rows)


def scored_row(
    symbol="TEST",
    setup="CONFIRMED BREAKOUT",
    close=99.0,
    ema8=98.0,
    ema20=97.0,
    atr14=2.0,
    high20_prev=100.0,
    entry_px=None,
):
    if entry_px is None:
        entry_px = round(close, 2)
    return {
        "symbol": symbol,
        "bucket": "TECH ACTIONABLE — EVENT CHECK",
        "setup": setup,
        "quality_score": 90.0,
        "entry_score": 80.0,
        "decision": "TECHNICALLY ACTIONABLE — VERIFY EVENT DATE",
        "entry_px": entry_px,
        "close": close,
        "ema8": ema8,
        "ema20": ema20,
        "atr14": atr14,
        "high20_prev": high20_prev,
    }


class EntryZoneV13cTests(unittest.TestCase):
    def test_empty_input_returns_schema(self):
        out = build_entry_zone_diagnostics(pd.DataFrame(), pd.DataFrame())
        self.assertTrue(out.empty)
        self.assertIn("trigger_price", out.columns)
        self.assertIn("max_acceptable_fill", out.columns)

    def test_inputs_are_not_mutated(self):
        scored = pd.DataFrame([scored_row()])
        bars = make_bars()
        scored_before = scored.copy(deep=True)
        bars_before = bars.copy(deep=True)
        build_entry_zone_diagnostics(scored, bars)
        assert_frame_equal(scored, scored_before)
        assert_frame_equal(bars, bars_before)

    def test_prior_structure_excludes_latest_observed_bar(self):
        bars = make_bars(last_close=150.0)
        scored = pd.DataFrame([scored_row(close=150.0)])
        out = build_entry_zone_diagnostics(scored, bars).iloc[0]
        self.assertAlmostEqual(out["prior_20_high"], 100.0)
        self.assertAlmostEqual(out["trigger_price"], 100.1)

    def test_breakout_trigger_uses_prior_20_high(self):
        scored = pd.DataFrame([scored_row(close=99.0)])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=99.0)).iloc[0]
        self.assertEqual(out["trigger_type"], "20D HIGH BREAK")
        self.assertAlmostEqual(out["trigger_price"], 100.1)
        self.assertEqual(out["plan_state"], "WAITING FOR TRIGGER")
        self.assertTrue(out["structured_plan"])

    def test_high20_structure_parity(self):
        scored = pd.DataFrame([scored_row(high20_prev=100.0)])
        out = build_entry_zone_diagnostics(scored, make_bars()).iloc[0]
        self.assertTrue(out["high20_structure_parity"])

    def test_high20_structure_parity_mismatch_is_visible(self):
        scored = pd.DataFrame([scored_row(high20_prev=99.0)])
        table = build_entry_zone_diagnostics(scored, make_bars())
        self.assertFalse(table.iloc[0]["high20_structure_parity"])
        summary = summarize_entry_zone_diagnostics(table)
        self.assertEqual(summary["high20_structure_parity_mismatches"], 1)

    def test_pullback_reclaim_trigger_can_enter_zone(self):
        highs = [96.0] * 19 + [99.5]
        bars = make_bars(last_close=100.0, prior_highs=highs)
        scored = pd.DataFrame([
            scored_row(
                setup="EMA20 PULLBACK",
                close=100.0,
                ema8=99.0,
                ema20=98.0,
                atr14=2.0,
                high20_prev=99.5,
            )
        ])
        out = build_entry_zone_diagnostics(scored, bars).iloc[0]
        self.assertEqual(out["trigger_type"], "PULLBACK RECLAIM")
        self.assertAlmostEqual(out["trigger_price"], 99.5995)
        self.assertEqual(out["plan_state"], "TRIGGERED — IN ENTRY ZONE")

    def test_vcp_uses_prior_10_structure_high(self):
        prior = [90.0] * 10 + [95.0] * 9 + [100.0]
        bars = make_bars(last_close=100.3, prior_highs=prior)
        scored = pd.DataFrame([
            scored_row(
                setup="VCP / TIGHTENING",
                close=100.3,
                ema8=99.0,
                ema20=98.5,
                atr14=2.0,
                high20_prev=100.0,
            )
        ])
        out = build_entry_zone_diagnostics(scored, bars).iloc[0]
        self.assertEqual(out["trigger_type"], "10D STRUCTURE BREAK")
        self.assertAlmostEqual(out["trigger_price"], 100.1)
        self.assertEqual(out["plan_state"], "TRIGGERED — IN ENTRY ZONE")

    def test_repair_gets_reclaim_plan_not_actionable_assumption(self):
        highs = [96.0] * 19 + [99.0]
        scored = pd.DataFrame([
            scored_row(
                setup="MA20 REPAIR WINDOW",
                close=97.5,
                ema8=98.0,
                ema20=98.5,
                atr14=2.0,
                high20_prev=99.0,
            )
        ])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=97.5, prior_highs=highs)).iloc[0]
        self.assertEqual(out["trigger_type"], "EMA20 REPAIR RECLAIM")
        self.assertEqual(out["plan_state"], "WAITING FOR TRIGGER")
        self.assertIn("repair trigger", out["confirmation_condition"].lower())

    def test_no_clean_setup_does_not_invent_trigger(self):
        scored = pd.DataFrame([scored_row(setup="TRENDING / NO CLEAN SETUP")])
        out = build_entry_zone_diagnostics(scored, make_bars()).iloc[0]
        self.assertFalse(out["structured_plan"])
        self.assertEqual(out["trigger_type"], "NONE")
        self.assertTrue(pd.isna(out["trigger_price"]))
        self.assertEqual(out["plan_state"], "NO STRUCTURED PLAN")
        self.assertEqual(out["plan_data_confidence"], "HIGH")

    def test_trigger_beyond_frozen_hard_ceiling_is_blocked(self):
        scored = pd.DataFrame([
            scored_row(
                setup="CONFIRMED BREAKOUT",
                close=98.0,
                ema8=95.0,
                ema20=94.0,
                atr14=2.0,
                high20_prev=100.0,
            )
        ])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=98.0)).iloc[0]
        self.assertTrue(out["trigger_beyond_hard_ceiling"])
        self.assertEqual(out["plan_state"], "BLOCKED — TRIGGER BEYOND HARD CEILING")
        self.assertLess(out["frozen_hard_ceiling_px"], out["trigger_price"])

    def test_entry_zone_and_max_fill_are_atr_sized_and_hard_capped(self):
        scored = pd.DataFrame([
            scored_row(
                setup="CONFIRMED BREAKOUT",
                close=100.2,
                ema8=100.0,
                ema20=99.0,
                atr14=2.0,
                high20_prev=100.0,
            )
        ])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=100.2)).iloc[0]
        self.assertAlmostEqual(out["trigger_price"], 100.1)
        self.assertAlmostEqual(out["entry_zone_high"], 100.6)
        self.assertAlmostEqual(out["raw_max_fill"], 101.1)
        self.assertAlmostEqual(out["max_acceptable_fill"], 101.1)
        self.assertAlmostEqual(out["entry_zone_width_atr"], 0.25)

    def test_above_zone_late_state(self):
        scored = pd.DataFrame([
            scored_row(
                close=100.8,
                ema8=100.0,
                ema20=99.0,
                atr14=2.0,
                high20_prev=100.0,
            )
        ])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=100.8)).iloc[0]
        self.assertEqual(out["plan_state"], "TRIGGERED — ABOVE ZONE / LATE")

    def test_above_max_fill_is_missed_no_chase(self):
        scored = pd.DataFrame([
            scored_row(
                close=102.0,
                ema8=100.0,
                ema20=99.0,
                atr14=2.0,
                high20_prev=100.0,
            )
        ])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=102.0)).iloc[0]
        self.assertEqual(out["plan_state"], "MISSED / NO CHASE — ABOVE MAX FILL")

    def test_official_entry_ref_current_match_is_measured_not_rewritten(self):
        scored = pd.DataFrame([scored_row(close=99.123, entry_px=99.12)])
        out = build_entry_zone_diagnostics(scored, make_bars(last_close=99.123)).iloc[0]
        self.assertTrue(out["official_entry_ref_matches_current_price"])
        self.assertEqual(out["official_entry_px"], 99.12)
        self.assertEqual(out["current_price"], 99.123)

    def test_missing_atr_is_not_ranked_without_imputation(self):
        scored = pd.DataFrame([scored_row(atr14=np.nan)])
        out = build_entry_zone_diagnostics(scored, make_bars()).iloc[0]
        self.assertEqual(out["plan_state"], "NOT RANKED")
        self.assertEqual(out["plan_data_confidence"], "LOW")
        self.assertTrue(pd.isna(out["max_acceptable_fill"]))

    def test_summary_reconciles_plan_states(self):
        rows = [
            scored_row("WAIT", close=99.0),
            scored_row("ZONE", close=100.2),
            scored_row("LATE", close=100.8),
            scored_row("MISS", close=102.0),
            scored_row("BLOCK", close=98.0, ema8=95.0, ema20=94.0),
            scored_row("NOPLAN", setup="TRENDING / NO CLEAN SETUP", close=99.0),
        ]
        bars = pd.concat([
            make_bars(symbol="WAIT", last_close=99.0),
            make_bars(symbol="ZONE", last_close=100.2),
            make_bars(symbol="LATE", last_close=100.8),
            make_bars(symbol="MISS", last_close=102.0),
            make_bars(symbol="BLOCK", last_close=98.0),
            make_bars(symbol="NOPLAN", last_close=99.0),
        ], ignore_index=True)
        table = build_entry_zone_diagnostics(pd.DataFrame(rows), bars)
        summary = summarize_entry_zone_diagnostics(table)
        self.assertEqual(summary["evaluated"], 6)
        self.assertEqual(summary["waiting_for_trigger"], 1)
        self.assertEqual(summary["in_entry_zone"], 1)
        self.assertEqual(summary["above_zone_late"], 1)
        self.assertEqual(summary["missed_no_chase"], 1)
        self.assertEqual(summary["trigger_blocked"], 1)
        self.assertEqual(summary["no_structured_plan"], 1)
        self.assertEqual(summary["structured_plans"], 5)


if __name__ == "__main__":
    unittest.main()
