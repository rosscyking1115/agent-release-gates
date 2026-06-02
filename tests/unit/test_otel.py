from internal_ai_agent.observability.otel import (
    otel_spans_from_agent_traces,
    otel_spans_from_evaluation_run,
)


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


def test_otel_spans_from_evaluation_run_exports_workflow_spans() -> None:
    spans = otel_spans_from_evaluation_run(
        dataset_counts={
            "runbooks": 24,
            "tickets": 180,
            "golden_cases": 264,
            "red_team_cases": 40,
        },
        retriever_comparison={
            "case_count": 264,
            "systems": [
                {
                    "label": "Baseline",
                    "citation_coverage": 0.2,
                    "failure_count": 10,
                },
                {
                    "label": "Hybrid",
                    "citation_coverage": 1.0,
                    "failure_count": 0,
                },
            ],
        },
        extraction={
            "dataset": "synthetic_tickets",
            "case_count": 180,
            "metrics": {"schema_validity": 1.0, "routing_team_accuracy": 1.0},
        },
        security={
            "dataset": "red_team_cases",
            "case_count": 40,
            "metrics": {"improved_block_rate": 1.0, "improved_safe_rate": 1.0},
        },
        agent={
            "dataset": "synthetic_tickets",
            "case_count": 180,
            "otel_span_count": 50,
            "metrics": {"side_effect_block_rate": 1.0, "approval_audit_rate": 1.0},
        },
    )

    assert len(spans) == 7
    assert spans[0]["name"] == "evaluation.run"
    assert spans[0]["parent_span_id"] is None
    assert {span["name"] for span in spans[1:]} == {
        "data.generate",
        "retriever.evaluate",
        "extraction.evaluate",
        "security.evaluate",
        "agent.evaluate",
        "api.report_export",
    }
    retriever_span = next(span for span in spans if span["name"] == "retriever.evaluate")
    assert retriever_span["parent_span_id"] == spans[0]["span_id"]
    assert retriever_span["attributes"]["lab.component"] == "retrieval"
    assert retriever_span["attributes"]["retriever.best_system"] == "Hybrid"
    assert retriever_span["attributes"]["retriever.max_citation_coverage"] == 1.0
