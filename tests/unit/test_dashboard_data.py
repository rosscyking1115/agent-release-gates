import json

from internal_ai_agent.dashboard.data import (
    agent_metric_rows,
    agent_otel_span_rows,
    agent_otel_summary,
    agent_otel_timeline_rows,
    agent_trace_rows,
    case_mix,
    coverage_count_rows,
    error_analysis_rows,
    evaluation_gate_rows,
    evaluation_history_rows,
    external_human_review_category_rows,
    external_human_review_disagreement_rows,
    extraction_metric_rows,
    failed_case_rows,
    failure_example_rows,
    failure_reason_rows,
    incident_replay_run_rows,
    incident_trace_event_rows,
    load_collector_export_preview,
    load_dataset_profile,
    load_evaluation_gates,
    load_external_human_review_summary,
    load_incident_release_gates,
    load_incident_replay_runs,
    load_incident_replay_summary,
    load_incident_trace_events,
    load_multi_model_comparison_plan,
    load_observability_trace_index,
    load_public_report,
    load_public_report_html,
    load_public_report_pdf,
    metric_rows,
    multi_model_comparison_target_rows,
    red_team_coverage_rows,
    retriever_experiment_rows,
    retriever_failure_example_rows,
    retriever_failure_overview,
    retriever_snapshot_rows,
    security_metric_rows,
    security_risk_breakdown_rows,
    trace_index_component_rows,
    trace_index_error_rows,
    trace_index_query_rows,
    trace_index_trace_rows,
)


def test_load_collector_export_preview_returns_empty_when_missing(tmp_path) -> None:
    assert load_collector_export_preview(tmp_path) == {}


def test_load_collector_export_preview_reads_json(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "collector_export_preview.json").write_text(
        '{"export_mode": "dry_run_preview", "span_count": 10, "payload_count": 1}\n',
        encoding="utf-8",
    )

    preview = load_collector_export_preview(tmp_path)

    assert preview["export_mode"] == "dry_run_preview"
    assert preview["span_count"] == 10


def test_load_observability_trace_index_reads_json(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "observability_trace_index.json").write_text(
        '{"index_type": "local_observability_trace_index", "trace_count": 2}\n',
        encoding="utf-8",
    )

    index = load_observability_trace_index(tmp_path)

    assert index["index_type"] == "local_observability_trace_index"
    assert index["trace_count"] == 2


def test_load_evaluation_gates_reads_json(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "evaluation_gates.json").write_text(
        '{"gate_set_type": "deterministic_evaluation_release_gates", "overall_status": "pass"}\n',
        encoding="utf-8",
    )

    gates = load_evaluation_gates(tmp_path)

    assert gates["gate_set_type"] == "deterministic_evaluation_release_gates"
    assert gates["overall_status"] == "pass"


def test_load_incident_replay_artifacts_return_defaults_when_missing(tmp_path) -> None:
    assert load_incident_replay_summary(tmp_path)["status"] == "not_configured"
    assert load_incident_replay_runs(tmp_path) == []
    assert load_incident_trace_events(tmp_path) == []
    assert load_incident_release_gates(tmp_path) == {}


def test_incident_replay_run_rows_format_replay_matrix() -> None:
    rows = incident_replay_run_rows(
        [
            {
                "incident_id": "INC-2026-0001",
                "severity": "critical",
                "decision": "block",
                "original_decision": "allow",
                "expected_behavior_match": True,
                "closed_by_replay": True,
                "must_not_violations": [],
                "risk_categories": ["prompt_injection", "approval_bypass"],
                "generated_regression_case_id": "REG-INC-2026-0001",
                "diff_summary": "Candidate blocked the unsafe request.",
            }
        ]
    )

    assert rows == [
        {
            "incident_id": "INC-2026-0001",
            "severity": "Critical",
            "decision": "Block",
            "original_decision": "Allow",
            "expected_behavior_match": True,
            "closed_by_replay": True,
            "must_not_violations": "None",
            "risk_categories": "prompt_injection, approval_bypass",
            "regression_case": "REG-INC-2026-0001",
            "diff_summary": "Candidate blocked the unsafe request.",
        }
    ]


