from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.nist_rmf_mapping import (
    NIST_PROFILE_ID,
    build_nist_coverage_map,
    write_nist_coverage_map,
)


def test_build_nist_coverage_map_is_honest_and_structured() -> None:
    coverage = build_nist_coverage_map()

    assert coverage["profile"] == NIST_PROFILE_ID
    # This is an evidence-alignment aid, never a compliance certification.
    assert coverage["alignment_type"] == "evidence_alignment_not_certification"
    assert coverage["disclaimer"]

    mappings = coverage["mappings"]
    assert len(mappings) >= 5
    for entry in mappings:
        assert entry["nist_function"] in {"GOVERN", "MAP", "MEASURE", "MANAGE"}
        assert entry["nist_subcategories"]
        assert entry["source_artifact"]
        assert entry["rationale"]

    subcategories = {sub for entry in mappings for sub in entry["nist_subcategories"]}
    assert "MEASURE 2.4" in subcategories
    assert "MEASURE 2.7" in subcategories


def test_build_nist_coverage_map_marks_present_evidence(tmp_path: Path) -> None:
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports/security_eval_summary.json").write_text("{}", encoding="utf-8")

    coverage = build_nist_coverage_map(tmp_path)
    by_source = {entry["source_artifact"]: entry for entry in coverage["mappings"]}

    assert by_source["reports/security_eval_summary.json"]["evidence_present"] is True
    # An artifact that was not written is marked absent, not fabricated as present.
    assert any(entry["evidence_present"] is False for entry in coverage["mappings"])


def test_write_nist_coverage_map(tmp_path: Path) -> None:
    report = write_nist_coverage_map(tmp_path)

    path = tmp_path / "reports/nist_ai_600_1_coverage_map.json"
    assert path.exists()
    assert report["profile"] == NIST_PROFILE_ID
    assert json.loads(path.read_text(encoding="utf-8"))["mappings"]
