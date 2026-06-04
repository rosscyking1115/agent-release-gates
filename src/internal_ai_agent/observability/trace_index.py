from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json


def build_trace_index(spans: list[dict[str, Any]]) -> dict[str, Any]:
    traces = _trace_rows(spans)
    components = _component_rows(spans)
    error_spans = _error_span_rows(spans)
    query_summaries = _query_summaries(spans)
    return {
        "index_type": "local_observability_trace_index",
        "span_count": len(spans),
        "trace_count": len(traces),
        "error_span_count": len(error_spans),
        "component_count": len(components),
        "components": components,
        "queries": query_summaries,
        "error_spans": error_spans[:50],
        "traces": traces,
    }


def write_trace_index(project_root: Path) -> dict[str, Any]:
    spans = read_jsonl(project_root / "reports/observability_otel_spans.jsonl")
    index = build_trace_index(spans)
    write_json(project_root / "reports/observability_trace_index.json", index)
    return index


def _trace_rows(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    spans_by_trace: dict[str, list[dict[str, Any]]] = {}
    for span in spans:
        spans_by_trace.setdefault(str(span["trace_id"]), []).append(span)

    rows: list[dict[str, Any]] = []
    for trace_id, trace_spans in spans_by_trace.items():
        sorted_spans = sorted(
            trace_spans,
            key=lambda span: (int(span["start_time_unix_nano"]), str(span["span_id"])),
        )
        root = next(
            (span for span in sorted_spans if span.get("parent_span_id") is None),
            sorted_spans[0],
        )
        start_ns = min(int(span["start_time_unix_nano"]) for span in sorted_spans)
        end_ns = max(int(span["end_time_unix_nano"]) for span in sorted_spans)
        error_spans = [_span for _span in sorted_spans if _status_code(_span) == "ERROR"]
        components = sorted({_component(span) for span in sorted_spans})
        rows.append(
            {
                "trace_id": trace_id,
                "trace_label": _trace_label(root, trace_id),
                "root_span_name": str(root["name"]),
                "component": _component(root),
                "components": components,
                "span_count": len(sorted_spans),
                "error_span_count": len(error_spans),
                "start_time_unix_nano": start_ns,
                "end_time_unix_nano": end_ns,
                "duration_ms": round((end_ns - start_ns) / 1_000_000, 3),
                "first_error_span": str(error_spans[0]["name"]) if error_spans else "",
                "first_error_case_id": _case_id(error_spans[0]) if error_spans else "",
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            -int(row["error_span_count"]),
            -int(row["span_count"]),
            str(row["trace_label"]),
        ),
    )


def _component_rows(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    components: dict[str, dict[str, int]] = {}
    for span in spans:
        component = _component(span)
        row = components.setdefault(
            component,
            {"span_count": 0, "root_span_count": 0, "error_span_count": 0},
        )
        row["span_count"] += 1
        if span.get("parent_span_id") is None:
            row["root_span_count"] += 1
        if _status_code(span) == "ERROR":
            row["error_span_count"] += 1

    return [
        {
            "component": component,
            "span_count": values["span_count"],
            "root_span_count": values["root_span_count"],
            "error_span_count": values["error_span_count"],
        }
        for component, values in sorted(
            components.items(), key=lambda item: (-item[1]["span_count"], item[0])
        )
    ]


def _error_span_rows(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for span in spans:
        if _status_code(span) != "ERROR":
            continue
        attributes = span.get("attributes", {})
        rows.append(
            {
                "trace_id": span["trace_id"],
                "trace_label": _trace_label(span, str(span["trace_id"])[:12]),
                "span_id": span["span_id"],
                "name": span["name"],
                "component": _component(span),
                "case_id": _case_id(span),
                "ticket_id": attributes.get("ticket.id", ""),
                "failure_reasons": attributes.get("retriever.failure_reasons", ""),
                "http_route": attributes.get("http.route", ""),
                "http_status_code": attributes.get("http.status_code", ""),
                "start_time_unix_nano": span["start_time_unix_nano"],
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row["component"]),
            str(row["trace_label"]),
            int(row["start_time_unix_nano"]),
        ),
    )


def _query_summaries(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    query_specs = [
        (
            "error_spans",
            "All spans with ERROR status",
            lambda span: _status_code(span) == "ERROR",
        ),
        (
            "retriever_failures",
            "Retriever case-failure spans",
            lambda span: str(span.get("name", "")) == "retriever.case_failure",
        ),
        (
            "api_error_cases",
            "Expected API validation and route errors",
            lambda span: str(span.get("name", "")) == "api.error_case",
        ),
        (
            "approval_decisions",
            "Agent approval-decision spans",
            lambda span: str(span.get("name", "")) == "agent.approval_decision",
        ),
        (
            "ranking_cases",
            "Retriever ranking-detail spans",
            lambda span: str(span.get("name", "")) == "retriever.ranking_case",
        ),
    ]
    return [
        {
            "query": name,
            "description": description,
            "span_count": sum(1 for span in spans if predicate(span)),
        }
        for name, description, predicate in query_specs
    ]


def _status_code(span: dict[str, Any]) -> str:
    return str(span.get("status", {}).get("code", ""))


def _component(span: dict[str, Any]) -> str:
    component = str(span.get("attributes", {}).get("lab.component", "agent"))
    return component or "agent"


def _trace_label(span: dict[str, Any], fallback: str) -> str:
    label = str(span.get("attributes", {}).get("lab.trace_id", ""))
    return label or fallback


def _case_id(span: dict[str, Any]) -> str:
    attributes = span.get("attributes", {})
    return str(attributes.get("eval.case_id", attributes.get("ticket.id", "")))
