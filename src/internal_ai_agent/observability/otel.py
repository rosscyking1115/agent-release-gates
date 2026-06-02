from __future__ import annotations

from hashlib import sha256
from typing import Any

BASE_TIME_UNIX_NANO = 1_735_689_600_000_000_000
TRACE_GAP_NANO = 1_000_000_000
SPAN_GAP_NANO = 10_000_000
SPAN_DURATION_NANO = 5_000_000


def otel_spans_from_agent_traces(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for trace_index, trace in enumerate(traces):
        trace_id = _stable_hex(trace["trace_id"], length=32)
        root_span_id = _stable_hex(f"{trace['trace_id']}:root", length=16)
        trace_start = BASE_TIME_UNIX_NANO + trace_index * TRACE_GAP_NANO
        audit_events = trace.get("audit_events", [])
        trace_end = trace_start + (len(audit_events) + 1) * SPAN_GAP_NANO
        spans.append(_root_span(trace, trace_id, root_span_id, trace_start, trace_end))
        for event in audit_events:
            spans.append(_event_span(trace, event, trace_id, root_span_id, trace_start))
    return spans


def otel_spans_from_evaluation_run(
    *,
    dataset_counts: dict[str, int],
    retriever_comparison: dict[str, Any],
    extraction: dict[str, Any],
    security: dict[str, Any],
    agent: dict[str, Any],
) -> list[dict[str, Any]]:
    trace_id = _stable_hex("evaluation_run:observability:v1", length=32)
    root_span_id = _stable_hex("evaluation_run:root", length=16)
    trace_start = BASE_TIME_UNIX_NANO + 100 * TRACE_GAP_NANO
    child_specs = [
        (
            "data.generate",
            "OK",
            {
                "lab.component": "data",
                "dataset.runbook_count": dataset_counts["runbooks"],
                "dataset.ticket_count": dataset_counts["tickets"],
                "dataset.golden_case_count": dataset_counts["golden_cases"],
                "dataset.red_team_case_count": dataset_counts["red_team_cases"],
            },
        ),
        (
            "retriever.evaluate",
            "OK",
            {
                "lab.component": "retrieval",
                "eval.dataset": "golden_cases",
                "eval.case_count": retriever_comparison["case_count"],
                "retriever.system_count": len(retriever_comparison["systems"]),
                "retriever.best_system": _best_retriever_label(retriever_comparison),
                "retriever.max_citation_coverage": _max_metric(
                    retriever_comparison["systems"], "citation_coverage"
                ),
            },
        ),
        (
            "extraction.evaluate",
            "OK",
            {
                "lab.component": "extraction",
                "eval.dataset": extraction["dataset"],
                "eval.case_count": extraction["case_count"],
                "eval.schema_validity": extraction["metrics"]["schema_validity"],
                "eval.routing_team_accuracy": extraction["metrics"]["routing_team_accuracy"],
            },
        ),
        (
            "security.evaluate",
            "OK",
            {
                "lab.component": "security",
                "eval.dataset": security["dataset"],
                "eval.case_count": security["case_count"],
                "eval.improved_block_rate": security["metrics"]["improved_block_rate"],
                "eval.improved_safe_rate": security["metrics"]["improved_safe_rate"],
            },
        ),
        (
            "agent.evaluate",
            "OK",
            {
                "lab.component": "agent",
                "eval.dataset": agent["dataset"],
                "eval.case_count": agent["case_count"],
                "eval.side_effect_block_rate": agent["metrics"]["side_effect_block_rate"],
                "eval.approval_audit_rate": agent["metrics"]["approval_audit_rate"],
                "eval.agent_otel_span_count": agent["otel_span_count"],
            },
        ),
        (
            "api.report_export",
            "OK",
            {
                "lab.component": "api",
                "http.route.evaluation_markdown": "/reports/evaluation",
                "http.route.evaluation_html": "/reports/evaluation.html",
                "http.route.agent_otel_spans": "/reports/agent/otel-spans",
                "http.route.observability_otel_spans": "/reports/observability/otel-spans",
                "report.markdown_path": "reports/evaluation_report.md",
                "report.html_path": "reports/evaluation_report.html",
            },
        ),
    ]
    trace_end = trace_start + (len(child_specs) + 1) * SPAN_GAP_NANO
    spans = [
        _make_span(
            trace_id=trace_id,
            span_id=root_span_id,
            parent_span_id=None,
            name="evaluation.run",
            start_time_unix_nano=trace_start,
            end_time_unix_nano=trace_end,
            status_code="OK",
            attributes={
                "lab.trace_id": "evaluation_run",
                "lab.component": "evaluation",
                "eval.stage_count": len(child_specs),
            },
        )
    ]
    for sequence, (name, status_code, attributes) in enumerate(child_specs, start=1):
        span_start = trace_start + sequence * SPAN_GAP_NANO
        spans.append(
            _make_span(
                trace_id=trace_id,
                span_id=_stable_hex(f"evaluation_run:{sequence}:{name}", length=16),
                parent_span_id=root_span_id,
                name=name,
                start_time_unix_nano=span_start,
                end_time_unix_nano=span_start + SPAN_DURATION_NANO,
                status_code=status_code,
                attributes={
                    "lab.trace_id": "evaluation_run",
                    "eval.sequence": sequence,
                    **attributes,
                },
            )
        )
    return spans


def otel_spans_from_retriever_failures(
    cases_by_system: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for system_index, (system, cases) in enumerate(sorted(cases_by_system.items())):
        failed_cases = [case for case in cases if case.get("failure_reasons")]
        trace_label = f"retriever_failures_{_slug(system)}"
        trace_id = _stable_hex(trace_label, length=32)
        root_span_id = _stable_hex(f"{trace_label}:root", length=16)
        trace_start = BASE_TIME_UNIX_NANO + (200 + system_index) * TRACE_GAP_NANO
        trace_end = trace_start + (len(failed_cases) + 1) * SPAN_GAP_NANO
        spans.append(
            _make_span(
                trace_id=trace_id,
                span_id=root_span_id,
                parent_span_id=None,
                name="retriever.failure_analysis",
                start_time_unix_nano=trace_start,
                end_time_unix_nano=trace_end,
                status_code="OK",
                attributes={
                    "lab.trace_id": trace_label,
                    "lab.component": "retrieval",
                    "retriever.system": system,
                    "retriever.failed_case_count": len(failed_cases),
                },
            )
        )
        for sequence, case in enumerate(failed_cases, start=1):
            span_start = trace_start + sequence * SPAN_GAP_NANO
            spans.append(
                _make_span(
                    trace_id=trace_id,
                    span_id=_stable_hex(
                        f"{trace_label}:{sequence}:{case['case_id']}", length=16
                    ),
                    parent_span_id=root_span_id,
                    name="retriever.case_failure",
                    start_time_unix_nano=span_start,
                    end_time_unix_nano=span_start + SPAN_DURATION_NANO,
                    status_code="ERROR",
                    attributes={
                        "lab.trace_id": trace_label,
                        "lab.component": "retrieval",
                        "eval.sequence": sequence,
                        "eval.case_id": case["case_id"],
                        "eval.task_type": case.get("task_type", ""),
                        "eval.noise_type": case.get("noise_type", ""),
                        "retriever.system": system,
                        "retriever.failure_reasons": ", ".join(
                            case.get("failure_reasons", [])
                        ),
                        "retriever.retrieval_hit_at_3": case.get(
                            "retrieval_hit_at_3", False
                        ),
                        "retriever.expected_citation_ids": ", ".join(
                            case.get("expected_citation_ids", [])
                        ),
                        "retriever.predicted_citation_ids": ", ".join(
                            case.get("predicted_citation_ids", [])
                        ),
                        "retriever.retrieved_citation_ids": ", ".join(
                            case.get("retrieved_citation_ids", [])
                        ),
                        "retriever.top_candidate_scores": _candidate_score_summary(
                            case.get("retrieved_candidate_scores", [])
                        ),
                        "retriever.recommended_fix": case.get("recommended_fix", ""),
                    },
                )
            )
    return spans


def otel_spans_from_agent_approval_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trace_label = "agent_approval_cases"
    trace_id = _stable_hex(trace_label, length=32)
    root_span_id = _stable_hex(f"{trace_label}:root", length=16)
    trace_start = BASE_TIME_UNIX_NANO + 300 * TRACE_GAP_NANO
    trace_end = trace_start + (len(cases) + 1) * SPAN_GAP_NANO
    spans = [
        _make_span(
            trace_id=trace_id,
            span_id=root_span_id,
            parent_span_id=None,
            name="agent.approval_analysis",
            start_time_unix_nano=trace_start,
            end_time_unix_nano=trace_end,
            status_code="OK",
            attributes={
                "lab.trace_id": trace_label,
                "lab.component": "agent",
                "agent.case_count": len(cases),
                "agent.approval_required_count": _count_true(cases, "approval_required"),
                "agent.side_effect_blocked_count": _count_true(
                    cases, "side_effect_blocked_without_approval"
                ),
                "agent.approved_action_executed_count": _count_true(
                    cases, "approved_action_executed"
                ),
            },
        )
    ]
    for sequence, case in enumerate(cases, start=1):
        span_start = trace_start + sequence * SPAN_GAP_NANO
        status_code = "OK" if _approval_case_passed(case) else "ERROR"
        spans.append(
            _make_span(
                trace_id=trace_id,
                span_id=_stable_hex(f"{trace_label}:{sequence}:{case['ticket_id']}", length=16),
                parent_span_id=root_span_id,
                name="agent.approval_decision",
                start_time_unix_nano=span_start,
                end_time_unix_nano=span_start + SPAN_DURATION_NANO,
                status_code=status_code,
                attributes={
                    "lab.trace_id": trace_label,
                    "lab.component": "agent",
                    "eval.sequence": sequence,
                    "ticket.id": case["ticket_id"],
                    "agent.approval_required": case.get("approval_required", False),
                    "agent.side_effect_blocked_without_approval": case.get(
                        "side_effect_blocked_without_approval", False
                    ),
                    "agent.approved_action_executed": case.get(
                        "approved_action_executed", False
                    ),
                    "agent.approval_audited": case.get("approval_audited", False),
                    "agent.route_tool_team_match": case.get("route_tool_team_match", False),
                    "agent.valid_tool_calls": case.get("valid_tool_calls", False),
                    "agent.monitoring_snapshot_present": case.get(
                        "monitoring_snapshot_present", False
                    ),
                    "agent.trace_id_present": case.get("trace_id_present", False),
                    "agent.unnecessary_tool_call": case.get("unnecessary_tool_call", False),
                },
            )
        )
    return spans


def _root_span(
    trace: dict[str, Any],
    trace_id: str,
    span_id: str,
    start_time_unix_nano: int,
    end_time_unix_nano: int,
) -> dict[str, Any]:
    return _make_span(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=None,
        name="agent.run",
        start_time_unix_nano=start_time_unix_nano,
        end_time_unix_nano=end_time_unix_nano,
        status_code="OK",
        attributes={
            "lab.trace_id": trace["trace_id"],
            "ticket.id": trace["ticket_id"],
            "approval.granted": trace["approval_granted"],
            "agent.answer_abstained": trace["answer_abstained"],
            "agent.route_tool_outcome": trace["route_tool_outcome"],
            "agent.tool_call_count": trace["tool_call_count"],
            "agent.executed_tool_call_count": trace["executed_tool_call_count"],
            "agent.blocked_tool_call_count": trace["blocked_tool_call_count"],
            "agent.citation_count": trace["citation_count"],
        },
    )


def _event_span(
    trace: dict[str, Any],
    event: dict[str, Any],
    trace_id: str,
    parent_span_id: str,
    trace_start: int,
) -> dict[str, Any]:
    sequence = int(event["sequence"])
    start_time_unix_nano = trace_start + sequence * SPAN_GAP_NANO
    attributes = {
        "lab.trace_id": trace["trace_id"],
        "ticket.id": trace["ticket_id"],
        "audit.sequence": sequence,
        "audit.component": event["component"],
        "audit.event_type": event["event_type"],
        "audit.outcome": event["outcome"],
    }
    for key, value in event.get("metadata", {}).items():
        attributes[f"audit.metadata.{key}"] = value
    return _make_span(
        trace_id=trace_id,
        span_id=_stable_hex(f"{trace['trace_id']}:{sequence}:{event['event_type']}", length=16),
        parent_span_id=parent_span_id,
        name=event["event_type"],
        start_time_unix_nano=start_time_unix_nano,
        end_time_unix_nano=start_time_unix_nano + SPAN_DURATION_NANO,
        status_code="OK",
        attributes=attributes,
    )


def _make_span(
    *,
    trace_id: str,
    span_id: str,
    parent_span_id: str | None,
    name: str,
    start_time_unix_nano: int,
    end_time_unix_nano: int,
    status_code: str,
    attributes: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "name": name,
        "kind": "INTERNAL",
        "start_time_unix_nano": start_time_unix_nano,
        "end_time_unix_nano": end_time_unix_nano,
        "status": {"code": status_code},
        "attributes": attributes,
    }


def _best_retriever_label(report: dict[str, Any]) -> str:
    best = sorted(
        report["systems"],
        key=lambda system: (-system["citation_coverage"], system["failure_count"], system["label"]),
    )[0]
    return str(best["label"])


def _max_metric(systems: list[dict[str, Any]], metric: str) -> float:
    return max(float(system[metric]) for system in systems)


def _candidate_score_summary(candidates: object) -> str:
    if not isinstance(candidates, list):
        return ""
    summaries: list[str] = []
    for candidate in candidates[:3]:
        if not isinstance(candidate, dict):
            continue
        section_id = str(candidate.get("section_id", ""))
        score = candidate.get("score", "")
        summaries.append(f"{section_id}={score}")
    return "; ".join(summaries)


def _approval_case_passed(case: dict[str, Any]) -> bool:
    return (
        bool(case.get("approval_required"))
        and bool(case.get("side_effect_blocked_without_approval"))
        and bool(case.get("approved_action_executed"))
        and bool(case.get("approval_audited"))
        and bool(case.get("route_tool_team_match"))
        and bool(case.get("valid_tool_calls"))
        and bool(case.get("monitoring_snapshot_present"))
        and bool(case.get("trace_id_present"))
        and not bool(case.get("unnecessary_tool_call"))
    )


def _count_true(cases: list[dict[str, Any]], key: str) -> int:
    return sum(1 for case in cases if case.get(key))


def _slug(value: str) -> str:
    return "_".join(value.lower().replace("-", " ").split())


def _stable_hex(value: str, *, length: int) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:length]
