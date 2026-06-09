from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.human_calibration import (
    CALIBRATION_CASES,
    evaluate_human_calibration,
)
from internal_ai_agent.io import read_jsonl, write_json

MULTI_MODEL_COMPARISON_PLAN = "reports/multi_model_comparison_plan.json"


def write_multi_model_comparison_plan(project_root: Path) -> dict[str, Any]:
    calibration_rows = _calibration_rows(project_root)
    reviewed_summaries = _reviewed_summaries(project_root)
    reviewed_providers = {str(row.get("provider", "")) for row in reviewed_summaries}
    plan = {
        "report_type": "multi_model_comparison_plan",
        "status": (
            "reviewed_partial_results"
            if len(reviewed_summaries) >= 2
            else "planned_not_run"
        ),
        "benchmark_track": "human_calibration_safety_judge",
        "case_count": len(calibration_rows),
        "target_model_count": 4,
        "reviewed_hosted_result_present": bool(reviewed_summaries),
        "reviewed_provider_count": len(reviewed_summaries),
        "reviewed_providers": sorted(reviewed_providers),
        "planned_targets": _planned_targets(reviewed_providers),
        "output_contract": {
            "per_model_summary_fields": [
                "provider",
                "model",
                "case_count",
                "model_judge_label_accuracy",
                "classifier_model_judge_agreement_rate",
                "unsafe_miss_count",
                "benign_auto_block_count",
                "average_model_judge_confidence",
                "publication_decision",
            ],
            "case_level_fields": [
                "case_id",
                "risk_category",
                "risk_severity",
                "human_adjudicated_label",
                "classifier_label",
                "model_judge_label",
                "model_judge_decision",
                "model_judge_confidence",
                "model_judge_error_type",
            ],
            "public_result_policy": (
                "Publish only reviewed summaries and sanitized disagreement examples; "
                "keep raw provider response ids and full rationales out of public artifacts."
            ),
        },
        "publication_gates": [
            "Evaluate every target on the same calibration case set.",
            "Include provider, model, run timestamp, and case count in every result.",
            "Do not publish a model row if provider errors or parse errors affected the run.",
            "Require manual review before publishing any unsafe miss or benign auto-block pattern.",
            "Report disagreement slices instead of ranking models by a single aggregate score.",
        ],
        "readiness_summary": {
            "adapter_available_count": 2,
            "adapter_planned_count": 2,
            "credentialed_result_count": len(reviewed_summaries),
            "ready_for_openai_repeat_run": True,
            "ready_for_anthropic_run": "anthropic" not in reviewed_providers,
            "ready_for_cross_provider_publication": len(reviewed_summaries) >= 2,
        },
        "next_steps": [
            "Repeat the OpenAI run when quota is available and promote only reviewed output.",
            (
                "Repeat the Anthropic run when needed and promote only reviewed output."
            ),
            "Add Google and local open-source judge adapters behind dry-run-first scripts.",
            "Compare model disagreement by category, severity, and error type.",
            "Add human external labels before treating model agreement as validation evidence.",
        ],
        "notes": [
            (
                "This artifact tracks reviewed provider coverage and publication gates; "
                "it is not a leaderboard."
            ),
            "Cross-provider findings should be reported as disagreement slices, not rankings.",
        ],
    }
    write_json(project_root / MULTI_MODEL_COMPARISON_PLAN, plan)
    return plan


def _planned_targets(reviewed_providers: set[str]) -> list[dict[str, Any]]:
    return [
        {
            "provider": "openai",
            "adapter_status": "available",
            "credential_env_var": "OPENAI_API_KEY",
            "model_env_var": "OPENAI_JUDGE_MODEL",
            "runner": "scripts/run_model_judge_eval.py --run",
            "result_state": (
                "reviewed_result_present" if "openai" in reviewed_providers else "not_run"
            ),
        },
        {
            "provider": "anthropic",
            "adapter_status": "available",
            "credential_env_var": "ANTHROPIC_API_KEY",
            "model_env_var": "ANTHROPIC_JUDGE_MODEL",
            "runner": "scripts/run_model_judge_eval.py --provider anthropic --run",
            "result_state": (
                "reviewed_result_present"
                if "anthropic" in reviewed_providers
                else "not_run"
            ),
        },
        {
            "provider": "google",
            "adapter_status": "planned",
            "credential_env_var": "GOOGLE_API_KEY",
            "model_env_var": "GOOGLE_JUDGE_MODEL",
            "runner": "planned",
            "result_state": "not_run",
        },
        {
            "provider": "local_open_source",
            "adapter_status": "planned",
            "credential_env_var": "not_required_for_local_runtime",
            "model_env_var": "LOCAL_JUDGE_MODEL",
            "runner": "planned",
            "result_state": "not_run",
        },
    ]


def _calibration_rows(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / CALIBRATION_CASES
    if not path.exists():
        evaluate_human_calibration(project_root)
    return read_jsonl(path)


def _reviewed_summaries(project_root: Path) -> list[dict[str, Any]]:
    reports_dir = project_root / "reports"
    paths = sorted(reports_dir.glob("model_judge_reviewed_summary*.json"))
    summaries = []
    for path in paths:
        summary = json.loads(path.read_text(encoding="utf-8"))
        if summary.get("report_type") == "reviewed_hosted_model_judge_result":
            summaries.append(summary)
    return summaries
