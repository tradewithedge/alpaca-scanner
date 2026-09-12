import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
ENTRY_ZONE = ROOT / "scanner" / "entry_zone.py"


class V13cAppIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.zone_source = ENTRY_ZONE.read_text(encoding="utf-8")

    def test_app_syntax_parses(self):
        self.assertIsInstance(self.tree, ast.Module)

    def test_version_is_v13c(self):
        self.assertIn('APP_VERSION = "V1.3c"', self.source)

    def test_entry_zone_module_is_imported_and_hot_reloaded(self):
        self.assertIn("import scanner.entry_zone as entry_zone_module", self.source)
        self.assertIn("    entry_zone_module,\n", self.source)
        self.assertLess(
            self.source.find("    entry_location_module,\n"),
            self.source.find("    entry_zone_module,\n"),
        )
        self.assertLess(
            self.source.find("    entry_zone_module,\n"),
            self.source.find("    regime_module,\n"),
        )

    def test_builder_and_summary_are_bound(self):
        self.assertIn(
            "build_entry_zone_diagnostics = entry_zone_module.build_entry_zone_diagnostics",
            self.source,
        )
        self.assertIn(
            "summarize_entry_zone_diagnostics = entry_zone_module.summarize_entry_zone_diagnostics",
            self.source,
        )

    def test_shadow_is_built_separately_and_integrity_checked(self):
        self.assertIn("_scored_before_entry_zone_shadow = scored.copy(deep=True)", self.source)
        self.assertIn("entry_zone_shadow = build_entry_zone_diagnostics(", self.source)
        self.assertIn(
            "entry_zone_official_integrity_pass = scored.equals(_scored_before_entry_zone_shadow)",
            self.source,
        )
        self.assertNotIn("scored = scored.merge(entry_zone_shadow", self.source)
        self.assertNotIn("scored.merge(entry_zone_shadow", self.source)

    def test_structure_parity_is_a_live_integrity_gate(self):
        self.assertIn(
            'entry_zone_shadow_summary.get("high20_structure_parity_checked", 0) > 0',
            self.source,
        )
        self.assertIn(
            'entry_zone_shadow_summary.get("high20_structure_parity_mismatches", 0) == 0',
            self.source,
        )
        self.assertIn("V1.3c PRIOR-20 STRUCTURE PARITY PASS", self.source)
        self.assertIn("V1.3c PRIOR-20 STRUCTURE PARITY FAIL", self.source)

    def test_shadow_results_are_stored_outside_official_scored(self):
        for field in [
            '"entry_zone_shadow": entry_zone_shadow,',
            '"entry_zone_shadow_summary": entry_zone_shadow_summary,',
            '"entry_zone_official_integrity_pass": entry_zone_official_integrity_pass,',
            '"entry_zone_structure_parity_pass": entry_zone_structure_parity_pass,',
            '"entry_zone_shadow_error": entry_zone_shadow_error,',
        ]:
            self.assertIn(field, self.source)

    def test_3i_section_exists_after_3h_and_before_swing_candidates(self):
        h = self.source.find('st.subheader("3H) Entry Location & Anti-Chase — Shadow Diagnostics")')
        i = self.source.find('st.subheader("3I) Trigger & Entry Zone — Shadow Diagnostics")')
        swing = self.source.find('st.subheader("4) Swing Candidates")')
        self.assertGreaterEqual(h, 0)
        self.assertGreater(i, h)
        self.assertGreater(swing, i)
        self.assertIn("render_entry_zone_diagnostics(res)", self.source)

    def test_app_declares_shadow_only_invariant(self):
        start = self.source.find("def render_entry_zone_diagnostics(scan):")
        end = self.source.find("def _symbol_key(symbol):", start)
        block = self.source[start:end]
        for phrase in [
            "SHADOW MODE",
            "Entry Quality",
            "legacy entry_px",
            "stop/T1/T2",
            "Candidate Quality",
            "F15 Composite",
            "ranking",
            "buckets",
            "event gates",
            "trade decisions",
        ]:
            self.assertIn(phrase, block)

    def test_current_price_is_separated_from_trigger_zone_and_max_fill(self):
        for phrase in [
            "current_price",
            "trigger_price",
            "entry_zone_low",
            "entry_zone_high",
            "max_acceptable_fill",
            "confirmation_condition",
        ]:
            self.assertIn(phrase, self.zone_source)

    def test_entry_zone_uses_prior_structure_not_latest_bar_as_reference(self):
        tree = ast.parse(self.zone_source)
        target = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_prior_structure"
        )
        segment = ast.get_source_segment(self.zone_source, target) or ""
        self.assertIn("g.iloc[:-1]", segment)
        self.assertIn("prior_20_high", segment)

    def test_no_clean_setup_does_not_get_invented_trigger(self):
        self.assertIn('"NONE",\n        np.nan,', self.zone_source)
        self.assertIn("NO STRUCTURED PLAN", self.zone_source)
        self.assertIn("does not receive a structured V1.3c plan", self.zone_source)

    def test_frozen_anti_chase_ceiling_caps_max_fill(self):
        self.assertIn("_frozen_hard_ceiling_price", self.zone_source)
        self.assertIn("max_fill = min(float(raw_max_fill), float(hard_ceiling))", self.zone_source)
        self.assertIn("BLOCKED — TRIGGER BEYOND HARD CEILING", self.zone_source)

    def test_reference_parameters_are_explicitly_provisional(self):
        self.assertIn("entry_zone_atr: float = 0.25", self.zone_source)
        self.assertIn("max_fill_atr: float = 0.50", self.zone_source)
        self.assertIn("provisional reference parameters", self.zone_source)
        self.assertIn("not proven production thresholds", self.source)

    def test_shadow_failure_is_isolated(self):
        self.assertIn("entry_zone_shadow_error = None", self.source)
        self.assertIn('"entry_zone_shadow_error": entry_zone_shadow_error,', self.source)
        self.assertIn("Trigger / Entry-Zone construction failed safely", self.source)

    def test_full_machine_readable_export_is_explicit(self):
        self.assertIn('"Download FULL V1.3c Trigger / Entry-Zone diagnostic CSV"', self.source)
        self.assertIn('file_name="v13c_trigger_entry_zone_full_diagnostic.csv"', self.source)
        self.assertIn("full_export.to_csv(index=False)", self.source)

    def test_v13a_and_v13b_frozen_layers_remain_before_v13c(self):
        self.assertIn("render_contextual_volume_quality(res)", self.source)
        self.assertIn("render_entry_location_diagnostics(res)", self.source)
        self.assertIn("render_entry_zone_diagnostics(res)", self.source)
        self.assertLess(
            self.source.find("render_contextual_volume_quality(res)"),
            self.source.find("render_entry_location_diagnostics(res)"),
        )
        self.assertLess(
            self.source.find("render_entry_location_diagnostics(res)"),
            self.source.find("render_entry_zone_diagnostics(res)"),
        )

    def test_entry_zone_module_does_not_import_scoring_or_mutate_official_fields(self):
        self.assertNotIn("scanner.scoring", self.zone_source)
        self.assertNotIn("from .scoring", self.zone_source)
        self.assertNotIn('r["entry_px"] =', self.zone_source)
        self.assertNotIn('r["entry_score"] =', self.zone_source)
        self.assertNotIn('r["bucket"] =', self.zone_source)


if __name__ == "__main__":
    unittest.main()
