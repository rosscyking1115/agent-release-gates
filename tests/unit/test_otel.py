from internal_ai_agent.observability.otel import otel_spans_from_agent_traces


def test_otel_spans_from_agent_traces_exports_root_and_event_spans() -> None:
    spans = otel_spans_from_agent_traces(
        [
            {
                "trace_id": "trace_eval_tck-0001_blocked",
                "ticket_id": "TCK-0001",
                "approval_granted": False,
                "answer_abstained": False,
                "citation_count": 1,
                "tool_call_count": 4,
                "executed_tool_call_count": 3,
                "blocked_tool_call_count": 1,
                "route_tool_outcome": "approval_required",
                "audit_events": [
                    {
                        "trace_id": "trace_eval_tck-0001_blocked",
                        "sequence": 1,
                        "component": "tool",
                        "event_type": "search_runbook",
                        "outcome": "executed",
                        "metadata": {"tool_type": "read_only"},
                    },
                    {
                        "trace_id": "trace_eval_tck-0001_blocked",
                        "sequence": 2,
                        "component": "tool",
                        "event_type": "route_ticket_mock",
                        "outcome": "approval_required",
                        "metadata": {"requires_approval": True},
                    },
                ],
            }
        ]
    )

    assert len(spans) == 3
    assert spans[0]["name"] == "agent.run"
    assert spans[0]["parent_span_id"] is None
    assert len(spans[0]["trace_id"]) == 32
    assert len(spans[0]["span_id"]) == 16
    assert spans[0]["attributes"]["lab.trace_id"] == "trace_eval_tck-0001_blocked"
    assert spans[0]["attributes"]["agent.route_tool_outcome"] == "approval_required"
    assert spans[2]["name"] == "route_ticket_mock"
    assert spans[2]["parent_span_id"] == spans[0]["span_id"]
    assert spans[2]["attributes"]["audit.outcome"] == "approval_required"
    assert spans[2]["attributes"]["audit.metadata.requires_approval"] is True
