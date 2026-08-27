import unittest

import pandas as pd

from scanner.regime import with_breadth


class RegimeIntegrityTests(unittest.TestCase):
    def test_selected_universe_breadth_does_not_mutate_market_score(self):
        base = {
            "score": 60.0,
            "label": "SELECTIVE RISK-ON",
            "exposure": "PLAY SLOW — SELECTIVE EXPOSURE",
            "details": {},
        }
        cross = pd.DataFrame({
            "close": [110.0, 90.0, 105.0, 80.0],
            "ema20": [100.0, 100.0, 100.0, 100.0],
            "ma50": [100.0, 100.0, 100.0, 100.0],
            "ma200": [95.0, 95.0, 95.0, 95.0],
        })

        out = with_breadth(base, cross)
        self.assertEqual(out["score"], 60.0)
        self.assertEqual(out["label"], "SELECTIVE RISK-ON")
        self.assertIn("deployment_score", out)
        self.assertNotEqual(out["deployment_score"], out["score"])
        self.assertEqual(out["breadth"]["members"], 4)


if __name__ == "__main__":
    unittest.main()
