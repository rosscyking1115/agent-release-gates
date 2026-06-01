from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel


class AuditEvent(BaseModel):
    trace_id: str
    sequence: int
    component: str
    event_type: str
    outcome: str
    metadata: dict[str, Any] = {}


def new_trace_id() -> str:
    return f"trace_{uuid4().hex}"


def audit_event(
    *,
    trace_id: str,
    sequence: int,
    component: str,
    event_type: str,
    outcome: str,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    return AuditEvent(
        trace_id=trace_id,
        sequence=sequence,
        component=component,
        event_type=event_type,
        outcome=outcome,
        metadata=metadata or {},
    )


def monitoring_snapshot(
    *,
    trace_id: str,
    tool_call_count: int,
    approval_required_count: int,
    blocked_tool_call_count: int,
    executed_tool_call_count: int,
    citation_count: int,
    abstained: bool,
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "tool_call_count": tool_call_count,
        "approval_required_count": approval_required_count,
        "blocked_tool_call_count": blocked_tool_call_count,
        "executed_tool_call_count": executed_tool_call_count,
        "citation_count": citation_count,
        "abstained": abstained,
    }
