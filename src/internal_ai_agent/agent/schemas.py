from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from internal_ai_agent.extraction.schemas import RoutingDecision, TicketExtraction
from internal_ai_agent.observability.audit import AuditEvent
from internal_ai_agent.security.policy import PolicyDecision

ToolName = Literal[
    "search_runbook",
    "extract_ticket",
    "draft_escalation_note",
    "route_ticket_mock",
    "create_followup_task_mock",
]

ToolType = Literal["read_only", "side_effect"]


class ToolDecision(BaseModel):
    tool_name: ToolName
    tool_type: ToolType
    requested: bool
    requires_approval: bool
    approval_granted: bool
    executed: bool
    valid_schema: bool
    rationale: str
    blocked_reason: str | None = None
    output: dict[str, Any] = {}


class AgentRunResult(BaseModel):
    trace_id: str
    question: str
    answer: str
    citations: list[str]
    abstained: bool
    extraction: TicketExtraction | None = None
    routing: RoutingDecision | None = None
    tool_decisions: list[ToolDecision]
    audit_log: list[str]
    audit_events: list[AuditEvent]
    monitoring: dict[str, Any]
    policy: PolicyDecision
