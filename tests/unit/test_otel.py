from internal_ai_agent.observability.otel import (
    otel_spans_from_agent_traces,
    otel_spans_from_evaluation_run,
    otel_spans_from_retriever_failures,
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


def test_otel_spans_from_retriever_failures_exports_case_level_spans() -> None:
    spans = otel_spans_from_retriever_failures(
        {
            "Vector": [
                {
                    "case_id": "MANUAL-CHAT-001",
                    "task_type": "manual_challenge_next_action",
                    "noise_type": "manual_chat_fragment",
                    "failure_reasons": ["missing_or_wrong_citation", "wrong_team"],
                    "retrieval_hit_at_3": True,
                    "expected_citation_ids": ["RB-CLIENT_ONBOARDING-01"],
                    "predicted_citation_ids": ["RB-TRADE_SUPPORT-06"],
                    "retrieved_citation_ids": [
                        "RB-TRADE_SUPPORT-06",
                        "RB-CLIENT_ONBOARDING-01",
                    ],
                    "retrieved_candidate_scores": [
                        {"section_id": "RB-TRADE_SUPPORT-06", "score": 24.76},
                        {"section_id": "RB-CLIENT_ONBOARDING-01", "score": 22.91},
                    ],
                    "recommended_fix": "Add stronger metadata filters.",
                },
                {
                    "case_id": "PASS-001",
                    "failure_reasons": [],
                },
            ]
        }
    )

    assert len(spans) == 2
    assert spans[0]["name"] == "retriever.failure_analysis"
    assert spans[0]["status"]["code"] == "OK"
    assert spans[0]["attributes"]["retriever.failed_case_count"] == 1
    assert spans[1]["name"] == "retriever.case_failure"
    assert spans[1]["status"]["code"] == "ERROR"
    assert spans[1]["parent_span_id"] == spans[0]["span_id"]
    assert spans[1]["attributes"]["eval.case_id"] == "MANUAL-CHAT-001"
    assert spans[1]["attributes"]["retriever.system"] == "Vector"
    assert spans[1]["attributes"]["retriever.retrieval_hit_at_3"] is True
    assert spans[1]["attributes"]["retriever.top_candidate_scores"] == (
        "RB-TRADE_SUPPORT-06=24.76; RB-CLIENT_ONBOARDING-01=22.91"
    )
