import unittest
from datetime import date

from scanner.fundamentals import build_fundamental_snapshot


def fact(
    start,
    end,
    filed,
    value,
    *,
    form="10-Q",
    fy=2026,
    fp="Q2",
    accn="000-test",
):
    return {
        "start": start,
        "end": end,
        "filed": filed,
        "val": value,
        "form": form,
        "fy": fy,
        "fp": fp,
        "accn": accn,
    }


def current_quarters(base=100.0, current=120.0):
    return [
        fact(
            "2025-04-01", "2025-06-30", "2025-08-01",
            base, fy=2025, accn="q-2025",
        ),
        fact(
            "2026-04-01", "2026-06-30", "2026-08-01",
            current, fy=2026, accn="q-2026",
        ),
    ]


def official_annuals(base=400.0, current=500.0):
    return [
        fact(
            "2024-01-01", "2024-12-31", "2025-02-15",
            base, form="10-K", fy=2024, fp="FY", accn="k-2024",
        ),
        fact(
            "2025-01-01", "2025-12-31", "2026-02-15",
            current, form="10-K", fy=2025, fp="FY", accn="k-2025",
        ),
    ]


def amzn_like_payload():
    revenue = (
        current_quarters(1000.0, 1196.0)
        + official_annuals(4000.0, 4496.0)
    )
    eps = current_quarters(1.0, 2.0) + official_annuals(4.0, 5.0)

    # Problematic year-length contexts carried in an interim filing.
    # They must not advance the official annual reference to 2026-06-30.
    revenue.append(
        fact(
            "2025-07-01", "2026-06-30", "2026-08-05",
            5000.0, form="10-Q", fy=2026, fp="Q2", accn="rev-ttm-q",
        )
    )
    eps.append(
        fact(
            "2025-07-01", "2026-06-30", "2026-08-05",
            6.0, form="10-Q", fy=2026, fp="Q2", accn="eps-ttm-q",
        )
    )

    return {
        "entityName": "Annual Horizon Test Co",
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {"USD": revenue}
                },
                "EarningsPerShareDiluted": {
                    "units": {"USD/shares": eps}
                },
            }
        },
    }


def migrated_uber_like_payload():
    old_revenue = [
        fact(
            "2018-04-01", "2018-06-30", "2018-08-01",
            100.0, fy=2018, accn="old-2018",
        ),
        fact(
            "2019-04-01", "2019-06-30", "2019-08-01",
            114.4, fy=2019, accn="old-2019",
        ),
    ]
    current_revenue = (
        current_quarters(1000.0, 1122.0)
        + official_annuals(4000.0, 4732.0)
    )

    return {
        "entityName": "Migrated Revenue Concept Co",
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {"USD": old_revenue}
                },
                "Revenues": {"units": {"USD": current_revenue}},
                "EarningsPerShareDiluted": {
                    "units": {
                        "USD/shares": (
                            current_quarters(1.0, 1.857)
                            + official_annuals(4.0, 4.148)
                        )
                    }
                },
            }
        },
    }


class AnnualHorizonIntegrityTests(unittest.TestCase):
    def test_interim_ttm_does_not_advance_official_annual_horizon(self):
        snap = build_fundamental_snapshot(
            "AMZN",
            amzn_like_payload(),
            as_of=date(2026, 8, 31),
        )

        self.assertEqual(
            snap["company_annual_reference_end"],
            date(2025, 12, 31),
        )
        self.assertEqual(snap["revenue_annual_end"], date(2025, 12, 31))
        self.assertEqual(snap["earnings_annual_end"], date(2025, 12, 31))
        self.assertEqual(snap["revenue_annual_latest_period_status"], "PASS")
        self.assertEqual(
            snap["fiscal_calendar"],
            "DECEMBER FY / CALENDAR-LIKE",
        )
        self.assertAlmostEqual(snap["revenue_annual_yoy"], 0.124, places=6)

    def test_annual_provenance_uses_annual_filing(self):
        snap = build_fundamental_snapshot(
            "AMZN",
            amzn_like_payload(),
            as_of=date(2026, 8, 31),
        )
        rows = {row["metric"]: row for row in snap["metric_integrity_rows"]}

        self.assertEqual(rows["Revenue annual"]["current_form"], "10-K")
        self.assertEqual(rows["Diluted EPS annual"]["current_form"], "10-K")
        self.assertEqual(rows["Revenue annual"]["integrity"], "PASS")
        self.assertEqual(rows["Diluted EPS annual"]["integrity"], "PASS")

    def test_later_interim_duplicate_cannot_replace_10k_annual_fact(self):
        data = amzn_like_payload()
        revenue_items = data["facts"]["us-gaap"][
            "RevenueFromContractWithCustomerExcludingAssessedTax"
        ]["units"]["USD"]

        revenue_items.append(
            fact(
                "2025-01-01", "2025-12-31", "2026-08-05",
                9999.0, form="10-Q", fy=2026, fp="Q2",
                accn="later-interim-duplicate",
            )
        )

        snap = build_fundamental_snapshot(
            "AMZN",
            data,
            as_of=date(2026, 8, 31),
        )
        row = next(
            r for r in snap["metric_integrity_rows"]
            if r["metric"] == "Revenue annual"
        )

        self.assertEqual(row["current_form"], "10-K")
        self.assertAlmostEqual(snap["revenue_annual_yoy"], 0.124, places=6)

    def test_uber_concept_migration_fix_remains_intact(self):
        snap = build_fundamental_snapshot(
            "UBER",
            migrated_uber_like_payload(),
            as_of=date(2026, 8, 31),
        )

        self.assertEqual(snap["revenue_quarter_concept"], "Revenues")
        self.assertEqual(snap["revenue_annual_concept"], "Revenues")
        self.assertEqual(snap["revenue_q_end"], date(2026, 6, 30))
        self.assertEqual(snap["revenue_annual_end"], date(2025, 12, 31))
        self.assertEqual(snap["metric_integrity_status"], "PASS")
        self.assertAlmostEqual(snap["revenue_q_yoy"], 0.122, places=6)


if __name__ == "__main__":
    unittest.main()
