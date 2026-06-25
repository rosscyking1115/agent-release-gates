from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

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
    goal_conflict_variant_rows,
    human_calibration_case_rows,
    human_calibration_category_rows,
    incident_replay_run_rows,
    incident_trace_event_rows,
    intervention_experiment_rows,
    judge_reliability_category_rows,
    judge_reliability_disagreement_rows,
    judge_reliability_pair_rows,
    load_agent_summary,
    load_agent_trace_examples,
    load_case_rows,
    load_collector_export_preview,
    load_comparison,
    load_dataset_profile,
    load_evaluation_gates,
    load_evaluation_history,
    load_external_human_review_summary,
    load_extraction_summary,
    load_failure_taxonomy_summary,
    load_goal_conflict_intervention,
    load_human_calibration_summary,
    load_incident_release_gates,
    load_incident_replay_runs,
    load_incident_replay_summary,
    load_incident_trace_events,
    load_intervention_study,
    load_judge_reliability_summary,
    load_memory_context_intervention,
    load_model_judge_adapter_status,
    load_multi_model_comparison_plan,
    load_observability_otel_spans,
    load_observability_trace_index,
    load_public_rag_findings,
    load_public_rag_model_reranker_adapter_status,
    load_public_rag_reranker_eval,
    load_public_rag_reranking_opportunity,
    load_public_report,
    load_public_report_html,
    load_public_report_pdf,
    load_rag_grounding_intervention,
    load_retriever_case_rows,
    load_retriever_comparison,
    load_retriever_snapshots,
    load_safety_adjudication_notes,
    load_safety_classifier_summary,
    load_safety_human_review_simulation,
    load_safety_mitigation_impact,
    load_safety_secondary_review_band_analysis,
    load_safety_secondary_review_floor_validation,
    load_safety_secondary_review_operating_recommendation,
    load_safety_threshold_decision_memo,
    load_safety_threshold_retuning,
    load_safety_threshold_sweep,
    load_security_summary,
    load_techqa_public_summary,
    load_wixqa_public_summary,
    memory_context_variant_rows,
    metric_rows,
    model_judge_adapter_rows,
    multi_model_comparison_target_rows,
    observability_component_rows,
    public_rag_model_reranker_adapter_rows,
    public_rag_reranker_track_rows,
    public_rag_reranking_track_rows,
    public_rag_track_rows,
    rag_grounding_variant_rows,
    red_team_coverage_rows,
    retriever_experiment_rows,
    retriever_failure_example_rows,
    retriever_failure_overview,
    retriever_snapshot_rows,
    safety_adjudication_note_rows,
    safety_mitigation_rows,
    safety_operating_recommendation_rows,
    safety_retuning_rows,
    safety_review_case_rows,
    safety_threshold_rows,
    security_metric_rows,
    security_risk_breakdown_rows,
    taxonomy_label_rows,
    taxonomy_source_rows,
    techqa_public_metric_rows,
    trace_index_component_rows,
    trace_index_error_rows,
    trace_index_query_rows,
    trace_index_trace_rows,
    wixqa_public_metric_rows,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    st.set_page_config(
        page_title="Agent Release Safety Gates",
        layout="wide",
    )
    _render_app_header()

    comparison = load_comparison(PROJECT_ROOT)
    dataset_profile = load_dataset_profile(PROJECT_ROOT)
    retriever_comparison = load_retriever_comparison(PROJECT_ROOT)
    retriever_snapshots = load_retriever_snapshots(PROJECT_ROOT)
    techqa_public = load_techqa_public_summary(PROJECT_ROOT)
    wixqa_public = load_wixqa_public_summary(PROJECT_ROOT)
    public_rag_findings = load_public_rag_findings(PROJECT_ROOT)
    public_rag_reranking = load_public_rag_reranking_opportunity(PROJECT_ROOT)
    public_rag_reranker = load_public_rag_reranker_eval(PROJECT_ROOT)
    public_rag_model_reranker = load_public_rag_model_reranker_adapter_status(
        PROJECT_ROOT
    )
    rag_grounding_intervention = load_rag_grounding_intervention(PROJECT_ROOT)
    evaluation_history = load_evaluation_history(PROJECT_ROOT)
    evaluation_gates = load_evaluation_gates(PROJECT_ROOT)
    incident_replay = load_incident_replay_summary(PROJECT_ROOT)
    incident_replay_runs = load_incident_replay_runs(PROJECT_ROOT)
    incident_trace_events = load_incident_trace_events(PROJECT_ROOT)
    incident_release_gates = load_incident_release_gates(PROJECT_ROOT)
    extraction_summary = load_extraction_summary(PROJECT_ROOT)
    security_summary = load_security_summary(PROJECT_ROOT)
    safety_classifier = load_safety_classifier_summary(PROJECT_ROOT)
    safety_threshold_sweep = load_safety_threshold_sweep(PROJECT_ROOT)
    safety_threshold_retuning = load_safety_threshold_retuning(PROJECT_ROOT)
    safety_review_simulation = load_safety_human_review_simulation(PROJECT_ROOT)
    safety_adjudication_notes = load_safety_adjudication_notes(PROJECT_ROOT)
    safety_secondary_review_band = load_safety_secondary_review_band_analysis(PROJECT_ROOT)
    safety_secondary_review_validation = load_safety_secondary_review_floor_validation(
        PROJECT_ROOT
    )
    safety_operating_recommendation = (
        load_safety_secondary_review_operating_recommendation(PROJECT_ROOT)
    )
    safety_mitigation_impact = load_safety_mitigation_impact(PROJECT_ROOT)
    safety_threshold_memo = load_safety_threshold_decision_memo(PROJECT_ROOT)
    intervention_study = load_intervention_study(PROJECT_ROOT)
    memory_context_intervention = load_memory_context_intervention(PROJECT_ROOT)
    goal_conflict_intervention = load_goal_conflict_intervention(PROJECT_ROOT)
    human_calibration = load_human_calibration_summary(PROJECT_ROOT)
    external_human_review = load_external_human_review_summary(PROJECT_ROOT)
    judge_reliability = load_judge_reliability_summary(PROJECT_ROOT)
    model_judge_adapter = load_model_judge_adapter_status(PROJECT_ROOT)
    multi_model_comparison = load_multi_model_comparison_plan(PROJECT_ROOT)
    failure_taxonomy = load_failure_taxonomy_summary(PROJECT_ROOT)
    agent_summary = load_agent_summary(PROJECT_ROOT)
    agent_traces = load_agent_trace_examples(PROJECT_ROOT)
    observability_otel_spans = load_observability_otel_spans(PROJECT_ROOT)
    observability_trace_index = load_observability_trace_index(PROJECT_ROOT)
    collector_export_preview = load_collector_export_preview(PROJECT_ROOT)
    public_report = load_public_report(PROJECT_ROOT)
    public_report_html = load_public_report_html(PROJECT_ROOT)
    public_report_pdf = load_public_report_pdf(PROJECT_ROOT)
    rows = metric_rows(comparison)
    extraction_rows = extraction_metric_rows(extraction_summary)
    security_rows = security_metric_rows(security_summary)
    agent_rows = agent_metric_rows(agent_summary)
    improved_cases = load_case_rows(PROJECT_ROOT, "improved")
    baseline_cases = load_case_rows(PROJECT_ROOT, "baseline")
    retriever_cases = load_retriever_case_rows(PROJECT_ROOT)

    section = _render_sidebar()
    if section == "Overview":
        _render_reviewer_summary(
            comparison,
            dataset_profile,
            safety_classifier,
            agent_summary,
            evaluation_gates,
            techqa_public,
            wixqa_public,
            public_rag_findings,
            public_rag_reranker,
            public_rag_model_reranker,
            human_calibration,
            external_human_review,
            model_judge_adapter,
            multi_model_comparison,
        )
        _render_summary(
            comparison,
            rows,
            improved_cases,
            safety_classifier,
            agent_summary,
            evaluation_gates,
        )
        _render_dataset_profile_summary(dataset_profile)
        _render_metric_comparison(rows)
        _render_retriever_experiment(retriever_comparison)
    elif section == "Dataset Profile":
        _render_dataset_profile(dataset_profile)
    elif section == "Retrieval Evaluation":
        _render_retriever_experiment(retriever_comparison)
        _render_techqa_public_benchmark(techqa_public)
        _render_wixqa_public_benchmark(wixqa_public)
        _render_public_rag_findings(public_rag_findings)
        _render_public_rag_reranking(public_rag_reranking)
        _render_public_rag_reranker(public_rag_reranker)
        _render_public_rag_model_reranker(public_rag_model_reranker)
        _render_retriever_snapshots(retriever_snapshots)
        _render_evaluation_history(evaluation_history)
        _render_evaluation_gates(evaluation_gates)
        _render_retriever_error_analysis(retriever_cases)
        _render_error_analysis(failure_taxonomy)
    elif section == "Safety & Extraction":
        _render_safety_classifier_workflow(
            safety_classifier,
            safety_threshold_sweep,
            safety_threshold_retuning,
            safety_review_simulation,
            safety_adjudication_notes,
            safety_secondary_review_band,
            safety_secondary_review_validation,
            safety_operating_recommendation,
            safety_mitigation_impact,
            safety_threshold_memo,
            human_calibration,
            external_human_review,
            judge_reliability,
            model_judge_adapter,
            multi_model_comparison,
        )
        _render_extraction_metrics(extraction_summary, extraction_rows)
        _render_security_metrics(security_summary, security_rows)
    elif section == "Intervention Study":
        _render_intervention_study(
            intervention_study,
            rag_grounding_intervention,
            memory_context_intervention,
            goal_conflict_intervention,
        )
    elif section == "Incident Replay":
        _render_incident_replay(
            incident_replay,
            incident_replay_runs,
            incident_trace_events,
            incident_release_gates,
        )
    elif section == "Agent Observability":
        _render_agent_metrics(
            agent_summary,
            agent_rows,
            agent_traces,
            observability_otel_spans,
            observability_trace_index,
            collector_export_preview,
        )
    elif section == "Evaluation Report":
        _render_public_report(public_report, public_report_html, public_report_pdf)
    elif section == "Case Review":
        _render_case_analysis(baseline_cases, improved_cases)


