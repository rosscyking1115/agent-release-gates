from internal_ai_agent.dashboard.data import (
    agent_metric_rows,
    agent_otel_span_rows,
    agent_otel_summary,
    agent_otel_timeline_rows,
    agent_trace_rows,
    case_mix,
    error_analysis_rows,
    extraction_metric_rows,
    failed_case_rows,
    failure_example_rows,
    failure_reason_rows,
    load_public_report,
    load_public_report_html,
    metric_rows,
    retriever_experiment_rows,
    retriever_failure_example_rows,
    retriever_failure_overview,
    retriever_snapshot_rows,
    security_metric_rows,
    security_risk_breakdown_rows,
)


def test_metric_rows_formats_before_after_values() -> None:
    comparison = {
        "metrics": {
            "retrieval_hit_rate_at_3": {"baseline": 0.4, "improved": 0.8, "delta": 0.4},
            "citation_coverage": {"baseline": 0.2, "improved": 0.7, "delta": 0.5},
            "issue_category_accuracy": {"baseline": 0.1, "improved": 0.6, "delta": 0.5},
            "team_accuracy": {"baseline": 0.9, "improved": 1.0, "delta": 0.1},
            "next_action_accuracy": {"baseline": 0.3, "improved": 0.75, "delta": 0.45},
            "abstention_rate": {"baseline": 0.0, "improved": 0.2, "delta": 0.2},
            "abstention_accuracy": {"baseline": 0.8, "improved": 1.0, "delta": 0.2},
        }
    }

    rows = metric_rows(comparison)

    assert rows[0]["label"] == "Retrieval hit rate@3"
    assert rows[0]["baseline_pct"] == "40.00%"
    assert rows[0]["delta_pct"] == "+40.00%"


def test_retriever_experiment_rows_formats_multiple_systems() -> None:
    rows = retriever_experiment_rows(
        {
            "systems": [
                {
                    "label": "Baseline",
                    "retrieval_hit_rate_at_3": 0.4,
                    "citation_coverage": 0.2,
                    "issue_category_accuracy": 0.2,
                    "next_action_accuracy": 0.2,
                    "abstention_accuracy": 0.8,
                    "failure_count": 10,
                },
                {
                    "label": "Hybrid",
                    "retrieval_hit_rate_at_3": 1.0,
                    "citation_coverage": 1.0,
                    "issue_category_accuracy": 1.0,
                    "next_action_accuracy": 1.0,
                    "abstention_accuracy": 1.0,
                    "failure_count": 0,
                },
            ]
        }
    )

    assert rows[1]["system"] == "Hybrid"
    assert rows[1]["citation_coverage_pct"] == "100.00%"


def test_retriever_snapshot_rows_formats_regression_deltas() -> None:
    rows = retriever_snapshot_rows(
        {
            "snapshots": [
                {
                    "snapshot_id": "001_baseline",
                    "label": "Baseline",
                    "citation_coverage": 0.2,
                    "failure_count": 10,
                    "citation_delta_from_previous": None,
                    "failure_delta_from_previous": None,
                    "regression": False,
                    "regression_reasons": [],
                },
                {
                    "snapshot_id": "002_vector",
                    "label": "Vector",
                    "citation_coverage": 0.19,
                    "failure_count": 12,
                    "citation_delta_from_previous": -0.01,
                    "failure_delta_from_previous": 2,
                    "regression": True,
                    "regression_reasons": [
                        "citation_coverage_decreased",
                        "failed_case_count_increased",
                    ],
                },
            ]
        }
    )

    assert rows[0]["citation_delta_pct"] == ""
    assert rows[1]["citation_delta_pct"] == "-1.00%"
    assert rows[1]["failure_delta"] == "+2"
    assert rows[1]["regression_reasons"] == (
        "citation_coverage_decreased, failed_case_count_increased"
    )


def test_failed_case_rows_flags_wrong_citation_or_abstention() -> None:
    rows = [
        {
            "abstention_correct": True,
            "expected_abstain": False,
            "citation_match": True,
            "next_action_match": True,
        },
        {
            "abstention_correct": True,
            "expected_abstain": False,
            "citation_match": False,
            "next_action_match": True,
        },
    ]

    assert failed_case_rows(rows) == [rows[1]]


def test_case_mix_counts_expected_abstentions_and_failures() -> None:
    rows = [
        {
            "abstention_correct": True,
            "expected_abstain": True,
            "citation_match": False,
            "next_action_match": False,
        },
        {
            "abstention_correct": False,
            "expected_abstain": False,
            "citation_match": False,
            "next_action_match": False,
        },
    ]

    assert case_mix(rows) == {
        "answerable_cases": 1,
        "expected_abstentions": 1,
        "failed_cases": 1,
    }


def test_extraction_metric_rows_formats_scores() -> None:
    rows = extraction_metric_rows(
        {
            "metrics": {
                "schema_validity": 1.0,
                "routing_team_accuracy": 0.75,
            }
        }
    )

    assert rows[0]["label"] == "Schema Validity"
    assert rows[0]["value_pct"] == "100.00%"


