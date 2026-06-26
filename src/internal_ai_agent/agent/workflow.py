from __future__ import annotations

from typing import Any

from internal_ai_agent.agent.schemas import AgentRunResult, ToolDecision
from internal_ai_agent.agent.tools import make_tool_decision
from internal_ai_agent.data.synthetic import build_runbooks
from internal_ai_agent.extraction.service import extract_and_route
from internal_ai_agent.observability.audit import (
    AuditEvent,
    audit_event,
    monitoring_snapshot,
    new_trace_id,
)
from internal_ai_agent.rag.baseline import answer_with_lexical
from internal_ai_agent.security.policy import assess_request, policy_refusal


def run_controlled_agent(
    question: str,
    *,
    ticket_text: str = "",
    retrieved_context_text: str = "",
    user_role: str = "operations_analyst",
    approval_granted: bool = False,
    trace_id: str | None = None,
) -> AgentRunResult:
    run_trace_id = trace_id or new_trace_id()
    audit_log: list[str] = []
    audit_events: list[AuditEvent] = []
    tool_decisions: list[ToolDecision] = []

    policy_decision = assess_request(f"{question} {ticket_text} {retrieved_context_text}")
    if policy_decision.blocked:
        audit_log.append("policy_blocked_before_tool_use")
        _append_event(
            audit_events,
            trace_id=run_trace_id,
            component="policy",
            event_type="risk_check",
            outcome="blocked",
            metadata={
                "reason": "policy_signal",
                "category": policy_decision.category,
                "severity": policy_decision.severity,
                "matched_signal": policy_decision.matched_signal,
            },
        )
        return AgentRunResult(
            trace_id=run_trace_id,
            question=question,
            answer=policy_refusal(),
            citations=[],
            abstained=True,
            tool_decisions=[],
            audit_log=audit_log,
            audit_events=audit_events,
            monitoring=_monitoring(run_trace_id, [], [], True),
            policy=policy_decision,
        )

    runbooks = [section.__dict__ for section in build_runbooks()]
    answer = answer_with_lexical(question, runbooks, user_role=user_role)
    tool_decisions.append(
        make_tool_decision(
            "search_runbook",
            {"query": question},
            rationale="Retrieve grounded synthetic runbook context before answering.",
        )
    )
    audit_log.append("search_runbook_executed")
    _append_tool_event(audit_events, run_trace_id, tool_decisions[-1])

    extraction = None
    routing = None
    if ticket_text:
        result = extract_and_route(ticket_text)
        extraction = result.extraction
        routing = result.routing
        tool_decisions.append(
            make_tool_decision(
                "extract_ticket",
                {"text": ticket_text},
                rationale="Extract structured ticket fields before deciding workflow actions.",
            )
        )
        audit_log.append("extract_ticket_executed")
        _append_tool_event(audit_events, run_trace_id, tool_decisions[-1])

        if extraction.ticket_id and routing.team != "unknown":
            _append_draft_and_route_tools(
                tool_decisions,
                audit_log,
                audit_events,
                trace_id=run_trace_id,
                ticket_id=extraction.ticket_id,
                team=routing.team,
                issue_category=extraction.issue_category or "unknown",
                approval_granted=approval_granted,
            )

    final_answer = _compose_answer(
        base_answer=answer.answer,
        routing_team=routing.team if routing else None,
        approval_pending=_approval_pending(tool_decisions),
        action_executed=_action_executed(tool_decisions),
    )
    return AgentRunResult(
        trace_id=run_trace_id,
        question=question,
        answer=final_answer,
        citations=answer.citations,
        abstained=answer.abstained,
        extraction=extraction,
        routing=routing,
        tool_decisions=tool_decisions,
        audit_log=audit_log,
        audit_events=audit_events,
        monitoring=_monitoring(run_trace_id, tool_decisions, answer.citations, answer.abstained),
        policy=policy_decision,
    )


def _append_draft_and_route_tools(
    tool_decisions: list[ToolDecision],
    audit_log: list[str],
    audit_events: list[AuditEvent],
    *,
    trace_id: str,
    ticket_id: str,
    team: str,
    issue_category: str,
    approval_granted: bool,
) -> None:
    draft_payload: dict[str, Any] = {
        "ticket_id": ticket_id,
        "team": team,
        "issue_category": issue_category,
    }
    tool_decisions.append(
        make_tool_decision(
            "draft_escalation_note",
            draft_payload,
            rationale="Prepare a non-side-effecting escalation note for analyst review.",
        )
    )
    audit_log.append("draft_escalation_note_executed")
    _append_tool_event(audit_events, trace_id, tool_decisions[-1])

    route_decision = make_tool_decision(
        "route_ticket_mock",
        {"ticket_id": ticket_id, "team": team},
        approval_granted=approval_granted,
        rationale="Route the synthetic ticket only after explicit human approval.",
    )
    tool_decisions.append(route_decision)
    if route_decision.executed:
        audit_log.append("route_ticket_mock_executed_after_approval")
    else:
        audit_log.append("route_ticket_mock_blocked_pending_approval")
    _append_tool_event(audit_events, trace_id, route_decision)


def _append_tool_event(
    audit_events: list[AuditEvent],
    trace_id: str,
    decision: ToolDecision,
) -> None:
    outcome = "executed" if decision.executed else decision.blocked_reason or "blocked"
    _append_event(
        audit_events,
        trace_id=trace_id,
        component="tool",
        event_type=decision.tool_name,
        outcome=outcome,
        metadata={
            "tool_type": decision.tool_type,
            "requires_approval": decision.requires_approval,
            "approval_granted": decision.approval_granted,
            "valid_schema": decision.valid_schema,
        },
    )


def _append_event(
    audit_events: list[AuditEvent],
    *,
    trace_id: str,
    component: str,
    event_type: str,
    outcome: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    audit_events.append(
        audit_event(
            trace_id=trace_id,
            sequence=len(audit_events) + 1,
            component=component,
            event_type=event_type,
            outcome=outcome,
            metadata=metadata,
        )
    )


def _monitoring(
    trace_id: str,
    tool_decisions: list[ToolDecision],
    citations: list[str],
    abstained: bool,
) -> dict[str, Any]:
    return monitoring_snapshot(
        trace_id=trace_id,
        tool_call_count=len(tool_decisions),
        approval_required_count=sum(1 for decision in tool_decisions if decision.requires_approval),
        blocked_tool_call_count=sum(
            1 for decision in tool_decisions if decision.requested and not decision.executed
        ),
        executed_tool_call_count=sum(1 for decision in tool_decisions if decision.executed),
        citation_count=len(citations),
        abstained=abstained,
    )


def _approval_pending(tool_decisions: list[ToolDecision]) -> bool:
    return any(
        decision.requires_approval
        and not decision.executed
        and decision.blocked_reason == "approval_required"
        for decision in tool_decisions
    )


def _action_executed(tool_decisions: list[ToolDecision]) -> bool:
    return any(
        decision.tool_type == "side_effect" and decision.executed for decision in tool_decisions
    )


def _compose_answer(
    *,
    base_answer: str,
    routing_team: str | None,
    approval_pending: bool,
    action_executed: bool,
) -> str:
    parts = [base_answer]
    if routing_team:
        parts.append(f"Structured routing recommends {routing_team}.")
    if approval_pending:
        parts.append("Mock ticket routing is prepared but waiting for human approval.")
    if action_executed:
        parts.append("Approved mock ticket routing was executed and logged.")
    return " ".join(parts)
