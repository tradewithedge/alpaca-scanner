import unittest
from datetime import date
import numpy as np

from scanner.fundamentals import build_fundamental_snapshot
from scanner.fundamental_batch import classify_batch_snapshot


def fact(start, end, filed, value, *, form="10-Q", fy=2026, fp="Q2", accn="000-test"):
    return {"start": start, "end": end, "filed": filed, "val": value,
            "form": form, "fy": fy, "fp": fp, "accn": accn}


def eps_series():
    return [
        fact("2025-04-01","2025-06-30","2025-08-05",-0.40,fy=2025,fp="Q2",accn="eps-q25"),
        fact("2026-04-01","2026-06-30","2026-08-06",-0.55,fy=2026,fp="Q2",accn="eps-q26"),
        fact("2024-01-01","2024-12-31","2025-02-20",-1.50,form="10-K",fy=2024,fp="FY",accn="eps-k24"),
        fact("2025-01-01","2025-12-31","2026-02-20",-2.00,form="10-K",fy=2025,fp="FY",accn="eps-k25"),
    ]


def sparse_eps_series():
    return [
        fact("2025-04-01","2025-06-30","2025-08-05",-0.40,fy=2025,fp="Q2",accn="eps-q25"),
        fact("2026-04-01","2026-06-30","2026-08-06",-0.55,fy=2026,fp="Q2",accn="eps-q26"),
        fact("2023-01-01","2023-12-31","2024-02-20",-1.20,form="10-K",fy=2023,fp="FY",accn="eps-k23"),
        fact("2024-01-01","2024-12-31","2025-02-20",-1.50,form="10-K",fy=2024,fp="FY",accn="eps-k24"),
    ]


def sparse_zero_revenue_payload():
    revenue = [
        fact("2022-01-01","2022-12-31","2023-02-20",12_000_000.0,form="10-K",fy=2022,fp="FY",accn="rev-k22"),
        fact("2024-01-01","2024-12-31","2025-02-20",0.0,form="10-K",fy=2024,fp="FY",accn="rev-k24"),
    ]
    return {"entityName":"Sparse Zero Revenue Biotech","facts":{"us-gaap":{
        "Revenues":{"units":{"USD":revenue}},
        "EarningsPerShareDiluted":{"units":{"USD/shares":sparse_eps_series()}},
    }}}


def valid_revenue_payload():
    revenue = [
        fact("2024-01-01","2024-12-31","2025-02-20",100.0,form="10-K",fy=2024,fp="FY",accn="rev-k24"),
        fact("2025-01-01","2025-12-31","2026-02-20",120.0,form="10-K",fy=2025,fp="FY",accn="rev-k25"),
        fact("2025-04-01","2025-06-30","2025-08-05",20.0,fy=2025,fp="Q2",accn="rev-q25"),
        fact("2026-04-01","2026-06-30","2026-08-06",25.0,fy=2026,fp="Q2",accn="rev-q26"),
    ]
    return {"entityName":"Normal Revenue Company","facts":{"us-gaap":{
        "Revenues":{"units":{"USD":revenue}},
        "EarningsPerShareDiluted":{"units":{"USD/shares":eps_series()}},
    }}}


def suspicious_current_pair_payload():
    revenue = [
        fact("2024-01-01","2024-12-31","2025-02-20",100.0,form="10-K",fy=2024,fp="FY",accn="rev-k24"),
        # Genuine comparable year, but impossible filing before period end.
        fact("2025-01-01","2025-12-31","2025-12-01",120.0,form="10-K",fy=2025,fp="FY",accn="rev-bad25"),
    ]
    return {"entityName":"Bad Pair Company","facts":{"us-gaap":{
        "Revenues":{"units":{"USD":revenue}},
        "EarningsPerShareDiluted":{"units":{"USD/shares":eps_series()}},
    }}}


class PreRevenueDomainIntegrityTests(unittest.TestCase):
    def test_sparse_zero_revenue_is_review_not_fail(self):
        snap=build_fundamental_snapshot("ZERO",sparse_zero_revenue_payload(),as_of=date(2026,8,31))
        self.assertEqual(snap["companyfacts_access_status"],"PASS")
        self.assertEqual(snap["metric_integrity_status"],"REVIEW")
        self.assertTrue(np.isnan(snap["revenue_annual_yoy"]))
        self.assertIsNone(snap["revenue_annual_pair"])
        status, interpretation=classify_batch_snapshot(snap)
        self.assertEqual(status,"REVIEW")
        self.assertIn("review",interpretation.lower())

    def test_nonconsecutive_history_is_blocked(self):
        snap=build_fundamental_snapshot("ZERO",sparse_zero_revenue_payload(),as_of=date(2026,8,31))
        self.assertIsNone(snap["revenue_annual_pair"])
        self.assertTrue(np.isnan(snap["revenue_annual_yoy"]))
        reason=str(snap.get("revenue_annual_pair_review_reason") or "").lower()
        self.assertIn("blocked",reason)
        self.assertIn("prior-year comparator",reason)

    def test_zero_revenue_state_is_explicit(self):
        snap=build_fundamental_snapshot("ZERO",sparse_zero_revenue_payload(),as_of=date(2026,8,31))
        self.assertEqual(snap["revenue_annual_state"],"NO CURRENT REVENUE")
        self.assertEqual(snap["revenue_annual_pair_status"],"REVIEW")

    def test_normal_consecutive_annual_revenue_remains_usable(self):
        snap=build_fundamental_snapshot("NORMAL",valid_revenue_payload(),as_of=date(2026,8,31))
        self.assertIsNotNone(snap["revenue_annual_pair"])
        self.assertAlmostEqual(snap["revenue_annual_yoy"],0.20,places=10)
        self.assertEqual(snap["metric_integrity_checks"]["Revenue annual"]["status"],"PASS")

    def test_genuine_structural_failure_remains_fail(self):
        snap=build_fundamental_snapshot("BAD",suspicious_current_pair_payload(),as_of=date(2026,8,31))
        self.assertEqual(snap["metric_integrity_checks"]["Revenue annual"]["status"],"FAIL")
        self.assertEqual(snap["metric_integrity_status"],"FAIL")
        status, interpretation=classify_batch_snapshot(snap)
        self.assertEqual(status,"FAIL")
        self.assertIn("structurally suspicious",interpretation.lower())

if __name__ == '__main__':
    unittest.main()
