import ast
import unittest
from pathlib import Path


class AppStaticIntegrityTests(unittest.TestCase):
    def test_numpy_alias_exists_when_np_is_used(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
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
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        ast.parse(app_path.read_text(encoding="utf-8"))

    def test_self_contained_reference_engine_present(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
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
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
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
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")
        self.assertIn("resolve_inspector_reference(", source)
        self.assertIn("inspector_reference_ctx", source)
        self.assertIn(
            "st.session_state.inspector_ticker,\n                inspector_reference_ctx,",
            source,
        )

    def test_ticker_input_is_not_inside_streamlit_form(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")
        self.assertNotIn('with st.form("ticker_inspector_form"', source)
        self.assertNotIn("st.form_submit_button(", source)

    def test_ticker_input_has_persistent_widget_key(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")
        self.assertIn('key="inspector_query_input"', source)
        # Explicit-action UX: Run Scanner must NOT consume or activate the
        # ticker field. The keyed input is committed only by Inspect ticker.
        self.assertIn("on_click=_submit_inspector_callback", source)

    def test_inspect_and_clear_use_callbacks(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")
        self.assertIn("def _submit_inspector_callback():", source)
        self.assertIn("def _clear_inspector_callback():", source)
        self.assertIn("on_click=_submit_inspector_callback", source)
        self.assertIn("on_click=_clear_inspector_callback", source)

    def test_inspector_state_initialized_before_sidebar(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")
        state_pos = source.find('if "inspector_query_input" not in st.session_state:')
        sidebar_pos = source.find("with st.sidebar:")
        self.assertGreaterEqual(state_pos, 0)
        self.assertGreater(sidebar_pos, state_pos)

    def test_run_scanner_has_no_inspector_state_authority(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")

        self.assertNotIn("inspector_state_on_scanner_run(", source)
        self.assertNotIn("inspector_transition", source)

        # The only non-initialization assignments controlling request state
        # must live in the explicit Inspect/Clear callbacks.
        self.assertIn("def _submit_inspector_callback():", source)
        self.assertIn("def _clear_inspector_callback():", source)
        self.assertIn(
            "st.session_state.inspector_requested = bool(normalized)",
            source,
        )
        self.assertIn(
            "st.session_state.inspector_requested = False",
            source,
        )

    def test_typing_ticker_alone_does_not_activate_inspector(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")

        self.assertIn('key="inspector_query_input"', source)
        self.assertIn("on_click=_submit_inspector_callback", source)

        # No on_change activation on text_input.
        ticker_block_start = source.find('ticker_query = st.text_input(')
        ticker_block_end = source.find('inspect_submit = st.button(', ticker_block_start)
        ticker_block = source[ticker_block_start:ticker_block_end]
        self.assertNotIn("on_change=", ticker_block)
        self.assertNotIn("inspector_requested", ticker_block)

    def test_clear_is_final_until_next_explicit_inspect(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")

        clear_start = source.find("def _clear_inspector_callback():")
        sidebar_start = source.find("with st.sidebar:", clear_start)
        clear_block = source[clear_start:sidebar_start]

        self.assertIn('st.session_state.inspector_query_input = ""', clear_block)
        self.assertIn('st.session_state.inspector_ticker = ""', clear_block)
        self.assertIn(
            "st.session_state.inspector_requested = False",
            clear_block,
        )
        self.assertIn(
            "st.session_state.inspector_expanded = False",
            clear_block,
        )

    def test_inspect_button_is_explicit_activation_boundary(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "ALPACA_Scanner_V1.2.1.3c_Ticker_Inspector_Explicit_Action_UX.py"
        )
        source = app_path.read_text(encoding="utf-8")

        submit_start = source.find("def _submit_inspector_callback():")
        clear_start = source.find("def _clear_inspector_callback():")
        submit_block = source[submit_start:clear_start]

        self.assertIn(
            "st.session_state.inspector_requested = bool(normalized)",
            submit_block,
        )
        self.assertIn(
            "st.session_state.inspector_expanded = True",
            submit_block,
        )


if __name__ == "__main__":
    unittest.main()
