from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from internal_ai_agent.dashboard.data import (
    agent_trace_rows,
    load_agent_trace_examples,
    load_retriever_case_rows,
    retriever_failure_example_rows,
    retriever_failure_overview,
    retriever_snapshot_rows,
)

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
    retriever_snapshots = _read_json(reports_dir / "retriever_metric_snapshots.json")
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
            (
                "- Current vector experiments: local TF-IDF vector retrieval and local "
                "embedding-store retrieval"
            ),
            "",
            "## Retrieval Evaluation",
            "",
            _retriever_table(retrievers),
            "",
            "The retrieval experiment compares a deliberately weak baseline, a lexical "
            "retriever, a local hybrid sparse semantic retriever, a TF-IDF vector "
            "retriever, and a local embedding-store retriever. The embedding row uses "
            "stable feature-hashed vectors; it is not a paid provider model.",
            "",
            "## Retriever Metric Snapshots",
            "",
            _retriever_snapshot_table(retriever_snapshots),
            "",
            "## Retriever Failure Analysis",
            "",
            _retriever_failure_overview_table(project_root),
            "",
            _retriever_failure_examples_table(project_root),
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
            "## Agent Trace Examples",
            "",
            _agent_trace_examples_table(project_root),
            "",
            "## What This Proves",
            "",
            "- The project can generate synthetic enterprise operations data safely.",
            (
                "- Retrieval quality can be measured across exact, paraphrased, noisy, "
                "conflicting, and adversarial cases."
            ),
            (
                "- Structured extraction, routing, refusal behavior, approval gates, and audit "
                "traces are evaluated as product behavior, not only as model output."
            ),
            "- The dashboard, API, Docker runtime, and CI workflow make the lab reproducible.",
            "",
            "## Current Limitations",
            "",
            "- The dataset is synthetic and templated.",
            "- Extraction is deterministic rather than LLM-backed.",
            "- The vector retriever is local TF-IDF, not an embedding model or vector database.",
            "- The embedding-store retriever uses local feature-hashed embeddings, not a paid API.",
            (
                "- Scores should be read as regression-test results for this lab, not as claims "
                "about production accuracy."
            ),
            "",
            "## Recommended Next Work",
            "",
            "- Add noisier, human-written ticket variants.",
            "- Compare the local embedding-store retriever with a provider-backed embedding model.",
            "- Add downloadable PDF report export.",
            "- Add OpenTelemetry-compatible trace export.",
            "- Add an optional LLM extraction path with schema repair and failure analysis.",
            "",
        ]
    )
    return markdown


def generate_public_report_html(project_root: Path) -> str:
    return _markdown_to_html_document(generate_public_report(project_root))


def write_public_report(project_root: Path) -> Path:
    output_path = project_root / "reports/evaluation_report.md"
    html_path = project_root / "reports/evaluation_report.html"
    markdown = generate_public_report(project_root)
    output_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(_markdown_to_html_document(markdown), encoding="utf-8")
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


def _agent_trace_examples_table(project_root: Path) -> str:
    traces = agent_trace_rows(load_agent_trace_examples(project_root))
    if not traces:
        return "No agent trace examples recorded."
    rows = [
        (
            "| Trace | Ticket | Approval | Route outcome | Tool calls | Executed | "
            "Blocked | Audit events |"
        ),
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for trace in traces[:10]:
        rows.append(
            "| {trace_id} | {ticket_id} | {approval_granted} | {route_tool_outcome} | "
            "{tool_call_count} | {executed_tool_call_count} | {blocked_tool_call_count} | "
            "{audit_event_count} |".format(**trace)
        )
    return "\n".join(rows)


def _retriever_snapshot_table(report: dict[str, Any]) -> str:
    rows = [
        "| Snapshot | System | Citation coverage | Failed cases | Citation delta | "
        "Failure delta | Regression | Reason |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in retriever_snapshot_rows(report):
        rows.append(
            "| {snapshot_id} | {system} | {citation_coverage_pct} | {failure_count} | "
            "{citation_delta_pct} | {failure_delta} | {regression} | "
            "{regression_reasons} |".format(**row)
        )
    return "\n".join(rows)


def _retriever_failure_overview_table(project_root: Path) -> str:
    rows = [
        "| System | Failed cases | Retrieved but not cited | Abstention mismatches | "
        "Top failure reason |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in retriever_failure_overview(load_retriever_case_rows(project_root)):
        rows.append(
            "| {system} | {failed_cases} | {retrieved_but_not_cited} | "
            "{abstention_mismatches} | {top_failure_reason} |".format(**row)
        )
    return "\n".join(rows)


def _retriever_failure_examples_table(project_root: Path) -> str:
    examples = retriever_failure_example_rows(
        load_retriever_case_rows(project_root), limit_per_system=3
    )
    if not examples:
        return "No retriever failure examples recorded."

    rows = [
        "| System | Case | Noise | Failure | Expected citation | Predicted citation | "
        "Retrieved but not cited | Top retrieved scores | Recommended fix |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in examples:
        rows.append(
            "| {system} | {case_id} | {noise_type} | {failure_reasons} | "
            "{expected_citation} | {predicted_citation} | {retrieved_but_not_cited} | "
            "{score_explanation} | {recommended_fix} |".format(**row)
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


def _markdown_to_html_document(markdown: str) -> str:
    body = _markdown_to_body_html(markdown)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Internal AI Agent Evaluation Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px auto; max-width: 1040px; "
            "line-height: 1.55; color: #1f2937; }",
            "h1, h2 { color: #111827; }",
            "table { border-collapse: collapse; width: 100%; margin: 16px 0 24px; }",
            "th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }",
            "th { background: #f3f4f6; }",
            "td:not(:first-child), th:not(:first-child) { text-align: right; }",
            "code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }",
            "</style>",
            "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
            "",
        ]
    )


def _markdown_to_body_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("# "):
            blocks.append(f"<h1>{escape(line[2:])}</h1>")
            index += 1
            continue
        if line.startswith("## "):
            blocks.append(f"<h2>{escape(line[3:])}</h2>")
            index += 1
            continue
        if line.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(f"<li>{escape(lines[index].strip()[2:])}</li>")
                index += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        if line.startswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            blocks.append(_markdown_table_to_html(table_lines))
            continue
        blocks.append(f"<p>{escape(line)}</p>")
        index += 1
    return "\n".join(blocks)


def _markdown_table_to_html(lines: list[str]) -> str:
    header = _table_cells(lines[0])
    rows = [_table_cells(line) for line in lines[2:]]
    html_rows = [
        "<thead><tr>"
        + "".join(f"<th>{escape(cell)}</th>" for cell in header)
        + "</tr></thead>"
    ]
    html_rows.append(
        "<tbody>"
        + "".join(
            "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        + "</tbody>"
    )
    return "<table>" + "".join(html_rows) + "</table>"


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"
