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
    extraction_metric_rows,
    failed_case_rows,
    failure_example_rows,
    failure_reason_rows,
    load_agent_summary,
    load_agent_trace_examples,
    load_case_rows,
    load_collector_export_preview,
    load_comparison,
    load_dataset_profile,
    load_evaluation_gates,
    load_evaluation_history,
    load_extraction_summary,
    load_observability_otel_spans,
    load_observability_trace_index,
    load_public_report,
    load_public_report_html,
    load_public_report_pdf,
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
    metric_rows,
    observability_component_rows,
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
    techqa_public_metric_rows,
    trace_index_component_rows,
    trace_index_error_rows,
    trace_index_query_rows,
    trace_index_trace_rows,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    st.set_page_config(
        page_title="Internal AI Agent Evaluation Lab",
        layout="wide",
    )
    _render_app_header()

    comparison = load_comparison(PROJECT_ROOT)
    dataset_profile = load_dataset_profile(PROJECT_ROOT)
    retriever_comparison = load_retriever_comparison(PROJECT_ROOT)
    retriever_snapshots = load_retriever_snapshots(PROJECT_ROOT)
    techqa_public = load_techqa_public_summary(PROJECT_ROOT)
    evaluation_history = load_evaluation_history(PROJECT_ROOT)
    evaluation_gates = load_evaluation_gates(PROJECT_ROOT)
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
        _render_retriever_snapshots(retriever_snapshots)
        _render_evaluation_history(evaluation_history)
        _render_evaluation_gates(evaluation_gates)
        _render_retriever_error_analysis(retriever_cases)
        _render_error_analysis()
    elif section == "Safety And Extraction":
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
        )
        _render_extraction_metrics(extraction_summary, extraction_rows)
        _render_security_metrics(security_summary, security_rows)
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
    st.title("Internal AI Agent Evaluation Lab")
    st.caption(
        "Synthetic evaluation dashboard for grounded retrieval, structured extraction, "
        "safety controls, approval-gated tools, and observability."
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
        "Internal runbooks, tickets, teams, procedures, and internal benchmark metrics are "
        "synthetic. The TechQA section is a separate public technical-support benchmark. "
        "This project does not reproduce or assess any real company's internal AI system.",
    )


def _render_sidebar() -> str:
    st.sidebar.title("Evaluation Lab")
    section = st.sidebar.radio(
        "View",
        [
            "Overview",
            "Dataset Profile",
            "Retrieval Evaluation",
            "Safety And Extraction",
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
    st.sidebar.caption("Synthetic internal benchmark plus public TechQA external benchmark.")
    return section


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
        "Internal benchmark data is generated and contains no real company, customer, "
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
    cols = st.columns(4)
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
    st.caption(
        "External validation over NVIDIA TechQA-RAG-Eval technical-support questions. "
        "This complements, but does not replace, the controlled synthetic internal benchmark."
    )
    table_df = pd.DataFrame(techqa_public_metric_rows(summary))
    if not table_df.empty:
        display_df = table_df[["label", "value_pct"]]
        display_df.columns = ["Metric", "Value"]
        st.dataframe(display_df, hide_index=True, use_container_width=True)


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


def _render_error_analysis() -> None:
    st.subheader("Noisy Case And Error Analysis")
    tab_noise, tab_task, tab_failures, tab_examples = st.tabs(
        ["Noise types", "Task types", "Failure reasons", "Failure examples"]
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
        tab_review,
        tab_notes,
        tab_review_band,
        tab_operating,
        tab_impact,
        tab_memo,
    ) = st.tabs(
        [
            "Thresholds",
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
        file_name="internal_ai_agent_evaluation_report.md",
        mime="text/markdown",
    )
    col_html.download_button(
        "Download HTML",
        data=report_html,
        file_name="internal_ai_agent_evaluation_report.html",
        mime="text/html",
    )
    col_pdf.download_button(
        "Download PDF",
        data=report_pdf,
        file_name="internal_ai_agent_evaluation_report.pdf",
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


if __name__ == "__main__":
    main()
