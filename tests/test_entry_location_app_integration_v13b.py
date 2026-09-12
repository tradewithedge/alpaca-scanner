import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
LOCATION = ROOT / "scanner" / "entry_location.py"


class V13bAppIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.location_source = LOCATION.read_text(encoding="utf-8")

    def test_app_syntax_parses(self):
        self.assertIsInstance(self.tree, ast.Module)

    def test_v13b_entry_location_layer_survives_later_app_versions(self):
        # V1.3b is a frozen architecture regression test, not a permanent lock
        # on the top-level app version. Later phases must retain the 3H layer.
        self.assertIn('st.subheader("3H) Entry Location & Anti-Chase — Shadow Diagnostics")', self.source)
        self.assertIn("render_entry_location_diagnostics(res)", self.source)

    def test_entry_location_module_is_imported_and_hot_reloaded(self):
        self.assertIn(
            "import scanner.entry_location as entry_location_module",
            self.source,
        )
        self.assertIn("    entry_location_module,\n", self.source)
        self.assertLess(
            self.source.find("    entry_location_module,\n"),
            self.source.find("    regime_module,\n"),
        )

    def test_builder_and_summary_are_bound(self):
        self.assertIn(
            "build_entry_location_diagnostics = entry_location_module.build_entry_location_diagnostics",
            self.source,
        )
        self.assertIn(
            "summarize_entry_location_diagnostics = entry_location_module.summarize_entry_location_diagnostics",
            self.source,
        )

    def test_shadow_is_built_separately_and_integrity_checked(self):
        self.assertIn(
            "_scored_before_entry_location_shadow = scored.copy(deep=True)",
            self.source,
        )
        self.assertIn(
            "entry_location_shadow = build_entry_location_diagnostics(",
            self.source,
        )
        self.assertIn(
            "entry_location_official_integrity_pass = scored.equals(",
            self.source,
        )
        self.assertNotIn("scored = scored.merge(entry_location_shadow", self.source)
        self.assertNotIn("scored.merge(entry_location_shadow", self.source)

    def test_shadow_results_are_stored_outside_official_scored(self):
        for field in [
            '"entry_location_shadow": entry_location_shadow,',
            '"entry_location_shadow_summary": entry_location_shadow_summary,',
            '"entry_location_official_integrity_pass": entry_location_official_integrity_pass,',
            '"entry_location_hard_ceiling_parity_pass": entry_location_hard_ceiling_parity_pass,',
            '"entry_location_shadow_error": entry_location_shadow_error,',
        ]:
            self.assertIn(field, self.source)

    def test_3h_section_exists_after_3g_and_before_swing_candidates(self):
        volume_pos = self.source.find(
            'st.subheader("3G) Contextual Volume Quality — Shadow Diagnostics")'
        )
        location_pos = self.source.find(
            'st.subheader("3H) Entry Location & Anti-Chase — Shadow Diagnostics")'
        )
        swing_pos = self.source.find('st.subheader("4) Swing Candidates")')
        self.assertGreaterEqual(volume_pos, 0)
        self.assertGreater(location_pos, volume_pos)
        self.assertGreater(swing_pos, location_pos)
        self.assertIn("render_entry_location_diagnostics(res)", self.source)

    def test_app_declares_shadow_only_invariant(self):
        render_start = self.source.find("def render_entry_location_diagnostics(scan):")
        symbol_key = self.source.find("def _symbol_key(symbol):", render_start)
        block = self.source[render_start:symbol_key]
        for phrase in [
            "SHADOW MODE",
            "Entry Quality",
            "Candidate Quality",
            "F15 Composite",
            "ranking",
            "buckets",
            "event gates",
            "trade decisions",
        ]:
            self.assertIn(phrase, block)

    def test_frozen_hard_ceiling_semantics_are_stated(self):
        self.assertIn(
            "Frozen hard NO CHASE semantics are preserved exactly: >5.0% above EMA8",
            self.source,
        )
        self.assertIn(">8.0% above EMA20", self.source)
        self.assertIn(">2.0 ATR above EMA20", self.source)
        self.assertIn("strict '>' rule", self.source)

    def test_hard_ceiling_parity_is_a_live_gate(self):
        self.assertIn(
            'entry_location_shadow_summary.get("hard_ceiling_parity_mismatches", 0) == 0',
            self.source,
        )
        self.assertIn("and not entry_location_shadow.empty", self.source)
        self.assertIn("V1.3b HARD NO CHASE PARITY PASS", self.source)
        self.assertIn("V1.3b HARD NO CHASE PARITY FAIL", self.source)

    def test_shadow_failure_is_isolated(self):
        self.assertIn("entry_location_shadow_error = None", self.source)
        self.assertIn('"entry_location_shadow_error": entry_location_shadow_error,', self.source)
        self.assertIn("Entry Location construction failed safely", self.source)

    def test_full_machine_readable_export_is_explicit(self):
        self.assertIn(
            '"Download FULL V1.3b Entry Location diagnostic CSV"',
            self.source,
        )
        self.assertIn(
            'file_name="v13b_entry_location_full_diagnostic.csv"',
            self.source,
        )
        self.assertIn("full_export.to_csv(index=False)", self.source)

    def test_v13a_volume_shadow_remains_present_and_before_v13b(self):
        self.assertIn(
            "import scanner.volume_quality as volume_quality_module",
            self.source,
        )
        self.assertIn("render_contextual_volume_quality(res)", self.source)
        self.assertLess(
            self.source.find("render_contextual_volume_quality(res)"),
            self.source.find("render_entry_location_diagnostics(res)"),
        )

    def test_entry_location_module_does_not_import_scoring(self):
        self.assertNotIn("scanner.scoring", self.location_source)
        self.assertNotIn("from .scoring", self.location_source)

    def test_location_state_does_not_read_official_setup(self):
        tree = ast.parse(self.location_source)
        target = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_location_state"
        )
        segment = ast.get_source_segment(self.location_source, target) or ""
        self.assertNotIn("setup", segment.lower())
        self.assertNotIn("entry_score", segment)
        self.assertNotIn("quality_score", segment)

    def test_no_production_location_score_is_created(self):
        self.assertNotIn('"entry_location_score"', self.location_source)
        self.assertNotIn('"location_score"', self.location_source)
        self.assertIn("max_chase_pressure_pct", self.location_source)


if __name__ == "__main__":
    unittest.main()
