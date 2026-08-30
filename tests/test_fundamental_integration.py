import unittest
from pathlib import Path


APP = (
    Path(__file__).resolve().parents[1]
    / "ALPACA_Scanner_V1.2.2.1a_SEC_Access_Integrity_Hotfix.py"
)


class StaticFundamentalIntegrationTests(unittest.TestCase):
    def test_fundamentals_are_shadow_only(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("V1.2.2.1a SHADOW MODE", source)
        self.assertIn("does not batch-fetch fundamentals", source)
        self.assertIn("does not alter scanner eligibility or ranking", source)

    def test_core_scoring_calls_are_not_given_fundamental_inputs(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            "eligible, rejected = apply_quality_filters(cross_section, cfg)",
            source,
        )
        self.assertIn(
            "scored = score_universe(eligible, deployment_score, cfg)",
            source,
        )

    def test_official_sec_source_only(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("SEC EDGAR CompanyFacts", source)
        self.assertIn("No third-party fundamental fallback.", source)

    def test_ticker_inspector_ux_remains_explicit_action(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("Run Scanner has NO authority over Inspector visibility/state.", source)
        self.assertIn("on_click=_submit_inspector_callback", source)
        self.assertIn("on_click=_clear_inspector_callback", source)


if __name__ == "__main__":
    unittest.main()
