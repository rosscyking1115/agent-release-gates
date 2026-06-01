from __future__ import annotations

from typing import Any

from internal_ai_agent.agent.schemas import ToolDecision, ToolName, ToolType

TOOL_TYPES: dict[ToolName, ToolType] = {
    "search_runbook": "read_only",
    "extract_ticket": "read_only",
    "draft_escalation_note": "read_only",
    "route_ticket_mock": "side_effect",
    "create_followup_task_mock": "side_effect",
}

REQUIRED_FIELDS: dict[ToolName, set[str]] = {
    "search_runbook": {"query"},
    "extract_ticket": {"text"},
    "draft_escalation_note": {"ticket_id", "team", "issue_category"},
    "route_ticket_mock": {"ticket_id", "team"},
    "create_followup_task_mock": {"ticket_id", "owner", "reason"},
}


def make_tool_decision(
    tool_name: ToolName,
    payload: dict[str, Any],
    *,
    approval_granted: bool = False,
    rationale: str,
) -> ToolDecision:
    tool_type = TOOL_TYPES[tool_name]
    valid_schema = _valid_payload(tool_name, payload)
    requires_approval = tool_type == "side_effect"
    blocked_reason: str | None = None
    executed = valid_schema

    if requires_approval and not approval_granted:
        executed = False
        blocked_reason = "approval_required"
    elif not valid_schema:
        executed = False
        blocked_reason = "invalid_tool_payload"

    return ToolDecision(
        tool_name=tool_name,
        tool_type=tool_type,
        requested=True,
        requires_approval=requires_approval,
        approval_granted=approval_granted,
        executed=executed,
        valid_schema=valid_schema,
        rationale=rationale,
        blocked_reason=blocked_reason,
        output=_tool_output(tool_name, payload) if executed else {},
    )


def _valid_payload(tool_name: ToolName, payload: dict[str, Any]) -> bool:
    required = REQUIRED_FIELDS[tool_name]
    return all(str(payload.get(field, "")).strip() for field in required)


def _tool_output(tool_name: ToolName, payload: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "route_ticket_mock":
        return {
            "status": "mock_routed",
            "ticket_id": payload["ticket_id"],
            "team": payload["team"],
        }
    if tool_name == "create_followup_task_mock":
        return {
            "status": "mock_followup_created",
            "ticket_id": payload["ticket_id"],
            "owner": payload["owner"],
        }
    if tool_name == "draft_escalation_note":
        return {
            "status": "drafted",
            "note": (
                f"Draft note for {payload['ticket_id']}: route to {payload['team']} "
                f"for {payload['issue_category']} review."
            ),
        }
    if tool_name == "extract_ticket":
        return {"status": "extracted"}
    return {"status": "searched"}
