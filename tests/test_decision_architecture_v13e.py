import unittest
import numpy as np
import pandas as pd

from scanner.decision_architecture import (
    EXECUTION_READY, READY, WATCH, WAIT, NO_CHASE,
    build_decision_architecture,
    summarize_decision_architecture,
)


class DecisionArchitectureTests(unittest.TestCase):
    def scored(self, close=100.0):
        return pd.DataFrame([{
            "symbol": "ABC", "bucket": "A-QUALITY — WAIT", "setup": "Breakout",
            "quality_score": 95.0, "entry_score": 90.0,
            "decision": "WAIT", "close": close,
        }])

    def zone(self, state="WAITING FOR TRIGGER"):
        return pd.DataFrame([{
            "symbol": "ABC", "plan_state": state,
            "structured_plan": True, "plan_data_confidence": "HIGH",
            "trigger_price": 101.0, "entry_zone_low": 101.0,
            "entry_zone_high": 101.5, "max_acceptable_fill": 102.0,
        }])

    def rr(self, max_fill_rr=2.0):
        return pd.DataFrame([{
            "symbol": "ABC", "max_fill_rr": max_fill_rr,
            "risk_geometry_state": "FAVOURABLE THROUGH ZONE",
        }])

    def test_ready(self):
        out = build_decision_architecture(self.scored(101.2), self.zone("TRIGGERED — IN ENTRY ZONE"), self.rr())
        self.assertEqual(out.iloc[0].decision_state, EXECUTION_READY)
        self.assertTrue(out.iloc[0].decision_ready)
        self.assertTrue(out.iloc[0].trade_quality_eligible)

    def test_watch_before_trigger(self):
        out = build_decision_architecture(self.scored(100.0), self.zone(), self.rr())
        self.assertEqual(out.iloc[0].decision_state, WATCH)
        self.assertFalse(out.iloc[0].decision_ready)

    def test_wait_when_max_fill_rr_is_weak(self):
        out = build_decision_architecture(self.scored(101.2), self.zone("TRIGGERED — IN ENTRY ZONE"), self.rr(1.49))
        self.assertEqual(out.iloc[0].decision_state, WAIT)

    def test_no_chase_for_missed_plan(self):
        out = build_decision_architecture(self.scored(103.0), self.zone("MISSED / NO CHASE — ABOVE MAX FILL"), self.rr())
        self.assertEqual(out.iloc[0].decision_state, NO_CHASE)

    def test_late_above_zone_is_no_chase(self):
        out = build_decision_architecture(self.scored(103.0), self.zone("TRIGGERED — ABOVE ZONE / LATE"), self.rr())
        self.assertEqual(out.iloc[0].decision_state, NO_CHASE)

    def test_unknown_or_missing_plan_never_becomes_ready(self):
        z = self.zone("UNKNOWN STATE")
        out = build_decision_architecture(self.scored(101.2), z, self.rr())
        self.assertEqual(out.iloc[0].decision_state, WAIT)
        self.assertFalse(out.iloc[0].decision_ready)

    def test_official_frame_is_unchanged(self):
        s = self.scored(101.2)
        before = s.copy(deep=True)
        build_decision_architecture(s, self.zone("TRIGGERED — IN ENTRY ZONE"), self.rr())
        pd.testing.assert_frame_equal(s, before)

    def test_developing_candidate_can_be_execution_ready_but_not_trade_quality_eligible(self):
        s = self.scored(101.2)
        s.loc[0, "bucket"] = "DEVELOPING"
        s.loc[0, "quality_score"] = 77.3
        out = build_decision_architecture(s, self.zone("TRIGGERED — IN ENTRY ZONE"), self.rr())
        self.assertEqual(out.iloc[0].decision_state, EXECUTION_READY)
        self.assertFalse(out.iloc[0].trade_quality_eligible)
        self.assertEqual(out.iloc[0].trade_quality_state, "NOT TRADE-QUALITY ELIGIBLE")

    def test_summary_exposes_execution_ready_outside_quality_layer(self):
        rows = [
            {"decision_state": EXECUTION_READY, "decision_ready": True, "trade_quality_eligible": False},
            {"decision_state": EXECUTION_READY, "decision_ready": True, "trade_quality_eligible": True},
        ]
        summary = summarize_decision_architecture(pd.DataFrame(rows))
        self.assertEqual(summary["ready"], 2)
        self.assertEqual(summary["trade_quality_eligible"], 1)
        self.assertEqual(summary["execution_ready_not_trade_quality"], 1)

    def test_summary(self):
        rows = []
        for state in [READY, WATCH, WAIT, NO_CHASE]:
            rows.append({"decision_state": state, "decision_ready": state == READY})
        summary = summarize_decision_architecture(pd.DataFrame(rows))
        self.assertEqual(summary["evaluated"], 4)
        self.assertEqual(summary["ready"], 1)
        self.assertEqual(summary["watch"], 1)
        self.assertEqual(summary["wait"], 1)
        self.assertEqual(summary["no_chase"], 1)
        self.assertEqual(summary["decision_ready"], 1)


if __name__ == "__main__":
    unittest.main()
