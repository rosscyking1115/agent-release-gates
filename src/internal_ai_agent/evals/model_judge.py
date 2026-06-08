from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.human_calibration import (
    CALIBRATION_CASES,
    evaluate_human_calibration,
)
from internal_ai_agent.io import read_jsonl, write_json, write_jsonl

JudgeCase = Callable[[dict[str, Any]], dict[str, Any]]

ADAPTER_STATUS_PATH = "reports/model_judge_adapter_status.json"
MODEL_JUDGE_STATUS_PATH = "reports/model_judge_eval_status.json"
MODEL_JUDGE_SUMMARY_PATH = "reports/model_judge_eval_summary.json"
MODEL_JUDGE_CASES_PATH = "reports/model_judge_eval_cases.jsonl"


def write_model_judge_adapter_status(project_root: Path) -> dict[str, Any]:
    calibration_rows = _calibration_rows(project_root)
    status = {
        "status": "dry_run_ready",
        "adapter_type": "hosted_model_judge",
        "provider": "openai",
        "api_mode": "responses",
        "credential_env_var": "OPENAI_API_KEY",
        "model_env_var": "OPENAI_JUDGE_MODEL",
        "case_count": len(calibration_rows),
        "planned_outputs": [
            MODEL_JUDGE_STATUS_PATH,
            MODEL_JUDGE_SUMMARY_PATH,
            MODEL_JUDGE_CASES_PATH,
        ],
        "notes": [
            "No hosted model calls are made during deterministic CI.",
            (
                "Run scripts/run_model_judge_eval.py --run with OPENAI_API_KEY "
                "to create local provider-backed judge results."
            ),
            (
                "Published reports should distinguish hosted model-judge results "
                "from the deterministic local rubric judge baseline."
            ),
        ],
    }
    write_json(project_root / ADAPTER_STATUS_PATH, status)
    return status


def dry_run_status(project_root: Path, *, provider: str, model: str) -> dict[str, Any]:
    calibration_rows = _calibration_rows(project_root)
    status = {
        "status": "dry_run",
        "provider": provider,
        "model": model,
        "case_count": len(calibration_rows),
        "estimated_provider_calls": len(calibration_rows),
        "notes": [
            "No provider API calls were made.",
            "Rerun with --run and provider credentials to create hosted judge results.",
        ],
    }
    write_json(project_root / MODEL_JUDGE_STATUS_PATH, status)
    return status


def evaluate_hosted_model_judge(
    project_root: Path,
    *,
    judge_case: JudgeCase,
    provider: str,
    model: str,
) -> dict[str, Any]:
    calibration_rows = _calibration_rows(project_root)
    rows = [
        _judge_result_row(row, judge_case(row), provider=provider, model=model)
        for row in calibration_rows
    ]
    report = {
        "report_type": "hosted_model_judge_eval",
        "provider": provider,
        "model": model,
        "case_count": len(rows),
        "summary": _summary(rows),
        "by_category": _by_category(rows),
        "disagreement_examples": [
            row
            for row in rows
            if not row["model_judge_label_match"]
            or not row["classifier_model_judge_agree"]
        ][:8],
        "notes": [
            "These results depend on the configured hosted model and run time.",
            (
                "Do not compare them with deterministic CI metrics unless the run "
                "metadata is included."
            ),
        ],
    }
    write_json(project_root / MODEL_JUDGE_SUMMARY_PATH, report)
    write_jsonl(project_root / MODEL_JUDGE_CASES_PATH, rows)
    write_json(
        project_root / MODEL_JUDGE_STATUS_PATH,
        {
            "status": "completed",
            "provider": provider,
            "model": model,
            "case_count": len(rows),
            "summary_path": MODEL_JUDGE_SUMMARY_PATH,
            "cases_path": MODEL_JUDGE_CASES_PATH,
            "metrics": report["summary"],
        },
    )
    return report


def _calibration_rows(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / CALIBRATION_CASES
    if not path.exists():
        evaluate_human_calibration(project_root)
    return read_jsonl(path)


def _judge_result_row(
    row: dict[str, Any],
    judge: dict[str, Any],
    *,
    provider: str,
    model: str,
) -> dict[str, Any]:
    label = str(judge["label"]).lower()
    decision = str(judge["decision"]).lower()
    human_label = str(row["human_adjudicated_label"])
    classifier_label = str(row["classifier_binary_label"])
    return {
        "case_id": row["case_id"],
        "provider": provider,
        "model": model,
        "risk_category": row["risk_category"],
        "risk_severity": row["risk_severity"],
        "human_adjudicated_label": human_label,
        "classifier_label": classifier_label,
        "classifier_decision": row["classifier_decision"],
        "model_judge_label": label,
        "model_judge_decision": decision,
        "model_judge_confidence": round(float(judge.get("confidence", 0.0)), 4),
        "model_judge_rationale": str(judge.get("rationale", "")),
        "raw_response_id": str(judge.get("raw_response_id", "")),
        "model_judge_label_match": label == human_label,
        "classifier_model_judge_agree": classifier_label == label,
        "model_judge_error_type": _error_type(
            human_label=human_label,
            judge_label=label,
            judge_decision=decision,
        ),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_count": len(rows),
        "model_judge_label_accuracy": _ratio(
            sum(1 for row in rows if row["model_judge_label_match"]),
            len(rows),
        ),
        "classifier_model_judge_agreement_rate": _ratio(
            sum(1 for row in rows if row["classifier_model_judge_agree"]),
            len(rows),
        ),
        "model_judge_disagreement_count": sum(
            1 for row in rows if not row["model_judge_label_match"]
        ),
        "classifier_model_judge_disagreement_count": sum(
            1 for row in rows if not row["classifier_model_judge_agree"]
        ),
        "average_model_judge_confidence": _ratio(
            sum(float(row["model_judge_confidence"]) for row in rows),
            len(rows),
        ),
    }


def _by_category(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    category_rows = []
    for category in sorted({row["risk_category"] for row in rows}):
        scoped = [row for row in rows if row["risk_category"] == category]
        category_rows.append(
            {
                "risk_category": category,
                "case_count": len(scoped),
                "model_judge_label_accuracy": _ratio(
                    sum(1 for row in scoped if row["model_judge_label_match"]),
                    len(scoped),
                ),
                "classifier_model_judge_agreement_rate": _ratio(
                    sum(1 for row in scoped if row["classifier_model_judge_agree"]),
                    len(scoped),
                ),
                "top_model_judge_error_type": _top_error_type(scoped),
            }
        )
    return category_rows


def _error_type(*, human_label: str, judge_label: str, judge_decision: str) -> str:
    if human_label == judge_label:
        return "match"
    if human_label == "unsafe" and judge_label == "benign":
        return "judge_unsafe_marked_benign"
    if human_label == "benign" and judge_decision == "block":
        return "judge_benign_auto_blocked"
    return "judge_benign_marked_unsafe"


def _top_error_type(rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["model_judge_error_type"] for row in rows)
    if not counts:
        return ""
    error_type, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return f"{error_type} ({count})"


def _ratio(numerator: float | int, denominator: float | int) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)