def _render_app_header() -> None:
    st.title("Agent Release Safety Gates")
    st.caption(
        "Public release-readiness dashboard for incident replay, grounded retrieval, "
        "safe refusal, approval-gated tools, safety trade-offs, and observability."
    )
    link_cols = st.columns(4)
    link_cols[0].link_button(
        "Project page",
        "https://rosscyking1115.github.io/internal-ai-agent-eval-lab/",
        use_container_width=True,
    )
    link_cols[1].link_button(
        "Full report",
        "https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.html",
        use_container_width=True,
    )
    link_cols[2].link_button(
        "PDF report",
        "https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.pdf",
        use_container_width=True,
    )
    link_cols[3].link_button(
        "GitHub repo",
        "https://github.com/rosscyking1115/internal-ai-agent-eval-lab",
        use_container_width=True,
    )
    st.info(
        "Controlled runbooks, tickets, teams, procedures, and benchmark metrics are "
        "synthetic. TechQA and WixQA are separate public-data RAG benchmarks. "
        "This project does not reproduce or assess any real company's internal AI system.",
    )


def _render_sidebar() -> str:
    st.sidebar.title("Safety & Reliability Lab")
    section = st.sidebar.radio(
        "View",
        [
            "Overview",
            "Dataset Profile",
            "Retrieval Evaluation",
            "Safety & Extraction",
            "Intervention Study",
            "Incident Replay",
            "Agent Observability",
            "Evaluation Report",
            "Case Review",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.link_button(
        "Project page",
        "https://rosscyking1115.github.io/internal-ai-agent-eval-lab/",
        use_container_width=True,
    )
    st.sidebar.link_button(
        "GitHub repository",
        "https://github.com/rosscyking1115/internal-ai-agent-eval-lab",
        use_container_width=True,
    )
    st.sidebar.caption("Synthetic benchmark plus TechQA and WixQA public validation.")
    return section


def _render_reviewer_summary(
    comparison: dict[str, object],
    dataset_profile: dict[str, object],
    safety_classifier: dict[str, object],
    agent_summary: dict[str, object],
    evaluation_gates: dict[str, object],
    techqa_public: dict[str, object],
    wixqa_public: dict[str, object],
    public_rag_findings: dict[str, object],
    public_rag_reranker: dict[str, object],
    public_rag_model_reranker: dict[str, object],
    human_calibration: dict[str, object],
    external_human_review: dict[str, object],
    model_judge_adapter: dict[str, object],
    multi_model_comparison: dict[str, object],
) -> None:
    st.subheader("Reviewer Summary")
    st.markdown(
        """
        This lab is a reproducible evaluation system for AI-agent safety and reliability.
        It combines a controlled synthetic operations benchmark with public TechQA and WixQA
        retrieval validation, safety-classifier analysis, human-review simulation, hosted
        judge evidence, release gates, and observability artifacts.
        """
    )

    metrics = comparison["metrics"]  # type: ignore[index]
    safety_metrics = safety_classifier["metrics"]  # type: ignore[index]
    agent_metrics = agent_summary["metrics"]  # type: ignore[index]
    public_rag_summary = public_rag_findings.get("summary", {})
    reranker_summary = public_rag_reranker.get("summary", {})
    dataset_counts = dataset_profile["dataset_counts"]  # type: ignore[index]

    evidence_cols = st.columns(4)
    evidence_cols[0].metric(
        "Synthetic eval cases",
        dataset_counts["golden_cases"],  # type: ignore[index]
    )
    evidence_cols[1].metric(
        "Public RAG cases",
        public_rag_summary.get("total_case_count", "Not available")  # type: ignore[union-attr]
        if public_rag_findings.get("status") == "evaluated"
        else "Not available",
    )
    evidence_cols[2].metric(
        "Safety recall",
        _format_pct(float(safety_metrics["recall"])),  # type: ignore[index]
    )
    evidence_cols[3].metric(
        "Gate status",
        _format_status(evaluation_gates.get("overall_status", "")),
    )

    st.markdown("**Current Evidence**")
    st.markdown(
        f"""
        - Improved synthetic citation coverage:
          {_format_pct(float(metrics["citation_coverage"]["improved"]))}
        - Improved synthetic abstention accuracy:
          {_format_pct(float(metrics["abstention_accuracy"]["improved"]))}
        - Agent side-effect block rate:
          {_format_pct(float(agent_metrics["side_effect_block_rate"]))}
        - Public TechQA retrieval@3:
          {_public_metric_text(techqa_public, "retrieval_hit_rate_at_3")}
        - Public WixQA retrieval@3:
          {_public_metric_text(wixqa_public, "retrieval_hit_rate_at_3")}
        - Local public reranker top-1 delta:
          {_public_signed_metric_text(reranker_summary, "top1_accuracy_delta")}
        """
    )

    st.markdown("**Validation Boundary**")
    st.markdown(
        f"""
        - Synthetic operations data is generated and intentionally contains no real
          company, customer, employee, runbook, or ticket data.
        - Public-data validation is currently limited to compact TechQA and WixQA samples.
        - Independent external human-review labels are still pending:
          {_format_status(external_human_review.get("status", "not_configured"))}.
        - Hosted model judge status:
          {_format_status(model_judge_adapter.get("status", "not_configured"))}.
        - Multi-model comparison status:
          {_format_status(multi_model_comparison.get("status", "not_configured"))}.
        - Hosted public RAG reranker status:
          {_format_status(public_rag_model_reranker.get("status", "not_configured"))}.
        """
    )


def _render_summary(
    comparison: dict[str, object],
    rows: list[dict[str, object]],
    improved_cases: list[dict[str, object]],
    safety_classifier: dict[str, object],
    agent_summary: dict[str, object],
    evaluation_gates: dict[str, object],
) -> None:
    mix = case_mix(improved_cases)
    cols = st.columns(4)
    metrics = comparison["metrics"]  # type: ignore[index]
    safety_metrics = safety_classifier["metrics"]  # type: ignore[index]
    agent_metrics = agent_summary["metrics"]  # type: ignore[index]
    citation_coverage = metrics["citation_coverage"]["improved"]  # type: ignore[index]
    safety_recall = safety_metrics["recall"]  # type: ignore[index]
    side_effect_block_rate = agent_metrics["side_effect_block_rate"]  # type: ignore[index]
    cols[0].metric("Golden cases", comparison["case_count"])
    cols[1].metric("Citation coverage", _format_pct(float(citation_coverage)))
    cols[2].metric("Safety recall", _format_pct(float(safety_recall)))
    cols[3].metric("Side-effect block", _format_pct(float(side_effect_block_rate)))

    st.caption(
        "Synthetic operations eval across exact, paraphrased, and weak-evidence cases. "
        "Controlled benchmark data is generated and contains no real company, customer, "
        "or employee information."
    )
    gate_cols = st.columns(4)
    gate_cols[0].metric("Expected abstentions", mix["expected_abstentions"])
    gate_cols[1].metric("Improved failures", mix["failed_cases"])
    gate_cols[2].metric("Gate status", evaluation_gates["overall_status"])
    gate_cols[3].metric("Gate failures", evaluation_gates["fail_count"])
    headline = [
        row
        for row in rows
        if row["metric"] in {"retrieval_hit_rate_at_3", "citation_coverage", "abstention_accuracy"}
    ]
    st.dataframe(
        pd.DataFrame(headline)[["label", "baseline_pct", "improved_pct", "delta_pct"]],
        hide_index=True,
        use_container_width=True,
    )


def _render_metric_comparison(rows: list[dict[str, object]]) -> None:
    st.subheader("Before And After")
    chart_df = pd.DataFrame(rows).set_index("label")[["baseline", "improved"]]
    st.bar_chart(chart_df, height=360)

    table_df = pd.DataFrame(rows)[["label", "baseline_pct", "improved_pct", "delta_pct"]]
    table_df.columns = ["Metric", "Baseline", "Improved lexical", "Delta"]
    st.dataframe(table_df, hide_index=True, use_container_width=True)


def _render_dataset_profile(profile: dict[str, object]) -> None:
    st.subheader("Dataset Profile")
    mix = profile["golden_case_mix"]
    cols = st.columns(5)
    cols[0].metric("Golden cases", profile["dataset_counts"]["golden_cases"])
    cols[1].metric("Manual cases", mix["manual_cases"])
    cols[2].metric("Manual share", f"{mix['manual_share'] * 100:.2f}%")
    cols[3].metric("Noise types", mix["noise_type_count"])
    cols[4].metric("Expected abstentions", mix["expected_abstentions"])

    tab_noise, tab_task, tab_issue, tab_red_team, tab_gaps = st.tabs(
        ["Noise", "Tasks", "Issues", "Red-team", "Gaps"]
    )
    with tab_noise:
        st.dataframe(
            pd.DataFrame(coverage_count_rows(profile, "by_noise_type")),
            hide_index=True,
            use_container_width=True,
        )
    with tab_task:
        st.dataframe(
            pd.DataFrame(coverage_count_rows(profile, "by_task_type")),
            hide_index=True,
            use_container_width=True,
        )
    with tab_issue:
        st.dataframe(
            pd.DataFrame(coverage_count_rows(profile, "by_issue_category")),
            hide_index=True,
            use_container_width=True,
        )
    with tab_red_team:
        risk_rows = red_team_coverage_rows(profile, "by_risk_type")
        st.dataframe(pd.DataFrame(risk_rows), hide_index=True, use_container_width=True)
    with tab_gaps:
        st.table(
            pd.DataFrame({"risk_label": profile["risk_labels"]}),
        )
        st.table(
            pd.DataFrame({"recommended_next_data_work": profile["recommended_next_data_work"]}),
        )


def _render_dataset_profile_summary(profile: dict[str, object]) -> None:
    st.subheader("Benchmark Transparency")
    mix = profile["golden_case_mix"]
    cols = st.columns(4)
    cols[0].metric("Manual golden cases", mix["manual_cases"])
    cols[1].metric("Manual share", f"{mix['manual_share'] * 100:.2f}%")
    cols[2].metric("Noise types", mix["noise_type_count"])
    cols[3].metric("Expected abstentions", mix["expected_abstentions"])
    risk_labels = ", ".join(str(label) for label in profile["risk_labels"])
    st.caption(f"Current data-quality labels: {risk_labels}")


def _render_retriever_experiment(comparison: dict[str, object]) -> None:
    st.subheader("Retriever Experiment")
    rows = retriever_experiment_rows(comparison)
    chart_df = pd.DataFrame(rows).set_index("system")[
        ["retrieval_hit_rate_at_3", "citation_coverage", "next_action_accuracy"]
    ]
    st.bar_chart(chart_df, height=300)

    table_df = pd.DataFrame(rows)[
        [
            "system",
            "retrieval_hit_rate_at_3_pct",
            "citation_coverage_pct",
            "issue_category_accuracy_pct",
            "next_action_accuracy_pct",
            "abstention_accuracy_pct",
            "failure_count",
        ]
    ]
    table_df.columns = [
        "System",
        "Retrieval@3",
        "Citation",
        "Issue",
        "Next action",
        "Abstention",
        "Failures",
    ]
    st.dataframe(table_df, hide_index=True, use_container_width=True)


def _render_techqa_public_benchmark(summary: dict[str, object]) -> None:
    st.subheader("External Public RAG Benchmark")
    if summary.get("status") != "evaluated":
        st.info("TechQA public benchmark is not configured in this runtime.")
        return

    metrics = summary["metrics"]  # type: ignore[index]
    profile = summary.get("benchmark_profile", {})
    cols = st.columns(5)
    cols[0].metric("TechQA cases", summary["case_count"])
    cols[1].metric("Answerable cases", summary["answerable_case_count"])  # type: ignore[index]
    cols[2].metric(
        "Retrieval@3",
        _format_pct(float(metrics["retrieval_hit_rate_at_3"])),  # type: ignore[index]
    )
    cols[3].metric(
        "Impossible abstention",
        _format_pct(float(metrics["impossible_abstention_rate"])),  # type: ignore[index]
    )
    cols[4].metric(
        "Public docs",
        profile.get("unique_document_count", summary.get("document_count", 0)),  # type: ignore[union-attr]
    )
    st.caption(
        "External validation over NVIDIA TechQA-RAG-Eval technical-support questions. "
        "This complements, but does not replace, the controlled synthetic benchmark."
    )
    table_df = pd.DataFrame(techqa_public_metric_rows(summary))
    if not table_df.empty:
        display_df = table_df[["label", "value_pct"]]
        display_df.columns = ["Metric", "Value"]
        st.dataframe(display_df, hide_index=True, use_container_width=True)
    systems_df = pd.DataFrame(summary.get("retriever_systems", []))
    if not systems_df.empty:
        comparison_df = pd.DataFrame(
            [
                {
                    "System": row["label"],
                    "Retrieval@3": _format_pct(
                        float(row["metrics"]["retrieval_hit_rate_at_3"])
                    ),
                    "Top-1 citation": _format_pct(
                        float(row["metrics"]["top1_citation_accuracy"])
                    ),
                    "Impossible abstention": _format_pct(
                        float(row["metrics"]["impossible_abstention_rate"])
                    ),
                    "Failed cases": row["failed_case_count"],
                }
                for row in summary.get("retriever_systems", [])
            ]
        )
        st.dataframe(comparison_df, hide_index=True, use_container_width=True)
    if profile:
        profile_df = pd.DataFrame(
            [
                {
                    "Sample cases": profile.get("sample_case_count", 0),
                    "Impossible share": _format_pct(
                        float(profile.get("impossible_case_share", 0.0))
                    ),
                    "Context coverage": _format_pct(
                        float(profile.get("answerable_context_coverage", 0.0))
                    ),
                    "Failed cases": profile.get("failed_case_count", 0),
                    "Provider result": profile.get(
                        "provider_backed_embedding_result_published",
                        False,
                    ),
                }
            ]
        )
        st.dataframe(profile_df, hide_index=True, use_container_width=True)


def _render_wixqa_public_benchmark(summary: dict[str, object]) -> None:
    st.subheader("WixQA Public Enterprise RAG Benchmark")
    if summary.get("status") != "evaluated":
        st.info("WixQA public benchmark is not configured in this runtime.")
        return

    metrics = summary["metrics"]  # type: ignore[index]
    profile = summary.get("benchmark_profile", {})
    cols = st.columns(5)
    cols[0].metric("WixQA cases", summary["case_count"])
    cols[1].metric("Public docs", summary["document_count"])  # type: ignore[index]
    cols[2].metric(
        "Retrieval@3",
        _format_pct(float(metrics["retrieval_hit_rate_at_3"])),  # type: ignore[index]
    )
    cols[3].metric(
        "Top-1 citation",
        _format_pct(float(metrics["top1_citation_accuracy"])),  # type: ignore[index]
    )
    cols[4].metric(
        "Multi-article cases",
        profile.get("multi_article_case_count", summary.get("multi_article_case_count", 0)),  # type: ignore[union-attr]
    )
    st.caption(
        "External validation over WixQA expert-written enterprise-support questions "
        "grounded in public Wix Help Center articles. This adds real public customer-support "
        "RAG evidence while keeping controlled operations scenarios synthetic."
    )
    table_df = pd.DataFrame(wixqa_public_metric_rows(summary))
    if not table_df.empty:
        display_df = table_df[["label", "value_pct"]]
        display_df.columns = ["Metric", "Value"]
        st.dataframe(display_df, hide_index=True, use_container_width=True)
    systems_df = pd.DataFrame(summary.get("retriever_systems", []))
    if not systems_df.empty:
        comparison_df = pd.DataFrame(
            [
                {
                    "System": row["label"],
                    "Retrieval@3": _format_pct(
                        float(row["metrics"]["retrieval_hit_rate_at_3"])
                    ),
                    "Top-1 citation": _format_pct(
                        float(row["metrics"]["top1_citation_accuracy"])
                    ),
                    "Failed cases": row["failed_case_count"],
                }
                for row in summary.get("retriever_systems", [])
            ]
        )
        st.dataframe(comparison_df, hide_index=True, use_container_width=True)


def _render_public_rag_findings(report: dict[str, object]) -> None:
    st.subheader("Cross-Public RAG Findings")
    if report.get("status") != "evaluated":
        st.info("Cross-public RAG findings are not configured in this runtime.")
        return

    summary = report["summary"]  # type: ignore[index]
    cols = st.columns(5)
    cols[0].metric("Public tracks", summary["evaluated_track_count"])  # type: ignore[index]
    cols[1].metric("Public cases", summary["total_case_count"])  # type: ignore[index]
    cols[2].metric(
        "Weighted RAG@3",
        _format_pct(float(summary["weighted_retrieval_hit_rate_at_3"])),  # type: ignore[index]
    )
    cols[3].metric(
        "Top-1 citation",
        _format_pct(float(summary["weighted_top1_citation_accuracy"])),  # type: ignore[index]
    )
    cols[4].metric("Top failure", summary["top_cross_track_failure_label"])  # type: ignore[index]

    track_df = pd.DataFrame(public_rag_track_rows(report))
    if not track_df.empty:
        st.dataframe(track_df, hide_index=True, use_container_width=True)

    finding_df = pd.DataFrame({"Finding": report.get("findings", [])})
    if not finding_df.empty:
        st.dataframe(finding_df, hide_index=True, use_container_width=True)

    recommendation_df = pd.DataFrame(
        {"Recommended next experiment": report.get("recommendations", [])}
    )
    if not recommendation_df.empty:
        st.dataframe(recommendation_df, hide_index=True, use_container_width=True)


def _render_public_rag_reranking(report: dict[str, object]) -> None:
    st.subheader("Public RAG Reranking Opportunity")
    if report.get("status") != "evaluated":
        st.info("Public RAG reranking opportunity is not configured in this runtime.")
        return

    summary = report["summary"]  # type: ignore[index]
    cols = st.columns(5)
    cols[0].metric("Answerable cases", summary["total_case_count"])  # type: ignore[index]
    cols[1].metric("Rerankable cases", summary["rerankable_case_count"])  # type: ignore[index]
    cols[2].metric(
        "Current top-1",
        _format_pct(float(summary["current_weighted_top1_citation_accuracy"])),  # type: ignore[index]
    )
    cols[3].metric(
        "Top-3 ceiling",
        _format_pct(float(summary["oracle_top3_rerank_ceiling"])),  # type: ignore[index]
    )
    cols[4].metric(
        "Residual gap",
        _format_pct(float(summary["residual_retrieval_gap"])),  # type: ignore[index]
    )

    track_df = pd.DataFrame(public_rag_reranking_track_rows(report))
    if not track_df.empty:
        st.dataframe(track_df, hide_index=True, use_container_width=True)

    finding_df = pd.DataFrame({"Finding": report.get("findings", [])})
    if not finding_df.empty:
        st.dataframe(finding_df, hide_index=True, use_container_width=True)


def _render_public_rag_reranker(report: dict[str, object]) -> None:
    st.subheader("Public RAG Reranker Evaluation")
    if report.get("status") != "evaluated":
        st.info("Public RAG reranker evaluation is not configured in this runtime.")
        return

    summary = report["summary"]  # type: ignore[index]
    cols = st.columns(5)
    cols[0].metric("Cases", summary["total_case_count"])  # type: ignore[index]
    cols[1].metric(
        "Baseline top-1",
        _format_pct(float(summary["baseline_top1_accuracy"])),  # type: ignore[index]
    )
    cols[2].metric(
        "Reranked top-1",
        _format_pct(float(summary["reranked_top1_accuracy"])),  # type: ignore[index]
    )
    cols[3].metric(
        "Top-1 delta",
        _format_signed_pct(float(summary["top1_accuracy_delta"])),  # type: ignore[index]
    )
    cols[4].metric("Regressions", summary["regressed_case_count"])  # type: ignore[index]

    track_df = pd.DataFrame(public_rag_reranker_track_rows(report))
    if not track_df.empty:
        st.dataframe(track_df, hide_index=True, use_container_width=True)

    finding_df = pd.DataFrame({"Finding": report.get("findings", [])})
    if not finding_df.empty:
        st.dataframe(finding_df, hide_index=True, use_container_width=True)


def _render_public_rag_model_reranker(status: dict[str, object]) -> None:
    st.subheader("Hosted Public RAG Reranker Adapter")
    if status.get("status") == "not_configured":
        st.info("Hosted public RAG reranker packet is not configured in this runtime.")
        return

    cols = st.columns(4)
    cols[0].metric("Status", _format_status(status.get("status", "")))
    cols[1].metric("Packet cases", int(status.get("candidate_case_count", 0)))
    cols[2].metric("Estimated calls", int(status.get("estimated_provider_calls", 0)))
    cols[3].metric(
        "Candidate docs",
        int(status.get("estimated_candidate_documents", 0)),
    )

    st.dataframe(
        pd.DataFrame(public_rag_model_reranker_adapter_rows(status)),
        hide_index=True,
        use_container_width=True,
    )
    notes = status.get("notes", [])
    if notes:
        st.dataframe(
            pd.DataFrame({"Note": notes}),
            hide_index=True,
            use_container_width=True,
        )


def _render_retriever_snapshots(snapshot_report: dict[str, object]) -> None:
    st.subheader("Retriever Metric Snapshots")
    rows = retriever_snapshot_rows(snapshot_report)
    table_df = pd.DataFrame(rows)
    if table_df.empty:
        st.info("No retriever metric snapshots recorded.")
        return

    chart_df = table_df.set_index("system")[["citation_coverage"]]
    st.line_chart(chart_df, height=240)

    display_df = table_df[
        [
            "snapshot_id",
            "system",
            "citation_coverage_pct",
            "failure_count",
            "citation_delta_pct",
            "failure_delta",
            "regression",
            "regression_reasons",
        ]
    ]
    display_df.columns = [
        "Snapshot",
        "System",
        "Citation",
        "Failures",
        "Citation delta",
        "Failure delta",
        "Regression",
        "Reason",
    ]
    st.dataframe(display_df, hide_index=True, use_container_width=True)


def _render_evaluation_history(history: dict[str, object]) -> None:
    st.subheader("Evaluation History")
    rows = evaluation_history_rows(history)
    table_df = pd.DataFrame(rows)
    if table_df.empty:
        st.info("No evaluation history milestones recorded.")
        return

    summary = history["current_summary"]
    cols = st.columns(4)
    cols[0].metric("Latest milestone", summary["latest_milestone"])
    cols[1].metric(
        "Current citation",
        f"{summary['current_citation_coverage'] * 100:.2f}%",
    )
    cols[2].metric("Current failures", summary["current_failure_count"])
    cols[3].metric("Best retriever", summary["best_retriever"])

    chart_df = table_df.set_index("milestone_at_utc")[["citation_coverage"]]
    st.line_chart(chart_df, height=240)

    display_df = table_df[
        [
            "milestone_at_utc",
            "milestone",
            "citation_coverage_pct",
            "failure_count",
            "citation_delta_pct",
            "failure_delta",
        ]
    ]
    display_df.columns = [
        "Milestone time",
        "Milestone",
        "Citation",
        "Failures",
        "Citation delta",
        "Failure delta",
    ]
    st.dataframe(display_df, hide_index=True, use_container_width=True)


def _render_evaluation_gates(gates: dict[str, object]) -> None:
    if not gates:
        return

    st.subheader("Evaluation Release Gates")
    cols = st.columns(4)
    cols[0].metric("Overall", str(gates["overall_status"]))
    cols[1].metric("Pass", gates["pass_count"])
    cols[2].metric("Warn", gates["warn_count"])
    cols[3].metric("Fail", gates["fail_count"])

    gate_df = pd.DataFrame(evaluation_gate_rows(gates))
    if not gate_df.empty:
        st.dataframe(gate_df, hide_index=True, use_container_width=True)


def _render_retriever_error_analysis(
    cases_by_system: dict[str, list[dict[str, object]]],
) -> None:
    st.subheader("Retriever Failure Analysis")
    overview_rows = retriever_failure_overview(cases_by_system)
    overview_df = pd.DataFrame(overview_rows)
    if not overview_df.empty:
        overview_df.columns = [
            "System",
            "Failed cases",
            "Retrieved but not cited",
            "Abstention mismatches",
            "Top failure reason",
        ]
        st.dataframe(overview_df, hide_index=True, use_container_width=True)

    example_rows = retriever_failure_example_rows(cases_by_system)
    example_df = pd.DataFrame(example_rows)
    if example_df.empty:
        st.success("No retriever failures recorded.")
        return

    st.dataframe(
        example_df[
            [
                "system",
                "case_id",
                "noise_type",
                "failure_reasons",
                "expected_citation",
                "predicted_citation",
                "retrieved_citations",
                "score_explanation",
                "retrieved_but_not_cited",
                "diagnostic",
                "recommended_fix",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )


def _render_error_analysis(failure_taxonomy: dict[str, object]) -> None:
    st.subheader("Noisy Case And Error Analysis")
    tab_noise, tab_task, tab_failures, tab_taxonomy, tab_examples = st.tabs(
        [
            "Noise types",
            "Task types",
            "Failure reasons",
            "Failure taxonomy",
            "Failure examples",
        ]
    )

    improved_summary = _load_eval_summary("improved_eval_summary.json")

    with tab_noise:
        rows = error_analysis_rows(improved_summary, "by_noise_type")
        table_df = pd.DataFrame(rows)
        if not table_df.empty:
            st.dataframe(
                table_df[
                    [
                        "group",
                        "case_count",
                        "failure_count",
                        "citation_coverage_pct",
                        "abstention_accuracy_pct",
                        "next_action_accuracy_pct",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

    with tab_task:
        rows = error_analysis_rows(improved_summary, "by_task_type")
        table_df = pd.DataFrame(rows)
        if not table_df.empty:
            st.dataframe(
                table_df[
                    [
                        "group",
                        "case_count",
                        "failure_count",
                        "citation_coverage_pct",
                        "abstention_accuracy_pct",
                        "next_action_accuracy_pct",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

    with tab_failures:
        rows = failure_reason_rows(improved_summary)
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.success("No improved-system failure reasons recorded.")

    with tab_taxonomy:
        st.metric("Taxonomy-labeled cases", failure_taxonomy["total_labeled_cases"])
        label_rows = taxonomy_label_rows(failure_taxonomy)
        source_rows = taxonomy_source_rows(failure_taxonomy)
        if label_rows:
            st.dataframe(
                pd.DataFrame(label_rows),
                hide_index=True,
                use_container_width=True,
            )
        if source_rows:
            st.dataframe(
                pd.DataFrame(source_rows),
                hide_index=True,
                use_container_width=True,
            )
        if not label_rows and not source_rows:
            st.info("Failure taxonomy summary is not available yet.")

    with tab_examples:
        rows = failure_example_rows(improved_summary)
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.success("No improved-system failure examples recorded.")


def _render_extraction_metrics(
    summary: dict[str, object],
    rows: list[dict[str, object]],
) -> None:
    st.subheader("Structured Extraction And Routing")
    cols = st.columns(2)
    cols[0].metric("Extraction cases", summary["case_count"])
    cols[1].metric("System", summary["system_version"])

    chart_df = pd.DataFrame(rows).set_index("label")[["value"]]
    st.bar_chart(chart_df, height=280)

    table_df = pd.DataFrame(rows)[["label", "value_pct"]]
    table_df.columns = ["Metric", "Score"]
    st.dataframe(table_df, hide_index=True, use_container_width=True)


def _render_security_metrics(
    summary: dict[str, object],
    rows: list[dict[str, object]],
) -> None:
    st.subheader("Security Red-Team Evaluation")
    cols = st.columns(4)
    cols[0].metric("Red-team cases", summary["case_count"])
    cols[1].metric("Improved block rate", f"{summary['metrics']['improved_block_rate'] * 100:.2f}%")
    cols[2].metric(
        "Weighted safe rate",
        f"{summary['metrics']['improved_weighted_safe_rate'] * 100:.2f}%",
    )
    cols[3].metric("Residual risk", summary["metrics"]["improved_residual_risk_score"])

    chart_df = pd.DataFrame(rows).set_index("label")[["baseline", "improved"]]
    st.bar_chart(chart_df, height=260)

    table_df = pd.DataFrame(rows)[["label", "baseline_pct", "improved_pct"]]
    table_df.columns = ["Metric", "Baseline", "Improved policy"]
    st.dataframe(table_df, hide_index=True, use_container_width=True)

    tab_risk, tab_channel, tab_severity = st.tabs(
        ["Risk types", "Attack channels", "Severity bands"]
    )
    with tab_risk:
        _render_security_breakdown(security_risk_breakdown_rows(summary, "by_risk_type"))
    with tab_channel:
        _render_security_breakdown(security_risk_breakdown_rows(summary, "by_attack_channel"))
    with tab_severity:
        _render_security_breakdown(security_risk_breakdown_rows(summary, "by_risk_severity"))


def _render_safety_classifier_workflow(
    classifier: dict[str, object],
    threshold_sweep: dict[str, object],
    threshold_retuning: dict[str, object],
    review_simulation: dict[str, object],
    adjudication_notes: dict[str, object],
    secondary_review_band: dict[str, object],
    secondary_review_validation: dict[str, object],
    operating_recommendation: dict[str, object],
    mitigation_impact: dict[str, object],
    threshold_memo: dict[str, object],
    human_calibration: dict[str, object],
    external_human_review: dict[str, object],
    judge_reliability: dict[str, object],
    model_judge_adapter: dict[str, object],
    multi_model_comparison: dict[str, object],
) -> None:
    st.subheader("Safety Prevalence And Classifier Workflow")
    metrics = classifier["metrics"]
    prevalence = classifier["weighted_prevalence"]
    review_summary = review_simulation["summary"]
    adjudication_summary = adjudication_notes["summary"]
    secondary_summary = secondary_review_band["summary"]
    validation_summary = secondary_review_validation["summary"]
    operating_summary = operating_recommendation["summary"]
    retuning_summary = threshold_retuning["summary"]
    cols = st.columns(5)
    cols[0].metric("Recall", f"{metrics['recall'] * 100:.2f}%")
    cols[1].metric("False positives", f"{metrics['false_positive_rate'] * 100:.2f}%")
    cols[2].metric("Unsafe prevalence", f"{prevalence['unsafe_prevalence'] * 100:.2f}%")
    cols[3].metric("FN reduction", retuning_summary["false_negative_reduction"])
    cols[4].metric(
        "Review floor",
        "recommended"
        if secondary_summary["secondary_review_floor_recommended"]
        else "not needed",
    )

    st.caption(str(threshold_memo["decision"]))
    (
        tab_thresholds,
        tab_calibration,
        tab_review,
        tab_notes,
        tab_review_band,
        tab_operating,
        tab_impact,
        tab_memo,
    ) = st.tabs(
        [
            "Thresholds",
            "Calibration",
            "Human review",
            "Adjudication notes",
            "Review band",
            "Operating model",
            "Mitigation impact",
            "Decision memo",
        ]
    )
    with tab_thresholds:
        retuning_cols = st.columns(4)
        retuning_cols[0].metric(
            "Legacy recall",
            f"{retuning_summary['legacy_recall'] * 100:.2f}%",
        )
        retuning_cols[1].metric(
            "Retuned recall",
            f"{retuning_summary['tuned_recall'] * 100:.2f}%",
        )
        retuning_cols[2].metric(
            "FN reduction",
            retuning_summary["false_negative_reduction"],
        )
        retuning_cols[3].metric(
            "Benign overblocks",
            retuning_summary["benign_near_miss_false_positive_count"],
        )
        retuning_df = pd.DataFrame(safety_retuning_rows(threshold_retuning))
        if not retuning_df.empty:
            st.dataframe(retuning_df, hide_index=True, use_container_width=True)

        threshold_df = pd.DataFrame(safety_threshold_rows(threshold_sweep))
        if not threshold_df.empty:
            chart_df = threshold_df.set_index("threshold")[
                ["recall", "false_positive_rate", "false_negative_rate", "review_rate"]
            ]
            st.line_chart(chart_df, height=260)
            display_df = threshold_df[
                [
                    "threshold",
                    "policy_label",
                    "precision_pct",
                    "recall_pct",
                    "false_positive_rate_pct",
                    "false_negative_rate_pct",
                    "review_rate_pct",
                    "high_severity_false_negative_count",
                ]
            ]
            display_df.columns = [
                "Threshold",
                "Policy",
                "Precision",
                "Recall",
                "False positive",
                "False negative",
                "Review",
                "High severity FN",
            ]
            st.dataframe(display_df, hide_index=True, use_container_width=True)
    with tab_calibration:
        calibration_summary = human_calibration.get("summary", {})
        if not calibration_summary:
            st.info("Human-label calibration summary is not available yet.")
        else:
            calibration_cols = st.columns(5)
            calibration_cols[0].metric("Cases", calibration_summary["case_count"])
            calibration_cols[1].metric(
                "Label accuracy",
                f"{calibration_summary['classifier_label_accuracy'] * 100:.2f}%",
            )
            calibration_cols[2].metric(
                "Action match",
                f"{calibration_summary['classifier_action_match_rate'] * 100:.2f}%",
            )
            calibration_cols[3].metric(
                "Reviewer agreement",
                f"{calibration_summary['reviewer_agreement_rate'] * 100:.2f}%",
            )
            calibration_cols[4].metric(
                "Unsafe auto-allowed",
                calibration_summary["unsafe_auto_allowed_count"],
            )
            category_df = pd.DataFrame(
                human_calibration_category_rows(human_calibration)
            )
            if not category_df.empty:
                st.dataframe(category_df, hide_index=True, use_container_width=True)
            case_df = pd.DataFrame(human_calibration_case_rows(human_calibration))
            if not case_df.empty:
                st.dataframe(case_df, hide_index=True, use_container_width=True)
            external_summary = external_human_review.get("summary", {})
            st.markdown("**External Human Review**")
            if not external_summary:
                st.info("External human-review summary is not available yet.")
            else:
                external_cols = st.columns(5)
                external_cols[0].metric(
                    "Status",
                    _format_status(external_human_review.get("status", "")),
                )
                external_cols[1].metric(
                    "Reviewers",
                    external_human_review.get("reviewer_count", 0),
                )
                external_cols[2].metric(
                    "Coverage",
                    _format_pct(float(external_summary["external_label_coverage"])),
                )
                external_cols[3].metric(
                    "Pairwise agreement",
                    _format_pct(float(external_summary["pairwise_agreement_rate"])),
                )
                external_cols[4].metric(
                    "Adjudication needed",
                    external_summary["adjudication_required_count"],
                )
                external_detail_cols = st.columns(3)
                external_detail_cols[0].metric(
                    "Two-reviewer cases",
                    external_summary["cases_with_two_or_more_reviewers"],
                )
                external_detail_cols[1].metric(
                    "Cohen kappa",
                    external_summary["pairwise_cohen_kappa"],
                )
                external_detail_cols[2].metric(
                    "Maintainer disagreements",
                    external_summary["external_maintainer_disagreement_count"],
                )
                external_category_df = pd.DataFrame(
                    external_human_review_category_rows(external_human_review)
                )
                if not external_category_df.empty:
                    st.dataframe(
                        external_category_df,
                        hide_index=True,
                        use_container_width=True,
                    )
                external_disagreement_df = pd.DataFrame(
                    external_human_review_disagreement_rows(external_human_review)
                )
                if not external_disagreement_df.empty:
                    st.dataframe(
                        external_disagreement_df,
                        hide_index=True,
                        use_container_width=True,
                    )
                for note in external_human_review.get("notes", []):
                    st.caption(str(note))
            judge_summary = judge_reliability.get("summary", {})
            st.markdown("**Judge Reliability**")
            if not judge_summary:
                st.info("Judge reliability summary is not available yet.")
            else:
                judge_cols = st.columns(5)
                judge_cols[0].metric(
                    "Judge accuracy",
                    f"{judge_summary['judge_label_accuracy'] * 100:.2f}%",
                )
                judge_cols[1].metric(
                    "Classifier accuracy",
                    f"{judge_summary['classifier_label_accuracy'] * 100:.2f}%",
                )
                judge_cols[2].metric(
                    "Judge kappa",
                    judge_summary["judge_kappa_vs_human"],
                )
                judge_cols[3].metric(
                    "Classifier/judge agree",
                    (
                        f"{judge_summary['classifier_judge_agreement_rate'] * 100:.2f}%"
                    ),
                )
                judge_cols[4].metric(
                    "Judge disagreements",
                    judge_summary["judge_disagreement_count"],
                )
                pair_df = pd.DataFrame(judge_reliability_pair_rows(judge_reliability))
                if not pair_df.empty:
                    st.dataframe(pair_df, hide_index=True, use_container_width=True)
                judge_category_df = pd.DataFrame(
                    judge_reliability_category_rows(judge_reliability)
                )
                if not judge_category_df.empty:
                    st.dataframe(
                        judge_category_df,
                        hide_index=True,
                        use_container_width=True,
                    )
                judge_disagreement_df = pd.DataFrame(
                    judge_reliability_disagreement_rows(judge_reliability)
                )
                if not judge_disagreement_df.empty:
                    st.dataframe(
                        judge_disagreement_df,
                        hide_index=True,
                        use_container_width=True,
                    )
            st.markdown("**Hosted Judge Adapter**")
            adapter_df = pd.DataFrame(model_judge_adapter_rows(model_judge_adapter))
            if not adapter_df.empty:
                st.dataframe(adapter_df, hide_index=True, use_container_width=True)
            for note in model_judge_adapter.get("notes", []):
                st.caption(str(note))
            st.markdown("**Multi-Model Comparison Plan**")
            readiness = multi_model_comparison.get("readiness_summary", {})
            if not readiness:
                st.info("Multi-model comparison plan is not configured yet.")
            else:
                plan_cols = st.columns(4)
                plan_cols[0].metric(
                    "Status",
                    _format_status(multi_model_comparison.get("status", "")),
                )
                plan_cols[1].metric(
                    "Target models",
                    multi_model_comparison.get("target_model_count", 0),
                )
                plan_cols[2].metric(
                    "Adapters available",
                    readiness["adapter_available_count"],
                )
                plan_cols[3].metric(
                    "Credentialed results",
                    readiness["credentialed_result_count"],
                )
                target_df = pd.DataFrame(
                    multi_model_comparison_target_rows(multi_model_comparison)
                )
                if not target_df.empty:
                    st.dataframe(target_df, hide_index=True, use_container_width=True)
                for gate in multi_model_comparison.get("publication_gates", []):
                    st.caption(str(gate))
    with tab_review:
        review_cols = st.columns(5)
        review_cols[0].metric(
            "Capacity utilization",
            f"{review_summary['capacity_utilization'] * 100:.2f}%",
        )
        review_cols[1].metric("Disagreements", review_summary["disagreement_count"])
        review_cols[2].metric("Escalations", review_summary["escalation_count"])
        review_cols[3].metric("Unsafe caught", review_summary["unsafe_caught_by_review"])
        review_cols[4].metric("SLA breaches", review_summary["sla_breach_count"])
        review_df = pd.DataFrame(safety_review_case_rows(review_simulation))
        if not review_df.empty:
            st.dataframe(review_df, hide_index=True, use_container_width=True)
    with tab_notes:
        note_cols = st.columns(4)
        note_cols[0].metric("Authored notes", adjudication_summary["adjudication_note_count"])
        note_cols[1].metric(
            "Medium severity notes",
            adjudication_summary["medium_severity_note_count"],
        )
        note_cols[2].metric(
            "Classifier disagreements",
            adjudication_summary["classifier_disagreement_count"],
        )
        note_cols[3].metric(
            "Unsafe found by notes",
            adjudication_summary["unsafe_cases_found_by_notes"],
        )
        note_df = pd.DataFrame(safety_adjudication_note_rows(adjudication_notes))
        if not note_df.empty:
            st.dataframe(note_df, hide_index=True, use_container_width=True)
    with tab_review_band:
        policy = secondary_review_band["candidate_policy"]
        band_cols = st.columns(4)
        band_cols[0].metric(
            "Recommendation",
            "Targeted floor"
            if secondary_summary["secondary_review_floor_recommended"]
            else "Keep current band",
        )
        band_cols[1].metric(
            "Target categories",
            secondary_summary["targeted_category_count"],
        )
        band_cols[2].metric(
            "Unsafe overrides",
            secondary_summary["unsafe_allow_to_block_count"],
        )
        band_cols[3].metric(
            "Benign overrides",
            secondary_summary["benign_review_to_allow_count"],
        )
        st.write(
            "Decision: "
            + str(secondary_summary["recommendation"]).replace("_", " ")
        )
        st.write(
            "Targeted categories: "
            + ", ".join(str(item) for item in secondary_summary["targeted_categories"])
        )
        st.write(
            "Candidate floor: "
            f"{policy['secondary_review_floor']} to {policy['secondary_review_ceiling']} "
            "for medium-severity cases in the targeted categories."
        )
        category_actions = pd.DataFrame(secondary_review_band["category_actions"])
        if not category_actions.empty:
            st.dataframe(category_actions, hide_index=True, use_container_width=True)
        st.markdown("**Validation Slice**")
        validation_cols = st.columns(4)
        validation_cols[0].metric(
            "Unsafe capture",
            f"{validation_summary['unsafe_capture_rate'] * 100:.2f}%",
        )
        validation_cols[1].metric(
            "Unsafe allowed",
            validation_summary["floor_unsafe_allowed_count"],
            delta=-validation_summary["unsafe_allowed_reduction"],
        )
        validation_cols[2].metric(
            "Benign new review",
            validation_summary["benign_new_review_count"],
        )
        validation_cols[3].metric(
            "Validation result",
            str(validation_summary["recommendation"]).replace("_", " "),
        )
        validation_cases = pd.DataFrame(secondary_review_validation["cases"])
        if not validation_cases.empty:
            st.dataframe(validation_cases, hide_index=True, use_container_width=True)
    with tab_operating:
        operating_cols = st.columns(4)
        operating_cols[0].metric(
            "Minimum capacity",
            (
                f"{operating_summary['minimum_reviewer_daily_capacity']} "
                "cases/reviewer/day"
            ),
        )
        operating_cols[1].metric(
            "Recommended utilization",
            f"{operating_summary['recommended_capacity_utilization'] * 100:.2f}%",
        )
        operating_cols[2].metric(
            "Capacity buffer",
            operating_summary["capacity_buffer_cases"],
        )
        operating_cols[3].metric(
            "Backlog days",
            operating_summary["recommended_estimated_backlog_days"],
        )
        st.write(str(operating_summary["decision"]))
        st.write("Staffing assumption: " + str(operating_summary["staffing_assumption"]))
        operating_df = pd.DataFrame(
            safety_operating_recommendation_rows(operating_recommendation)
        )
        if not operating_df.empty:
            st.dataframe(operating_df, hide_index=True, use_container_width=True)
        st.markdown("**Controls**")
        for item in operating_recommendation["operating_controls"]:
            st.write(f"- {item}")
    with tab_impact:
        impact_df = pd.DataFrame(safety_mitigation_rows(mitigation_impact))
        if not impact_df.empty:
            chart_df = impact_df.set_index("scenario")[
                ["unsafe_allowed", "unsafe_intercepted", "overblocks", "manual_touches"]
            ]
            st.bar_chart(chart_df, height=280)
            st.dataframe(impact_df, hide_index=True, use_container_width=True)
    with tab_memo:
        st.markdown("**Rationale**")
        for item in threshold_memo["rationale"]:
            st.write(f"- {item}")
        st.markdown("**Next Threshold Work**")
        for item in threshold_memo["next_threshold_work"]:
            st.write(f"- {item}")


def _render_security_breakdown(rows: list[dict[str, object]]) -> None:
    table_df = pd.DataFrame(rows)
    if table_df.empty:
        st.info("No security breakdown rows recorded.")
        return

    display_df = table_df[
        [
            "group",
            "case_count",
            "max_risk_severity",
            "safe_rate_pct",
            "weighted_safe_rate_pct",
            "residual_risk_score",
        ]
    ]
    display_df.columns = [
        "Group",
        "Cases",
        "Max severity",
        "Safe rate",
        "Weighted safe rate",
        "Residual risk",
    ]
    st.dataframe(display_df, hide_index=True, use_container_width=True)


def _render_intervention_study(
    report: dict[str, object],
    rag_grounding_report: dict[str, object],
    memory_context_report: dict[str, object],
    goal_conflict_report: dict[str, object],
) -> None:
    st.subheader("Safety Intervention Results")
    if report.get("status") == "not_configured":
        st.info("Agent safety intervention study has not been generated yet.")
        return

    st.markdown(str(report["main_finding"]))
    cols = st.columns(3)
    cols[0].metric("Experiments", int(report["experiment_count"]))
    cols[1].metric("Baseline", str(report["baseline_label"]))
    cols[2].metric("Status", str(report["status"]).replace("_", " ").title())

    rows = intervention_experiment_rows(report)
    if rows:
        df = pd.DataFrame(rows)
        display_df = df[
            [
                "experiment",
                "cases",
                "recommended_variant",
                "baseline_value",
                "recommended_value",
                "absolute_improvement",
                "review_burden_per_100",
            ]
        ].rename(
            columns={
                "experiment": "Experiment",
                "cases": "Cases",
                "recommended_variant": "Recommended variant",
                "baseline_value": "Baseline",
                "recommended_value": "Recommended",
                "absolute_improvement": "Delta",
                "review_burden_per_100": "Review burden / 100",
            }
        )
        st.dataframe(display_df, hide_index=True, use_container_width=True)

        chart_df = df.melt(
            id_vars=["experiment"],
            value_vars=["absolute_improvement", "review_burden_per_100"],
            var_name="measure",
            value_name="value",
        )
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("experiment:N", title="Experiment", sort=None),
                y=alt.Y("value:Q", title="Value"),
                color=alt.Color("measure:N", title="Measure"),
                tooltip=["experiment", "measure", "value"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

        with st.expander("Headline findings", expanded=True):
            for row in rows:
                st.markdown(f"- {row['headline']}")

    st.subheader("Evaluation Reliability")
    st.markdown(str(report["responsible_release_boundary"]))
    next_steps = report.get("next_steps", [])
    if next_steps:
        st.markdown("**Next validation work**")
        for item in next_steps:
            st.markdown(f"- {item}")

    _render_rag_grounding_intervention(rag_grounding_report)
    _render_memory_context_intervention(memory_context_report)
    _render_goal_conflict_intervention(goal_conflict_report)


def _render_rag_grounding_intervention(report: dict[str, object]) -> None:
    st.subheader("RAG Grounding And Abstention")
    if report.get("status") != "evaluated":
        st.info("RAG grounding intervention study is not configured in this runtime.")
        return

    summary = report.get("summary", {})
    cols = st.columns(4)
    cols[0].metric("Public RAG cases", int(summary.get("case_count", 0)))
    cols[1].metric(
        "Baseline unsupported",
        _format_pct(float(summary.get("baseline_unsupported_answer_rate", 0.0))),
    )
    cols[2].metric(
        "Moderate unsupported",
        _format_pct(float(summary.get("moderate_unsupported_answer_rate", 0.0))),
    )
    cols[3].metric(
        "Strict review / 100",
        f"{float(summary.get('strict_review_burden_per_100', 0.0)):.2f}",
    )

    rows = rag_grounding_variant_rows(report)
    if not rows:
        return
    df = pd.DataFrame(rows)
    display_df = df[
        [
            "variant",
            "cases",
            "unsupported_answer_rate_pct",
            "useful_answer_rate_pct",
            "false_abstention_or_review_rate_pct",
            "impossible_intercept_rate_pct",
            "review_burden_per_100",
        ]
    ].rename(
        columns={
            "variant": "Variant",
            "cases": "Cases",
            "unsupported_answer_rate_pct": "Unsupported answer",
            "useful_answer_rate_pct": "Useful answer",
            "false_abstention_or_review_rate_pct": "False abstention/review",
            "impossible_intercept_rate_pct": "Impossible intercept",
            "review_burden_per_100": "Review burden / 100",
        }
    )
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    chart_df = df.melt(
        id_vars=["variant"],
        value_vars=[
            "unsupported_answer_rate",
            "useful_answer_rate",
            "false_abstention_or_review_rate",
        ],
        var_name="metric",
        value_name="value",
    )
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("variant:N", title="Variant", sort=None),
            y=alt.Y("value:Q", title="Rate"),
            color=alt.Color("metric:N", title="Metric"),
            tooltip=["variant", "metric", "value"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Grounding findings", expanded=True):
        for item in report.get("findings", []):
            st.markdown(f"- {item}")


def _render_memory_context_intervention(report: dict[str, object]) -> None:
    st.subheader("Memory And Context Pollution")
    if report.get("status") != "evaluated":
        st.info("Memory/context intervention study is not configured in this runtime.")
        return

    summary = report.get("summary", {})
    cols = st.columns(4)
    cols[0].metric("Cases", int(report.get("case_count", 0)))
    cols[1].metric(
        "Baseline polluted follow",
        _format_pct(float(summary.get("baseline_polluted_memory_follow_rate", 0.0))),
    )
    cols[2].metric(
        "Scoped review follow",
        _format_pct(
            float(summary.get("scoped_review_polluted_memory_follow_rate", 0.0))
        ),
    )
    cols[3].metric(
        "Review / 100",
        f"{float(summary.get('scoped_review_review_burden_per_100_cases', 0.0)):.2f}",
    )

    rows = memory_context_variant_rows(report)
    if not rows:
        return
    df = pd.DataFrame(rows)
    display_df = df[
        [
            "variant",
            "cases",
            "polluted_memory_follow_rate_pct",
            "pollution_detection_rate_pct",
            "current_evidence_priority_rate_pct",
            "cross_user_leak_rate_pct",
            "benign_memory_usefulness_rate_pct",
            "review_burden_per_100",
        ]
    ].rename(
        columns={
            "variant": "Variant",
            "cases": "Cases",
            "polluted_memory_follow_rate_pct": "Polluted memory followed",
            "pollution_detection_rate_pct": "Pollution detected",
            "current_evidence_priority_rate_pct": "Current evidence prioritized",
            "cross_user_leak_rate_pct": "Cross-user leak",
            "benign_memory_usefulness_rate_pct": "Benign memory useful",
            "review_burden_per_100": "Review burden / 100",
        }
    )
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    chart_df = df.melt(
        id_vars=["variant"],
        value_vars=[
            "polluted_memory_follow_rate",
            "current_evidence_priority_rate",
            "benign_memory_usefulness_rate",
        ],
        var_name="metric",
        value_name="value",
    )
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("variant:N", title="Variant", sort=None),
            y=alt.Y("value:Q", title="Rate"),
            color=alt.Color("metric:N", title="Metric"),
            tooltip=["variant", "metric", "value"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Memory/context findings", expanded=True):
        for item in report.get("findings", []):
            st.markdown(f"- {item}")


def _render_goal_conflict_intervention(report: dict[str, object]) -> None:
    st.subheader("Goal Conflict Arbitration")
    if report.get("status") != "evaluated":
        st.info("Goal-conflict intervention study is not configured in this runtime.")
        return

    summary = report.get("summary", {})
    cols = st.columns(4)
    cols[0].metric("Cases", int(report.get("case_count", 0)))
    cols[1].metric(
        "Baseline unsafe compliance",
        _format_pct(float(summary.get("baseline_unsafe_goal_compliance_rate", 0.0))),
    )
    cols[2].metric(
        "Layered unsafe compliance",
        _format_pct(float(summary.get("layered_unsafe_goal_compliance_rate", 0.0))),
    )
    cols[3].metric(
        "Review / 100",
        f"{float(summary.get('layered_review_burden_per_100_cases', 0.0)):.2f}",
    )

    rows = goal_conflict_variant_rows(report)
    if not rows:
        return
    df = pd.DataFrame(rows)
    display_df = df[
        [
            "variant",
            "cases",
            "unsafe_goal_compliance_rate_pct",
            "conflict_detection_rate_pct",
            "safe_alternative_rate_pct",
            "high_risk_action_block_rate_pct",
            "benign_completion_rate_pct",
            "review_burden_per_100",
        ]
    ].rename(
        columns={
            "variant": "Variant",
            "cases": "Cases",
            "unsafe_goal_compliance_rate_pct": "Unsafe goal complied",
            "conflict_detection_rate_pct": "Conflict detected",
            "safe_alternative_rate_pct": "Safe alternative",
            "high_risk_action_block_rate_pct": "High-risk action blocked",
            "benign_completion_rate_pct": "Benign goal completed",
            "review_burden_per_100": "Review burden / 100",
        }
    )
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    chart_df = df.melt(
        id_vars=["variant"],
        value_vars=[
            "unsafe_goal_compliance_rate",
            "conflict_detection_rate",
            "benign_completion_rate",
        ],
        var_name="metric",
        value_name="value",
    )
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("variant:N", title="Variant", sort=None),
            y=alt.Y("value:Q", title="Rate"),
            color=alt.Color("metric:N", title="Metric"),
            tooltip=["variant", "metric", "value"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Goal-conflict findings", expanded=True):
        for item in report.get("findings", []):
            st.markdown(f"- {item}")


def _render_incident_replay(
    summary: dict[str, object],
    replay_runs: list[dict[str, object]],
    trace_events: list[dict[str, object]],
    release_gates: dict[str, object],
) -> None:
    st.subheader("Incident Replay Workspace")
    if summary.get("status") != "evaluated":
        st.info("Incident replay suite has not been generated yet.")
        return

    metrics_obj = summary.get("summary", {})
    metrics = metrics_obj if isinstance(metrics_obj, dict) else {}
    cols = st.columns(5)
    cols[0].metric("Incidents", int(summary.get("case_count", 0)))
    cols[1].metric(
        "Gate status",
        _format_status(metrics.get("release_gate_status", "not_configured")),
    )
    cols[2].metric(
        "Closure rate",
        _format_pct(float(metrics.get("incident_closure_rate", 0.0))),
    )
    cols[3].metric(
        "Must-not violations",
        int(metrics.get("must_not_violation_count", 0)),
    )
    cols[4].metric(
        "Trace coverage",
        _format_pct(float(metrics.get("trace_event_coverage_rate", 0.0))),
    )

    st.markdown(
        """
        Replay redacted incident fixtures against the current controlled agent,
        inspect the original trace evidence, and decide whether the release gate
        should stay open.
        """
    )

    run_rows = incident_replay_run_rows(replay_runs)
    if not run_rows:
        st.info("No incident replay runs are available.")
        return

    selected_label = st.selectbox(
        "Incident",
        [
            (
                f"{row['incident_id']} | {row['severity']} | "
                f"{row['original_decision']} -> {row['decision']}"
            )
            for row in run_rows
        ],
    )
    selected_incident_id = selected_label.split(" | ", maxsplit=1)[0]
    selected_run = next(
        row for row in replay_runs if row["incident_id"] == selected_incident_id
    )
    selected_display = next(
        row for row in run_rows if row["incident_id"] == selected_incident_id
    )
    selected_trace_rows = [
        row
        for row in incident_trace_event_rows(trace_events)
        if row["incident_id"] == selected_incident_id
    ]

    tabs = st.tabs(
        [
            "Incident queue",
            "Replay matrix",
            "Trace timeline",
            "Decision memo",
            "Release gates",
        ]
    )

    with tabs[0]:
        _render_incident_queue(run_rows, selected_display)

    with tabs[1]:
        _render_incident_replay_matrix(selected_run, run_rows)

    with tabs[2]:
        _render_incident_trace_timeline(selected_run, selected_trace_rows)

    with tabs[3]:
        _render_incident_decision_memo(summary, selected_incident_id)

    with tabs[4]:
        _render_incident_release_gates(summary, release_gates)


def _render_incident_queue(
    run_rows: list[dict[str, object]],
    selected_display: dict[str, object],
) -> None:
    selected_cols = st.columns(4)
    selected_cols[0].metric("Selected", selected_display["incident_id"])
    selected_cols[1].metric("Severity", selected_display["severity"])
    selected_cols[2].metric("Replay decision", selected_display["decision"])
    selected_cols[3].metric(
        "Status",
        "Closed" if selected_display["closed_by_replay"] else "Review",
    )

    queue_df = pd.DataFrame(run_rows)
    queue_df["review_status"] = queue_df.apply(
        lambda row: "Closed"
        if bool(row["closed_by_replay"])
        else "Review required",
        axis=1,
    )
    display_df = queue_df[
        [
            "incident_id",
            "severity",
            "review_status",
            "original_decision",
            "decision",
            "expected_behavior_match",
            "must_not_violations",
            "risk_categories",
            "regression_case",
        ]
    ].rename(
        columns={
            "incident_id": "Incident",
            "severity": "Severity",
            "review_status": "Queue status",
            "original_decision": "Original",
            "decision": "Replay",
            "expected_behavior_match": "Expected match",
            "must_not_violations": "Replay violations",
            "risk_categories": "Risk categories",
            "regression_case": "Regression fixture",
        }
    )
    st.dataframe(display_df, hide_index=True, use_container_width=True)


def _render_incident_replay_matrix(
    selected_run: dict[str, object],
    run_rows: list[dict[str, object]],
) -> None:
    matrix_df = pd.DataFrame(run_rows)
    st.dataframe(
        matrix_df[
            [
                "incident_id",
                "severity",
                "original_decision",
                "decision",
                "closed_by_replay",
                "diff_summary",
            ]
        ].rename(
            columns={
                "incident_id": "Incident",
                "severity": "Severity",
                "original_decision": "Original",
                "decision": "Replay",
                "closed_by_replay": "Closed",
                "diff_summary": "Replay finding",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("**Selected replay controls**")
    control_cols = st.columns(4)
    control_cols[0].metric("Expected behavior", selected_run["expected_behavior"])
    control_cols[1].metric(
        "Expected matched",
        "Yes" if selected_run["expected_behavior_match"] else "No",
    )
    control_cols[2].metric("Audit events", selected_run["audit_event_count"])
    control_cols[3].metric("Citations", selected_run["citation_count"])

    tool_outcomes = selected_run.get("tool_outcomes", [])
    if isinstance(tool_outcomes, list) and tool_outcomes:
        tool_df = pd.DataFrame(tool_outcomes)
        st.dataframe(
            tool_df.rename(
                columns={
                    "tool": "Tool",
                    "tool_type": "Type",
                    "requires_approval": "Requires approval",
                    "approval_granted": "Approval granted",
                    "executed": "Executed",
                    "blocked_reason": "Blocked reason",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("This replay blocked before tool execution.")


def _render_incident_trace_timeline(
    selected_run: dict[str, object],
    trace_rows: list[dict[str, object]],
) -> None:
    if trace_rows:
        trace_df = pd.DataFrame(trace_rows)
        chart = (
            alt.Chart(trace_df)
            .mark_circle(size=170)
            .encode(
                x=alt.X("event_seq:O", title="Event"),
                y=alt.Y("actor:N", title="Actor"),
                color=alt.Color("event_type:N", title="Event type"),
                size=alt.Size("risk_score:Q", title="Risk score"),
                tooltip=[
                    "event_seq",
                    "actor",
                    "event_type",
                    "risk_score",
                    "requires_approval",
                    "tool_name",
                    "content",
                ],
            )
            .properties(height=240)
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(
            trace_df[
                [
                    "event_seq",
                    "timestamp_utc",
                    "actor",
                    "event_type",
                    "risk_score",
                    "requires_approval",
                    "tool_name",
                    "content",
                ]
            ].rename(
                columns={
                    "event_seq": "Seq",
                    "timestamp_utc": "Timestamp",
                    "actor": "Actor",
                    "event_type": "Event type",
                    "risk_score": "Risk",
                    "requires_approval": "Approval needed",
                    "tool_name": "Tool",
                    "content": "Evidence",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No original trace events are attached to this incident.")

    replay_steps = _incident_replay_step_rows(selected_run)
    if replay_steps:
        st.markdown("**Replay lane**")
        st.dataframe(
            pd.DataFrame(replay_steps),
            hide_index=True,
            use_container_width=True,
        )


def _render_incident_decision_memo(
    summary: dict[str, object],
    selected_incident_id: str,
) -> None:
    memo_path = _memo_path_for_incident(summary, selected_incident_id)
    if not memo_path:
        st.info("No generated memo path is available for this incident.")
        return
    memo = _read_text_artifact(PROJECT_ROOT / memo_path)
    st.caption(str(memo_path))
    if memo:
        st.markdown(memo)
    else:
        st.info("Memo file is listed but not present in this runtime.")


def _render_incident_release_gates(
    summary: dict[str, object],
    release_gates: dict[str, object],
) -> None:
    if release_gates:
        gate_cols = st.columns(4)
        gate_cols[0].metric("Overall", _format_status(release_gates["overall_status"]))
        gate_cols[1].metric("Pass", release_gates["pass_count"])
        gate_cols[2].metric("Warn", release_gates["warn_count"])
        gate_cols[3].metric("Fail", release_gates["fail_count"])
        gate_df = pd.DataFrame(evaluation_gate_rows(release_gates))
        if not gate_df.empty:
            st.dataframe(gate_df, hide_index=True, use_container_width=True)
    else:
        st.info("Incident release gates are not available.")

    st.markdown("**Findings and recommendations**")
    for item in summary.get("findings", []):
        st.markdown(f"- {item}")
    for item in summary.get("recommendations", []):
        st.markdown(f"- {item}")


def _incident_replay_step_rows(selected_run: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "Step": 1,
            "Replay stage": "Decision",
            "Outcome": _format_status(str(selected_run["decision"])),
            "Detail": selected_run["diff_summary"],
        }
    ]
    tool_outcomes = selected_run.get("tool_outcomes", [])
    if isinstance(tool_outcomes, list):
        for index, row in enumerate(tool_outcomes, start=2):
            if not isinstance(row, dict):
                continue
            outcome = "Executed" if row.get("executed") else "Blocked"
            rows.append(
                {
                    "Step": index,
                    "Replay stage": row.get("tool", "tool"),
                    "Outcome": outcome,
                    "Detail": row.get("blocked_reason") or row.get("tool_type", ""),
                }
            )
    return rows


def _memo_path_for_incident(
    summary: dict[str, object],
    selected_incident_id: str,
) -> Path | None:
    memo_paths = summary.get("memo_paths", [])
    if not isinstance(memo_paths, list):
        return None
    for path in memo_paths:
        candidate = Path(str(path))
        if selected_incident_id in candidate.name:
            return candidate
    return None


def _render_agent_metrics(
    summary: dict[str, object],
    rows: list[dict[str, object]],
    traces: list[dict[str, object]],
    otel_spans: list[dict[str, object]],
    trace_index: dict[str, object],
    collector_preview: dict[str, object],
) -> None:
    st.subheader("Controlled Agent And Tool Governance")
    cols = st.columns(2)
    cols[0].metric("Agent cases", summary["case_count"])
    cols[1].metric(
        "Side-effect block rate",
        f"{summary['metrics']['side_effect_block_rate'] * 100:.2f}%",
    )

    chart_df = pd.DataFrame(rows).set_index("label")[["value"]]
    st.bar_chart(chart_df, height=280)

    table_df = pd.DataFrame(rows)[["label", "value_pct"]]
    table_df.columns = ["Metric", "Score"]
    st.dataframe(table_df, hide_index=True, use_container_width=True)

    trace_rows = agent_trace_rows(traces)
    if trace_rows:
        st.dataframe(pd.DataFrame(trace_rows), hide_index=True, use_container_width=True)

    otel_summary = agent_otel_summary(otel_spans)
    if otel_summary["span_count"]:
        cols = st.columns(5)
        cols[0].metric("OTel-style spans", f"{otel_summary['span_count']:,}")
        cols[1].metric("Exported traces", f"{otel_summary['trace_count']:,}")
        cols[2].metric("Root spans", f"{otel_summary['root_span_count']:,}")
        cols[3].metric("Child spans", f"{otel_summary['child_span_count']:,}")
        cols[4].metric("Tool spans", f"{otel_summary['tool_span_count']:,}")
        if collector_preview:
            collector_cols = st.columns(4)
            collector_cols[0].metric(
                "Collector payloads",
                f"{collector_preview['payload_count']:,}",
            )
            collector_cols[1].metric(
                "Collector span count",
                f"{collector_preview['span_count']:,}",
            )
            collector_cols[2].metric(
                "Collector mode",
                str(collector_preview["export_mode"]),
            )
            collector_cols[3].metric(
                "Batch size",
                f"{collector_preview['batch_size']:,}",
            )
        component_df = pd.DataFrame(observability_component_rows(otel_spans))
        if not component_df.empty:
            st.dataframe(component_df, hide_index=True, use_container_width=True)
        _render_trace_index(trace_index)
        _render_agent_trace_timeline(otel_spans)
        st.dataframe(
            pd.DataFrame(agent_otel_span_rows(otel_spans)),
            hide_index=True,
            use_container_width=True,
        )


def _render_trace_index(trace_index: dict[str, object]) -> None:
    if not trace_index:
        return

    st.subheader("Local Trace Index")
    cols = st.columns(4)
    cols[0].metric("Indexed traces", f"{trace_index['trace_count']:,}")
    cols[1].metric("Indexed spans", f"{trace_index['span_count']:,}")
    cols[2].metric("Error spans", f"{trace_index['error_span_count']:,}")
    cols[3].metric("Components", f"{trace_index['component_count']:,}")

    tab_traces, tab_errors, tab_components, tab_queries = st.tabs(
        ["Traces", "Errors", "Components", "Queries"]
    )
    with tab_traces:
        trace_df = pd.DataFrame(trace_index_trace_rows(trace_index))
        if not trace_df.empty:
            st.dataframe(
                trace_df[
                    [
                        "trace_label",
                        "root_span_name",
                        "component",
                        "span_count",
                        "error_span_count",
                        "duration_ms",
                        "first_error_span",
                        "first_error_case_id",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )
    with tab_errors:
        error_df = pd.DataFrame(trace_index_error_rows(trace_index))
        if not error_df.empty:
            st.dataframe(
                error_df[
                    [
                        "trace_label",
                        "name",
                        "component",
                        "case_id",
                        "ticket_id",
                        "failure_reasons",
                        "http_route",
                        "http_status_code",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("No error spans indexed.")
    with tab_components:
        component_df = pd.DataFrame(trace_index_component_rows(trace_index))
        if not component_df.empty:
            st.dataframe(component_df, hide_index=True, use_container_width=True)
    with tab_queries:
        query_df = pd.DataFrame(trace_index_query_rows(trace_index))
        if not query_df.empty:
            st.dataframe(query_df, hide_index=True, use_container_width=True)


def _render_agent_trace_timeline(otel_spans: list[dict[str, object]]) -> None:
    timeline_rows = agent_otel_timeline_rows(otel_spans)
    if not timeline_rows:
        return

    timeline_df = pd.DataFrame(timeline_rows)
    trace_labels = sorted(
        timeline_df["trace_label"].drop_duplicates().tolist(),
        key=lambda label: (label != "evaluation_run", label),
    )
    selected_trace = st.selectbox("Trace timeline", trace_labels)
    selected_df = timeline_df[timeline_df["trace_label"] == selected_trace].copy()
    selected_df = selected_df.sort_values("span_order")
    y_sort = selected_df["span_label"].tolist()

    chart = (
        alt.Chart(selected_df)
        .mark_bar(cornerRadius=2)
        .encode(
            x=alt.X("start_ms:Q", title="Start (ms)"),
            x2=alt.X2("end_ms:Q"),
            y=alt.Y("span_label:N", sort=y_sort, title="Span"),
            color=alt.Color("outcome:N", title="Outcome"),
            tooltip=[
                alt.Tooltip("trace_label:N", title="Trace"),
                alt.Tooltip("ticket_id:N", title="Ticket"),
                alt.Tooltip("name:N", title="Span"),
                alt.Tooltip("outcome:N", title="Outcome"),
                alt.Tooltip("start_ms:Q", title="Start ms"),
                alt.Tooltip("duration_ms:Q", title="Duration ms"),
                alt.Tooltip("span_id:N", title="Span id"),
                alt.Tooltip("parent_span_id:N", title="Parent span id"),
            ],
        )
        .properties(height=240)
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(
        selected_df[
            [
                "span_order",
                "name",
                "outcome",
                "start_ms",
                "duration_ms",
                "span_id",
                "parent_span_id",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )


def _render_public_report(
    report_markdown: str,
    report_html: str,
    report_pdf: bytes,
) -> None:
    st.subheader("Evaluation Report")
    col_markdown, col_html, col_pdf = st.columns(3)
    col_markdown.download_button(
        "Download Markdown",
        data=report_markdown,
        file_name="agent_release_safety_gates_report.md",
        mime="text/markdown",
    )
    col_html.download_button(
        "Download HTML",
        data=report_html,
        file_name="agent_release_safety_gates_report.html",
        mime="text/html",
    )
    col_pdf.download_button(
        "Download PDF",
        data=report_pdf,
        file_name="agent_release_safety_gates_report.pdf",
        mime="application/pdf",
    )
    st.markdown(report_markdown)


def _render_case_analysis(
    baseline_cases: list[dict[str, object]],
    improved_cases: list[dict[str, object]],
) -> None:
    st.subheader("Case Analysis")
    tab_baseline, tab_improved = st.tabs(["Baseline failures", "Improved failures"])
    with tab_baseline:
        _render_failures(baseline_cases)
    with tab_improved:
        _render_failures(improved_cases)


def _render_failures(cases: list[dict[str, object]]) -> None:
    failures = failed_case_rows(cases)
    if not failures:
        st.success("No failed cases in the displayed slice.")
        return

    df = pd.DataFrame(failures)
    columns = [
        "case_id",
        "expected_abstain",
        "abstained",
        "expected_citation_ids",
        "predicted_citation_ids",
        "expected_issue_category",
        "predicted_issue_category",
        "expected_team",
        "predicted_team",
    ]
    st.dataframe(df[columns], hide_index=True, use_container_width=True)


def _load_eval_summary(filename: str) -> dict[str, object]:
    path = PROJECT_ROOT / "reports" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _read_text_artifact(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _format_signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"


def _public_metric_text(report: dict[str, object], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not available"
    metrics = report.get("metrics", {})
    if not isinstance(metrics, dict) or metric not in metrics:
        return "Not available"
    return _format_pct(float(metrics[metric]))


def _public_signed_metric_text(summary: object, metric: str) -> str:
    if not isinstance(summary, dict) or metric not in summary:
        return "Not available"
    return _format_signed_pct(float(summary[metric]))


def _format_status(status: object) -> str:
    labels = {
        "awaiting_labels": "Awaiting independent labels",
        "dry_run_ready": "Ready for credentialed run",
        "dry_run_preview": "Prepared preview",
        "not_configured": "Not available",
        "not_published": "Not yet published",
        "pass_with_warnings": "Pass with warnings",
        "blocking": "Blocking",
        "non_blocking": "Non-blocking",
        "completed": "Completed",
        "evaluated": "Evaluated",
    }
    value = str(status)
    if "_" not in value:
        return labels.get(value, value)
    return labels.get(value, value.replace("_", " ").title())


if __name__ == "__main__":
    main()
