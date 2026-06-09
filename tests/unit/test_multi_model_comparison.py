from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.multi_model_comparison import (
    write_model_judge_provider_comparison,
    write_multi_model_comparison_plan,
)
from internal_ai_agent.io import read_jsonl, write_json, write_jsonl


def test_multi_model_comparison_plan_declares_targets_and_gates(tmp_path) -> None:
    write_jsonl(
        tmp_path / "data/eval/human_calibration_cases.jsonl",
        read_jsonl(Path("data/eval/human_calibration_cases.jsonl")),
    )
    write_json(
        tmp_path / "reports/model_judge_reviewed_summary.json",
        {"report_type": "reviewed_hosted_model_judge_result"},
    )

    plan = write_multi_model_comparison_plan(tmp_path)

    assert plan["report_type"] == "multi_model_comparison_plan"
    assert plan["status"] == "planned_not_run"
    assert plan["case_count"] == 24
    assert plan["target_model_count"] == 4
    assert plan["reviewed_hosted_result_present"] is True
    assert plan["readiness_summary"]["adapter_available_count"] == 2
    assert plan["readiness_summary"]["adapter_planned_count"] == 2
    assert plan["readiness_summary"]["credentialed_result_count"] == 1
    assert plan["readiness_summary"]["ready_for_anthropic_run"] is True
    assert plan["readiness_summary"]["ready_for_cross_provider_publication"] is False
    assert {target["provider"] for target in plan["planned_targets"]} == {
        "anthropic",
        "google",
        "local_open_source",
        "openai",
    }
    anthropic_target = next(
        target for target in plan["planned_targets"] if target["provider"] == "anthropic"
    )
    assert anthropic_target["adapter_status"] == "available"
    assert "--provider anthropic --run" in anthropic_target["runner"]
    assert "model_judge_label_accuracy" in plan["output_contract"][
        "per_model_summary_fields"
    ]
    assert (tmp_path / "reports/multi_model_comparison_plan.json").exists()


def test_model_judge_provider_comparison_reports_disagreement_slices(tmp_path) -> None:
    write_jsonl(
        tmp_path / "data/eval/human_calibration_cases.jsonl",
        read_jsonl(Path("data/eval/human_calibration_cases.jsonl")),
    )
    write_json(
        tmp_path / "reports/model_judge_reviewed_summary.json",
        _reviewed_summary(
            provider="openai",
            model="gpt-4.1-mini",
            accuracy=0.9583,
            disagreement_examples=[
                {
                    "case_id": "HUMAN-CAL-010",
                    "risk_category": "tool_misuse",
                    "risk_severity": "low",
                    "human_label": "benign",
                    "classifier_label": "benign",
                    "model_judge_label": "unsafe",
                    "model_judge_decision": "block",
                    "model_judge_error_type": "judge_benign_auto_blocked",
                }
            ],
        ),
    )
    write_json(
        tmp_path / "reports/model_judge_reviewed_summary_anthropic.json",
        _reviewed_summary(
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            accuracy=1.0,
            disagreement_examples=[],
        ),
    )

    report = write_model_judge_provider_comparison(tmp_path)

    assert report["report_type"] == "reviewed_model_judge_provider_comparison"
    assert report["status"] == "ready"
    assert report["provider_count"] == 2
    assert report["comparison_metrics"]["provider_label_agreement_rate"] == 0.9583
    assert report["comparison_metrics"]["cross_provider_label_disagreement_count"] == 1
    assert report["comparison_metrics"]["any_provider_benign_auto_block_count"] == 1
    assert report["cross_provider_disagreement_cases"][0]["case_id"] == "HUMAN-CAL-010"
    assert {
        result["provider"]: result["model_judge_label"]
        for result in report["cross_provider_disagreement_cases"][0][
            "provider_results"
        ]
    } == {"anthropic": "benign", "openai": "unsafe"}
    assert (tmp_path / "reports/model_judge_provider_comparison.json").exists()


def _reviewed_summary(
    *,
    provider: str,
    model: str,
    accuracy: float,
    disagreement_examples: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "report_type": "reviewed_hosted_model_judge_result",
        "provider": provider,
        "model": model,
        "manual_publication_decision": "publish",
        "case_count": 24,
        "metrics": {
            "average_model_judge_confidence": 0.9,
            "case_count": 24,
            "classifier_model_judge_agreement_rate": 0.9,
            "classifier_model_judge_disagreement_count": 0,
            "model_judge_disagreement_count": len(disagreement_examples),
            "model_judge_label_accuracy": accuracy,
        },
        "publication_review": {
            "decision": "publishable",
            "unsafe_miss_count": 0,
            "benign_auto_block_count": len(disagreement_examples),
        },
        "public_disagreement_examples": disagreement_examples,
        "by_category": [],
        "limitations": [],
    }
