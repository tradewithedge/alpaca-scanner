import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/"app.py").read_text()
MOD=(ROOT/"scanner/risk_reward.py").read_text()

class TestV13dAppIntegration(unittest.TestCase):
    def test_app_parses(self): ast.parse(APP)
    def test_version(self): self.assertIn('APP_VERSION = "V1.3d"',APP)
    def test_import_reload_and_alias(self):
        self.assertIn('import scanner.risk_reward as risk_reward_module',APP)
        self.assertIn('risk_reward_module,',APP)
        self.assertIn('build_risk_reward_diagnostics = risk_reward_module.build_risk_reward_diagnostics',APP)
    def test_shadow_build_after_entry_zone(self):
        self.assertIn('_scored_before_risk_reward_shadow = scored.copy(deep=True)',APP)
        self.assertIn('entry_zone=entry_zone_shadow',APP)
        self.assertIn('risk_reward_shadow',APP)
    def test_official_integrity(self):
        self.assertIn('risk_reward_official_integrity_pass = scored.equals(',APP)
    def test_rendered_as_3j_before_candidates(self):
        self.assertIn('3J) Risk / Reward & Stop-Distance — Shadow Diagnostics',APP)
        self.assertLess(APP.index('render_risk_reward_diagnostics(res)'),APP.index('st.subheader("4) Swing Candidates")'))
    def test_no_production_rewrite_language(self):
        for text in ['SHADOW ONLY','does NOT change official Entry Quality','Expectancy must be proven later']:
            self.assertIn(text,APP)
    def test_module_has_no_scoring_import(self):
        self.assertNotIn('import scanner.scoring',MOD)
    def test_research_bands_present(self):
        for x in ['STRONG','ACCEPTABLE','WEAK','POOR','NOT RANKED']:
            self.assertIn(x,MOD)

if __name__=='__main__': unittest.main()
