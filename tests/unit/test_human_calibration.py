from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.human_calibration import evaluate_human_calibration
from internal_ai_agent.io import read_jsonl, write_jsonl


def test_human_calibration_compares_classifier_against_labels(
    tmp_path: Path,
) -> None:
    write_jsonl(
        tmp_path / "data/eval/human_calibration_cases.jsonl",
        read_jsonl(Path("data/eval/human_calibration_cases.jsonl")),
    )

    report = evaluate_human_calibration(tmp_path)

    assert report["report_type"] == "human_label_calibration"
    assert report["case_count"] == 24
    assert report["summary"]["unsafe_case_count"] == 12
    assert report["summary"]["benign_case_count"] == 12
    assert report["summary"]["reviewer_disagreement_count"] == 3
    assert report["summary"]["classifier_label_accuracy"] > 0.8
    assert report["summary"]["unsafe_capture_rate"] == 0.8333
    assert report["summary"]["unsafe_auto_allowed_count"] == 2
    assert any(
        row["reviewer_disagreement"] for row in report["sample_cases"]
    )
    assert (tmp_path / "reports/human_calibration_summary.json").exists()
    assert (tmp_path / "reports/human_calibration_cases.jsonl").exists()
    assert (tmp_path / "reports/judge_reliability_summary.json").exists()
    assert (tmp_path / "reports/judge_reliability_cases.jsonl").exists()

    judge_report = read_jsonl(tmp_path / "reports/judge_reliability_cases.jsonl")
    assert len(judge_report) == 24
    assert all("judge_label" in row for row in judge_report)
    assert all("judge_confidence" in row for row in judge_report)
