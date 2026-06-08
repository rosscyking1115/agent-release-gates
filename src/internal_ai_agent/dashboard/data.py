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


def load_retriever_snapshots(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/retriever_metric_snapshots.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_techqa_public_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/techqa_public_rag_summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "dataset": "nvidia/TechQA-RAG-Eval",
        "benchmark_track": "external_public_rag",
        "status": "not_configured",
        "case_count": 0,
        "benchmark_profile": {"sample_case_count": 0},
        "metrics": {},
        "notes": [],
    }


def load_wixqa_public_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/wixqa_public_rag_summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "dataset": "Wix/WixQA expert-written",
        "benchmark_track": "external_public_enterprise_rag",
        "status": "not_configured",
        "case_count": 0,
        "benchmark_profile": {"sample_case_count": 0},
        "metrics": {},
        "notes": [],
    }


def load_evaluation_history(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/evaluation_history.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_evaluation_gates(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/evaluation_gates.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_dataset_profile(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/dataset_profile.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_extraction_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/extraction_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_security_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/security_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_classifier_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_classifier_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_threshold_sweep(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_threshold_sweep.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_threshold_retuning(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_threshold_retuning.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_human_review_simulation(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_human_review_simulation.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_adjudication_notes(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_adjudication_notes.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_secondary_review_band_analysis(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_secondary_review_band_analysis.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_secondary_review_floor_validation(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_secondary_review_floor_validation.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_secondary_review_operating_recommendation(
    project_root: Path,
) -> dict[str, Any]:
    path = project_root / "reports/safety_secondary_review_operating_recommendation.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_mitigation_impact(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_mitigation_impact.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_safety_threshold_decision_memo(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/safety_threshold_decision_memo.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_human_calibration_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/human_calibration_summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "report_type": "human_label_calibration",
        "case_count": 0,
        "summary": {},
        "by_category": [],
        "by_error_type": {},
        "sample_cases": [],
        "notes": [],
    }


def load_judge_reliability_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/judge_reliability_summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "report_type": "judge_reliability_calibration",
        "case_count": 0,
        "summary": {},
        "pairwise_agreement": [],
        "by_category": [],
        "disagreement_examples": [],
        "notes": [],
    }


def load_model_judge_adapter_status(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/model_judge_adapter_status.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "status": "not_configured",
        "adapter_type": "hosted_model_judge",
        "provider": "",
        "case_count": 0,
        "planned_outputs": [],
        "notes": [],
    }


def load_failure_taxonomy_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/failure_taxonomy_summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "report_type": "failure_taxonomy_summary",
        "total_labeled_cases": 0,
        "by_label": {},
        "by_source": {},
        "definitions": {},
    }


def load_agent_summary(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/agent_eval_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent_trace_examples(project_root: Path) -> list[dict[str, Any]]:
    return read_jsonl(project_root / "reports/agent_trace_examples.jsonl")


def load_agent_otel_spans(project_root: Path) -> list[dict[str, Any]]:
    return read_jsonl(project_root / "reports/agent_otel_spans.jsonl")


def load_observability_otel_spans(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / "reports/observability_otel_spans.jsonl"
    if path.exists():
        return read_jsonl(path)
    return load_agent_otel_spans(project_root)


def load_collector_export_preview(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/collector_export_preview.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_observability_trace_index(project_root: Path) -> dict[str, Any]:
    path = project_root / "reports/observability_trace_index.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_public_report(project_root: Path) -> str:
    path = project_root / "reports/evaluation_report.md"
    return path.read_text(encoding="utf-8")


def load_public_report_html(project_root: Path) -> str:
    path = project_root / "reports/evaluation_report.html"
    return path.read_text(encoding="utf-8")


def load_public_report_pdf(project_root: Path) -> bytes:
    path = project_root / "reports/evaluation_report.pdf"
    return path.read_bytes()


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


def retriever_snapshot_rows(snapshot_report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for snapshot in snapshot_report["snapshots"]:
        rows.append(
            {
                "snapshot_id": snapshot["snapshot_id"],
                "system": snapshot["label"],
                "citation_coverage": snapshot["citation_coverage"],
                "failure_count": snapshot["failure_count"],
                "citation_delta_from_previous": snapshot["citation_delta_from_previous"],
                "failure_delta_from_previous": snapshot["failure_delta_from_previous"],
                "regression": snapshot["regression"],
                "regression_reasons": ", ".join(snapshot["regression_reasons"]),
                "citation_coverage_pct": _as_percent(snapshot["citation_coverage"]),
                "citation_delta_pct": _optional_signed_percent(
                    snapshot["citation_delta_from_previous"]
                ),
                "failure_delta": _optional_signed_int(snapshot["failure_delta_from_previous"]),
            }
        )
    return rows


def techqa_public_metric_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        "retrieval_hit_rate_at_3": "Retrieval hit rate@3",
        "top1_citation_accuracy": "Top-1 citation accuracy",
        "mean_reciprocal_rank_at_3": "Mean reciprocal rank@3",
        "abstention_accuracy": "Abstention accuracy",
        "impossible_abstention_rate": "Impossible-question abstention",
        "answerable_false_abstention_rate": "Answerable false abstention",
    }
    metrics = summary.get("metrics", {})
    return [
        {
            "metric": metric,
            "label": label,
            "value": metrics.get(metric, 0.0),
            "value_pct": _as_percent(float(metrics.get(metric, 0.0))),
        }
        for metric, label in labels.items()
        if metric in metrics
    ]


def wixqa_public_metric_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        "retrieval_hit_rate_at_3": "Retrieval hit rate@3",
        "top1_citation_accuracy": "Top-1 citation accuracy",
        "mean_reciprocal_rank_at_3": "Mean reciprocal rank@3",
        "multi_article_retrieval_hit_rate_at_3": "Multi-article retrieval@3",
    }
    metrics = summary.get("metrics", {})
    return [
        {
            "metric": metric,
            "label": label,
            "value": metrics.get(metric, 0.0),
            "value_pct": _as_percent(float(metrics.get(metric, 0.0))),
        }
        for metric, label in labels.items()
        if metric in metrics
    ]


def evaluation_history_rows(history: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for milestone in history["milestones"]:
        rows.append(
            {
                "milestone_at_utc": milestone["milestone_at_utc"],
                "milestone": milestone["milestone"],
                "system_version": milestone["system_version"],
                "retrieval_hit_rate_at_3": milestone["retrieval_hit_rate_at_3"],
                "citation_coverage": milestone["citation_coverage"],
                "next_action_accuracy": milestone["next_action_accuracy"],
                "abstention_accuracy": milestone["abstention_accuracy"],
                "failure_count": milestone["failure_count"],
                "citation_delta_from_previous": milestone[
                    "citation_delta_from_previous"
                ],
                "failure_delta_from_previous": milestone["failure_delta_from_previous"],
                "retrieval_hit_rate_at_3_pct": _as_percent(
                    milestone["retrieval_hit_rate_at_3"]
                ),
                "citation_coverage_pct": _as_percent(milestone["citation_coverage"]),
                "next_action_accuracy_pct": _as_percent(
                    milestone["next_action_accuracy"]
                ),
                "abstention_accuracy_pct": _as_percent(
                    milestone["abstention_accuracy"]
                ),
                "citation_delta_pct": _optional_signed_percent(
                    milestone["citation_delta_from_previous"]
                ),
                "failure_delta": _optional_signed_int(
                    milestone["failure_delta_from_previous"]
                ),
            }
        )
    return rows


def evaluation_gate_rows(gates: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "area": gate["area"],
            "label": gate["label"],
            "status": gate["status"],
            "severity": gate["severity"],
            "observed": _format_gate_value(gate["observed"], gate.get("value_format", "number")),
            "threshold": _format_gate_value(
                gate["threshold"], gate.get("value_format", "number")
            ),
            "rationale": gate["rationale"],
        }
        for gate in gates.get("gates", [])
    ]


def coverage_count_rows(profile: dict[str, Any], section: str) -> list[dict[str, Any]]:
    return [
        {"value": value, "case_count": count}
        for value, count in profile["golden_coverage"].get(section, {}).items()
    ]


def red_team_coverage_rows(profile: dict[str, Any], section: str) -> list[dict[str, Any]]:
    return [
        {"value": value, "case_count": count}
        for value, count in profile["red_team_coverage"].get(section, {}).items()
    ]


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


def taxonomy_label_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    definitions = summary.get("definitions", {})
    return [
        {
            "label": label,
            "group": definitions.get(label, {}).get("group", "unknown"),
            "count": count,
        }
        for label, count in sorted(
            summary.get("by_label", {}).items(),
            key=lambda item: (-int(item[1]), str(item[0])),
        )
    ]


def taxonomy_source_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, labels in sorted(summary.get("by_source", {}).items()):
        if not labels:
            continue
        top_label, count = sorted(
            labels.items(), key=lambda item: (-int(item[1]), str(item[0]))
        )[0]
        rows.append({"source": source, "top_label": top_label, "count": count})
    return rows


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
        {
            "metric": "weighted_safe_rate",
            "label": "Weighted safe response rate",
            "baseline": metrics["baseline_weighted_safe_rate"],
            "improved": metrics["improved_weighted_safe_rate"],
            "baseline_pct": _as_percent(metrics["baseline_weighted_safe_rate"]),
            "improved_pct": _as_percent(metrics["improved_weighted_safe_rate"]),
        },
    ]


def security_risk_breakdown_rows(
    summary: dict[str, Any],
    dimension: str,
) -> list[dict[str, Any]]:
    groups = summary.get(dimension, {})
    return [
        {
            "group": group,
            "case_count": values["case_count"],
            "max_risk_severity": values["max_risk_severity"],
            "block_rate": values["block_rate"],
            "safe_rate": values["safe_rate"],
            "weighted_safe_rate": values["weighted_safe_rate"],
            "residual_risk_score": values["residual_risk_score"],
            "block_rate_pct": _as_percent(values["block_rate"]),
            "safe_rate_pct": _as_percent(values["safe_rate"]),
            "weighted_safe_rate_pct": _as_percent(values["weighted_safe_rate"]),
        }
        for group, values in groups.items()
    ]


def safety_threshold_rows(sweep: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "threshold": row["threshold"],
            "policy_label": row["policy_label"],
            "precision": row["precision"],
            "recall": row["recall"],
            "false_positive_rate": row["false_positive_rate"],
            "false_negative_rate": row["false_negative_rate"],
            "review_rate": row["review_rate"],
            "auto_block_rate": row["auto_block_rate"],
            "precision_pct": _as_percent(row["precision"]),
            "recall_pct": _as_percent(row["recall"]),
            "false_positive_rate_pct": _as_percent(row["false_positive_rate"]),
            "false_negative_rate_pct": _as_percent(row["false_negative_rate"]),
            "review_rate_pct": _as_percent(row["review_rate"]),
            "auto_block_rate_pct": _as_percent(row["auto_block_rate"]),
            "high_severity_false_negative_count": row[
                "high_severity_false_negative_count"
            ],
        }
        for row in sweep.get("candidates", [])
    ]


def safety_retuning_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "risk_category": row["risk_category"],
            "legacy_recall_pct": _as_percent(row["legacy_recall"]),
            "tuned_recall_pct": _as_percent(row["tuned_recall"]),
            "recall_delta_pct": _as_signed_percent(row["recall_delta"]),
            "legacy_false_negative_count": row["legacy_false_negative_count"],
            "tuned_false_negative_count": row["tuned_false_negative_count"],
            "false_negative_reduction": row["false_negative_reduction"],
            "false_positive_delta": row["false_positive_delta"],
        }
        for row in report.get("category_comparison", [])
    ]


def safety_review_case_rows(simulation: dict[str, Any], *, limit: int = 30) -> list[dict[str, Any]]:
    rows = simulation.get("review_cases", [])
    return [
        {
            "case_id": row["case_id"],
            "source": row["source"],
            "risk_category": row["risk_category"],
            "risk_severity": row["risk_severity"],
            "score": row["max_score"],
            "primary_decision": row["primary_decision"],
            "secondary_decision": row["secondary_decision"],
            "final_decision": row["final_decision"],
            "disagreement": row["disagreement"],
            "escalated": row["escalated"],
            "turnaround_minutes": row["turnaround_minutes"],
            "rationale": row["review_rationale"],
        }
        for row in rows[:limit]
    ]


def safety_adjudication_note_rows(
    report: dict[str, Any],
    *,
    limit: int = 30,
) -> list[dict[str, Any]]:
    rows = report.get("notes", [])
    return [
        {
            "case_id": row["case_id"],
            "source": row["source"],
            "risk_category": row["risk_category"],
            "risk_severity": row["risk_severity"],
            "in_review_queue": row["in_review_queue"],
            "classifier_decision": row["classifier_decision"],
            "recommended_decision": row["recommended_decision"],
            "classifier_disagreed": row["classifier_disagreed"],
            "score": row["classifier_score"],
            "note": row["adjudication_note"],
        }
        for row in rows[:limit]
    ]


def safety_mitigation_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "scenario": row["label"],
            "unsafe_allowed": row["unsafe_allowed_count"],
            "unsafe_intercepted": row["unsafe_intercepted_count"],
            "overblocks": row["overblock_count"],
            "manual_touches": row["reviewed_count"] + row["held_for_review_count"],
            "unsafe_allowed_rate_pct": _as_percent(row["unsafe_allowed_rate"]),
            "unsafe_intercepted_rate_pct": _as_percent(row["unsafe_intercepted_rate"]),
            "overblock_rate_pct": _as_percent(row["overblock_rate"]),
            "manual_touch_rate_pct": _as_percent(row["manual_touch_rate"]),
        }
        for row in report.get("scenarios", [])
    ]


def safety_operating_recommendation_rows(
    report: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "reviewer_daily_capacity": row["reviewer_daily_capacity"],
            "reviewer_count": row["reviewer_count"],
            "total_daily_capacity": row["total_daily_capacity"],
            "floor_review_count": row["floor_review_count"],
            "capacity_utilization": row["capacity_utilization"],
            "capacity_utilization_pct": _as_percent(row["capacity_utilization"]),
            "capacity_buffer_cases": row["capacity_buffer_cases"],
            "capacity_buffer_rate_pct": _as_percent(row["capacity_buffer_rate"]),
            "estimated_backlog_days": row["estimated_backlog_days"],
            "capacity_status": row["capacity_status"],
            "operating_decision": row["operating_decision"],
        }
        for row in report.get("scenarios", [])
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


def agent_trace_rows(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "trace_id": trace["trace_id"],
            "ticket_id": trace["ticket_id"],
            "approval_granted": trace["approval_granted"],
            "route_tool_outcome": trace["route_tool_outcome"],
            "tool_call_count": trace["tool_call_count"],
            "executed_tool_call_count": trace["executed_tool_call_count"],
            "blocked_tool_call_count": trace["blocked_tool_call_count"],
            "audit_event_count": len(trace.get("audit_events", [])),
        }
        for trace in traces
    ]


def agent_otel_span_rows(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "trace_id": span["trace_id"],
            "span_id": span["span_id"],
            "parent_span_id": span["parent_span_id"] or "",
            "name": span["name"],
            "component": span["attributes"].get("lab.component", ""),
            "ticket_id": span["attributes"].get("ticket.id", ""),
            "outcome": span["attributes"].get("audit.outcome", span["status"]["code"]),
            "start_time_unix_nano": span["start_time_unix_nano"],
            "end_time_unix_nano": span["end_time_unix_nano"],
        }
        for span in spans
    ]


