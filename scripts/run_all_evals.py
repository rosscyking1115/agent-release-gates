from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.data.synthetic import generate_all
from internal_ai_agent.evals.agent import evaluate_agent
from internal_ai_agent.evals.dataset_profile import write_dataset_profile
from internal_ai_agent.evals.external_review import prepare_external_human_review
from internal_ai_agent.evals.extraction import evaluate_extraction
from internal_ai_agent.evals.failure_taxonomy import write_failure_taxonomy_summary
from internal_ai_agent.evals.gates import write_evaluation_gates
from internal_ai_agent.evals.goal_conflict_intervention import (
    write_goal_conflict_intervention,
)
from internal_ai_agent.evals.human_calibration import evaluate_human_calibration
from internal_ai_agent.evals.incident_replay import write_incident_replay_suite
from internal_ai_agent.evals.intervention_study import (
    write_agent_safety_intervention_study,
)
from internal_ai_agent.evals.memory_context_intervention import (
    write_memory_context_intervention,
)
from internal_ai_agent.evals.model_judge import write_model_judge_adapter_status
from internal_ai_agent.evals.multi_model_comparison import (
    write_model_judge_provider_comparison,
    write_multi_model_comparison_plan,
)
from internal_ai_agent.evals.multilingual_safety import write_multilingual_safety
from internal_ai_agent.evals.nist_rmf_mapping import write_nist_coverage_map
from internal_ai_agent.evals.public_rag_findings import write_public_rag_findings
from internal_ai_agent.evals.public_rag_model_reranker import (
    write_public_rag_model_reranker_adapter_status,
)
from internal_ai_agent.evals.public_rag_reranker import write_public_rag_reranker_eval
from internal_ai_agent.evals.public_rag_reranking import (
    write_public_rag_reranking_opportunity,
)
from internal_ai_agent.evals.rag_grounding_intervention import (
    write_rag_grounding_intervention,
)
from internal_ai_agent.evals.runner import (
    evaluate_comparison,
    evaluate_retriever_comparison,
    write_evaluation_history,
)
from internal_ai_agent.evals.safety_classifier import evaluate_safety_classifier
from internal_ai_agent.evals.security import evaluate_security
from internal_ai_agent.evals.techqa_public import evaluate_techqa_public
from internal_ai_agent.evals.wixqa_public import evaluate_wixqa_public
from internal_ai_agent.io import read_jsonl, write_jsonl
from internal_ai_agent.observability.collector import write_collector_export_preview
from internal_ai_agent.observability.otel import (
    otel_spans_from_agent_approval_cases,
    otel_spans_from_api_contracts,
    otel_spans_from_evaluation_run,
    otel_spans_from_extraction_cases,
    otel_spans_from_retriever_failures,
    otel_spans_from_retriever_rankings,
)
from internal_ai_agent.observability.trace_index import write_trace_index
from internal_ai_agent.reporting.public_report import write_public_report


