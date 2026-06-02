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
    error_analysis_rows,
    evaluation_history_rows,
    extraction_metric_rows,
    failed_case_rows,
    failure_example_rows,
    failure_reason_rows,
    load_agent_summary,
    load_agent_trace_examples,
    load_case_rows,
    load_comparison,
    load_evaluation_history,
    load_extraction_summary,
    load_observability_otel_spans,
    load_public_report,
    load_public_report_html,
    load_public_report_pdf,
    load_retriever_case_rows,
    load_retriever_comparison,
    load_retriever_snapshots,
    load_security_summary,
    metric_rows,
    observability_component_rows,
    retriever_experiment_rows,
    retriever_failure_example_rows,
    retriever_failure_overview,
    retriever_snapshot_rows,
    security_metric_rows,
    security_risk_breakdown_rows,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    st.set_page_config(
        page_title="Internal AI Agent Evaluation Lab",
        layout="wide",
    )
    st.title("Internal AI Agent Evaluation Lab")
    st.caption("Project 5: synthetic internal AI agent evaluation dashboard")

    comparison = load_comparison(PROJECT_ROOT)
    retriever_comparison = load_retriever_comparison(PROJECT_ROOT)
    retriever_snapshots = load_retriever_snapshots(PROJECT_ROOT)
    evaluation_history = load_evaluation_history(PROJECT_ROOT)
    extraction_summary = load_extraction_summary(PROJECT_ROOT)
    security_summary = load_security_summary(PROJECT_ROOT)
    agent_summary = load_agent_summary(PROJECT_ROOT)
    agent_traces = load_agent_trace_examples(PROJECT_ROOT)
    observability_otel_spans = load_observability_otel_spans(PROJECT_ROOT)
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

    _render_summary(comparison, rows, improved_cases)
    _render_metric_comparison(rows)
    _render_retriever_experiment(retriever_comparison)
    _render_retriever_snapshots(retriever_snapshots)
    _render_evaluation_history(evaluation_history)
    _render_retriever_error_analysis(retriever_cases)
    _render_error_analysis()
    _render_extraction_metrics(extraction_summary, extraction_rows)
    _render_security_metrics(security_summary, security_rows)
    _render_agent_metrics(agent_summary, agent_rows, agent_traces, observability_otel_spans)
    _render_public_report(public_report, public_report_html, public_report_pdf)
    _render_case_analysis(baseline_cases, improved_cases)


def _render_summary(
    comparison: dict[str, object],
    rows: list[dict[str, object]],
    improved_cases: list[dict[str, object]],
) -> None:
    mix = case_mix(improved_cases)
    cols = st.columns(4)
    cols[0].metric("Eval cases", comparison["case_count"])
    cols[1].metric("Answerable", mix["answerable_cases"])
    cols[2].metric("Expected abstentions", mix["expected_abstentions"])
    cols[3].metric("Improved failures", mix["failed_cases"])

    st.caption(
        "Synthetic operations eval across exact, paraphrased, and weak-evidence cases. "
        "All data is generated and contains no real company, customer, or employee information."
    )
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
        component_df = pd.DataFrame(observability_component_rows(otel_spans))
        if not component_df.empty:
            st.dataframe(component_df, hide_index=True, use_container_width=True)
        _render_agent_trace_timeline(otel_spans)
        st.dataframe(
            pd.DataFrame(agent_otel_span_rows(otel_spans)),
            hide_index=True,
            use_container_width=True,
        )


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


if __name__ == "__main__":
    main()
