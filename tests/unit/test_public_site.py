from __future__ import annotations

import importlib.util
import json
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
    assert 'href="incident_replay_summary.json"' in html
    assert 'href="incident_release_gates.json"' in html
    assert 'href="incident_response_plan.json"' in html
    assert 'href="incident_pack_v1.schema.json"' in html
    assert 'href="candidate_results_v1.schema.json"' in html
    assert 'href="safety_classifier_eval_summary.json"' in html
    assert "progress checker" not in html.lower()
    assert "internal notes" not in html.lower()


def test_public_docs_link_evaluate_your_agent_quickstart() -> None:
    project_root = Path(__file__).resolve().parents[2]
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    artifacts = (project_root / "docs/technical_artifacts.md").read_text(encoding="utf-8")
    site_builder = (project_root / "scripts/build_public_site.py").read_text(
        encoding="utf-8"
    )

    assert "docs/evaluate_your_agent_quickstart.md" in readme
    assert "evaluate_your_agent_quickstart.md" in artifacts
    assert "Evaluate your agent" in site_builder
    assert "docs/evaluate_your_agent_quickstart.md" in site_builder


def test_candidate_results_schema_describes_jsonl_row() -> None:
    schema_path = (
        Path(__file__).resolve().parents[2] / "schemas/candidate_results_v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["title"] == "Agent Safety Candidate Result Row v1"
    assert set(schema["required"]) == {
        "incident_id",
        "candidate_id",
        "decision",
        "answer",
    }
    assert schema["properties"]["candidate_id"]["pattern"] == (
        "^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"
    )
    assert "candidate_results" not in schema["properties"]


def test_artifact_index_only_links_current_incident_memos(tmp_path) -> None:
    public_site = _load_public_site_module()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    current_memo = reports_dir / "incident_memo_INC-CURRENT.md"
    stale_memo = reports_dir / "incident_memo_INC-STALE.md"
    current_memo.write_text("# current", encoding="utf-8")
    stale_memo.write_text("# stale", encoding="utf-8")
    (reports_dir / "incident_replay_summary.json").write_text(
        json.dumps({"memo_paths": ["reports/incident_memo_INC-CURRENT.md"]}),
        encoding="utf-8",
    )

    artifact_links = public_site._public_artifact_links(tmp_path)
    linked_artifacts = {href for _, _, href in artifact_links}

    assert "incident_memo_INC-CURRENT.md" in linked_artifacts
    assert "incident_memo_INC-STALE.md" not in linked_artifacts