def agent_otel_timeline_rows(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    spans_by_trace: dict[str, list[dict[str, Any]]] = {}
    for span in spans:
        spans_by_trace.setdefault(span["trace_id"], []).append(span)

    rows: list[dict[str, Any]] = []
    for trace_id, trace_spans in sorted(
        spans_by_trace.items(),
        key=lambda item: min(int(span["start_time_unix_nano"]) for span in item[1]),
    ):
        trace_start_ns = min(int(span["start_time_unix_nano"]) for span in trace_spans)
        sorted_spans = sorted(
            trace_spans,
            key=lambda span: (int(span["start_time_unix_nano"]), span["span_id"]),
        )
        for span_order, span in enumerate(sorted_spans, start=1):
            attributes = span.get("attributes", {})
            start_ns = int(span["start_time_unix_nano"])
            end_ns = max(int(span["end_time_unix_nano"]), start_ns)
            name = str(span["name"])
            trace_label = str(attributes.get("lab.trace_id", trace_id[:12]))
            start_ms = (start_ns - trace_start_ns) / 1_000_000
            end_ms = (end_ns - trace_start_ns) / 1_000_000
            rows.append(
                {
                    "trace_id": trace_id,
                    "trace_label": trace_label,
                    "ticket_id": attributes.get("ticket.id", ""),
                    "span_id": span["span_id"],
                    "parent_span_id": span["parent_span_id"] or "",
                    "name": name,
                    "span_label": f"{span_order}. {name}",
                    "span_order": span_order,
                    "outcome": _span_outcome(span),
                    "is_root": span["parent_span_id"] is None,
                    "start_ms": round(start_ms, 3),
                    "end_ms": round(end_ms, 3),
                    "duration_ms": round(end_ms - start_ms, 3),
                }
            )
    return rows


def agent_otel_summary(spans: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "span_count": len(spans),
        "trace_count": len({span["trace_id"] for span in spans}),
        "root_span_count": sum(1 for span in spans if span["parent_span_id"] is None),
        "child_span_count": sum(1 for span in spans if span["parent_span_id"] is not None),
        "tool_span_count": sum(
            1
            for span in spans
            if span["parent_span_id"] is not None
            and span.get("attributes", {}).get("audit.component") == "tool"
        ),
    }


def observability_component_rows(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, int]] = {}
    for span in spans:
        component = str(span.get("attributes", {}).get("lab.component", "agent"))
        if not component:
            component = "agent"
        row = counts.setdefault(component, {"span_count": 0, "root_span_count": 0})
        row["span_count"] += 1
        if span["parent_span_id"] is None:
            row["root_span_count"] += 1
    return [
        {
            "component": component,
            "span_count": values["span_count"],
            "root_span_count": values["root_span_count"],
        }
        for component, values in sorted(counts.items())
    ]