def run_all(project_root: Path) -> dict[str, Any]:
    dataset_counts = generate_all(project_root)
    dataset_profile = write_dataset_profile(project_root)
    comparison = evaluate_comparison(project_root)
    retriever_comparison = evaluate_retriever_comparison(project_root)
    techqa_public = evaluate_techqa_public(project_root)
    wixqa_public = evaluate_wixqa_public(project_root)
    public_rag_findings = write_public_rag_findings(
        project_root,
        techqa_public=techqa_public,
        wixqa_public=wixqa_public,
    )
    public_rag_reranking = write_public_rag_reranking_opportunity(project_root)
    public_rag_reranker = write_public_rag_reranker_eval(project_root)
    public_rag_model_reranker = write_public_rag_model_reranker_adapter_status(project_root)
    rag_grounding_intervention = write_rag_grounding_intervention(project_root)
    extraction = evaluate_extraction(project_root)
    security = evaluate_security(project_root)
    safety_classifier = evaluate_safety_classifier(project_root)
    human_calibration = evaluate_human_calibration(project_root)
    external_review = prepare_external_human_review(project_root)
    model_judge_adapter = write_model_judge_adapter_status(project_root)
    multi_model_comparison = write_multi_model_comparison_plan(project_root)
    model_judge_provider_comparison = write_model_judge_provider_comparison(
        project_root
    )
    agent = evaluate_agent(project_root)
    intervention_study = write_agent_safety_intervention_study(
        project_root,
        comparison=comparison,
        retriever_comparison=retriever_comparison,
        safety_classifier=safety_classifier,
        security=security,
        agent=agent,
    )
    memory_context_intervention = write_memory_context_intervention(project_root)
    goal_conflict_intervention = write_goal_conflict_intervention(project_root)
    incident_replay = write_incident_replay_suite(project_root)
    evaluation_history = write_evaluation_history(
        project_root,
        retriever_report=retriever_comparison,
        extraction=extraction,
        security=security,
        agent=agent,
    )
    observability_spans_path = write_observability_spans(
        project_root=project_root,
        dataset_counts=dataset_counts,
        retriever_comparison=retriever_comparison,
        extraction=extraction,
        security=security,
        agent=agent,
    )
    trace_index = write_trace_index(project_root)
    collector_export_preview = write_collector_export_preview(project_root)
    failure_taxonomy = write_failure_taxonomy_summary(project_root)
    gates = write_evaluation_gates(
        project_root,
        comparison=comparison,
        retriever_comparison=retriever_comparison,
        extraction=extraction,
        security=security,
        agent=agent,
        dataset_profile=dataset_profile,
        trace_index=trace_index,
        collector_export_preview=collector_export_preview,
        incident_release_gates=incident_replay["release_gates"],
    )
    write_multilingual_safety(project_root)
    write_nist_coverage_map(project_root)
    public_report_path = write_public_report(project_root)
    return {
        "dataset_counts": dataset_counts,
        "dataset_profile": dataset_profile,
        "comparison": comparison,
        "retriever_comparison": retriever_comparison,
        "techqa_public": techqa_public,
        "wixqa_public": wixqa_public,
        "public_rag_findings": public_rag_findings,
        "public_rag_reranking": public_rag_reranking,
        "public_rag_reranker": public_rag_reranker,
        "public_rag_model_reranker": public_rag_model_reranker,
        "rag_grounding_intervention": rag_grounding_intervention,
        "extraction": extraction,
        "security": security,
        "safety_classifier": safety_classifier,
        "human_calibration": human_calibration,
        "external_review": external_review,
        "model_judge_adapter": model_judge_adapter,
        "multi_model_comparison": multi_model_comparison,
        "model_judge_provider_comparison": model_judge_provider_comparison,
        "agent": agent,
        "intervention_study": intervention_study,
        "memory_context_intervention": memory_context_intervention,
        "goal_conflict_intervention": goal_conflict_intervention,
        "incident_replay": incident_replay,
        "evaluation_history": evaluation_history,
        "observability_spans_path": str(observability_spans_path),
        "trace_index": trace_index,
        "collector_export_preview": collector_export_preview,
        "failure_taxonomy": failure_taxonomy,
        "evaluation_gates": gates,
        "public_report_path": str(public_report_path),
    }


def write_observability_spans(
    *,
    project_root: Path,
    dataset_counts: dict[str, int],
    retriever_comparison: dict[str, Any],
    extraction: dict[str, Any],
    security: dict[str, Any],
    agent: dict[str, Any],
) -> Path:
    agent_spans = read_jsonl(project_root / "reports/agent_otel_spans.jsonl")
    evaluation_spans = otel_spans_from_evaluation_run(
        dataset_counts=dataset_counts,
        retriever_comparison=retriever_comparison,
        extraction=extraction,
        security=security,
        agent=agent,
    )
    retriever_failure_spans = otel_spans_from_retriever_failures(
        _retriever_cases_by_system(project_root)
    )
    retriever_ranking_spans = otel_spans_from_retriever_rankings(
        _retriever_ranking_cases_by_system(project_root)
    )
    extraction_case_spans = otel_spans_from_extraction_cases(
        read_jsonl(project_root / "reports/extraction_eval_cases.jsonl")
    )
    agent_approval_spans = otel_spans_from_agent_approval_cases(
        read_jsonl(project_root / "reports/agent_eval_cases.jsonl")
    )
    api_contract_spans = otel_spans_from_api_contracts()
    output_path = project_root / "reports/observability_otel_spans.jsonl"
    write_jsonl(
        output_path,
        [
            *evaluation_spans,
            *retriever_failure_spans,
            *retriever_ranking_spans,
            *extraction_case_spans,
            *agent_approval_spans,
            *api_contract_spans,
            *agent_spans,
        ],
    )
    return output_path


def _retriever_cases_by_system(project_root: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        "Baseline team hints": read_jsonl(project_root / "reports/baseline_eval_cases.jsonl"),
        "Improved lexical": read_jsonl(project_root / "reports/improved_eval_cases.jsonl"),
        "Hybrid sparse semantic": read_jsonl(project_root / "reports/hybrid_eval_cases.jsonl"),
        "Local TF-IDF vector": read_jsonl(project_root / "reports/vector_eval_cases.jsonl"),
        "Local embedding store": read_jsonl(project_root / "reports/embedding_eval_cases.jsonl"),
    }


