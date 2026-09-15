import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"
SRC = APP.read_text(encoding="utf-8")


def test_app_parses():
    ast.parse(SRC)


def test_v13e_module_and_alias_present():
    assert "import scanner.decision_architecture as decision_architecture_module" in SRC
    assert "build_decision_architecture = decision_architecture_module.build_decision_architecture" in SRC
    assert "summarize_decision_architecture = decision_architecture_module.summarize_decision_architecture" in SRC


def test_v13e_shadow_build_comes_after_risk_reward():
    assert SRC.index("risk_reward_shadow = build_risk_reward_diagnostics(") < SRC.index("decision_shadow = build_decision_architecture(")


def test_v13e_official_integrity_guard_present():
    assert "_scored_before_decision_shadow = scored.copy(deep=True)" in SRC
    assert "decision_official_integrity_pass = scored.equals(" in SRC


def test_v13e_rendered_before_candidates():
    assert 'render_decision_architecture_diagnostics(res)' in SRC
    assert SRC.index('render_decision_architecture_diagnostics(res)') < SRC.index('st.subheader("4) Swing Candidates")')


def test_v13e_is_shadow_not_production_gate():
    assert "V1.3e SHADOW MODE" in SRC
    assert "official trade decisions" in SRC
    assert "not a production gate" in SRC or "does not" in SRC.lower()
