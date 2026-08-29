import ast
import unittest
from pathlib import Path


class AppStaticIntegrityTests(unittest.TestCase):
    def test_numpy_alias_exists_when_np_is_used(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3a_Ticker_Inspector_Final_Polish_Hotfix.py"
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
            / "ALPACA_Scanner_V1.2.1.3a_Ticker_Inspector_Final_Polish_Hotfix.py"
        )
        ast.parse(app_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
