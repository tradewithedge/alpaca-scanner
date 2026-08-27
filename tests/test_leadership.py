import unittest

import numpy as np
import pandas as pd

from scanner.leadership import add_leadership_features


def make_series(symbol, spy_closes, alpha=0.0, stress_boost=0.0):
    dates = pd.date_range("2025-01-02", periods=len(spy_closes), freq="B", tz="UTC")
    spy = pd.Series(spy_closes, index=dates, dtype=float)
    spy_ret = spy.pct_change().fillna(0.0)

    stock = [100.0]
    for r in spy_ret.iloc[1:]:
        extra = alpha
        if r <= -0.01:
            extra += stress_boost
        stock.append(stock[-1] * (1.0 + float(r) + extra))

    return pd.DataFrame(
        {"symbol": symbol, "timestamp": dates, "close": stock}
    )


class LeadershipEngineTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(42)
        rets = rng.normal(0.0004, 0.009, 140)
        # Force genuine stress sessions.
        rets[[20, 45, 70, 95, 120]] = [-0.018, -0.015, -0.022, -0.017, -0.019]
        spy_close = 100 * np.cumprod(1 + rets)
        dates = pd.date_range("2025-01-02", periods=len(spy_close), freq="B", tz="UTC")
        self.spy = pd.DataFrame(
            {"symbol": "SPY", "timestamp": dates, "close": spy_close}
        )
        self.spy_close = spy_close

    def test_strong_leader_scores_above_laggard(self):
        leader = make_series(
            "LEAD",
            self.spy_close,
            alpha=0.0015,
            stress_boost=0.015,
        )
        laggard = make_series(
            "LAG",
            self.spy_close,
            alpha=-0.0005,
            stress_boost=-0.005,
        )
        neutral = make_series(
            "MID",
            self.spy_close,
            alpha=0.0003,
            stress_boost=0.003,
        )
        bars = pd.concat([leader, laggard, neutral], ignore_index=True)
        cross = pd.DataFrame({"symbol": ["LEAD", "LAG", "MID"]})

        out = add_leadership_features(cross, bars, self.spy)
        scores = out.set_index("symbol")["leadership_score"]

        self.assertGreater(scores["LEAD"], scores["MID"])
        self.assertGreater(scores["MID"], scores["LAG"])
        self.assertGreaterEqual(scores["LEAD"], 75)
        self.assertLessEqual(scores["LAG"], 25)

    def test_stress_resilience_is_visible(self):
        leader = make_series(
            "LEAD",
            self.spy_close,
            alpha=0.0008,
            stress_boost=0.02,
        )
        bars = leader.copy()
        cross = pd.DataFrame({"symbol": ["LEAD"]})

        out = add_leadership_features(cross, bars, self.spy)
        row = out.iloc[0]
        self.assertGreaterEqual(row["stress_day_count"], 3)
        self.assertGreater(row["stress_outperform_pct"], 50)
        self.assertIn(row["leadership_confidence"], {"HIGH", "MEDIUM"})

    def test_shadow_engine_preserves_rows(self):
        bars = pd.concat(
            [
                make_series("A", self.spy_close, alpha=0.001),
                make_series("B", self.spy_close, alpha=0.0),
            ],
            ignore_index=True,
        )
        cross = pd.DataFrame(
            {
                "symbol": ["A", "B"],
                "quality_score_legacy_marker": [1, 2],
            }
        )
        out = add_leadership_features(cross, bars, self.spy)

        self.assertEqual(len(out), len(cross))
        self.assertEqual(
            list(out["quality_score_legacy_marker"]),
            [1, 2],
        )
        self.assertTrue(
            out["leadership_score"].dropna().between(0, 100).all()
        )

    def test_long_term_rs_and_interpretability_fields(self):
        leader = make_series(
            "LEAD",
            self.spy_close,
            alpha=0.0012,
            stress_boost=0.012,
        )
        cross = pd.DataFrame({"symbol": ["LEAD"]})
        out = add_leadership_features(cross, leader, self.spy)
        row = out.iloc[0]

        self.assertTrue(pd.notna(row["rs_vs_spy_100_pct"]))
        self.assertTrue(pd.notna(row["rs20_10d_ago_pct"]))
        self.assertTrue(pd.notna(row["rs20_change_10d_pp"]))
        self.assertGreaterEqual(row["rs_line_index"], 0)
        self.assertLessEqual(row["rs_line_index"], 100)

    def test_stress_explanation_fields_are_numeric(self):
        leader = make_series(
            "LEAD",
            self.spy_close,
            alpha=0.0005,
            stress_boost=0.01,
        )
        cross = pd.DataFrame({"symbol": ["LEAD"]})
        out = add_leadership_features(cross, leader, self.spy)
        row = out.iloc[0]

        self.assertGreaterEqual(int(row["stress_day_count"]), 3)
        self.assertGreaterEqual(int(row["stress_win_count"]), 0)
        self.assertLessEqual(
            int(row["stress_win_count"]),
            int(row["stress_day_count"]),
        )
        self.assertTrue(pd.notna(row["stress_excess_mean_pct"]))
        self.assertTrue(pd.notna(row["downside_capture_pct"]))
        self.assertIn(
            row["downside_capture_label"],
            {"EXCELLENT", "GOOD", "MARKET-LIKE", "WEAKENING", "POOR"},
        )


if __name__ == "__main__":
    unittest.main()
