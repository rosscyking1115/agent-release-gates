from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_public_site_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts/build_public_site.py"
    spec = importlib.util.spec_from_file_location("build_public_site", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_artifact_index_keeps_technical_links_off_homepage() -> None:
    public_site = _load_public_site_module()
    html = public_site._artifact_index_html(public_site._public_artifact_links())

    assert "<h1>Technical Artifact Index</h1>" in html
    assert 'href="index.html"' in html
    assert 'href="evaluation_gates.json"' in html
    assert 'href="safety_classifier_eval_summary.json"' in html
    assert "progress checker" not in html.lower()
    assert "internal notes" not in html.lower()