def trace_index_component_rows(index: dict[str, Any]) -> list[dict[str, Any]]:
    return list(index.get("components", []))


def trace_index_query_rows(index: dict[str, Any]) -> list[dict[str, Any]]:
    return list(index.get("queries", []))


def trace_index_error_rows(index: dict[str, Any]) -> list[dict[str, Any]]:
    return list(index.get("error_spans", []))


def trace_index_trace_rows(index: dict[str, Any], *, limit: int = 20) -> list[dict[str, Any]]:
    rows = list(index.get("traces", []))
    return rows[:limit]


def human_calibration_category_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in report.get("by_category", []):
        rows.append(
            {
                **row,
                "classifier_label_accuracy_pct": _as_percent(
                    float(row["classifier_label_accuracy"])
                ),
                "classifier_action_match_pct": _as_percent(
                    float(row["classifier_action_match_rate"])
                ),
            }
        )
    return rows


def human_calibration_case_rows(
    report: dict[str, Any],
    *,
    limit: int = 12,
) -> list[dict[str, Any]]:
    rows = []
    for row in list(report.get("sample_cases", []))[:limit]:
        rows.append(
            {
                "case_id": row["case_id"],
                "risk_category": row["risk_category"],
                "risk_severity": row["risk_severity"],
                "human_label": row["human_adjudicated_label"],
                "expected_action": row["expected_action"],
                "classifier_decision": row["classifier_decision"],
                "classifier_score": row["classifier_score"],
                "reviewer_disagreement": row["reviewer_disagreement"],
                "error_type": row["error_type"],
            }
        )
    return rows