def test_incident_trace_event_rows_format_replay_evidence(tmp_path) -> None:
    incident_dir = tmp_path / "data/incidents"
    incident_dir.mkdir(parents=True)
    (incident_dir / "trace_events.jsonl").write_text(
        json.dumps(
            {
                "incident_id": "INC-2026-0001",
                "trace_id": "original_INC-2026-0001",
                "event_seq": 1,
                "actor": "assistant",
                "event_type": "tool_call",
                "content": "Original behavior attempted a side effect.",
                "tool_name": "route_ticket_mock",
                "tool_args": {},
                "tool_result": {},
                "timestamp_utc": "2026-06-24T09:00:03Z",
                "annotations": {"risk_score": 1.0, "requires_approval": True},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    events = load_incident_trace_events(tmp_path)
    rows = incident_trace_event_rows(events)

    assert rows == [
        {
            "incident_id": "INC-2026-0001",
            "trace_id": "original_INC-2026-0001",
            "event_seq": 1,
            "actor": "Assistant",
            "event_type": "Tool Call",
            "content": "Original behavior attempted a side effect.",
            "tool_name": "route_ticket_mock",
            "risk_score": 1.0,
            "requires_approval": True,
            "timestamp_utc": "2026-06-24T09:00:03Z",
        }
    ]


def test_load_dataset_profile_reads_json(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "dataset_profile.json").write_text(
        '{"profile_type": "synthetic_dataset_profile", "golden_case_mix": {"manual_cases": 2}}\n',
        encoding="utf-8",
    )

    profile = load_dataset_profile(tmp_path)

    assert profile["profile_type"] == "synthetic_dataset_profile"
    assert profile["golden_case_mix"]["manual_cases"] == 2


def test_external_human_review_rows_format_public_metrics(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "external_human_review_summary.json").write_text(
        json.dumps(
            {
                "report_type": "external_human_review",
                "status": "evaluated",
                "case_count": 2,
                "label_row_count": 4,
                "reviewer_count": 2,
                "summary": {
                    "external_label_coverage": 1.0,
                    "cases_with_two_or_more_reviewers": 2,
                    "pairwise_agreement_rate": 0.5,
                    "pairwise_cohen_kappa": 0.0,
                    "external_maintainer_agreement_rate": 1.0,
                    "external_maintainer_disagreement_count": 0,
                    "adjudication_required_count": 1,
                },
                "by_category": [
                    {
                        "risk_category": "tool_misuse",
                        "case_count": 2,
                        "reviewed_case_count": 2,
                        "external_maintainer_agreement_rate": 0.5,
                        "adjudication_required_count": 1,
                    }
                ],
                "disagreement_examples": [
                    {
                        "case_id": "HUMAN-CAL-002",
                        "risk_category": "tool_misuse",
                        "risk_severity": "medium",
                        "maintainer_label": "benign",
                        "external_reviewer_count": 2,
                        "external_consensus_label": "adjudication_required",
                        "external_maintainer_agree": None,
                        "adjudication_required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = load_external_human_review_summary(tmp_path)
    category_rows = external_human_review_category_rows(report)
    disagreement_rows = external_human_review_disagreement_rows(report)

    assert report["status"] == "evaluated"
    assert category_rows[0]["external_maintainer_agreement_pct"] == "50.00%"
    assert disagreement_rows[0]["case_id"] == "HUMAN-CAL-002"
    assert disagreement_rows[0]["adjudication_required"] is True


def test_multi_model_comparison_plan_rows_format_targets(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "multi_model_comparison_plan.json").write_text(
        json.dumps(
            {
                "report_type": "multi_model_comparison_plan",
                "status": "planned_not_run",
                "case_count": 24,
                "target_model_count": 2,
                "planned_targets": [
                    {
                        "provider": "openai",
                        "adapter_status": "available",
                        "credential_env_var": "OPENAI_API_KEY",
                        "model_env_var": "OPENAI_JUDGE_MODEL",
                        "result_state": "one_reviewed_result_present",
                    }
                ],
                "readiness_summary": {"adapter_available_count": 1},
            }
        ),
        encoding="utf-8",
    )

    plan = load_multi_model_comparison_plan(tmp_path)
    rows = multi_model_comparison_target_rows(plan)

    assert plan["status"] == "planned_not_run"
    assert rows == [
        {
            "provider": "openai",
            "adapter_status": "Available",
            "credential_env_var": "OPENAI_API_KEY",
            "model_env_var": "OPENAI_JUDGE_MODEL",
            "result_state": "One reviewed result present",
        }
    ]


def test_dataset_profile_rows_format_coverage_counts() -> None:
    profile = {
        "golden_coverage": {
            "by_noise_type": {
                "manual_review_bundle": 6,
                "clean_exact": 48,
            }
        },
        "red_team_coverage": {
            "by_risk_type": {
                "prompt_injection": 4,
            }
        },
    }

    assert coverage_count_rows(profile, "by_noise_type") == [
        {"value": "manual_review_bundle", "case_count": 6},
        {"value": "clean_exact", "case_count": 48},
    ]
    assert red_team_coverage_rows(profile, "by_risk_type") == [
        {"value": "prompt_injection", "case_count": 4}
    ]


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


def test_evaluation_history_rows_formats_milestone_deltas() -> None:
    rows = evaluation_history_rows(
        {
            "milestones": [
                {
                    "milestone_at_utc": "2026-06-02T09:00:00Z",
                    "milestone": "Baseline",
                    "system_version": "baseline",
                    "retrieval_hit_rate_at_3": 0.45,
                    "citation_coverage": 0.2,
                    "next_action_accuracy": 0.2,
                    "abstention_accuracy": 0.78,
                    "failure_count": 200,
                    "citation_delta_from_previous": None,
                    "failure_delta_from_previous": None,
                },
                {
                    "milestone_at_utc": "2026-06-02T10:00:00Z",
                    "milestone": "Hybrid",
                    "system_version": "hybrid",
                    "retrieval_hit_rate_at_3": 1.0,
                    "citation_coverage": 1.0,
                    "next_action_accuracy": 1.0,
                    "abstention_accuracy": 1.0,
                    "failure_count": 0,
                    "citation_delta_from_previous": 0.8,
                    "failure_delta_from_previous": -200,
                },
            ]
        }
    )

    assert rows[0]["citation_delta_pct"] == ""
    assert rows[1]["citation_coverage_pct"] == "100.00%"
    assert rows[1]["citation_delta_pct"] == "+80.00%"
    assert rows[1]["failure_delta"] == "-200"


def test_evaluation_gate_rows_formats_percent_values() -> None:
    rows = evaluation_gate_rows(
        {
            "gates": [
                {
                    "area": "Benchmark",
                    "label": "Manual share",
                    "status": "pass",
                    "severity": "blocking",
                    "observed": 0.2686,
                    "threshold": 0.25,
                    "value_format": "percent",
                    "rationale": "Manual cases reduce overfitting.",
                }
            ]
        }
    )

    assert rows == [
            {
                "area": "Benchmark",
                "label": "Manual share",
                "status": "Pass",
                "severity": "Blocking",
                "observed": "26.86%",
                "threshold": "25.00%",
            "rationale": "Manual cases reduce overfitting.",
        }
    ]


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


def test_trace_index_rows_format_index_sections() -> None:
    index = {
        "components": [
            {"component": "retrieval", "span_count": 5, "error_span_count": 1}
        ],
        "queries": [
            {"query": "error_spans", "description": "Errors", "span_count": 1}
        ],
        "error_spans": [
            {
                "trace_label": "retriever_failures_vector",
                "name": "retriever.case_failure",
                "component": "retrieval",
            }
        ],
        "traces": [
            {"trace_label": "evaluation_run", "span_count": 7},
            {"trace_label": "retriever_failures_vector", "span_count": 2},
        ],
    }

    assert trace_index_component_rows(index)[0]["component"] == "retrieval"
    assert trace_index_query_rows(index)[0]["query"] == "error_spans"
    assert trace_index_error_rows(index)[0]["name"] == "retriever.case_failure"
    assert len(trace_index_trace_rows(index, limit=1)) == 1


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


def test_load_public_report_pdf_reads_pdf_bytes(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "evaluation_report.pdf").write_bytes(b"%PDF-1.4\n")

    assert load_public_report_pdf(tmp_path) == b"%PDF-1.4\n"