def test_error_analysis_rows_format_grouped_metrics() -> None:
    rows = error_analysis_rows(
        {
            "by_noise_type": {
                "abbreviated_ticket": {
                    "case_count": 8,
                    "failure_count": 2,
                    "citation_coverage": 0.75,
                    "abstention_accuracy": 1.0,
                    "next_action_accuracy": 0.75,
                }
            }
        },
        "by_noise_type",
    )

    assert rows[0]["group"] == "abbreviated_ticket"
    assert rows[0]["citation_coverage_pct"] == "75.00%"


def test_failure_reason_rows_format_counts() -> None:
    rows = failure_reason_rows({"failure_reasons": {"wrong_next_action": 3}})

    assert rows == [{"reason": "wrong_next_action", "count": 3}]


def test_failure_example_rows_format_diagnostics() -> None:
    rows = failure_example_rows(
        {
            "failure_examples": [
                {
                    "case_id": "CASE-1",
                    "noise_type": "paraphrase",
                    "failure_reasons": ["wrong_issue_category"],
                    "expected_issue_category": "duplicate_record_cluster",
                    "predicted_issue_category": "stale_reference_data",
                    "expected_citation_ids": ["RB-1"],
                    "predicted_citation_ids": ["RB-2"],
                    "diagnostic": "Wrong procedure.",
                    "recommended_fix": "Add semantic retrieval.",
                }
            ]
        }
    )

    assert rows[0]["case_id"] == "CASE-1"
    assert rows[0]["failure_reasons"] == "wrong_issue_category"
    assert rows[0]["recommended_fix"] == "Add semantic retrieval."


def test_retriever_failure_overview_flags_retrieved_but_not_cited() -> None:
    cases_by_system = {
        "Vector": [
            {
                "abstention_correct": True,
                "expected_abstain": False,
                "citation_match": False,
                "next_action_match": False,
                "retrieval_hit_at_3": True,
                "failure_reasons": ["missing_or_wrong_citation"],
            }
        ]
    }

    rows = retriever_failure_overview(cases_by_system)

    assert rows == [
        {
            "system": "Vector",
            "failed_cases": 1,
            "retrieved_but_not_cited": 1,
            "abstention_mismatches": 0,
            "top_failure_reason": "missing_or_wrong_citation (1)",
        }
    ]


def test_retriever_failure_example_rows_formats_case_level_diagnostics() -> None:
    cases_by_system = {
        "Vector": [
            {
                "abstention_correct": True,
                "expected_abstain": False,
                "citation_match": False,
                "next_action_match": False,
                "retrieval_hit_at_3": True,
                "case_id": "CASE-1",
                "noise_type": "missing_metadata",
                "failure_reasons": ["missing_or_wrong_citation"],
                "expected_citation_ids": ["RB-1"],
                "predicted_citation_ids": ["RB-2"],
                "retrieved_citation_ids": ["RB-2", "RB-1"],
                "retrieved_candidate_scores": [
                    {
                        "section_id": "RB-2",
                        "score": 12.5,
                        "score_breakdown": {"vector": 10.0, "alias": 2.5},
                    },
                    {
                        "section_id": "RB-1",
                        "score": 11.0,
                        "score_breakdown": {"vector": 9.0, "current_evidence": 2.0},
                    },
                ],
                "diagnostic": "Expected section retrieved but not selected.",
                "recommended_fix": "Improve reranking.",
            }
        ]
    }

    rows = retriever_failure_example_rows(cases_by_system)

    assert rows[0]["system"] == "Vector"
    assert rows[0]["retrieved_but_not_cited"] is True
    assert rows[0]["retrieved_citations"] == "RB-2, RB-1"
    assert rows[0]["score_explanation"] == (
        "RB-2 total=12.5 (vector=10.0, alias=2.5); "
        "RB-1 total=11.0 (vector=9.0, current_evidence=2.0)"
    )


def test_security_metric_rows_formats_before_after_scores() -> None:
    rows = security_metric_rows(
        {
            "metrics": {
                "baseline_block_rate": 0.0,
                "improved_block_rate": 1.0,
                "baseline_safe_rate": 0.25,
                "improved_safe_rate": 0.75,
                "baseline_weighted_safe_rate": 0.2,
                "improved_weighted_safe_rate": 0.8,
            }
        }
    )

    assert rows[0]["label"] == "Policy block rate"
    assert rows[0]["baseline_pct"] == "0.00%"
    assert rows[0]["improved_pct"] == "100.00%"
    assert rows[2]["label"] == "Weighted safe response rate"
    assert rows[2]["improved_pct"] == "80.00%"


def test_security_risk_breakdown_rows_formats_group_scores() -> None:
    rows = security_risk_breakdown_rows(
        {
            "by_risk_type": {
                "prompt_injection": {
                    "case_count": 4,
                    "max_risk_severity": "high",
                    "block_rate": 1.0,
                    "safe_rate": 1.0,
                    "weighted_safe_rate": 1.0,
                    "residual_risk_score": 0,
                }
            }
        },
        "by_risk_type",
    )

    assert rows == [
        {
            "group": "prompt_injection",
            "case_count": 4,
            "max_risk_severity": "high",
            "block_rate": 1.0,
            "safe_rate": 1.0,
            "weighted_safe_rate": 1.0,
            "residual_risk_score": 0,
            "block_rate_pct": "100.00%",
            "safe_rate_pct": "100.00%",
            "weighted_safe_rate_pct": "100.00%",
        }
    ]


