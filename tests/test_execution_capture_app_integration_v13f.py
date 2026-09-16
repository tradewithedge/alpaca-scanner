from pathlib import Path


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_loads_execution_capture_module():
    text = APP.read_text(encoding="utf-8")
    assert "scanner.execution_capture as execution_capture_module" in text
    assert "build_execution_capture_log = execution_capture_module.build_execution_capture_log" in text
    assert "append_execution_capture = execution_capture_module.append_execution_capture" in text


def test_app_version_is_v13f():
    text = APP.read_text(encoding="utf-8")
    assert 'APP_VERSION = "V1.3f"' in text


def test_app_renders_shadow_capture_section():
    text = APP.read_text(encoding="utf-8")
    assert "3L) Shadow Execution Capture & Staged-Execution Preparation" in text
    assert "Capture this scan into V1.3f Forward-Test Log" in text
    assert "Download V1.3f Forward-Test Capture Log CSV" in text


def test_app_keeps_execution_analysis_only():
    text = APP.read_text(encoding="utf-8")
    assert "does NOT place orders" in text
    assert "does NOT" in text
    assert "broker/execution action" in text


def test_app_distinguishes_current_scan_from_session_capture_totals():
    text = APP.read_text(encoding="utf-8")
    assert 'CURRENT SCAN — selected universe' in text
    assert 'SESSION CAPTURE LOG — cumulative across captured universes' in text
    assert 'SIGNAL ROWS' in text
    assert 'session_summary = summarize_execution_capture(existing)' in text
    assert 'current_summary = summarize_execution_capture(snapshot)' in text
    assert 'Current-scan metrics describe only the selected universe.' in text


def test_app_does_not_label_cumulative_session_rows_as_current_universe_rows():
    text = APP.read_text(encoding="utf-8")
    assert 's1.metric("CAPTURED ROWS", session_summary["rows"])' in text
    assert 'c1.metric("SIGNAL ROWS", current_summary["rows"])' in text
    assert 'all V1.3f captures in this Streamlit session' in text
