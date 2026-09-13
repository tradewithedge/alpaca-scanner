import unittest
import numpy as np
import pandas as pd

from scanner.risk_reward import build_risk_reward_diagnostics, summarize_risk_reward_diagnostics


def bars(symbol="ABC"):
    rows=[]
    for i in range(25):
        rows.append({"symbol":symbol,"timestamp":f"2026-09-{max(1,i+1):02d}T20:00:00Z","high":100+i*0.2,"low":95+i*0.2,"close":98+i*0.2,"volume":100000})
    return pd.DataFrame(rows)

class TestV13d(unittest.TestCase):
    def scored(self, **kw):
        base={"symbol":"ABC","bucket":"A-QUALITY — WAIT","setup":"EMA20 PULLBACK","quality_score":95,"entry_score":70,"decision":"WAIT","close":100.0,"ema20":99.0,"atr14":2.0,"entry_px":100.0}
        base.update(kw); return pd.DataFrame([base])
    def zone(self, **kw):
        base={"symbol":"ABC","official_bucket":"A-QUALITY — WAIT","official_setup":"EMA20 PULLBACK","plan_state":"WAITING FOR TRIGGER","structured_plan":True,"plan_data_confidence":"HIGH","trigger_price":101.0,"entry_zone_low":101.0,"entry_zone_high":101.5,"max_acceptable_fill":102.0}
        base.update(kw); return pd.DataFrame([base])
    def test_input_not_mutated_and_official_entry_untouched(self):
        s=self.scored(); before=s.copy(deep=True)
        build_risk_reward_diagnostics(s,bars(),entry_zone=self.zone())
        pd.testing.assert_frame_equal(s,before)
    def test_structural_stop_and_rr_geometry(self):
        rr=build_risk_reward_diagnostics(self.scored(),bars(),entry_zone=self.zone())
        r=rr.iloc[0]
        self.assertAlmostEqual(r.stop_price, 95.3, places=6)  # prior-20 low from synthetic history
        self.assertGreater(r.trigger_rr, 0)
        self.assertEqual(r.trigger_rr_band, "STRONG")
        self.assertLess(r.zone_high_rr, r.trigger_rr)
        self.assertLess(r.max_fill_rr, r.zone_high_rr)
    def test_nonstructured_plan_not_ranked(self):
        z=self.zone(structured_plan=False,plan_state="NO STRUCTURED PLAN")
        rr=build_risk_reward_diagnostics(self.scored(),bars(),entry_zone=z)
        self.assertEqual(rr.iloc[0].trigger_rr_band,"NOT RANKED")
    def test_invalid_structural_stop_not_imputed(self):
        s=self.scored(ema20=101.5,atr14=0.1)
        z=self.zone(trigger_price=101.0,entry_zone_high=101.2,max_acceptable_fill=101.3)
        high_bars=bars().copy(); high_bars["low"] = 102.0; high_bars["high"] = 103.0; high_bars["close"] = 102.5
        rr=build_risk_reward_diagnostics(s,high_bars,entry_zone=z)
        self.assertEqual(rr.iloc[0].trigger_rr_band,"NOT RANKED")
    def test_summary_reconciles(self):
        s=pd.concat([self.scored(),self.scored(symbol="DEF")],ignore_index=True)
        z=pd.concat([self.zone(),self.zone(symbol="DEF",trigger_price=110,entry_zone_low=110,entry_zone_high=110.5,max_acceptable_fill=111)],ignore_index=True)
        rr=build_risk_reward_diagnostics(s,bars(),entry_zone=z)
        sm=summarize_risk_reward_diagnostics(rr)
        self.assertEqual(sm["evaluated"],2)
        self.assertEqual(sm["structured"],2)
        self.assertEqual(sum(sm[k] for k in ["strong_trigger_rr","acceptable_trigger_rr","weak_trigger_rr","poor_trigger_rr","not_ranked"]),2)

if __name__ == "__main__": unittest.main()
