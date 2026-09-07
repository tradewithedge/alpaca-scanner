import unittest
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from scanner.volume_quality import (
    build_contextual_volume_quality,
    completed_session_bars,
    summarize_contextual_volume_quality,
)


def make_bars(
    symbol="AAA",
    n=80,
    start="2026-05-01",
    volumes=None,
    closes=None,
):
    dates = pd.bdate_range(start=start, periods=n, tz="America/New_York")
    ts = dates.tz_convert("UTC")
    if closes is None:
        closes = np.linspace(100.0, 120.0, n)
    closes = np.asarray(closes, dtype=float)
    if volumes is None:
        volumes = np.full(n, 1_000_000.0)
    volumes = np.asarray(volumes, dtype=float)
    return pd.DataFrame(
        {
            "symbol": symbol,
            "timestamp": ts,
            "open": closes * 0.997,
            "high": closes * 1.005,
            "low": closes * 0.992,
            "close": closes,
            "volume": volumes,
        }
    )


def scored(symbol="AAA"):
    return pd.DataFrame(
        [
            {
                "symbol": symbol,
                "bucket": "A-QUALITY — WAIT",
                "setup": "TRENDING / NO CLEAN SETUP",
                "quality_score": 92.0,
                "entry_score": 66.0,
            }
        ]
    )


class CompletedSessionTests(unittest.TestCase):
    def test_same_day_bar_is_excluded_before_1630_et(self):
        bars = make_bars(n=40)
        current_date = bars.iloc[-1]["timestamp"].tz_convert("America/New_York").date()
        asof = pd.Timestamp(f"{current_date} 15:00", tz="America/New_York").tz_convert("UTC")
        out, excluded = completed_session_bars(bars, asof_utc=asof)
        self.assertTrue(excluded)
        self.assertEqual(len(out), len(bars) - 1)

    def test_same_day_bar_is_allowed_after_1630_et(self):
        bars = make_bars(n=40)
        current_date = bars.iloc[-1]["timestamp"].tz_convert("America/New_York").date()
        asof = pd.Timestamp(f"{current_date} 17:00", tz="America/New_York").tz_convert("UTC")
        out, excluded = completed_session_bars(bars, asof_utc=asof)
        self.assertFalse(excluded)
        self.assertEqual(len(out), len(bars))


class ContextualVolumeTests(unittest.TestCase):
    def _after_close(self, bars):
        d = bars.iloc[-1]["timestamp"].tz_convert("America/New_York").date()
        return pd.Timestamp(f"{d} 17:00", tz="America/New_York").tz_convert("UTC")

    def test_input_frames_are_not_mutated(self):
        bars = make_bars()
        official = scored()
        bars_before = bars.copy(deep=True)
        official_before = official.copy(deep=True)
        build_contextual_volume_quality(official, bars, asof_utc=self._after_close(bars))
        pd.testing.assert_frame_equal(bars, bars_before)
        pd.testing.assert_frame_equal(official, official_before)

    def test_rvol_uses_prior_20_sessions_only(self):
        volumes = np.full(80, 1_000_000.0)
        volumes[-1] = 2_000_000.0
        bars = make_bars(volumes=volumes)
        table = build_contextual_volume_quality(scored(), bars, asof_utc=self._after_close(bars))
        self.assertAlmostEqual(float(table.iloc[0]["rvol_20"]), 2.0, places=6)

    def test_breakout_with_expansion_is_confirming(self):
        closes = np.linspace(100.0, 120.0, 80)
        prior_high = (closes[:-1] * 1.005)[-20:].max()
        closes[-1] = prior_high * 1.02
        volumes = np.full(80, 1_000_000.0)
        volumes[-1] = 1_600_000.0
        bars = make_bars(closes=closes, volumes=volumes)
        table = build_contextual_volume_quality(scored(), bars, asof_utc=self._after_close(bars))
        row = table.iloc[0]
        self.assertEqual(row["price_context"], "BREAKOUT")
        self.assertEqual(row["contextual_volume_state"], "CONFIRMING")
        self.assertEqual(row["volume_data_confidence"], "HIGH")

    def test_breakout_without_expansion_is_conflict_watch(self):
        closes = np.linspace(100.0, 120.0, 80)
        prior_high = (closes[:-1] * 1.005)[-20:].max()
        closes[-1] = prior_high * 1.02
        volumes = np.full(80, 1_000_000.0)
        volumes[-1] = 700_000.0
        bars = make_bars(closes=closes, volumes=volumes)
        table = build_contextual_volume_quality(scored(), bars, asof_utc=self._after_close(bars))
        row = table.iloc[0]
        self.assertEqual(row["price_context"], "BREAKOUT")
        self.assertEqual(row["contextual_volume_state"], "CONFLICT / WATCH")

    def test_pullback_dry_up_can_confirm(self):
        closes = np.linspace(100.0, 120.0, 80)
        closes[-1] = 118.5
        volumes = np.full(80, 1_000_000.0)
        volumes[-5:] = 600_000.0
        bars = make_bars(closes=closes, volumes=volumes)
        table = build_contextual_volume_quality(scored(), bars, asof_utc=self._after_close(bars))
        row = table.iloc[0]
        self.assertEqual(row["price_context"], "EMA20 PULLBACK")
        self.assertLessEqual(float(row["vol5_vs_prior20"]), 0.90)
        self.assertEqual(row["contextual_volume_state"], "CONFIRMING")

    def test_low_confidence_is_not_ranked(self):
        bars = make_bars(n=30)
        table = build_contextual_volume_quality(scored(), bars, asof_utc=self._after_close(bars))
        row = table.iloc[0]
        self.assertEqual(row["volume_data_confidence"], "LOW")
        self.assertEqual(row["contextual_volume_state"], "NOT RANKED")

    def test_distribution_watch_is_counted(self):
        closes = np.linspace(100.0, 120.0, 80)
        volumes = np.full(80, 1_000_000.0)
        # Two high-volume down sessions in the final 10 completed sessions.
        closes[-8] = closes[-9] * 0.98
        closes[-3] = closes[-4] * 0.98
        volumes[-8] = 1_500_000.0
        volumes[-3] = 1_500_000.0
        bars = make_bars(closes=closes, volumes=volumes)
        table = build_contextual_volume_quality(scored(), bars, asof_utc=self._after_close(bars))
        summary = summarize_contextual_volume_quality(table)
        self.assertGreaterEqual(int(table.iloc[0]["distribution_days_10"]), 2)
        self.assertEqual(summary["distribution_watch"], 1)

    def test_summary_reconciles_evaluated_count(self):
        a = make_bars("AAA")
        b = make_bars("BBB")
        bars = pd.concat([a, b], ignore_index=True)
        official = pd.concat([scored("AAA"), scored("BBB")], ignore_index=True)
        table = build_contextual_volume_quality(official, bars, asof_utc=self._after_close(a))
        summary = summarize_contextual_volume_quality(table)
        self.assertEqual(summary["evaluated"], 2)
        self.assertEqual(len(table), 2)


if __name__ == "__main__":
    unittest.main()
