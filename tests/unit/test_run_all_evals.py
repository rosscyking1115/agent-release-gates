from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_run_all():
    script_path = Path(__file__).resolve().parents[2] / "scripts/run_all_evals.py"
    spec = importlib.util.spec_from_file_location("run_all_evals", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load run_all_evals.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_all


def test_run_all_evals_generates_reports(tmp_path) -> None:
    run_all = _load_run_all()
    summary = run_all(tmp_path)

    assert summary["dataset_counts"]["runbooks"] == 24
    assert summary["dataset_counts"]["safety_challenge_cases"] == 40
    assert summary["dataset_counts"]["safety_secondary_review_validation_cases"] == 39
    assert summary["dataset_counts"]["safety_prevalence_cases"] == 80
    assert summary["dataset_profile"]["golden_case_mix"]["manual_cases"] == 102
    assert summary["dataset_profile"]["golden_case_mix"]["noise_type_count"] >= 30
    assert summary["comparison"]["case_count"] == 358
    assert summary["retriever_comparison"]["case_count"] == 358
    assert len(summary["retriever_comparison"]["systems"]) == 5
    assert summary["techqa_public"]["status"] == "not_configured"
    assert summary["techqa_public"]["benchmark_profile"]["sample_case_count"] == 0
    assert summary["wixqa_public"]["status"] == "not_configured"
    assert summary["wixqa_public"]["benchmark_profile"]["sample_case_count"] == 0
    assert summary["public_rag_findings"]["status"] == "not_configured"
    assert summary["public_rag_findings"]["summary"]["evaluated_track_count"] == 0
    assert summary["public_rag_reranking"]["status"] == "not_configured"
    assert summary["public_rag_reranking"]["summary"]["evaluated_track_count"] == 0
    assert summary["public_rag_reranker"]["status"] == "not_configured"
    assert summary["public_rag_reranker"]["summary"]["evaluated_track_count"] == 0
    assert summary["public_rag_model_reranker"]["status"] == "not_configured"
    assert summary["public_rag_model_reranker"]["candidate_case_count"] == 0
    assert summary["rag_grounding_intervention"]["status"] == "not_configured"
    assert summary["rag_grounding_intervention"]["case_count"] == 0
    assert summary["extraction"]["metrics"]["schema_validity"] == 1.0
    assert summary["security"]["metrics"]["improved_safe_rate"] == 1.0
    assert summary["security"]["metrics"]["improved_weighted_safe_rate"] == 1.0
    assert summary["security"]["metrics"]["improved_residual_risk_score"] == 0
    assert summary["security"]["case_count"] == 60
    assert summary["safety_classifier"]["metrics"]["high_severity_false_negative_count"] == 0
    assert summary["safety_classifier"]["weighted_decision_mix"]["review"] > 0
    assert summary["safety_classifier"]["human_review_simulation"]["queue_count"] > 0
    assert summary["safety_classifier"]["human_adjudication_notes"]["adjudication_note_count"] > 0
    assert summary["safety_classifier"]["human_adjudication_notes"][
        "classifier_disagreement_count"
    ] > 0
    assert summary["safety_classifier"]["reviewer_disagreement_slices"][
        "disagreement_count"
    ] == summary["safety_classifier"]["human_adjudication_notes"][
        "classifier_disagreement_count"
    ]
    assert summary["safety_classifier"]["secondary_review_band_analysis"][
        "secondary_review_floor_recommended"
    ]
    assert summary["safety_classifier"]["secondary_review_band_analysis"][
        "global_threshold_change_recommended"
    ] is False
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "unsafe_capture_rate"
    ] == 1.0
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "multi_turn_unsafe_capture_rate"
    ] == 1.0
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "multi_turn_benign_new_review_rate"
    ] == 0.0
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "benign_new_review_count"
    ] > 0
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "reviewer_label_coverage"
    ] == 1.0
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "floor_reviewer_precision"
    ] > 0.8
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "rubric_label_coverage"
    ] == 1.0
    assert summary["safety_classifier"]["secondary_review_floor_validation"][
        "capacity_sensitivity_floor_review_count"
    ] == 17
    assert summary["safety_classifier"]["secondary_review_operating_recommendation"][
        "minimum_reviewer_daily_capacity"
    ] == 16
    assert summary["safety_classifier"]["secondary_review_operating_recommendation"][
        "capacity_buffer_cases"
    ] == 15
    assert summary["safety_classifier"]["mitigation_impact"]["unsafe_allowed_reduction"] > 0
    assert summary["safety_classifier"]["threshold_retuning"]["false_negative_reduction"] > 0
    assert summary["agent"]["metrics"]["side_effect_block_rate"] == 1.0
    assert summary["intervention_study"]["experiment_count"] == 3
    assert summary["intervention_study"]["status"] == "evaluated"
    assert summary["evaluation_history"]["current_summary"]["best_retriever"] == (
        "Local TF-IDF vector"
    )
    assert len(summary["evaluation_history"]["milestones"]) == 5
    assert summary["collector_export_preview"]["export_mode"] == "dry_run_preview"
    assert summary["model_judge_adapter"]["status"] == "dry_run_ready"
    assert summary["model_judge_adapter"]["api_mode"] == "responses"
    assert summary["multi_model_comparison"]["status"] == "planned_not_run"
    assert summary["multi_model_comparison"]["target_model_count"] == 4
    assert summary["collector_export_preview"]["span_count"] > 0
    assert summary["collector_export_preview"]["payload_count"] > 0
    assert summary["trace_index"]["index_type"] == "local_observability_trace_index"
    assert summary["trace_index"]["trace_count"] > 0
    assert summary["trace_index"]["error_span_count"] > 0
    assert summary["evaluation_gates"]["gate_set_type"] == (
        "deterministic_evaluation_release_gates"
    )
    assert summary["evaluation_gates"]["fail_count"] == 0
    assert (tmp_path / "reports/eval_comparison.json").exists()
    assert (tmp_path / "reports/dataset_profile.json").exists()
    assert (tmp_path / "reports/retriever_comparison.json").exists()
    assert (tmp_path / "reports/techqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/techqa_public_benchmark_profile.json").exists()
    assert (tmp_path / "reports/techqa_public_rag_cases.jsonl").exists()
    assert (tmp_path / "reports/techqa_public_retriever_comparison.json").exists()
    assert (tmp_path / "reports/techqa_public_retriever_cases.jsonl").exists()
    assert (tmp_path / "reports/wixqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/wixqa_public_benchmark_profile.json").exists()
    assert (tmp_path / "reports/wixqa_public_rag_cases.jsonl").exists()
    assert (tmp_path / "reports/wixqa_public_retriever_comparison.json").exists()
    assert (tmp_path / "reports/wixqa_public_retriever_cases.jsonl").exists()
    assert (tmp_path / "reports/public_rag_findings.json").exists()
    assert (tmp_path / "reports/public_rag_reranking_opportunity.json").exists()
    assert (tmp_path / "reports/public_rag_reranker_eval.json").exists()
    assert (
        tmp_path / "reports/public_rag_model_reranker_adapter_status.json"
    ).exists()
    assert (tmp_path / "reports/public_rag_model_reranker_packet.jsonl").exists()
    assert (tmp_path / "reports/rag_grounding_intervention.json").exists()
    assert (tmp_path / "reports/rag_grounding_intervention.md").exists()
    assert (tmp_path / "reports/retriever_metric_snapshots.json").exists()
    assert (tmp_path / "reports/evaluation_history.json").exists()
    assert (tmp_path / "reports/hybrid_eval_summary.json").exists()
    assert (tmp_path / "reports/vector_eval_summary.json").exists()
    assert (tmp_path / "reports/embedding_eval_summary.json").exists()
    assert (tmp_path / "reports/agent_eval_summary.json").exists()
    assert (tmp_path / "reports/baseline_v1_summary.json").exists()
    assert (tmp_path / "reports/agent_safety_intervention_study.json").exists()
    assert (tmp_path / "reports/instruction_hierarchy_intervention.json").exists()
    assert (tmp_path / "reports/action_gate_intervention.json").exists()
    assert (tmp_path / "reports/safety_classifier_intervention_study.json").exists()
    assert (tmp_path / "data/eval_cases/instruction_hierarchy_cases.jsonl").exists()
    assert (tmp_path / "config/action_risk_policy.yaml").exists()
    assert (tmp_path / "reports/agent_otel_spans.jsonl").exists()
    assert (tmp_path / "reports/observability_otel_spans.jsonl").exists()
    assert (tmp_path / "reports/observability_trace_index.json").exists()
    assert (tmp_path / "reports/evaluation_gates.json").exists()
    assert (tmp_path / "reports/safety_classifier_eval_summary.json").exists()
    assert (tmp_path / "reports/safety_classifier_eval_cases.jsonl").exists()
    assert (tmp_path / "reports/safety_threshold_sweep.json").exists()
    assert (tmp_path / "reports/safety_threshold_retuning.json").exists()
    assert (tmp_path / "reports/safety_human_review_simulation.json").exists()
    assert (tmp_path / "reports/safety_adjudication_notes.json").exists()
    assert (tmp_path / "reports/safety_reviewer_disagreement_slices.json").exists()
    assert (tmp_path / "reports/safety_secondary_review_band_analysis.json").exists()
    assert (tmp_path / "reports/safety_secondary_review_floor_validation.json").exists()
    assert (
        tmp_path / "reports/safety_secondary_review_operating_recommendation.json"
    ).exists()
    assert (tmp_path / "reports/safety_mitigation_impact.json").exists()
    assert (tmp_path / "reports/safety_threshold_decision_memo.json").exists()
    assert (tmp_path / "reports/model_judge_adapter_status.json").exists()
    assert (tmp_path / "reports/multi_model_comparison_plan.json").exists()
    assert (tmp_path / "reports/collector_export_preview.json").exists()
    assert (tmp_path / "reports/evaluation_report.md").exists()
    assert (tmp_path / "reports/evaluation_report.html").exists()
    assert (tmp_path / "reports/evaluation_report.pdf").exists()
    assert (tmp_path / "reports/evaluation_report.pdf").read_bytes().startswith(b"%PDF-1.4")
    assert Path(summary["observability_spans_path"]).name == "observability_otel_spans.jsonl"
    assert Path(summary["public_report_path"]).name == "evaluation_report.md"