def judge_reliability_pair_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in report.get("pairwise_agreement", []):
        rows.append(
            {
                **row,
                "agreement_rate_pct": _as_percent(float(row["agreement_rate"])),
            }
        )
    return rows


def judge_reliability_category_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in report.get("by_category", []):
        rows.append(
            {
                **row,
                "judge_label_accuracy_pct": _as_percent(
                    float(row["judge_label_accuracy"])
                ),
                "classifier_label_accuracy_pct": _as_percent(
                    float(row["classifier_label_accuracy"])
                ),
                "classifier_judge_agreement_pct": _as_percent(
                    float(row["classifier_judge_agreement_rate"])
                ),
            }
        )
    return rows


def judge_reliability_disagreement_rows(
    report: dict[str, Any],
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    rows = []
    for row in list(report.get("disagreement_examples", []))[:limit]:
        rows.append(
            {
                "case_id": row["case_id"],
                "risk_category": row["risk_category"],
                "human_label": row["human_adjudicated_label"],
                "classifier_label": row["classifier_label"],
                "judge_label": row["judge_label"],
                "judge_confidence": row["judge_confidence"],
                "classifier_error_type": row["classifier_error_type"],
                "judge_error_type": row["judge_error_type"],
            }
        )
    return rows


def model_judge_adapter_rows(status: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"field": "Status", "value": status.get("status", "")},
        {"field": "Provider", "value": status.get("provider", "")},
        {"field": "API mode", "value": status.get("api_mode", "")},
        {"field": "Calibration cases", "value": status.get("case_count", 0)},
        {
            "field": "Credential env var",
            "value": status.get("credential_env_var", ""),
        },
        {"field": "Model env var", "value": status.get("model_env_var", "")},
    ]


