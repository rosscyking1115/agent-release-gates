from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from internal_ai_agent.dashboard.data import (
    agent_metric_rows,
    case_mix,
    error_analysis_rows,
    extraction_metric_rows,
    failed_case_rows,
    failure_example_rows,
    failure_reason_rows,
    load_agent_summary,
    load_case_rows,
    load_comparison,
    load_extraction_summary,
    load_retriever_comparison,
    load_security_summary,
    metric_rows,
    retriever_experiment_rows,
    security_metric_rows,
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
    extraction_summary = load_extraction_summary(PROJECT_ROOT)
    security_summary = load_security_summary(PROJECT_ROOT)
    agent_summary = load_agent_summary(PROJECT_ROOT)
    rows = metric_rows(comparison)
    extraction_rows = extraction_metric_rows(extraction_summary)
    security_rows = security_metric_rows(security_summary)
    agent_rows = agent_metric_rows(agent_summary)
    improved_cases = load_case_rows(PROJECT_ROOT, "improved")
    baseline_cases = load_case_rows(PROJECT_ROOT, "baseline")

    _render_summary(comparison, rows, improved_cases)
    _render_metric_comparison(rows)
    _render_retriever_experiment(retriever_comparison)
    _render_error_analysis()
    _render_extraction_metrics(extraction_summary, extraction_rows)
    _render_security_metrics(security_summary, security_rows)
    _render_agent_metrics(agent_summary, agent_rows)
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
    cols = st.columns(2)
    cols[0].metric("Red-team cases", summary["case_count"])
    cols[1].metric("Improved block rate", f"{summary['metrics']['improved_block_rate'] * 100:.2f}%")

    chart_df = pd.DataFrame(rows).set_index("label")[["baseline", "improved"]]
    st.bar_chart(chart_df, height=260)

    table_df = pd.DataFrame(rows)[["label", "baseline_pct", "improved_pct"]]
    table_df.columns = ["Metric", "Baseline", "Improved policy"]
    st.dataframe(table_df, hide_index=True, use_container_width=True)


def _render_agent_metrics(
    summary: dict[str, object],
    rows: list[dict[str, object]],
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
