from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.external_review import (
    evaluate_external_human_review,
    prepare_external_human_review,
)
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


def test_external_human_review_packet_is_prepared_without_labels(
    tmp_path: Path,
) -> None:
    _copy_calibration_fixture(tmp_path)

    report = prepare_external_human_review(tmp_path)

    assert report["report_type"] == "external_human_review"
    assert report["status"] == "awaiting_labels"
    assert report["case_count"] == 24
    assert report["summary"]["external_label_coverage"] == 0.0
    assert (tmp_path / "data/review/external_human_review_packet.csv").exists()
    assert (
        tmp_path / "data/review/external_human_review_label_template.csv"
    ).exists()
    assert (
        tmp_path / "data/review/external_human_review_reviewer_guide.md"
    ).exists()
    assert (tmp_path / "reports/external_human_review_manifest.json").exists()
    assert (tmp_path / "reports/external_human_review_summary.json").exists()
    assert report["review_workflow"]["target_reviewer_count"] == 2
    assert report["review_workflow"]["target_label_rows"] == 48
    assert report["reviewer_guide_path"].endswith("external_human_review_reviewer_guide.md")
    assert report["manifest_path"].endswith("external_human_review_manifest.json")


def test_external_human_review_evaluates_completed_labels(
    tmp_path: Path,
) -> None:
    _copy_calibration_fixture(tmp_path)
    labels_path = tmp_path / "data/review/external_human_review_labels.csv"
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.write_text(
        "\n".join(
            [
                (
                    "reviewer_id,case_id,reviewer_label,recommended_decision,"
                    "confidence,rationale,notes"
                ),
                "reviewer_a,HUMAN-CAL-001,unsafe,block,0.90,Policy bypass,",
                "reviewer_b,HUMAN-CAL-001,unsafe,block,0.80,Unsafe request,",
                "reviewer_a,HUMAN-CAL-002,benign,allow,0.70,Educational,",
                "reviewer_b,HUMAN-CAL-002,unsafe,review,0.60,Ambiguous,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = evaluate_external_human_review(tmp_path)

    assert report["status"] == "evaluated"
    assert report["label_row_count"] == 4
    assert report["reviewer_count"] == 2
    assert report["summary"]["external_label_coverage"] == 0.0833
    assert report["summary"]["cases_with_two_or_more_reviewers"] == 2
    assert report["summary"]["pairwise_agreement_rate"] == 0.5
    assert report["summary"]["adjudication_required_count"] == 1
    assert report["summary"]["external_maintainer_agreement_rate"] == 1.0
    assert report["review_workflow"]["minimum_publish_label_coverage"] == 1.0
    assert (tmp_path / "reports/external_human_review_manifest.json").exists()
    assert (tmp_path / "reports/external_human_review_cases.jsonl").exists()


def _copy_calibration_fixture(tmp_path: Path) -> None:
    write_jsonl(
        tmp_path / "data/eval/human_calibration_cases.jsonl",
        read_jsonl(Path("data/eval/human_calibration_cases.jsonl")),
    )
