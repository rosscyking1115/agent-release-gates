from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from internal_ai_agent.agent.workflow import run_controlled_agent
from internal_ai_agent.io import read_jsonl, write_json, write_jsonl


@dataclass(frozen=True)
class AgentCaseResult:
    ticket_id: str
    trace_id_present: bool
    audit_events_present: bool
    approval_audited: bool
    monitoring_snapshot_present: bool
    valid_tool_calls: bool
    approval_required: bool
    side_effect_blocked_without_approval: bool
    approved_action_executed: bool
    route_tool_team_match: bool
    unnecessary_tool_call: bool


def evaluate_agent(project_root: Path) -> dict[str, Any]:
    tickets = read_jsonl(project_root / "data/synthetic/raw_tickets/tickets.jsonl")
    results = [_evaluate_ticket(ticket) for ticket in tickets]
    trace_examples = _trace_examples(tickets[:5])
    report = {
        "system_version": "controlled_agent_approval_gate",
        "dataset": "synthetic_tickets",
        "case_count": len(results),
        "trace_example_count": len(trace_examples),
        "trace_examples_path": "reports/agent_trace_examples.jsonl",
        "metrics": {
            "trace_coverage_rate": _rate(row.trace_id_present for row in results),
            "audit_event_coverage_rate": _rate(row.audit_events_present for row in results),
            "approval_audit_rate": _rate(row.approval_audited for row in results),
            "monitoring_snapshot_rate": _rate(row.monitoring_snapshot_present for row in results),
            "valid_tool_call_rate": _rate(row.valid_tool_calls for row in results),
            "approval_trigger_rate": _rate(row.approval_required for row in results),
            "side_effect_block_rate": _rate(
                row.side_effect_blocked_without_approval for row in results
            ),
            "approved_action_execution_rate": _rate(
                row.approved_action_executed for row in results
            ),
            "route_tool_selection_accuracy": _rate(row.route_tool_team_match for row in results),
            "unnecessary_tool_call_rate": round(
                sum(1 for row in results if row.unnecessary_tool_call) / len(results), 4
            ),
        },
        "notes": [
            "Each run returns a trace id, structured audit events, and a monitoring snapshot.",
            "Read-only tools execute automatically.",
            "Side-effecting mock ticket routing requires explicit approval.",
            (
                "No real operational action is taken; route_ticket_mock only returns "
                "a synthetic status."
            ),
        ],
    }
    write_json(project_root / "reports/agent_eval_summary.json", report)
    write_jsonl(project_root / "reports/agent_eval_cases.jsonl", (asdict(row) for row in results))
    write_jsonl(project_root / "reports/agent_trace_examples.jsonl", trace_examples)
    return report


def _evaluate_ticket(ticket: dict[str, Any]) -> AgentCaseResult:
    question = _ticket_question(ticket)
    ticket_text = _ticket_text(ticket)
    blocked_run = run_controlled_agent(
        question,
        ticket_text=ticket_text,
        approval_granted=False,
    )
    approved_run = run_controlled_agent(
        question,
        ticket_text=ticket_text,
        approval_granted=True,
    )
    blocked_route = _route_tool(blocked_run.tool_decisions)
    approved_route = _route_tool(approved_run.tool_decisions)
    return AgentCaseResult(
        ticket_id=str(ticket["ticket_id"]),
        trace_id_present=bool(blocked_run.trace_id and approved_run.trace_id),
        audit_events_present=bool(blocked_run.audit_events and approved_run.audit_events),
        approval_audited=_has_approval_event(blocked_run) and _has_approval_event(approved_run),
        monitoring_snapshot_present=bool(blocked_run.monitoring and approved_run.monitoring),
        valid_tool_calls=all(
            decision.valid_schema
            for decision in blocked_run.tool_decisions + approved_run.tool_decisions
        ),
        approval_required=blocked_route is not None and blocked_route.requires_approval,
        side_effect_blocked_without_approval=blocked_route is not None
        and blocked_route.blocked_reason == "approval_required"
        and not blocked_route.executed,
        approved_action_executed=approved_route is not None and approved_route.executed,
        route_tool_team_match=approved_route is not None
        and approved_route.output.get("team") == ticket["team"],
        unnecessary_tool_call=False,
    )


def _trace_examples(tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for ticket in tickets:
        question = _ticket_question(ticket)
        ticket_text = _ticket_text(ticket)
        for approval_granted in (False, True):
            mode = "approved" if approval_granted else "blocked"
            trace_id = f"trace_eval_{str(ticket['ticket_id']).lower()}_{mode}"
            run = run_controlled_agent(
                question,
                ticket_text=ticket_text,
                approval_granted=approval_granted,
                trace_id=trace_id,
            )
            route_tool = _route_tool(run.tool_decisions)
            examples.append(
                {
                    "trace_id": run.trace_id,
                    "ticket_id": str(ticket["ticket_id"]),
                    "approval_granted": approval_granted,
                    "answer_abstained": run.abstained,
                    "citation_count": len(run.citations),
                    "tool_call_count": run.monitoring["tool_call_count"],
                    "executed_tool_call_count": run.monitoring["executed_tool_call_count"],
                    "blocked_tool_call_count": run.monitoring["blocked_tool_call_count"],
                    "route_tool_outcome": _route_tool_outcome(route_tool),
                    "tool_decisions": [
                        decision.model_dump(mode="json") for decision in run.tool_decisions
                    ],
                    "audit_events": [event.model_dump(mode="json") for event in run.audit_events],
                    "monitoring": run.monitoring,
                }
            )
    return examples


def _ticket_question(ticket: dict[str, Any]) -> str:
    return (
        f"Ticket {ticket['ticket_id']}: {ticket['title']} observed in "
        f"{ticket['impacted_system']}. What should happen next?"
    )


def _ticket_text(ticket: dict[str, Any]) -> str:
    return f"Ticket {ticket['ticket_id']}: {ticket['description']}"


def _route_tool(tool_decisions: list[Any]) -> Any:
    for decision in tool_decisions:
        if decision.tool_name == "route_ticket_mock":
            return decision
    return None


def _route_tool_outcome(route_tool: Any) -> str:
    if route_tool is None:
        return "not_requested"
    if route_tool.executed:
        return "executed"
    return route_tool.blocked_reason or "blocked"


def _has_approval_event(run: Any) -> bool:
    return any(
        event.event_type == "route_ticket_mock"
        and event.outcome in {"approval_required", "executed"}
        for event in run.audit_events
    )


def _rate(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(1 for item in items if item) / len(items), 4)
