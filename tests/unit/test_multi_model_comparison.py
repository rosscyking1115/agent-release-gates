from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.multi_model_comparison import (
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
