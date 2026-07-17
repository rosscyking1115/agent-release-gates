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
MODEL_JUDGE_PROVIDER_COMPARISON = "reports/model_judge_provider_comparison.json"


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
            (
                "Add a Google (Gemini) judge adapter behind a dry-run-first script to "
                "reach the fourth distinct provider."
            ),
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


def write_model_judge_provider_comparison(project_root: Path) -> dict[str, Any]:
    calibration_rows = _calibration_rows(project_root)
    reviewed_summaries = _reviewed_summaries(project_root)
    case_rows = _case_comparison_rows(calibration_rows, reviewed_summaries)
    provider_rows = _provider_summary_rows(reviewed_summaries)
    report = {
        "report_type": "reviewed_model_judge_provider_comparison",
        "status": "ready" if len(reviewed_summaries) >= 2 else "needs_more_providers",
        "case_count": len(calibration_rows),
        "provider_count": len(reviewed_summaries),
        "providers": [row["provider"] for row in provider_rows],
        "provider_summaries": provider_rows,
        "comparison_metrics": _comparison_metrics(case_rows, reviewed_summaries),
        "cross_provider_disagreement_cases": [
            row for row in case_rows if not row["provider_label_agreement"]
        ],
        "classifier_hosted_disagreement_cases": [
            row
            for row in case_rows
            if any(
                provider["classifier_disagrees_with_provider"]
                for provider in row["provider_results"]
            )
        ],
        "case_comparison_rows": case_rows,
        "publication_policy": (
            "This artifact is derived only from sanitized reviewed summaries and "
            "maintainer-labeled calibration metadata. It excludes raw provider "
            "response ids and full provider rationales."
        ),
        "interpretation": [
            "Use disagreement slices to inspect failure modes; "
            "do not rank providers by one aggregate score.",
            "The current comparison is limited by a 24-case maintainer-labeled calibration set.",
            "Independent human labels are still needed before treating model agreement "
            "as validation.",
        ],
    }
    write_json(project_root / MODEL_JUDGE_PROVIDER_COMPARISON, report)
    return report


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
            "adapter_status": "available",
            "credential_env_var": "not_required_for_local_runtime",
            "model_env_var": "LOCAL_JUDGE_MODEL",
            "runner": "scripts/run_model_judge_eval.py --provider local --run",
            "result_state": (
                "reviewed_result_present"
                if "local_open_source" in reviewed_providers
                else "not_run"
            ),
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


def _provider_summary_rows(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for summary in sorted(summaries, key=lambda row: str(row["provider"])):
        metrics = summary["metrics"]
        review = summary["publication_review"]
        rows.append(
            {
                "provider": summary["provider"],
                "model": summary["model"],
                "case_count": summary["case_count"],
                "manual_publication_decision": summary[
                    "manual_publication_decision"
                ],
                "model_judge_label_accuracy": metrics[
                    "model_judge_label_accuracy"
                ],
                "classifier_model_judge_agreement_rate": metrics[
                    "classifier_model_judge_agreement_rate"
                ],
                "average_model_judge_confidence": metrics[
                    "average_model_judge_confidence"
                ],
                "model_judge_disagreement_count": metrics[
                    "model_judge_disagreement_count"
                ],
                "unsafe_miss_count": review["unsafe_miss_count"],
                "benign_auto_block_count": review["benign_auto_block_count"],
                "publication_gate_decision": review["decision"],
            }
        )
    return rows


def _case_comparison_rows(
    calibration_rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    sorted_summaries = sorted(summaries, key=lambda row: str(row["provider"]))
    examples_by_provider = {
        str(summary["provider"]): {
            example["case_id"]: example
            for example in summary.get("public_disagreement_examples", [])
        }
        for summary in sorted_summaries
    }
    for case in calibration_rows:
        human_label = str(case["human_adjudicated_label"])
        classifier_label = str(case["classifier_binary_label"])
        provider_results = []
        for summary in sorted_summaries:
            provider = str(summary["provider"])
            example = examples_by_provider[provider].get(case["case_id"])
            if example:
                model_label = str(example["model_judge_label"])
                model_decision = str(example["model_judge_decision"])
                error_type = str(example["model_judge_error_type"])
                classifier_label_for_provider = str(example["classifier_label"])
            else:
                model_label = human_label
                model_decision = str(case["expected_action"])
                error_type = "match"
                classifier_label_for_provider = classifier_label
            provider_results.append(
                {
                    "provider": provider,
                    "model": summary["model"],
                    "model_judge_label": model_label,
                    "model_judge_decision": model_decision,
                    "model_judge_error_type": error_type,
                    "matches_human": model_label == human_label,
                    "classifier_disagrees_with_provider": (
                        classifier_label_for_provider != model_label
                    ),
                }
            )
        provider_labels = {
            result["model_judge_label"] for result in provider_results
        }
        provider_decisions = {
            result["model_judge_decision"] for result in provider_results
        }
        rows.append(
            {
                "case_id": case["case_id"],
                "risk_category": case["risk_category"],
                "risk_severity": case["risk_severity"],
                "human_label": human_label,
                "classifier_label": classifier_label,
                "provider_label_agreement": len(provider_labels) <= 1,
                "provider_decision_agreement": len(provider_decisions) <= 1,
                "provider_results": provider_results,
            }
        )
    return rows


def _comparison_metrics(
    case_rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    case_count = len(case_rows)
    label_agreement_count = sum(
        1 for row in case_rows if row["provider_label_agreement"]
    )
    decision_agreement_count = sum(
        1 for row in case_rows if row["provider_decision_agreement"]
    )
    provider_mismatch_count = {
        str(summary["provider"]): sum(
            1
            for row in case_rows
            for provider in row["provider_results"]
            if provider["provider"] == summary["provider"]
            and not provider["matches_human"]
        )
        for summary in summaries
    }
    return {
        "provider_label_agreement_rate": _ratio(label_agreement_count, case_count),
        "provider_decision_agreement_rate": _ratio(
            decision_agreement_count,
            case_count,
        ),
        "cross_provider_label_disagreement_count": (
            case_count - label_agreement_count
        ),
        "cross_provider_decision_disagreement_count": (
            case_count - decision_agreement_count
        ),
        "provider_human_mismatch_count": provider_mismatch_count,
        "any_provider_unsafe_miss_count": sum(
            1
            for row in case_rows
            if any(
                provider["model_judge_error_type"] == "judge_unsafe_marked_benign"
                for provider in row["provider_results"]
            )
        ),
        "any_provider_benign_auto_block_count": sum(
            1
            for row in case_rows
            if any(
                provider["model_judge_error_type"] == "judge_benign_auto_blocked"
                for provider in row["provider_results"]
            )
        ),
    }


def _ratio(numerator: float | int, denominator: float | int) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)
