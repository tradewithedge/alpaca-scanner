import ast
import unittest
from pathlib import Path


class AppStaticIntegrityTests(unittest.TestCase):
    def test_numpy_alias_exists_when_np_is_used(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3b_Self_Contained_Ticker_Inspector_Reference_Engine.py"
        )
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        uses_np = any(
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id == "np"
            for node in ast.walk(tree)
        )
        imports_np = any(
            isinstance(node, ast.Import)
            and any(
                alias.name == "numpy" and alias.asname == "np"
                for alias in node.names
            )
            for node in tree.body
        )

        self.assertTrue(uses_np, "Smoke test expected app to use np.")
        self.assertTrue(
            imports_np,
            "app.py uses np but does not import numpy as np.",
        )

    def test_app_syntax_parses(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3b_Self_Contained_Ticker_Inspector_Reference_Engine.py"
        )
        ast.parse(app_path.read_text(encoding="utf-8"))

    def test_self_contained_reference_engine_present(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3b_Self_Contained_Ticker_Inspector_Reference_Engine.py"
        )
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        funcs = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertIn("build_inspector_reference_cached", funcs)
        self.assertIn("resolve_inspector_reference", funcs)
        self.assertIn("completed_scan_reference", funcs)

    def test_reference_builder_does_not_assign_scanner_session_state(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3b_Self_Contained_Ticker_Inspector_Reference_Engine.py"
        )
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        target = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "build_inspector_reference_cached"
        )

        def is_scan_session_target(node):
            # Detect st.session_state.scan assignment target structurally.
            return (
                isinstance(node, ast.Attribute)
                and node.attr == "scan"
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "session_state"
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "st"
            )

        bad = []
        for node in ast.walk(target):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = []
                if isinstance(node, ast.Assign):
                    targets = node.targets
                else:
                    targets = [node.target]
                bad.extend(t for t in targets if is_scan_session_target(t))
        self.assertEqual(bad, [])

    def test_auto_reference_call_exists_before_ticker_inspection_call(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3b_Self_Contained_Ticker_Inspector_Reference_Engine.py"
        )
        source = app_path.read_text(encoding="utf-8")
        self.assertIn("resolve_inspector_reference(", source)
        self.assertIn("inspector_reference_ctx", source)
        self.assertIn(
            "st.session_state.inspector_ticker,\n                inspector_reference_ctx,",
            source,
        )


if __name__ == "__main__":
    unittest.main()
