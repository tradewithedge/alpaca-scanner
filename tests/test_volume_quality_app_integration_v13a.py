import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
VOLUME = ROOT / "scanner" / "volume_quality.py"


class V13aAppIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.volume_source = VOLUME.read_text(encoding="utf-8")

    def test_app_syntax_parses(self):
        self.assertIsInstance(self.tree, ast.Module)

    def test_version_is_v13a(self):
        self.assertIn('APP_VERSION = "V1.3a"', self.source)

    def test_volume_module_is_imported_and_hot_reloaded(self):
        self.assertIn(
            "import scanner.volume_quality as volume_quality_module",
            self.source,
        )
        self.assertIn("    volume_quality_module,\n    regime_module,", self.source)

    def test_shadow_builder_and_summary_are_bound(self):
        self.assertIn(
            "build_contextual_volume_quality = volume_quality_module.build_contextual_volume_quality",
            self.source,
        )
        self.assertIn(
            "summarize_contextual_volume_quality = volume_quality_module.summarize_contextual_volume_quality",
            self.source,
        )

    def test_shadow_is_built_separately_and_integrity_checked(self):
        self.assertIn("_scored_before_volume_shadow = scored.copy(deep=True)", self.source)
        self.assertIn("volume_shadow = build_contextual_volume_quality(", self.source)
        self.assertIn(
            "volume_shadow_official_integrity_pass = scored.equals(_scored_before_volume_shadow)",
            self.source,
        )
        self.assertNotIn("scored = scored.merge(volume_shadow", self.source)
        self.assertNotIn("scored.merge(volume_shadow", self.source)

    def test_shadow_results_are_stored_outside_official_scored(self):
        self.assertIn('"volume_shadow": volume_shadow,', self.source)
        self.assertIn('"volume_shadow_summary": volume_shadow_summary,', self.source)
        self.assertIn(
            '"volume_shadow_official_integrity_pass": volume_shadow_official_integrity_pass,',
            self.source,
        )

    def test_3g_section_exists_before_swing_candidates(self):
        volume_pos = self.source.find(
            'st.subheader("3G) Contextual Volume Quality — Shadow Diagnostics")'
        )
        swing_pos = self.source.find('st.subheader("4) Swing Candidates")')
        self.assertGreaterEqual(volume_pos, 0)
        self.assertGreater(swing_pos, volume_pos)
        self.assertIn("render_contextual_volume_quality(res)", self.source)

    def test_app_declares_shadow_only_invariant(self):
        render_start = self.source.find("def render_contextual_volume_quality(scan):")
        symbol_key = self.source.find("def _symbol_key(symbol):", render_start)
        block = self.source[render_start:symbol_key]
        for phrase in [
            "SHADOW MODE",
            "Candidate Quality",
            "F15 Composite",
            "Entry Quality",
            "candidate buckets",
            "trade decisions",
        ]:
            self.assertIn(phrase, block)


    def test_shadow_failure_is_isolated_from_official_scanner(self):
        self.assertIn("volume_shadow_error = None", self.source)
        self.assertIn("except Exception as exc:", self.source)
        self.assertIn('"volume_shadow_error": volume_shadow_error,', self.source)
        self.assertIn("failed safely", self.source)

    def test_legacy_volume_logic_is_explicitly_not_rewritten(self):
        self.assertIn(
            "Frozen V1.2.3c setup/Entry logic still retains its legacy vol_ratio behavior.",
            self.source,
        )

    def test_volume_module_does_not_import_scoring(self):
        self.assertNotIn("scanner.scoring", self.volume_source)
        self.assertNotIn("from .scoring", self.volume_source)

    def test_volume_context_is_price_first_not_official_setup_driven(self):
        tree = ast.parse(self.volume_source)
        target = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_price_context"
        )
        names = {
            node.id for node in ast.walk(target)
            if isinstance(node, ast.Name)
        }
        self.assertNotIn("setup", names)
        source_segment = ast.get_source_segment(self.volume_source, target) or ""
        self.assertNotIn("vol_ratio", source_segment)

        # No data access to a volume field is allowed inside price-context logic.
        accessed_keys = set()
        for node in ast.walk(target):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "get" and node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        accessed_keys.add(arg.value.lower())
            if isinstance(node, ast.Subscript):
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                    accessed_keys.add(sl.value.lower())
        self.assertNotIn("volume", accessed_keys)


if __name__ == "__main__":
    unittest.main()