def _span_outcome(span: dict[str, Any]) -> str:
    attributes = span.get("attributes", {})
    return str(
        attributes.get(
            "audit.outcome",
            attributes.get(
                "agent.route_tool_outcome",
                span.get("status", {}).get("code", ""),
            ),
        )
    )


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
                    "score_explanation": _candidate_score_summary(
                        case.get("retrieved_candidate_scores", [])
                    ),
                    "retrieved_but_not_cited": retrieved_but_not_cited(case),
                    "diagnostic": case["diagnostic"],
                    "recommended_fix": case["recommended_fix"],
                }
            )
    return rows


def _candidate_score_summary(candidates: object) -> str:
    if not isinstance(candidates, list):
        return ""
    summaries: list[str] = []
    for candidate in candidates[:3]:
        if not isinstance(candidate, dict):
            continue
        section_id = str(candidate.get("section_id", ""))
        score = candidate.get("score", "")
        breakdown = candidate.get("score_breakdown", {})
        if not isinstance(breakdown, dict) or not breakdown:
            summaries.append(f"{section_id} total={score}")
            continue
        components = ", ".join(
            f"{key}={value}"
            for key, value in breakdown.items()
            if isinstance(value, (int, float)) and value != 0
        )
        summaries.append(f"{section_id} total={score} ({components})")
    return "; ".join(summaries)


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


def _optional_signed_percent(value: float | None) -> str:
    if value is None:
        return ""
    return _as_signed_percent(value)


def _optional_signed_int(value: int | None) -> str:
    if value is None:
        return ""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value}"


def _format_gate_value(value: object, value_format: str) -> object:
    if isinstance(value, (float, int)) and value_format == "percent":
        return _as_percent(float(value))
    return value
