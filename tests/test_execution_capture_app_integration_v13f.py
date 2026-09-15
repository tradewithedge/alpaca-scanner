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
