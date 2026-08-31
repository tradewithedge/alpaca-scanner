import unittest
from datetime import date
import pandas as pd
from scanner.fundamentals import build_fundamental_snapshot


def fact(start,end,filed,value,form="10-Q",fy=2026,fp="Q2",accn="000-test"):
    return {"start":start,"end":end,"filed":filed,"val":value,"form":form,"fy":fy,"fp":fp,"accn":accn}


def eps_current():
    return [
        fact("2025-04-01","2025-06-30","2025-08-01",1.0,fy=2025),
        fact("2026-04-01","2026-06-30","2026-08-01",2.0,fy=2026),
        fact("2024-01-01","2024-12-31","2025-02-15",4.0,form="10-K",fy=2024,fp="FY"),
        fact("2025-01-01","2025-12-31","2026-02-15",5.0,form="10-K",fy=2025,fp="FY"),
    ]


def migrated_revenue_payload():
    old = [
        fact("2018-04-01","2018-06-30","2018-08-01",100,fy=2018),
        fact("2019-04-01","2019-06-30","2019-08-01",114.4,fy=2019),
    ]
    current = [
        fact("2025-04-01","2025-06-30","2025-08-01",1000,fy=2025),
        fact("2026-04-01","2026-06-30","2026-08-01",1144,fy=2026),
        fact("2024-01-01","2024-12-31","2025-02-15",4000,form="10-K",fy=2024,fp="FY"),
        fact("2025-01-01","2025-12-31","2026-02-15",4500,form="10-K",fy=2025,fp="FY"),
    ]
    return {"entityName":"Migrated Co","facts":{"us-gaap":{
        "RevenueFromContractWithCustomerExcludingAssessedTax":{"units":{"USD":old}},
        "Revenues":{"units":{"USD":current}},
        "EarningsPerShareDiluted":{"units":{"USD/shares":eps_current()}},
    }}}


class ConceptContinuityTests(unittest.TestCase):
    def test_fresher_revenue_concept_beats_first_old_candidate(self):
        snap=build_fundamental_snapshot("MIGR",migrated_revenue_payload(),as_of=date(2026,8,30))
        self.assertEqual(snap["revenue_quarter_concept"],"Revenues")
        self.assertEqual(snap["revenue_annual_concept"],"Revenues")
        self.assertEqual(snap["revenue_q_end"],date(2026,6,30))
        self.assertAlmostEqual(snap["revenue_q_yoy"],0.144,places=6)
        self.assertEqual(snap["revenue_quarter_latest_period_status"],"PASS")
        self.assertNotIn("2019",str(snap["metric_integrity_rows"][0]))

    def test_split_current_sources_are_explicitly_supported(self):
        q=[
            fact("2025-04-01","2025-06-30","2025-08-01",100,fy=2025),
            fact("2026-04-01","2026-06-30","2026-08-01",120,fy=2026),
        ]
        a=[
            fact("2024-01-01","2024-12-31","2025-02-15",400,form="10-K",fy=2024,fp="FY"),
            fact("2025-01-01","2025-12-31","2026-02-15",500,form="10-K",fy=2025,fp="FY"),
        ]
        data={"entityName":"Split Co","facts":{"us-gaap":{
            "RevenueFromContractWithCustomerExcludingAssessedTax":{"units":{"USD":q}},
            "Revenues":{"units":{"USD":a}},
            "EarningsPerShareDiluted":{"units":{"USD/shares":eps_current()}},
        }}}
        snap=build_fundamental_snapshot("SPLT",data,as_of=date(2026,8,30))
        self.assertEqual(snap["revenue_quarter_concept"],"RevenueFromContractWithCustomerExcludingAssessedTax")
        self.assertEqual(snap["revenue_annual_concept"],"Revenues")
        self.assertEqual(snap["revenue_concept_continuity"],"SPLIT CURRENT SOURCES")
        self.assertAlmostEqual(snap["revenue_q_yoy"],0.20,places=6)
        self.assertAlmostEqual(snap["revenue_annual_yoy"],0.25,places=6)

    def test_stale_only_revenue_is_blocked_not_displayed_as_latest(self):
        old=[
            fact("2018-04-01","2018-06-30","2018-08-01",100,fy=2018),
            fact("2019-04-01","2019-06-30","2019-08-01",114,fy=2019),
            fact("2018-01-01","2018-12-31","2019-02-01",400,form="10-K",fy=2018,fp="FY"),
            fact("2019-01-01","2019-12-31","2020-02-01",450,form="10-K",fy=2019,fp="FY"),
        ]
        data={"entityName":"Stale Co","facts":{"us-gaap":{
            "RevenueFromContractWithCustomerExcludingAssessedTax":{"units":{"USD":old}},
            "EarningsPerShareDiluted":{"units":{"USD/shares":eps_current()}},
        }}}
        snap=build_fundamental_snapshot("STAL",data,as_of=date(2026,8,30))
        self.assertEqual(snap["company_quarter_reference_end"],date(2026,6,30))
        self.assertEqual(snap["revenue_quarter_latest_period_status"],"REVIEW")
        self.assertTrue(pd.isna(snap["revenue_q_yoy"]))
        self.assertIsNone(snap["revenue_q_end"])
        self.assertIn("CONCEPT REVIEW REQUIRED",snap["fundamental_risks"])

    def test_latest_period_hard_gate_never_falls_back_for_pair_availability(self):
        # Fresh concept has current quarter but no prior-year comparator. Old
        # concept has a valid 2018/2019 pair. The current metric must be N/A,
        # never the old pair.
        old=[
            fact("2018-04-01","2018-06-30","2018-08-01",100,fy=2018),
            fact("2019-04-01","2019-06-30","2019-08-01",120,fy=2019),
        ]
        fresh=[fact("2026-04-01","2026-06-30","2026-08-01",1200,fy=2026)]
        data={"entityName":"No Pair Co","facts":{"us-gaap":{
            "RevenueFromContractWithCustomerExcludingAssessedTax":{"units":{"USD":old}},
            "Revenues":{"units":{"USD":fresh}},
            "EarningsPerShareDiluted":{"units":{"USD/shares":eps_current()}},
        }}}
        snap=build_fundamental_snapshot("NOPR",data,as_of=date(2026,8,30))
        self.assertEqual(snap["revenue_quarter_concept"],"Revenues")
        self.assertTrue(pd.isna(snap["revenue_q_yoy"]))
        self.assertEqual(snap["revenue_q_end"],date(2026,6,30))
        self.assertEqual(snap["metric_integrity_status"],"REVIEW")

    def test_future_facts_are_excluded_from_reference_selection(self):
        data=migrated_revenue_payload()
        data["facts"]["us-gaap"]["Revenues"]["units"]["USD"].append(
            fact("2027-04-01","2027-06-30","2027-08-01",9999,fy=2027)
        )
        snap=build_fundamental_snapshot("MIGR",data,as_of=date(2026,8,30))
        self.assertEqual(snap["company_quarter_reference_end"],date(2026,6,30))
        self.assertEqual(snap["revenue_q_end"],date(2026,6,30))


if __name__=='__main__': unittest.main()
