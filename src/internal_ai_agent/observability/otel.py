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


def _root_span(
    trace: dict[str, Any],
    trace_id: str,
    span_id: str,
    start_time_unix_nano: int,
    end_time_unix_nano: int,
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": None,
        "name": "agent.run",
        "kind": "INTERNAL",
        "start_time_unix_nano": start_time_unix_nano,
        "end_time_unix_nano": end_time_unix_nano,
        "status": {"code": "OK"},
        "attributes": {
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
    }


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
    return {
        "trace_id": trace_id,
        "span_id": _stable_hex(f"{trace['trace_id']}:{sequence}:{event['event_type']}", length=16),
        "parent_span_id": parent_span_id,
        "name": event["event_type"],
        "kind": "INTERNAL",
        "start_time_unix_nano": start_time_unix_nano,
        "end_time_unix_nano": start_time_unix_nano + SPAN_DURATION_NANO,
        "status": {"code": "OK"},
        "attributes": attributes,
    }


def _stable_hex(value: str, *, length: int) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:length]
