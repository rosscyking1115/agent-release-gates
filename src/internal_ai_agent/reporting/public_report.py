from __future__ import annotations

import json
from pathlib import Path
from typing import Any

METRIC_LABELS = {
    "retrieval_hit_rate_at_3": "Retrieval hit rate@3",
    "citation_coverage": "Citation coverage",
    "issue_category_accuracy": "Issue category accuracy",
    "next_action_accuracy": "Next action accuracy",
    "abstention_accuracy": "Abstention accuracy",
}

EXTRACTION_METRIC_LABELS = {
    "schema_validity": "Schema validity",
    "issue_category_accuracy": "Issue category accuracy",
    "severity_accuracy": "Severity accuracy",
    "impacted_system_accuracy": "Impacted system accuracy",
    "routing_team_accuracy": "Routing team accuracy",
}

AGENT_METRIC_LABELS = {
    "trace_coverage_rate": "Trace coverage",
    "audit_event_coverage_rate": "Audit event coverage",
    "approval_audit_rate": "Approval audit coverage",
    "side_effect_block_rate": "Side-effect block rate",
    "approved_action_execution_rate": "Approved action execution rate",
    "unnecessary_tool_call_rate": "Unnecessary tool-call rate",
}


def generate_public_report(project_root: Path) -> str:
    reports_dir = project_root / "reports"
    comparison = _read_json(reports_dir / "eval_comparison.json")
    retrievers = _read_json(reports_dir / "retriever_comparison.json")
    extraction = _read_json(reports_dir / "extraction_eval_summary.json")
    security = _read_json(reports_dir / "security_eval_summary.json")
    agent = _read_json(reports_dir / "agent_eval_summary.json")

    markdown = "\n".join(
        [
            "# Internal AI Agent Evaluation Report",
            "",
            "## Executive Summary",
            "",
            "This report summarizes a fully synthetic evaluation lab for internal AI agent "
            "workflows. It does not use real company documents, customer data, employee "
            "data, confidential processes, or real operational actions.",
            "",
            f"- Golden retrieval cases: {comparison['case_count']}",
            f"- Synthetic ticket extraction and agent cases: {agent['case_count']}",
            f"- Red-team safety cases: {security['case_count']}",
            "- Best current retriever: Hybrid sparse semantic retrieval",
            "- Current strongest result: perfect hybrid citation coverage on the synthetic suite",
            "",
            "## Retrieval Evaluation",
            "",
            _retriever_table(retrievers),
            "",
            "The retrieval experiment compares a deliberately weak baseline, a lexical "
            "retriever, and a local hybrid sparse semantic retriever. The hybrid system "
            "adds synonym-aware scoring, phrase matching, and false-lead handling before "
            "the project introduces heavier vector infrastructure.",
            "",
            "## Baseline To Improved Delta",
            "",
            _before_after_table(comparison),
            "",
            "## Structured Extraction",
            "",
            _single_metric_table(extraction["metrics"], EXTRACTION_METRIC_LABELS),
            "",
            "Extraction currently uses deterministic synthetic ticket patterns. The value "
            "of this stage is the schema, routing contract, and evaluation harness rather "
            "than a claim that messy real tickets are solved.",
            "",
            "## Safety Red-Team",
            "",
            _security_table(security),
            "",
            "Block rate requires an explicit policy refusal. Safe response rate checks that "
            "forbidden behavior is absent from the response.",
            "",
            "## Controlled Agent Workflow",
            "",
            _single_metric_table(agent["metrics"], AGENT_METRIC_LABELS),
            "",
            "The controlled workflow separates read-only tools from side-effecting actions. "
            "The mock ticket routing tool is prepared but blocked until approval is granted, "
            "and every run returns trace, audit, and monitoring fields.",
            "",
            "## What This Proves",
            "",
            "- The project can generate synthetic enterprise operations data safely.",
            "- Retrieval quality can be measured across exact, paraphrased, noisy, conflicting, "
            "and adversarial cases.",
            "- Structured extraction, routing, refusal behavior, approval gates, and audit traces "
            "are evaluated as product behavior, not only as model output.",
            "- The dashboard, API, Docker runtime, and CI workflow make the lab reproducible.",
            "",
            "## Current Limitations",
            "",
            "- The dataset is synthetic and templated.",
            "- Extraction is deterministic rather than LLM-backed.",
            "- The hybrid retriever is local and sparse; it is not yet a vector database.",
            "- Scores should be read as regression-test results for this lab, not as claims "
            "about production accuracy.",
            "",
            "## Recommended Next Work",
            "",
            "- Add noisier, human-written ticket variants.",
            "- Introduce a real embedding/vector retrieval experiment.",
            "- Add report export from the dashboard UI.",
            "- Add OpenTelemetry-compatible trace export.",
            "- Add an optional LLM extraction path with schema repair and failure analysis.",
            "",
        ]
    )
    return markdown


def write_public_report(project_root: Path) -> Path:
    output_path = project_root / "reports/evaluation_report.md"
    output_path.write_text(generate_public_report(project_root), encoding="utf-8")
    return output_path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _retriever_table(report: dict[str, Any]) -> str:
    rows = [
        "| System | Hit rate@3 | Citation coverage | Next action accuracy | "
        "Abstention accuracy | Failures |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for system in report["systems"]:
        rows.append(
            "| {label} | {hit} | {citation} | {next_action} | {abstention} | {failures} |".format(
                label=system["label"],
                hit=_pct(system["retrieval_hit_rate_at_3"]),
                citation=_pct(system["citation_coverage"]),
                next_action=_pct(system["next_action_accuracy"]),
                abstention=_pct(system["abstention_accuracy"]),
                failures=system["failure_count"],
            )
        )
    return "\n".join(rows)


def _before_after_table(report: dict[str, Any]) -> str:
    rows = [
        "| Metric | Baseline | Improved lexical | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for metric, label in METRIC_LABELS.items():
        values = report["metrics"][metric]
        rows.append(
            f"| {label} | {_pct(values['baseline'])} | {_pct(values['improved'])} | "
            f"{_signed_pct(values['delta'])} |"
        )
    return "\n".join(rows)


def _single_metric_table(metrics: dict[str, float], labels: dict[str, str]) -> str:
    rows = [
        "| Metric | Score |",
        "| --- | ---: |",
    ]
    for metric, label in labels.items():
        if metric in metrics:
            rows.append(f"| {label} | {_pct(metrics[metric])} |")
    return "\n".join(rows)


def _security_table(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    return "\n".join(
        [
            "| Metric | Baseline | Improved policy |",
            "| --- | ---: | ---: |",
            f"| Policy block rate | {_pct(metrics['baseline_block_rate'])} | "
            f"{_pct(metrics['improved_block_rate'])} |",
            f"| Safe response rate | {_pct(metrics['baseline_safe_rate'])} | "
            f"{_pct(metrics['improved_safe_rate'])} |",
        ]
    )


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"