def _retriever_ranking_cases_by_system(project_root: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        "Local TF-IDF vector": read_jsonl(project_root / "reports/vector_eval_cases.jsonl"),
        "Local embedding store": read_jsonl(project_root / "reports/embedding_eval_cases.jsonl"),
    }


def main() -> None:
    summary = run_all(Path.cwd())
    print("Synthetic data and all evaluations complete")
    print("Dataset counts")
    for name, count in summary["dataset_counts"].items():
        print(f"- {name}: {count}")

    print("Core metrics")
    comparison_metrics = summary["comparison"]["metrics"]
    retriever_systems = summary["retriever_comparison"]["systems"]
    print(
        "- citation_coverage: "
        f"{comparison_metrics['citation_coverage']['baseline']:.4f} -> "
        f"{comparison_metrics['citation_coverage']['improved']:.4f}"
    )
    print(
        "- retrieval_hit_rate_at_3: "
        f"{comparison_metrics['retrieval_hit_rate_at_3']['baseline']:.4f} -> "
        f"{comparison_metrics['retrieval_hit_rate_at_3']['improved']:.4f}"
    )
    print(f"- hybrid_citation_coverage: {retriever_systems[-3]['citation_coverage']:.4f}")
    print(f"- vector_citation_coverage: {retriever_systems[-2]['citation_coverage']:.4f}")
    print(f"- embedding_citation_coverage: {retriever_systems[-1]['citation_coverage']:.4f}")
    if summary["techqa_public"]["status"] == "evaluated":
        techqa_metrics = summary["techqa_public"]["metrics"]
        print(
            "- techqa_public_retrieval_hit_rate_at_3: "
            f"{techqa_metrics['retrieval_hit_rate_at_3']:.4f}"
        )
        print(
            "- techqa_public_impossible_abstention_rate: "
            f"{techqa_metrics['impossible_abstention_rate']:.4f}"
        )
    if summary["wixqa_public"]["status"] == "evaluated":
        wixqa_metrics = summary["wixqa_public"]["metrics"]
        print(
            "- wixqa_public_retrieval_hit_rate_at_3: "
            f"{wixqa_metrics['retrieval_hit_rate_at_3']:.4f}"
        )
        print(
            "- wixqa_public_top1_citation_accuracy: "
            f"{wixqa_metrics['top1_citation_accuracy']:.4f}"
        )
    if summary["public_rag_findings"]["status"] == "evaluated":
        findings_summary = summary["public_rag_findings"]["summary"]
        print(
            "- public_rag_weighted_retrieval_hit_rate_at_3: "
            f"{findings_summary['weighted_retrieval_hit_rate_at_3']:.4f}"
        )
        print(
            "- public_rag_top_failure_label: "
            f"{findings_summary['top_cross_track_failure_label']}"
        )
    if summary["public_rag_reranking"]["status"] == "evaluated":
        reranking_summary = summary["public_rag_reranking"]["summary"]
        print(
            "- public_rag_rerank_ceiling_top1_citation_accuracy: "
            f"{reranking_summary['oracle_top3_rerank_ceiling']:.4f}"
        )
        print(
            "- public_rag_rerankable_case_count: "
            f"{reranking_summary['rerankable_case_count']}"
        )
    if summary["public_rag_reranker"]["status"] == "evaluated":
        reranker_summary = summary["public_rag_reranker"]["summary"]
        print(
            "- public_rag_reranker_top1_accuracy_delta: "
            f"{reranker_summary['top1_accuracy_delta']:.4f}"
        )
        print(
            "- public_rag_reranker_regressed_cases: "
            f"{reranker_summary['regressed_case_count']}"
        )
    print(
        "- public_rag_model_reranker_adapter_status: "
        f"{summary['public_rag_model_reranker']['status']}"
    )
    print(
        "- public_rag_model_reranker_packet_cases: "
        f"{summary['public_rag_model_reranker']['candidate_case_count']}"
    )
    print(
        "- rag_grounding_intervention_status: "
        f"{summary['rag_grounding_intervention']['status']}"
    )
    if summary["rag_grounding_intervention"]["status"] == "evaluated":
        grounding_summary = summary["rag_grounding_intervention"]["summary"]
        print(
            "- rag_grounding_moderate_unsupported_answer_rate: "
            f"{grounding_summary['moderate_unsupported_answer_rate']:.4f}"
        )
        print(
            "- rag_grounding_strict_review_burden_per_100: "
            f"{grounding_summary['strict_review_burden_per_100']:.2f}"
        )
    print(
        f"- extraction_schema_validity: {summary['extraction']['metrics']['schema_validity']:.4f}"
    )
    print(
        f"- security_improved_safe_rate: {summary['security']['metrics']['improved_safe_rate']:.4f}"
    )
    print(
        "- security_improved_weighted_safe_rate: "
        f"{summary['security']['metrics']['improved_weighted_safe_rate']:.4f}"
    )
    print(
        "- security_improved_residual_risk_score: "
        f"{summary['security']['metrics']['improved_residual_risk_score']}"
    )
    print(
        "- safety_classifier_false_negative_rate: "
        f"{summary['safety_classifier']['metrics']['false_negative_rate']:.4f}"
    )
    print(
        "- safety_classifier_false_negative_reduction: "
        f"{summary['safety_classifier']['threshold_retuning']['false_negative_reduction']}"
    )
    print(
        "- safety_prevalence_estimate: "
        f"{summary['safety_classifier']['weighted_prevalence']['unsafe_prevalence']:.4f}"
    )
    print(
        "- safety_secondary_floor_unsafe_capture_rate: "
        f"{summary['safety_classifier']['secondary_review_floor_validation']['unsafe_capture_rate']:.4f}"
    )
    print(
        "- human_calibration_label_accuracy: "
        f"{summary['human_calibration']['summary']['classifier_label_accuracy']:.4f}"
    )
    print(f"- external_human_review_status: {summary['external_review']['status']}")
    print(f"- model_judge_adapter_status: {summary['model_judge_adapter']['status']}")
    print(
        "- multi_model_comparison_status: "
        f"{summary['multi_model_comparison']['status']}"
    )
    print(
        "- model_judge_provider_comparison_status: "
        f"{summary['model_judge_provider_comparison']['status']}"
    )
    print(
        "- agent_side_effect_block_rate: "
        f"{summary['agent']['metrics']['side_effect_block_rate']:.4f}"
    )
    print(
        "- intervention_study_experiments: "
        f"{summary['intervention_study']['experiment_count']}"
    )
    print(
        "- memory_context_intervention_status: "
        f"{summary['memory_context_intervention']['status']}"
    )
    print(
        "- memory_context_polluted_follow_rate: "
        f"{summary['memory_context_intervention']['summary']['scoped_review_polluted_memory_follow_rate']:.4f}"
    )
    print(
        "- memory_context_review_burden_per_100: "
        f"{summary['memory_context_intervention']['summary']['scoped_review_review_burden_per_100_cases']:.2f}"
    )
    print(
        "- goal_conflict_intervention_status: "
        f"{summary['goal_conflict_intervention']['status']}"
    )
    print(
        "- goal_conflict_unsafe_goal_compliance_rate: "
        f"{summary['goal_conflict_intervention']['summary']['layered_unsafe_goal_compliance_rate']:.4f}"
    )
    print(
        "- goal_conflict_review_burden_per_100: "
        f"{summary['goal_conflict_intervention']['summary']['layered_review_burden_per_100_cases']:.2f}"
    )
    print(
        "- incident_replay_gate_status: "
        f"{summary['incident_replay']['summary']['release_gate_status']}"
    )
    print(
        "- incident_replay_closure_rate: "
        f"{summary['incident_replay']['summary']['incident_closure_rate']:.4f}"
    )
    print(
        "- historical_snapshot_latest: "
        f"{summary['evaluation_history']['current_summary']['latest_milestone']}"
    )
    print(
        "- collector_export_payloads: "
        f"{summary['collector_export_preview']['payload_count']} dry-run payloads"
    )
    print(
        "- trace_index: "
        f"{summary['trace_index']['trace_count']} traces, "
        f"{summary['trace_index']['error_span_count']} error spans"
    )
    print(
        "- evaluation_gates: "
        f"{summary['evaluation_gates']['overall_status']} "
        f"({summary['evaluation_gates']['pass_count']} pass, "
        f"{summary['evaluation_gates']['warn_count']} warn, "
        f"{summary['evaluation_gates']['fail_count']} fail)"
    )
    print(
        "- taxonomy_labeled_cases: "
        f"{summary['failure_taxonomy']['total_labeled_cases']}"
    )
    print(
        "- manual_golden_cases: "
        f"{summary['dataset_profile']['golden_case_mix']['manual_cases']}"
    )
    print(f"Public report: {summary['public_report_path']}")


if __name__ == "__main__":
    main()
