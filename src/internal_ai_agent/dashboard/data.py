from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl

METRIC_LABELS = {
    "retrieval_hit_rate_at_3": "Retrieval hit rate@3",
    "citation_coverage": "Citation coverage",
    "issue_category_accuracy": "Issue category accuracy",
    "team_accuracy": "Team accuracy",
    "next_action_accuracy": "Next action accuracy",
    "abstention_rate": "Abstention rate",
    "abstention_accuracy": "Abstention accuracy",
}

METRIC_ORDER = [
    "retrieval_hit_rate_at_3",
    "citation_coverage",
    "issue_category_accuracy",
    "team_accuracy",
    "next_action_accuracy",
    "abstention_accuracy",
    "abstention_rate",
]

AGENT_METRIC_LABELS = {
    "trace_coverage_rate": "Trace coverage rate",
    "audit_event_coverage_rate": "Audit event coverage rate",
    "approval_audit_rate": "Approval audit rate",
    "monitoring_snapshot_rate": "Monitoring snapshot rate",
    "valid_tool_call_rate": "Valid tool-call rate",
    "approval_trigger_rate": "Approval trigger rate",
    "side_effect_block_rate": "Side-effect block rate",
    "approved_action_execution_rate": "Approved action execution rate",
    "route_tool_selection_accuracy": "Route-tool selection accuracy",
    "unnecessary_tool_call_rate": "Unnecessary tool-call rate",
}

AGENT_METRIC_ORDER = [
    "trace_coverage_rate",
    "audit_event_coverage_rate",
    "approval_audit_rate",
    "monitoring_snapshot_rate",
    "valid_tool_call_rate",
    "approval_trigger_rate",
    "side_effect_block_rate",
    "approved_action_execution_rate",
    "route_tool_selection_accuracy",
    "unnecessary_tool_call_rate",
]

RETRIEVER_CASE_FILES = {
    "Baseline team hints": "baseline",
    "Improved lexical": "improved",
    "Hybrid sparse semantic": "hybrid",
    "Local TF-IDF vector": "vector",
    "Local embedding store": "embedding",
}


def load_comparison(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/eval_comparison.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_retriever_comparison(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/retriever_comparison.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_extraction_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/extraction_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_security_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/security_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/agent_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_public_report(project_root: Path) -> str:
    path = project_root / "reports/evaluation_report.md"
    return path.read_text(encoding="utf-8")


def load_public_report_html(project_root: Path) -> str:
    path = project_root / "reports/evaluation_report.html"
    return path.read_text(encoding="utf-8")


def metric_rows(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = comparison["metrics"]
    rows: list[dict[str, Any]] = []
    for metric in METRIC_ORDER:
        values = metrics[metric]
        rows.append(
            {
                "metric": metric,
                "label": METRIC_LABELS[metric],
                "baseline": values["baseline"],
                "improved": values["improved"],
                "delta": values["delta"],
                "baseline_pct": _as_percent(values["baseline"]),
                "improved_pct": _as_percent(values["improved"]),
                "delta_pct": _as_signed_percent(values["delta"]),
            }
        )
    return rows


def retriever_experiment_rows(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for system in comparison["systems"]:
        rows.append(
            {
                "system": system["label"],
                "retrieval_hit_rate_at_3": system["retrieval_hit_rate_at_3"],
                "citation_coverage": system["citation_coverage"],
                "issue_category_accuracy": system["issue_category_accuracy"],
                "next_action_accuracy": system["next_action_accuracy"],
                "abstention_accuracy": system["abstention_accuracy"],
                "failure_count": system["failure_count"],
                "retrieval_hit_rate_at_3_pct": _as_percent(system["retrieval_hit_rate_at_3"]),
                "citation_coverage_pct": _as_percent(system["citation_coverage"]),
                "issue_category_accuracy_pct": _as_percent(system["issue_category_accuracy"]),
                "next_action_accuracy_pct": _as_percent(system["next_action_accuracy"]),
                "abstention_accuracy_pct": _as_percent(system["abstention_accuracy"]),
            }
        )
    return rows


def error_analysis_rows(summary: dict[str, Any], dimension: str) -> list[dict[str, Any]]:
    groups = summary.get(dimension, {})
    return [
        {
            "group": group,
            "case_count": values["case_count"],
            "failure_count": values["failure_count"],
            "citation_coverage": values["citation_coverage"],
            "abstention_accuracy": values["abstention_accuracy"],
            "next_action_accuracy": values["next_action_accuracy"],
            "citation_coverage_pct": _as_percent(values["citation_coverage"]),
            "abstention_accuracy_pct": _as_percent(values["abstention_accuracy"]),
            "next_action_accuracy_pct": _as_percent(values["next_action_accuracy"]),
        }
        for group, values in groups.items()
    ]


def failure_reason_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"reason": reason, "count": count}
        for reason, count in summary.get("failure_reasons", {}).items()
    ]


def failure_example_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row["case_id"],
            "noise_type": row["noise_type"],
            "failure_reasons": ", ".join(row["failure_reasons"]),
            "expected": row["expected_issue_category"],
            "predicted": row["predicted_issue_category"],
            "expected_citation": ", ".join(row["expected_citation_ids"]),
            "predicted_citation": ", ".join(row["predicted_citation_ids"]),
            "diagnostic": row["diagnostic"],
            "recommended_fix": row["recommended_fix"],
        }
        for row in summary.get("failure_examples", [])
    ]


