from internal_ai_agent.dashboard.data import (
    agent_metric_rows,
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
    security_metric_rows,
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


def test_security_metric_rows_formats_before_after_scores() -> None:
    rows = security_metric_rows(
        {
            "metrics": {
                "baseline_block_rate": 0.0,
                "improved_block_rate": 1.0,
                "baseline_safe_rate": 0.25,
                "improved_safe_rate": 0.75,
            }
        }
    )

    assert rows[0]["label"] == "Policy block rate"
    assert rows[0]["baseline_pct"] == "0.00%"
    assert rows[0]["improved_pct"] == "100.00%"


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
