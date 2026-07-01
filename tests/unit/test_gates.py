from internal_ai_agent.evals.gates import evaluation_gates


def test_evaluation_gates_summarize_release_readiness() -> None:
    report = evaluation_gates(
        comparison={
            "metrics": {
                "abstention_accuracy": {"improved": 1.0},
            }
        },
        retriever_comparison={
            "systems": [
                {"label": "Local TF-IDF vector", "citation_coverage": 1.0},
                {"label": "Local embedding store", "citation_coverage": 1.0},
            ]
        },
        extraction={"metrics": {"schema_validity": 1.0}},
        security={
            "metrics": {
                "improved_weighted_safe_rate": 1.0,
                "improved_residual_risk_score": 0,
            }
        },
        agent={
            "metrics": {
                "side_effect_block_rate": 1.0,
                "approval_audit_rate": 1.0,
            }
        },
        dataset_profile={
            "dataset_counts": {"golden_cases": 350},
            "golden_case_mix": {"manual_share": 0.2686},
        },
        trace_index={"trace_count": 21, "span_count": 1306},
        collector_export_preview={"span_count": 1306},
    )

    assert report["gate_set_type"] == "deterministic_evaluation_release_gates"
    assert report["overall_status"] == "pass_with_warnings"
    assert report["fail_count"] == 0
    assert report["warn_count"] == 1
    assert report["pass_count"] == 12
    assert report["gates"][-1]["severity"] == "non_blocking"


def test_published_provider_embedding_result_clears_the_warning() -> None:
    report = evaluation_gates(
        comparison={"metrics": {"abstention_accuracy": {"improved": 1.0}}},
        retriever_comparison={
            "systems": [
                {"label": "Local TF-IDF vector", "citation_coverage": 1.0},
                {"label": "Local embedding store", "citation_coverage": 1.0},
            ]
        },
        extraction={"metrics": {"schema_validity": 1.0}},
        security={
            "metrics": {
                "improved_weighted_safe_rate": 1.0,
                "improved_residual_risk_score": 0,
            }
        },
        agent={"metrics": {"side_effect_block_rate": 1.0, "approval_audit_rate": 1.0}},
        dataset_profile={
            "dataset_counts": {"golden_cases": 350},
            "golden_case_mix": {"manual_share": 0.2686},
        },
        trace_index={"trace_count": 21, "span_count": 1306},
        collector_export_preview={"span_count": 1306},
        provider_embedding_published={
            "status": "published",
            "provider": "openai",
            "model": "text-embedding-3-small",
            "case_count": 358,
            "metrics": {"retrieval_hit_rate_at_3": 1.0},
        },
    )

    assert report["overall_status"] == "pass"
    assert report["warn_count"] == 0
    assert report["pass_count"] == 13
    provider_gate = next(
        gate
        for gate in report["gates"]
        if gate["gate_id"] == "retrieval.provider_embedding_result"
    )
    assert provider_gate["status"] == "pass"
    assert provider_gate["observed"] == "published"


def test_evaluation_gates_fail_when_blocking_threshold_is_missed() -> None:
    report = evaluation_gates(
        comparison={
            "metrics": {
                "abstention_accuracy": {"improved": 1.0},
            }
        },
        retriever_comparison={
            "systems": [
                {"label": "Local TF-IDF vector", "citation_coverage": 1.0},
                {"label": "Local embedding store", "citation_coverage": 0.97},
            ]
        },
        extraction={"metrics": {"schema_validity": 1.0}},
        security={
            "metrics": {
                "improved_weighted_safe_rate": 1.0,
                "improved_residual_risk_score": 0,
            }
        },
        agent={
            "metrics": {
                "side_effect_block_rate": 1.0,
                "approval_audit_rate": 1.0,
            }
        },
        dataset_profile={
            "dataset_counts": {"golden_cases": 350},
            "golden_case_mix": {"manual_share": 0.2686},
        },
        trace_index={"trace_count": 21, "span_count": 1306},
        collector_export_preview={"span_count": 1306},
    )

    assert report["overall_status"] == "fail"
    assert report["fail_count"] == 1
    failed_gate = next(gate for gate in report["gates"] if gate["status"] == "fail")
    assert failed_gate["gate_id"] == "retrieval.local_embedding_store_citation"


def test_evaluation_gates_fail_when_incident_replay_gate_fails() -> None:
    report = evaluation_gates(
        comparison={
            "metrics": {
                "abstention_accuracy": {"improved": 1.0},
            }
        },
        retriever_comparison={
            "systems": [
                {"label": "Local TF-IDF vector", "citation_coverage": 1.0},
                {"label": "Local embedding store", "citation_coverage": 1.0},
            ]
        },
        extraction={"metrics": {"schema_validity": 1.0}},
        security={
            "metrics": {
                "improved_weighted_safe_rate": 1.0,
                "improved_residual_risk_score": 0,
            }
        },
        agent={
            "metrics": {
                "side_effect_block_rate": 1.0,
                "approval_audit_rate": 1.0,
            }
        },
        dataset_profile={
            "dataset_counts": {"golden_cases": 350},
            "golden_case_mix": {"manual_share": 0.2686},
        },
        trace_index={"trace_count": 21, "span_count": 1306},
        collector_export_preview={"span_count": 1306},
        incident_release_gates={"overall_status": "fail"},
    )

    assert report["overall_status"] == "fail"
    failed_gate = next(
        gate for gate in report["gates"] if gate["gate_id"] == "incident.replay_release_gates"
    )
    assert failed_gate["status"] == "fail"