def test_agent_metric_rows_formats_scores() -> None:
    rows = agent_metric_rows(
        {
            "metrics": {
                "trace_coverage_rate": 1.0,
                "valid_tool_call_rate": 1.0,
                "side_effect_block_rate": 1.0,
                "unnecessary_tool_call_rate": 0.0,
            }
        }
    )

    assert rows[0]["label"] == "Trace coverage rate"
    assert rows[0]["value_pct"] == "100.00%"


def test_agent_trace_rows_formats_trace_examples() -> None:
    rows = agent_trace_rows(
        [
            {
                "trace_id": "trace_eval_tck_1_blocked",
                "ticket_id": "TCK-1",
                "approval_granted": False,
                "route_tool_outcome": "approval_required",
                "tool_call_count": 4,
                "executed_tool_call_count": 3,
                "blocked_tool_call_count": 1,
                "audit_events": [{"event_type": "route_ticket_mock"}],
            }
        ]
    )

    assert rows == [
        {
            "trace_id": "trace_eval_tck_1_blocked",
            "ticket_id": "TCK-1",
            "approval_granted": False,
            "route_tool_outcome": "approval_required",
            "tool_call_count": 4,
            "executed_tool_call_count": 3,
            "blocked_tool_call_count": 1,
            "audit_event_count": 1,
        }
    ]


def test_agent_otel_rows_and_summary_format_span_export() -> None:
    spans = [
        {
            "trace_id": "0" * 32,
            "span_id": "1" * 16,
            "parent_span_id": None,
            "name": "agent.run",
            "start_time_unix_nano": 1,
            "end_time_unix_nano": 2,
            "status": {"code": "OK"},
            "attributes": {"ticket.id": "TCK-1"},
        },
        {
            "trace_id": "0" * 32,
            "span_id": "2" * 16,
            "parent_span_id": "1" * 16,
            "name": "route_ticket_mock",
            "start_time_unix_nano": 3,
            "end_time_unix_nano": 4,
            "status": {"code": "OK"},
            "attributes": {
                "ticket.id": "TCK-1",
                "audit.component": "tool",
                "audit.outcome": "approval_required",
            },
        },
    ]

    assert agent_otel_summary(spans) == {
        "span_count": 2,
        "trace_count": 1,
        "root_span_count": 1,
        "child_span_count": 1,
        "tool_span_count": 1,
    }
    assert agent_otel_span_rows(spans)[1] == {
        "trace_id": "0" * 32,
        "span_id": "2" * 16,
        "parent_span_id": "1" * 16,
        "name": "route_ticket_mock",
        "component": "",
        "ticket_id": "TCK-1",
        "outcome": "approval_required",
        "start_time_unix_nano": 3,
        "end_time_unix_nano": 4,
    }


def test_agent_otel_timeline_rows_normalize_span_timing_by_trace() -> None:
    spans = [
        {
            "trace_id": "a" * 32,
            "span_id": "1" * 16,
            "parent_span_id": None,
            "name": "agent.run",
            "start_time_unix_nano": 1_000_000,
            "end_time_unix_nano": 9_000_000,
            "status": {"code": "OK"},
            "attributes": {
                "lab.trace_id": "trace_eval_tck_1_blocked",
                "ticket.id": "TCK-1",
                "agent.route_tool_outcome": "approval_required",
            },
        },
        {
            "trace_id": "a" * 32,
            "span_id": "2" * 16,
            "parent_span_id": "1" * 16,
            "name": "route_ticket_mock",
            "start_time_unix_nano": 4_000_000,
            "end_time_unix_nano": 6_500_000,
            "status": {"code": "OK"},
            "attributes": {
                "lab.trace_id": "trace_eval_tck_1_blocked",
                "ticket.id": "TCK-1",
                "audit.outcome": "blocked_pending_approval",
            },
        },
    ]

    rows = agent_otel_timeline_rows(spans)

    assert rows[0]["trace_label"] == "trace_eval_tck_1_blocked"
    assert rows[0]["start_ms"] == 0.0
    assert rows[0]["duration_ms"] == 8.0
    assert rows[0]["outcome"] == "approval_required"
    assert rows[1]["span_label"] == "2. route_ticket_mock"
    assert rows[1]["start_ms"] == 3.0
    assert rows[1]["duration_ms"] == 2.5
    assert rows[1]["outcome"] == "blocked_pending_approval"


def test_load_public_report_reads_markdown(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "evaluation_report.md").write_text("# Report\n", encoding="utf-8")

    assert load_public_report(tmp_path) == "# Report\n"


def test_load_public_report_html_reads_html(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "evaluation_report.html").write_text("<h1>Report</h1>\n", encoding="utf-8")

    assert load_public_report_html(tmp_path) == "<h1>Report</h1>\n"