def extraction_metric_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "metric": metric,
            "label": metric.replace("_", " ").title(),
            "value": value,
            "value_pct": _as_percent(value),
        }
        for metric, value in summary["metrics"].items()
    ]


def security_metric_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = summary["metrics"]
    return [
        {
            "metric": "block_rate",
            "label": "Policy block rate",
            "baseline": metrics["baseline_block_rate"],
            "improved": metrics["improved_block_rate"],
            "baseline_pct": _as_percent(metrics["baseline_block_rate"]),
            "improved_pct": _as_percent(metrics["improved_block_rate"]),
        },
        {
            "metric": "safe_rate",
            "label": "Safe response rate",
            "baseline": metrics["baseline_safe_rate"],
            "improved": metrics["improved_safe_rate"],
            "baseline_pct": _as_percent(metrics["baseline_safe_rate"]),
            "improved_pct": _as_percent(metrics["improved_safe_rate"]),
        },
    ]


def agent_metric_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = summary["metrics"]
    return [
        {
            "metric": metric,
            "label": AGENT_METRIC_LABELS[metric],
            "value": metrics[metric],
            "value_pct": _as_percent(metrics[metric]),
        }
        for metric in AGENT_METRIC_ORDER
        if metric in metrics
    ]


def load_case_rows(project_root: Path, system: str) -> list[dict[str, Any]]:
    filename = f"{system}_eval_cases.jsonl"
    return read_jsonl(project_root / "reports" / filename)


def load_retriever_case_rows(project_root: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        label: load_case_rows(project_root, system)
        for label, system in RETRIEVER_CASE_FILES.items()
    }


def failed_case_rows(rows: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    failed = [row for row in rows if case_failed(row)]
    return failed[:limit]


def case_failed(row: dict[str, Any]) -> bool:
    return not (
        row["abstention_correct"]
        and (row["expected_abstain"] or row["citation_match"])
        and (row["expected_abstain"] or row["next_action_match"])
    )


def retrieved_but_not_cited(row: dict[str, Any]) -> bool:
    return (
        not row["expected_abstain"]
        and row["retrieval_hit_at_3"]
        and not row["citation_match"]
    )


def retriever_failure_overview(
    cases_by_system: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for system, cases in cases_by_system.items():
        failures = [case for case in cases if case_failed(case)]
        rows.append(
            {
                "system": system,
                "failed_cases": len(failures),
                "retrieved_but_not_cited": sum(
                    1 for case in failures if retrieved_but_not_cited(case)
                ),
                "abstention_mismatches": sum(
                    1
                    for case in failures
                    if "abstention_mismatch" in case.get("failure_reasons", [])
                ),
                "top_failure_reason": _top_failure_reason(failures),
            }
        )
    return rows


def retriever_failure_example_rows(
    cases_by_system: dict[str, list[dict[str, Any]]],
    *,
    limit_per_system: int = 5,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for system, cases in cases_by_system.items():
        failures = [case for case in cases if case_failed(case)][:limit_per_system]
        for case in failures:
            rows.append(
                {
                    "system": system,
                    "case_id": case["case_id"],
                    "noise_type": case["noise_type"],
                    "failure_reasons": ", ".join(case.get("failure_reasons", [])),
                    "expected_citation": ", ".join(case["expected_citation_ids"]),
                    "predicted_citation": ", ".join(case["predicted_citation_ids"]),
                    "retrieved_citations": ", ".join(case["retrieved_citation_ids"]),
                    "retrieved_but_not_cited": retrieved_but_not_cited(case),
                    "diagnostic": case["diagnostic"],
                    "recommended_fix": case["recommended_fix"],
                }
            )
    return rows


def case_mix(rows: list[dict[str, Any]]) -> dict[str, int]:
    answerable = sum(1 for row in rows if not row["expected_abstain"])
    abstain = sum(1 for row in rows if row["expected_abstain"])
    failed = len(failed_case_rows(rows, limit=len(rows)))
    return {
        "answerable_cases": answerable,
        "expected_abstentions": abstain,
        "failed_cases": failed,
    }


def _top_failure_reason(failures: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for row in failures:
        for reason in row.get("failure_reasons", []):
            counts[reason] = counts.get(reason, 0) + 1
    if not counts:
        return ""
    reason, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return f"{reason} ({count})"


def _as_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _as_signed_percent(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"
