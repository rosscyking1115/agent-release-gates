from __future__ import annotations

import importlib.util
from pathlib import Path


def test_streamlit_dashboard_module_imports() -> None:
    # Smoke test for the otherwise-untested dashboard monolith. Loading the
    # module executes its module-level imports (including the ~40 names pulled
    # from dashboard.data) and all function definitions, so it catches syntax
    # errors and broken/renamed imports before any refactor. main() is not
    # invoked here -- it requires a running Streamlit context.
    script_path = Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py"
    spec = importlib.util.spec_from_file_location("streamlit_app_smoke", script_path)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert callable(module.main)
