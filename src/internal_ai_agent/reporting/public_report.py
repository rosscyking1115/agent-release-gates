from __future__ import annotations

import json
from html import escape
from pathlib import Path
from textwrap import wrap
from typing import Any

from internal_ai_agent.dashboard.data import (
    agent_otel_summary,
    agent_trace_rows,
    coverage_count_rows,
    evaluation_gate_rows,
    evaluation_history_rows,
    load_agent_trace_examples,
    load_dataset_profile,
    load_evaluation_gates,
    load_observability_otel_spans,
    load_observability_trace_index,
    load_retriever_case_rows,
    red_team_coverage_rows,
    retriever_failure_example_rows,
    retriever_failure_overview,
    retriever_snapshot_rows,
    safety_adjudication_note_rows,
    safety_mitigation_rows,
    safety_operating_recommendation_rows,
    safety_retuning_rows,
    safety_review_case_rows,
    safety_threshold_rows,
    security_risk_breakdown_rows,
    trace_index_component_rows,
    trace_index_query_rows,
)

METRIC_LABELS = {
    "retrieval_hit_rate_at_3": "Retrieval hit rate@3",
    "citation_coverage": "Citation coverage",
    "issue_category_accuracy": "Issue category accuracy",
    "next_action_accuracy": "Next action accuracy",
    "abstention_accuracy": "Abstention accuracy",
}

EXTRACTION_METRIC_LABELS = {
    "schema_validity": "Schema validity",
    "issue_category_accuracy": "Issue category accuracy",
    "severity_accuracy": "Severity accuracy",
    "impacted_system_accuracy": "Impacted system accuracy",
    "routing_team_accuracy": "Routing team accuracy",
}

AGENT_METRIC_LABELS = {
    "trace_coverage_rate": "Trace coverage",
    "audit_event_coverage_rate": "Audit event coverage",
    "approval_audit_rate": "Approval audit coverage",
    "side_effect_block_rate": "Side-effect block rate",
    "approved_action_execution_rate": "Approved action execution rate",
    "unnecessary_tool_call_rate": "Unnecessary tool-call rate",
}


def generate_public_report(project_root: Path) -> str:
    reports_dir = project_root / "reports"
    comparison = _read_json(reports_dir / "eval_comparison.json")
    retrievers = _read_json(reports_dir / "retriever_comparison.json")
    retriever_snapshots = _read_json(reports_dir / "retriever_metric_snapshots.json")
    techqa_public = _read_optional_json(reports_dir / "techqa_public_rag_summary.json")
    wixqa_public = _read_optional_json(reports_dir / "wixqa_public_rag_summary.json")
    public_rag_findings = _read_optional_json(reports_dir / "public_rag_findings.json")
    public_rag_reranking = _read_optional_json(
        reports_dir / "public_rag_reranking_opportunity.json"
    )
    public_rag_reranker = _read_optional_json(reports_dir / "public_rag_reranker_eval.json")
    public_rag_model_reranker = _read_optional_json(
        reports_dir / "public_rag_model_reranker_adapter_status.json"
    )
    evaluation_history = _read_json(reports_dir / "evaluation_history.json")
    dataset_profile = load_dataset_profile(project_root)
    evaluation_gates = load_evaluation_gates(project_root)
    collector_preview = _read_json(reports_dir / "collector_export_preview.json")
    extraction = _read_json(reports_dir / "extraction_eval_summary.json")
    security = _read_json(reports_dir / "security_eval_summary.json")
    safety_classifier = _read_json(reports_dir / "safety_classifier_eval_summary.json")
    safety_threshold_sweep = _read_json(reports_dir / "safety_threshold_sweep.json")
    safety_threshold_retuning = _read_json(reports_dir / "safety_threshold_retuning.json")
    safety_review = _read_json(reports_dir / "safety_human_review_simulation.json")
    safety_adjudication = _read_json(reports_dir / "safety_adjudication_notes.json")
    safety_disagreements = _read_json(
        reports_dir / "safety_reviewer_disagreement_slices.json"
    )
    safety_secondary_review_band = _read_json(
        reports_dir / "safety_secondary_review_band_analysis.json"
    )
    safety_secondary_review_validation = _read_json(
        reports_dir / "safety_secondary_review_floor_validation.json"
    )
    safety_operating_recommendation = _read_json(
        reports_dir / "safety_secondary_review_operating_recommendation.json"
    )
    safety_mitigation = _read_json(reports_dir / "safety_mitigation_impact.json")
    safety_memo = _read_json(reports_dir / "safety_threshold_decision_memo.json")
    human_calibration = _read_optional_json(
        reports_dir / "human_calibration_summary.json"
    )
    external_review = _read_optional_json(
        reports_dir / "external_human_review_summary.json"
    )
    judge_reliability = _read_optional_json(
        reports_dir / "judge_reliability_summary.json"
    )
    model_judge_adapter = _read_optional_json(
        reports_dir / "model_judge_adapter_status.json"
    )
    multi_model_comparison = _read_optional_json(
        reports_dir / "multi_model_comparison_plan.json"
    )
    model_judge_reviewed = _read_reviewed_model_judge_summaries(reports_dir)
    model_judge_provider_comparison = _read_optional_json(
        reports_dir / "model_judge_provider_comparison.json"
    )
    failure_taxonomy = _read_optional_json(reports_dir / "failure_taxonomy_summary.json")
    agent = _read_json(reports_dir / "agent_eval_summary.json")

    markdown = "\n".join(
        [
            "# Agent Safety & Reliability Evaluation Report",
            "",
            "## Executive Summary",
            "",
            "This report summarizes a public AI-agent safety and reliability "
            "evaluation lab. The core benchmark uses a synthetic internal-operations "
            "domain, with separate public TechQA and WixQA retrieval benchmarks. It does not "
            "use real company documents, customer data, employee data, confidential "
            "processes, or real operational actions.",
            "",
            f"- Golden retrieval cases: {comparison['case_count']}",
            f"- Synthetic ticket extraction and agent cases: {agent['case_count']}",
            f"- Red-team safety cases: {security['case_count']}",
            "- Best current retriever: "
            f"{evaluation_history['current_summary']['best_retriever']}",
            (
                "- Current vector experiments: local TF-IDF vector retrieval and local "
                "embedding-store retrieval"
            ),
            "",
            "## Evaluation Release Gates",
            "",
            _evaluation_gate_table(evaluation_gates),
            "",
            "## Dataset Profile",
            "",
            _dataset_profile_table(dataset_profile),
            "",
            _dataset_profile_coverage_table(dataset_profile),
            "",
            "This profile is generated from the same JSONL artifacts as the eval runner. "
            "It makes the synthetic benchmark mix visible, including manual-case share, "
            "abstention coverage, risk coverage, and known data gaps.",
            "",
            "## Retrieval Evaluation",
            "",
            _retriever_table(retrievers),
            "",
            "The retrieval experiment compares a deliberately weak baseline, a lexical "
            "retriever, a local hybrid sparse semantic retriever, a TF-IDF vector "
            "retriever, and a local embedding-store retriever. The embedding row uses "
            "stable feature-hashed vectors; it is not a paid provider model. A separate "
            "provider-backed embedding script is available but not included in deterministic CI.",
            "",
            "## Retriever Metric Snapshots",
            "",
            _retriever_snapshot_table(retriever_snapshots),
            "",
            "## External Public RAG Benchmark",
            "",
            _techqa_public_table(techqa_public),
            "",
            "## WixQA Public Enterprise RAG Benchmark",
            "",
            _wixqa_public_table(wixqa_public),
            "",
            "## Public RAG Findings",
            "",
            _public_rag_findings_table(public_rag_findings),
            "",
            "## Public RAG Reranking Opportunity",
            "",
            _public_rag_reranking_table(public_rag_reranking),
            "",
            "## Public RAG Reranker Evaluation",
            "",
            _public_rag_reranker_table(public_rag_reranker),
            "",
            "## Hosted Public RAG Reranker Adapter",
            "",
            _public_rag_model_reranker_table(public_rag_model_reranker),
            "",
            "## Historical Evaluation Snapshots",
            "",
            _evaluation_history_table(evaluation_history),
            "",
            "## Retriever Failure Analysis",
            "",
            _retriever_failure_overview_table(project_root),
            "",
            _retriever_failure_examples_table(project_root),
            "",
            "## Failure Taxonomy",
            "",
            _failure_taxonomy_table(failure_taxonomy),
            "",
            "## Baseline To Improved Delta",
            "",
            _before_after_table(comparison),
            "",
            "## Structured Extraction",
            "",
            _single_metric_table(extraction["metrics"], EXTRACTION_METRIC_LABELS),
            "",
            "Extraction currently uses deterministic synthetic ticket patterns. The value "
            "of this stage is the schema, routing contract, and evaluation harness rather "
            "than a claim that messy real tickets are solved.",
            "",
            "## Safety Red-Team",
            "",
            _security_table(security),
            "",
            "Block rate requires an explicit policy refusal. Safe response rate checks that "
            "forbidden behavior is absent from the response. Weighted safe response rate "
            "prioritizes higher-severity attack types, and residual risk score is the "
            "remaining unsafe severity-weighted case total.",
            "",
            _security_breakdown_table(security),
            "",
            "## Safety Classifier Workflow",
            "",
            _safety_classifier_table(safety_classifier),
            "",
            _human_calibration_table(human_calibration),
            "",
            _external_review_table(external_review),
            "",
            _judge_reliability_table(judge_reliability),
            "",
            _model_judge_adapter_table(model_judge_adapter),
            "",
            _multi_model_comparison_table(multi_model_comparison),
            "",
            _model_judge_reviewed_table(model_judge_reviewed),
            "",
            _model_judge_provider_comparison_table(model_judge_provider_comparison),
            "",
            _safety_threshold_table(safety_threshold_sweep),
            "",
            _safety_retuning_table(safety_threshold_retuning),
            "",
            _safety_review_table(safety_review),
            "",
            _safety_adjudication_notes_table(safety_adjudication),
            "",
            _safety_disagreement_slice_table(safety_disagreements),
            "",
            _safety_secondary_review_band_table(safety_secondary_review_band),
            "",
            _safety_secondary_review_validation_table(safety_secondary_review_validation),
            "",
            _safety_operating_recommendation_table(safety_operating_recommendation),
            "",
            _safety_mitigation_table(safety_mitigation),
            "",
            _safety_decision_memo_table(safety_memo),
            "",
            "## Controlled Agent Workflow",
            "",
            _single_metric_table(agent["metrics"], AGENT_METRIC_LABELS),
            "",
            "The controlled workflow separates read-only tools from side-effecting actions. "
            "The mock ticket routing tool is prepared but blocked until approval is granted, "
            "and every run returns trace, audit, and monitoring fields.",
            "",
            "## Agent Trace Examples",
            "",
            _agent_trace_examples_table(project_root),
            "",
            "## Observability Span Export",
            "",
            _agent_otel_summary_table(project_root),
            "",
            _trace_index_table(project_root),
            "",
            _collector_export_table(collector_preview),
            "",
            (
                "The combined export includes workflow-level spans, agent tool/audit spans, "
                "case-level retriever failure spans, retriever ranking-detail spans, "
                "case-level extraction spans, case-level agent approval spans, plus API "
                "contract and error-case spans for local inspection. The collector adapter "
                "translates this local JSONL into OTLP/HTTP JSON; the Docker Compose "
                "observability profile verifies that the same payloads are accepted by an "
                "OpenTelemetry Collector using collector self-metrics."
            ),
            "",
            "## What This Proves",
            "",
            "- The project can generate synthetic enterprise operations data safely.",
            "- The retrieval harness can also run against selected public technical-support data.",
            (
                "- Retrieval quality can be measured across exact, paraphrased, noisy, "
                "conflicting, and adversarial cases."
            ),
            (
                "- Structured extraction, routing, refusal behavior, approval gates, and audit "
                "traces are evaluated as product behavior, not only as model output."
            ),
            "- The dashboard, API, Docker runtime, and CI workflow make the lab reproducible.",
            "",
            "## Current Limitations",
            "",
            "- The dataset is synthetic and templated.",
            "- Extraction is deterministic rather than LLM-backed.",
            "- The vector retriever is local TF-IDF, not an embedding model or vector database.",
            "- The embedding-store retriever uses local feature-hashed embeddings, not a paid API.",
            (
                "- The TechQA public track is a 160-case compact external sample, "
                "not the full dataset."
            ),
            (
                "- The WixQA public track is an 80-case compact expert-written sample, "
                "not the full benchmark suite."
            ),
            (
                "- Scores should be read as regression-test results for this lab, not as claims "
                "about production accuracy."
            ),
            (
                "- Human-review workflow labels are simulated; the calibration "
                "sample is maintainer-labelled and not yet independently reviewed."
            ),
            (
                "- Hosted LLM-as-judge evidence is currently a single reviewed "
                "OpenAI calibration run, not a multi-model comparison."
            ),
            (
                "- Independent external human labels and inter-rater agreement "
                "are not yet published."
            ),
            "",
            "## Recommended Next Work",
            "",
            "- Formalize the failure taxonomy across safety, retrieval, citation, "
            "privacy, tool-use, and usefulness failures.",
            "- Add independent external human review for the calibration sample "
            "and compare it with deterministic rules and hosted LLM-as-judge decisions.",
            "- Extend the reviewed hosted judge track beyond the first OpenAI run "
            "and publish disagreement slices separately from the local rubric baseline.",
            "- Add optional multi-model evaluation adapters and publish only "
            "reproducible result tables.",
            "- Run safety intervention experiments across refusal policy, retrieval "
            "grounding, tool approval gates, secondary review, and classifier thresholds.",
            (
                "- Expand the TechQA public benchmark beyond 160 cases and compare "
                "against provider embeddings."
            ),
            "- Expand the WixQA public track and add provider-backed embedding comparison.",
            "",
        ]
    )
    return markdown


def generate_public_report_html(project_root: Path) -> str:
    return _markdown_to_html_document(generate_public_report(project_root))


def generate_public_report_pdf(project_root: Path) -> bytes:
    return _markdown_to_pdf_document(generate_public_report(project_root))


def write_public_report(project_root: Path) -> Path:
    output_path = project_root / "reports/evaluation_report.md"
    html_path = project_root / "reports/evaluation_report.html"
    pdf_path = project_root / "reports/evaluation_report.pdf"
    markdown = generate_public_report(project_root)
    output_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(_markdown_to_html_document(markdown), encoding="utf-8")
    pdf_path.write_bytes(_markdown_to_pdf_document(markdown))
    return output_path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return _read_json(path)
    return {"status": "not_configured", "metrics": {}, "case_count": 0}


def _read_reviewed_model_judge_summaries(reports_dir: Path) -> list[dict[str, Any]]:
    summaries = []
    for path in sorted(reports_dir.glob("model_judge_reviewed_summary*.json")):
        summary = _read_json(path)
        if summary.get("report_type") == "reviewed_hosted_model_judge_result":
            summaries.append(summary)
    return sorted(
        summaries,
        key=lambda row: (str(row.get("provider", "")), str(row.get("model", ""))),
    )


def _retriever_table(report: dict[str, Any]) -> str:
    rows = [
        "| System | Hit rate@3 | Citation coverage | Next action accuracy | "
        "Abstention accuracy | Failures |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for system in report["systems"]:
        rows.append(
            "| {label} | {hit} | {citation} | {next_action} | {abstention} | {failures} |".format(
                label=system["label"],
                hit=_pct(system["retrieval_hit_rate_at_3"]),
                citation=_pct(system["citation_coverage"]),
                next_action=_pct(system["next_action_accuracy"]),
                abstention=_pct(system["abstention_accuracy"]),
                failures=system["failure_count"],
            )
        )
    return "\n".join(rows)


def _techqa_public_table(report: dict[str, Any]) -> str:
    if report.get("status") != "evaluated":
        return "TechQA public benchmark is not configured."
    metrics = report["metrics"]
    profile = report.get("benchmark_profile", {})
    rows = [
        "| TechQA public RAG metric | Value |",
        "| --- | ---: |",
        f"| Dataset | {report['dataset']} |",
        f"| License | {report['license']} |",
        f"| Cases | {report['case_count']} |",
        f"| Sample scope | {profile.get('sample_scope', 'tracked_compact_public_sample')} |",
        f"| Answerable cases | {report['answerable_case_count']} |",
        f"| Impossible cases | {report['impossible_case_count']} |",
        (
            "| Impossible-case share | "
            f"{_pct(profile.get('impossible_case_share', 0.0))} |"
        ),
        f"| Indexed public documents | {report['document_count']} |",
        (
            "| Answerable context coverage | "
            f"{_pct(profile.get('answerable_context_coverage', 0.0))} |"
        ),
        f"| Retrieval hit rate@3 | {_pct(metrics['retrieval_hit_rate_at_3'])} |",
        f"| Top-1 citation accuracy | {_pct(metrics['top1_citation_accuracy'])} |",
        f"| Mean reciprocal rank@3 | {_pct(metrics['mean_reciprocal_rank_at_3'])} |",
        f"| Abstention accuracy | {_pct(metrics['abstention_accuracy'])} |",
        (
            "| Impossible-question abstention | "
            f"{_pct(metrics['impossible_abstention_rate'])} |"
        ),
        (
            "| Answerable false abstention | "
            f"{_pct(metrics['answerable_false_abstention_rate'])} |"
        ),
        f"| Failed cases | {profile.get('failed_case_count', 0)} |",
        (
            "| Provider-backed embedding result published | "
            f"{profile.get('provider_backed_embedding_result_published', False)} |"
        ),
        "",
        (
            "| TechQA retriever | Retrieval@3 | Top-1 citation | "
            "Impossible abstention | Failed cases |"
        ),
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for system in report.get("retriever_systems", []):
        metrics = system["metrics"]
        rows.append(
            f"| {system['label']} | {_pct(metrics['retrieval_hit_rate_at_3'])} | "
            f"{_pct(metrics['top1_citation_accuracy'])} | "
            f"{_pct(metrics['impossible_abstention_rate'])} | "
            f"{system['failed_case_count']} |"
        )
    return "\n".join(rows)


def _wixqa_public_table(report: dict[str, Any]) -> str:
    if report.get("status") != "evaluated":
        return "WixQA public benchmark is not configured."
    metrics = report["metrics"]
    profile = report.get("benchmark_profile", {})
    rows = [
        "| WixQA public RAG metric | Value |",
        "| --- | ---: |",
        f"| Dataset | {report['dataset']} |",
        f"| License | {report['license']} |",
        f"| Cases | {report['case_count']} |",
        f"| Sample scope | {profile.get('sample_scope', 'tracked_compact_public_sample')} |",
        f"| Indexed public documents | {report['document_count']} |",
        f"| Multi-article cases | {report['multi_article_case_count']} |",
        (
            "| Multi-article case share | "
            f"{_pct(profile.get('multi_article_case_share', 0.0))} |"
        ),
        (
            "| Avg grounding docs / case | "
            f"{profile.get('average_grounding_documents_per_case', 0.0)} |"
        ),
        f"| Retrieval hit rate@3 | {_pct(metrics['retrieval_hit_rate_at_3'])} |",
        f"| Top-1 citation accuracy | {_pct(metrics['top1_citation_accuracy'])} |",
        f"| Mean reciprocal rank@3 | {_pct(metrics['mean_reciprocal_rank_at_3'])} |",
        (
            "| Multi-article retrieval@3 | "
            f"{_pct(metrics['multi_article_retrieval_hit_rate_at_3'])} |"
        ),
        f"| Failed cases | {profile.get('failed_case_count', 0)} |",
        (
            "| Provider-backed embedding result published | "
            f"{profile.get('provider_backed_embedding_result_published', False)} |"
        ),
        "",
        "| WixQA retriever | Retrieval@3 | Top-1 citation | Failed cases |",
        "| --- | ---: | ---: | ---: |",
    ]
    for system in report.get("retriever_systems", []):
        system_metrics = system["metrics"]
        rows.append(
            f"| {system['label']} | {_pct(system_metrics['retrieval_hit_rate_at_3'])} | "
            f"{_pct(system_metrics['top1_citation_accuracy'])} | "
            f"{system['failed_case_count']} |"
        )
    return "\n".join(rows)


def _public_rag_findings_table(report: dict[str, Any]) -> str:
    if report.get("status") != "evaluated":
        return "Public RAG findings are not configured."
    summary = report["summary"]
    rows = [
        "| Cross-public RAG finding metric | Value |",
        "| --- | ---: |",
        f"| Evaluated public tracks | {summary['evaluated_track_count']} |",
        f"| Total public cases | {summary['total_case_count']} |",
        f"| Total public documents | {summary['total_document_count']} |",
        f"| Weighted retrieval hit rate@3 | {_pct(summary['weighted_retrieval_hit_rate_at_3'])} |",
        (
            "| Weighted top-1 citation accuracy | "
            f"{_pct(summary['weighted_top1_citation_accuracy'])} |"
        ),
        f"| Weighted failure rate | {_pct(summary['weighted_failure_rate'])} |",
        f"| Top cross-track failure label | {summary['top_cross_track_failure_label']} |",
        f"| Largest retrieval lift | {summary['largest_retrieval_lift_track']} |",
        f"| Largest top-1 lift | {summary['largest_top1_lift_track']} |",
        "",
        "| Finding |",
        "| --- |",
    ]
    for finding in report.get("findings", []):
        rows.append(f"| {finding} |")
    rows.extend(["", "| Recommendation |", "| --- |"])
    for recommendation in report.get("recommendations", []):
        rows.append(f"| {recommendation} |")
    return "\n".join(rows)


def _public_rag_reranking_table(report: dict[str, Any]) -> str:
    if report.get("status") != "evaluated":
        return "Public RAG reranking opportunity is not configured."
    summary = report["summary"]
    rows = [
        "| Reranking opportunity metric | Value |",
        "| --- | ---: |",
        f"| Evaluated public tracks | {summary['evaluated_track_count']} |",
        f"| Public answerable cases | {summary['total_case_count']} |",
        (
            "| Current weighted top-1 citation accuracy | "
            f"{_pct(summary['current_weighted_top1_citation_accuracy'])} |"
        ),
        f"| Oracle top-3 rerank ceiling | {_pct(summary['oracle_top3_rerank_ceiling'])} |",
        f"| Possible weighted top-1 lift | {_pct(summary['possible_weighted_top1_lift'])} |",
        f"| Rerankable cases | {summary['rerankable_case_count']} |",
        f"| Residual retrieval misses | {summary['not_retrieved_case_count']} |",
        f"| Residual retrieval gap | {_pct(summary['residual_retrieval_gap'])} |",
        f"| Largest rerankable track | {summary['largest_rerankable_track']} |",
        f"| Largest residual gap track | {summary['largest_residual_gap_track']} |",
        "",
        "| Finding |",
        "| --- |",
    ]
    for finding in report.get("findings", []):
        rows.append(f"| {finding} |")
    rows.extend(["", "| Recommendation |", "| --- |"])
    for recommendation in report.get("recommendations", []):
        rows.append(f"| {recommendation} |")
    return "\n".join(rows)


def _public_rag_reranker_table(report: dict[str, Any]) -> str:
    if report.get("status") != "evaluated":
        return "Public RAG reranker evaluation is not configured."
    summary = report["summary"]
    reranker = report.get("reranker", {})
    rows = [
        "| Reranker evaluation metric | Value |",
        "| --- | ---: |",
        f"| Reranker | {reranker.get('label', '')} |",
        f"| Public answerable cases | {summary['total_case_count']} |",
        f"| Baseline top-1 citation accuracy | {_pct(summary['baseline_top1_accuracy'])} |",
        f"| Reranked top-1 citation accuracy | {_pct(summary['reranked_top1_accuracy'])} |",
        f"| Top-1 accuracy delta | {_signed_pct(summary['top1_accuracy_delta'])} |",
        f"| Changed cases | {summary['changed_case_count']} |",
        f"| Improved cases | {summary['improved_case_count']} |",
        f"| Regressed cases | {summary['regressed_case_count']} |",
        f"| Regression rate | {_pct(summary['regression_rate'])} |",
        "",
        "| Finding |",
        "| --- |",
    ]
    for finding in report.get("findings", []):
        rows.append(f"| {finding} |")
    rows.extend(["", "| Recommendation |", "| --- |"])
    for recommendation in report.get("recommendations", []):
        rows.append(f"| {recommendation} |")
    return "\n".join(rows)


def _public_rag_model_reranker_table(report: dict[str, Any]) -> str:
    if report.get("status") == "not_configured":
        return "Hosted public RAG reranker adapter is not configured."
    selection_counts = report.get("selection_counts", {})
    dataset_counts = report.get("dataset_case_counts", {})
    datasets = ", ".join(
        f"{dataset}: {count}" for dataset, count in dataset_counts.items()
    )
    rows = [
        "| Hosted reranker readiness field | Value |",
        "| --- | --- |",
        f"| Status | {_display_status(report.get('status', ''))} |",
        f"| Provider | {report.get('provider', '')} |",
        f"| API mode | {report.get('api_mode', '')} |",
        f"| Default model | {report.get('default_model', '')} |",
        f"| Packet cases | {report.get('candidate_case_count', 0)} |",
        f"| Estimated provider calls | {report.get('estimated_provider_calls', 0)} |",
        (
            "| Candidate documents | "
            f"{report.get('estimated_candidate_documents', 0)} |"
        ),
        (
            "| Rerankable/control split | "
            f"{selection_counts.get('rerankable', 0)} / "
            f"{selection_counts.get('top1_control', 0)} |"
        ),
        f"| Datasets | {datasets} |",
        f"| Credential setting | {report.get('credential_env_var', '')} |",
        f"| Model setting | {report.get('model_env_var', '')} |",
        f"| Packet path | {report.get('packet_path', '')} |",
        f"| Publication rule | {report.get('publication_rule', '')} |",
    ]
    return "\n".join(rows)


def _agent_trace_examples_table(project_root: Path) -> str:
    traces = agent_trace_rows(load_agent_trace_examples(project_root))
    if not traces:
        return "No agent trace examples recorded."
    rows = [
        (
            "| Trace | Ticket | Approval | Route outcome | Tool calls | Executed | "
            "Blocked | Audit events |"
        ),
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for trace in traces[:10]:
        rows.append(
            "| {trace_id} | {ticket_id} | {approval_granted} | {route_tool_outcome} | "
            "{tool_call_count} | {executed_tool_call_count} | {blocked_tool_call_count} | "
            "{audit_event_count} |".format(**trace)
        )
    return "\n".join(rows)


def _agent_otel_summary_table(project_root: Path) -> str:
    summary = agent_otel_summary(load_observability_otel_spans(project_root))
    rows = [
        "| Export metric | Value |",
        "| --- | ---: |",
        f"| OTel-style spans | {summary['span_count']} |",
        f"| Exported traces | {summary['trace_count']} |",
        f"| Root spans | {summary['root_span_count']} |",
        f"| Child spans | {summary['child_span_count']} |",
        f"| Tool spans | {summary['tool_span_count']} |",
    ]
    return "\n".join(rows)


def _trace_index_table(project_root: Path) -> str:
    trace_index = load_observability_trace_index(project_root)
    if not trace_index:
        return "No local trace index recorded."

    rows = [
        "| Local trace index metric | Value |",
        "| --- | ---: |",
        f"| Indexed traces | {trace_index['trace_count']} |",
        f"| Indexed spans | {trace_index['span_count']} |",
        f"| Error spans | {trace_index['error_span_count']} |",
        f"| Components | {trace_index['component_count']} |",
    ]
    for row in trace_index_query_rows(trace_index):
        rows.append(f"| query:{row['query']} | {row['span_count']} |")
    for row in trace_index_component_rows(trace_index)[:6]:
        rows.append(f"| component:{row['component']} | {row['span_count']} |")
    return "\n".join(rows)


def _collector_export_table(preview: dict[str, Any]) -> str:
    rows = [
        "| Collector export preview | Value |",
        "| --- | ---: |",
        f"| Mode | {_display_status(preview['export_mode'])} |",
        f"| Endpoint | {preview['collector_endpoint']} |",
        f"| Spans prepared | {preview['span_count']} |",
        f"| OTLP payloads | {preview['payload_count']} |",
        f"| Batch size | {preview['batch_size']} |",
    ]
    return "\n".join(rows)


def _evaluation_gate_table(gates: dict[str, Any]) -> str:
    if not gates:
        return "No evaluation release gates recorded."

    rows = [
        "| Gate | Area | Status | Severity | Observed | Threshold |",
        "| --- | --- | --- | --- | ---: | ---: |",
        (
            f"| Overall status | Release | {_display_status(gates['overall_status'])} | summary | "
            f"{gates['pass_count']} pass / {gates['warn_count']} warn | "
            f"{gates['fail_count']} fail |"
        ),
    ]
    for gate in evaluation_gate_rows(gates):
        rows.append(
            "| {label} | {area} | {status} | {severity} | {observed} | {threshold} |".format(
                **{**gate, "status": _display_status(gate["status"])}
            )
        )
    return "\n".join(rows)


def _dataset_profile_table(profile: dict[str, Any]) -> str:
    counts = profile["dataset_counts"]
    mix = profile["golden_case_mix"]
    rows = [
        "| Dataset profile metric | Value |",
        "| --- | ---: |",
        f"| Runbook sections | {counts['runbooks']} |",
        f"| Synthetic tickets | {counts['tickets']} |",
        f"| Golden cases | {counts['golden_cases']} |",
        f"| Manual golden cases | {mix['manual_cases']} |",
        f"| Manual share | {_pct(mix['manual_share'])} |",
        f"| Expected abstentions | {mix['expected_abstentions']} |",
        f"| Abstention share | {_pct(mix['abstention_share'])} |",
        f"| Noise types | {mix['noise_type_count']} |",
        f"| Task types | {mix['task_type_count']} |",
        f"| Red-team cases | {counts['red_team_cases']} |",
    ]
    return "\n".join(rows)


def _dataset_profile_coverage_table(profile: dict[str, Any]) -> str:
    top_noise = coverage_count_rows(profile, "by_noise_type")[:8]
    risk_rows = red_team_coverage_rows(profile, "by_risk_type")[:8]
    rows = [
        "| Coverage sample | Cases |",
        "| --- | ---: |",
    ]
    for row in top_noise:
        rows.append(f"| noise:{row['value']} | {row['case_count']} |")
    for row in risk_rows:
        rows.append(f"| red_team:{row['value']} | {row['case_count']} |")
    rows.append(f"| risk labels | {len(profile['risk_labels'])} |")
    return "\n".join(rows)


def _retriever_snapshot_table(report: dict[str, Any]) -> str:
    rows = [
        "| Snapshot | System | Citation coverage | Failed cases | Citation delta | "
        "Failure delta | Regression | Reason |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in retriever_snapshot_rows(report):
        rows.append(
            "| {snapshot_id} | {system} | {citation_coverage_pct} | {failure_count} | "
            "{citation_delta_pct} | {failure_delta} | {regression} | "
            "{regression_reasons} |".format(**row)
        )
    return "\n".join(rows)


def _evaluation_history_table(report: dict[str, Any]) -> str:
    rows = [
        "| Milestone time | Milestone | Citation coverage | Failed cases | "
        "Citation delta | Failure delta |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in evaluation_history_rows(report):
        rows.append(
            "| {milestone_at_utc} | {milestone} | {citation_coverage_pct} | "
            "{failure_count} | {citation_delta_pct} | {failure_delta} |".format(**row)
        )
    return "\n".join(rows)


def _retriever_failure_overview_table(project_root: Path) -> str:
    rows = [
        "| System | Failed cases | Retrieved but not cited | Abstention mismatches | "
        "Top failure reason |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in retriever_failure_overview(load_retriever_case_rows(project_root)):
        rows.append(
            "| {system} | {failed_cases} | {retrieved_but_not_cited} | "
            "{abstention_mismatches} | {top_failure_reason} |".format(**row)
        )
    return "\n".join(rows)


def _retriever_failure_examples_table(project_root: Path) -> str:
    examples = retriever_failure_example_rows(
        load_retriever_case_rows(project_root), limit_per_system=3
    )
    if not examples:
        return "No retriever failure examples recorded."

    rows = [
        "| System | Case | Noise | Failure | Expected citation | Predicted citation | "
        "Retrieved but not cited | Top retrieved scores | Recommended fix |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in examples:
        rows.append(
            "| {system} | {case_id} | {noise_type} | {failure_reasons} | "
            "{expected_citation} | {predicted_citation} | {retrieved_but_not_cited} | "
            "{score_explanation} | {recommended_fix} |".format(**row)
        )
    return "\n".join(rows)


def _failure_taxonomy_table(report: dict[str, Any]) -> str:
    if report.get("report_type") != "failure_taxonomy_summary":
        return "Failure taxonomy summary is not configured."
    definitions = report.get("definitions", {})
    label_rows = sorted(
        report.get("by_label", {}).items(),
        key=lambda item: (-int(item[1]), str(item[0])),
    )[:10]
    rows = [
        f"Total taxonomy-labeled cases: {report['total_labeled_cases']}",
        "",
        "| Taxonomy label | Group | Count |",
        "| --- | --- | ---: |",
    ]
    for label, count in label_rows:
        group = definitions.get(label, {}).get("group", "unknown")
        rows.append(f"| {label} | {group} | {count} |")
    rows.extend(
        [
            "",
            "| Source | Top taxonomy label | Count |",
            "| --- | --- | ---: |",
        ]
    )
    for source, labels in sorted(report.get("by_source", {}).items()):
        if not labels:
            continue
        top_label, count = sorted(
            labels.items(), key=lambda item: (-int(item[1]), str(item[0]))
        )[0]
        rows.append(f"| {source} | {top_label} | {count} |")
    return "\n".join(rows)


def _before_after_table(report: dict[str, Any]) -> str:
    rows = [
        "| Metric | Baseline | Improved lexical | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for metric, label in METRIC_LABELS.items():
        values = report["metrics"][metric]
        rows.append(
            f"| {label} | {_pct(values['baseline'])} | {_pct(values['improved'])} | "
            f"{_signed_pct(values['delta'])} |"
        )
    return "\n".join(rows)


def _single_metric_table(metrics: dict[str, float], labels: dict[str, str]) -> str:
    rows = [
        "| Metric | Score |",
        "| --- | ---: |",
    ]
    for metric, label in labels.items():
        if metric in metrics:
            rows.append(f"| {label} | {_pct(metrics[metric])} |")
    return "\n".join(rows)


def _security_table(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    return "\n".join(
        [
            "| Metric | Baseline | Improved policy |",
            "| --- | ---: | ---: |",
            f"| Policy block rate | {_pct(metrics['baseline_block_rate'])} | "
            f"{_pct(metrics['improved_block_rate'])} |",
            f"| Safe response rate | {_pct(metrics['baseline_safe_rate'])} | "
            f"{_pct(metrics['improved_safe_rate'])} |",
            f"| Weighted safe response rate | {_pct(metrics['baseline_weighted_safe_rate'])} | "
            f"{_pct(metrics['improved_weighted_safe_rate'])} |",
            f"| Residual risk score | {metrics['baseline_residual_risk_score']} | "
            f"{metrics['improved_residual_risk_score']} |",
        ]
    )


def _security_breakdown_table(report: dict[str, Any]) -> str:
    rows = [
        "| Risk type | Cases | Max severity | Safe rate | Weighted safe rate | Residual risk |",
        "| --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in security_risk_breakdown_rows(report, "by_risk_type"):
        rows.append(
            "| {group} | {case_count} | {max_risk_severity} | {safe_rate_pct} | "
            "{weighted_safe_rate_pct} | {residual_risk_score} |".format(**row)
        )
    return "\n".join(rows)


def _safety_classifier_table(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    prevalence = report["weighted_prevalence"]
    review = report["human_review_simulation"]
    mitigation = report["mitigation_impact"]
    rows = [
        "| Safety classifier metric | Value |",
        "| --- | ---: |",
        f"| Challenge cases | {report['challenge_case_count']} |",
        (
            "| Secondary-floor validation cases | "
            f"{report['secondary_review_validation_case_count']} |"
        ),
        f"| Sampled prevalence cases | {report['prevalence_case_count']} |",
        f"| Selected threshold | {report['selected_threshold']} |",
        f"| Recall | {_pct(metrics['recall'])} |",
        f"| False positive rate | {_pct(metrics['false_positive_rate'])} |",
        f"| False negative rate | {_pct(metrics['false_negative_rate'])} |",
        f"| High-severity false negatives | {metrics['high_severity_false_negative_count']} |",
        f"| Synthetic unsafe prevalence | {_pct(prevalence['unsafe_prevalence'])} |",
        f"| Review queue cases | {review['queue_count']} |",
        (
            "| Residual unsafe allowed after review | "
            f"{mitigation['final_residual_unsafe_allowed_count']} |"
        ),
    ]
    return "\n".join(rows)


def _human_calibration_table(report: dict[str, Any]) -> str:
    if report.get("report_type") != "human_label_calibration":
        return "Human-label calibration is not configured."
    summary = report["summary"]
    rows = [
        "| Maintainer-labelled calibration metric | Value |",
        "| --- | ---: |",
        f"| Calibration cases | {summary['case_count']} |",
        f"| Unsafe cases | {summary['unsafe_case_count']} |",
        f"| Benign cases | {summary['benign_case_count']} |",
        f"| Reviewer agreement rate | {_pct(summary['reviewer_agreement_rate'])} |",
        f"| Classifier label accuracy | {_pct(summary['classifier_label_accuracy'])} |",
        (
            "| Classifier expected-action match | "
            f"{_pct(summary['classifier_action_match_rate'])} |"
        ),
        f"| Unsafe capture rate | {_pct(summary['unsafe_capture_rate'])} |",
        f"| Unsafe auto-allowed | {summary['unsafe_auto_allowed_count']} |",
        f"| Benign auto-blocked | {summary['benign_auto_blocked_count']} |",
        f"| Benign sent to review | {summary['benign_reviewed_count']} |",
    ]
    if report["by_category"]:
        rows.extend(
            [
                "",
                "| Category | Cases | Unsafe | Label accuracy | Action match | Top error |",
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for row in report["by_category"]:
            rows.append(
                "| {risk_category} | {case_count} | {unsafe_case_count} | "
                "{label_accuracy} | {action_match} | {top_error_type} |".format(
                    label_accuracy=_pct(row["classifier_label_accuracy"]),
                    action_match=_pct(row["classifier_action_match_rate"]),
                    **row,
                )
            )
    if report["sample_cases"]:
        rows.extend(
            [
                "",
                (
                    "| Case | Human label | Expected action | Classifier decision | "
                    "Reviewer disagreement | Error type |"
                ),
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in report["sample_cases"][:6]:
            rows.append(
                "| {case_id} | {human_adjudicated_label} | {expected_action} | "
                "{classifier_decision} | {reviewer_disagreement} | {error_type} |".format(
                    **row
                )
            )
    return "\n".join(rows)


def _external_review_table(report: dict[str, Any]) -> str:
    if report.get("report_type") != "external_human_review":
        return "External human review is not configured."
    summary = report["summary"]
    rows = [
        "| External human-review artifact | Value |",
        "| --- | --- |",
        f"| Status | {_display_status(report['status'])} |",
        f"| Calibration cases | {report['case_count']} |",
        f"| Label rows | {report['label_row_count']} |",
        f"| Reviewers | {report['reviewer_count']} |",
        f"| Label coverage | {_pct(summary['external_label_coverage'])} |",
        (
            "| Cases with two or more reviewers | "
            f"{summary['cases_with_two_or_more_reviewers']} |"
        ),
        f"| Pairwise agreement | {_pct(summary['pairwise_agreement_rate'])} |",
        f"| Pairwise Cohen kappa | {summary['pairwise_cohen_kappa']} |",
        (
            "| External / maintainer agreement | "
            f"{_pct(summary['external_maintainer_agreement_rate'])} |"
        ),
        (
            "| External / maintainer disagreements | "
            f"{summary['external_maintainer_disagreement_count']} |"
        ),
        f"| Adjudication required | {summary['adjudication_required_count']} |",
        f"| Review packet | {report['packet_path']} |",
        f"| Label template | {report['label_template_path']} |",
        f"| Reviewer guide | {report['reviewer_guide_path']} |",
        f"| Review manifest | {report['manifest_path']} |",
    ]
    if report.get("disagreement_examples"):
        rows.extend(
            [
                "",
                (
                    "| External review case | Category | Maintainer | "
                    "External consensus | Adjudication |"
                ),
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in report["disagreement_examples"][:8]:
            rows.append(
                "| {case_id} | {risk_category} | {maintainer_label} | "
                "{external_consensus_label} | {adjudication_required} |".format(
                    **row
                )
            )
    rows.extend(["", "| External review note |", "| --- |"])
    for note in report.get("notes", []):
        rows.append(f"| {note} |")
    return "\n".join(rows)


def _judge_reliability_table(report: dict[str, Any]) -> str:
    if report.get("report_type") != "judge_reliability_calibration":
        return "Judge reliability calibration is not configured."
    summary = report["summary"]
    rows = [
        "| Judge reliability metric | Value |",
        "| --- | ---: |",
        f"| Calibration cases | {summary['case_count']} |",
        f"| Local rubric judge accuracy | {_pct(summary['judge_label_accuracy'])} |",
        f"| Classifier label accuracy | {_pct(summary['classifier_label_accuracy'])} |",
        (
            "| Classifier / rubric judge agreement | "
            f"{_pct(summary['classifier_judge_agreement_rate'])} |"
        ),
        f"| Reviewer pair agreement | {_pct(summary['reviewer_pair_agreement_rate'])} |",
        f"| Rubric judge kappa vs human | {summary['judge_kappa_vs_human']} |",
        f"| Classifier kappa vs human | {summary['classifier_kappa_vs_human']} |",
        f"| Classifier / judge kappa | {summary['classifier_judge_kappa']} |",
        f"| Rubric judge disagreements | {summary['judge_disagreement_count']} |",
        f"| Classifier disagreements | {summary['classifier_disagreement_count']} |",
    ]
    if report["pairwise_agreement"]:
        rows.extend(
            [
                "",
                "| Rater A | Rater B | Agreement | Cohen kappa | Disagreements |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for row in report["pairwise_agreement"]:
            rows.append(
                "| {rater_a} | {rater_b} | {agreement} | {cohen_kappa} | "
                "{disagreement_count} |".format(
                    agreement=_pct(row["agreement_rate"]),
                    **row,
                )
            )
    if report["by_category"]:
        rows.extend(
            [
                "",
                (
                    "| Category | Cases | Judge accuracy | Classifier accuracy | "
                    "Classifier/judge agreement | Top judge error |"
                ),
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for row in report["by_category"]:
            rows.append(
                "| {risk_category} | {case_count} | {judge_accuracy} | "
                "{classifier_accuracy} | {agreement} | {top_judge_error_type} |".format(
                    judge_accuracy=_pct(row["judge_label_accuracy"]),
                    classifier_accuracy=_pct(row["classifier_label_accuracy"]),
                    agreement=_pct(row["classifier_judge_agreement_rate"]),
                    **row,
                )
            )
    if report["disagreement_examples"]:
        rows.extend(
            [
                "",
                (
                    "| Case | Human | Classifier | Rubric judge | Judge confidence | "
                    "Judge error |"
                ),
                "| --- | --- | --- | --- | ---: | --- |",
            ]
        )
        for row in report["disagreement_examples"][:6]:
            rows.append(
                "| {case_id} | {human_adjudicated_label} | {classifier_label} | "
                "{judge_label} | {judge_confidence} | {judge_error_type} |".format(
                    **row
                )
            )
    return "\n".join(rows)


def _model_judge_adapter_table(report: dict[str, Any]) -> str:
    if report.get("adapter_type") != "hosted_model_judge":
        return "Hosted model-judge adapter status is not configured."
    rows = [
        "| Hosted model-judge adapter | Value |",
        "| --- | --- |",
        f"| Status | {_display_status(report['status'])} |",
        f"| Provider | {report['provider']} |",
        f"| API mode | {report['api_mode']} |",
        f"| Calibration cases | {report['case_count']} |",
        f"| Credential setting | {report['credential_env_var']} |",
        f"| Model setting | {report['model_env_var']} |",
    ]
    rows.extend(["", "| Planned local output |", "| --- |"])
    for path in report.get("planned_outputs", []):
        rows.append(f"| {path} |")
    return "\n".join(rows)


def _multi_model_comparison_table(report: dict[str, Any]) -> str:
    if report.get("report_type") != "multi_model_comparison_plan":
        return "Multi-model comparison plan is not configured."
    readiness = report["readiness_summary"]
    rows = [
        "| Multi-model comparison plan | Value |",
        "| --- | --- |",
        f"| Status | {_display_status(report['status'])} |",
        f"| Benchmark track | {report['benchmark_track']} |",
        f"| Calibration cases | {report['case_count']} |",
        f"| Target model count | {report['target_model_count']} |",
        f"| Adapters available | {readiness['adapter_available_count']} |",
        f"| Adapters planned | {readiness['adapter_planned_count']} |",
        f"| Credentialed reviewed results | {readiness['credentialed_result_count']} |",
        (
            "| Ready for cross-provider publication | "
            f"{readiness['ready_for_cross_provider_publication']} |"
        ),
    ]
    rows.extend(
        [
            "",
            "| Provider | Adapter status | Credential | Model setting | Result state |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for target in report["planned_targets"]:
        row = {**target, "result_state": _display_status(target["result_state"])}
        rows.append(
            "| {provider} | {adapter_status} | {credential_env_var} | "
            "{model_env_var} | {result_state} |".format(**row)
        )
    return "\n".join(rows)


def _model_judge_reviewed_table(reports: list[dict[str, Any]]) -> str:
    if not reports:
        return "Reviewed hosted model-judge result is not published."
    rows = [
        "| Reviewed hosted model-judge results | Provider | Model | Value |",
        "| --- | --- | --- | --- |",
    ]
    for report in reports:
        metrics = report["metrics"]
        review = report["publication_review"]
        rows.extend(
            [
                f"| Manual publication decision | {report['provider']} | {report['model']} | "
                f"{_display_status(report['manual_publication_decision'])} |",
                f"| Review note | {report['provider']} | {report['model']} | "
                f"{report['review_note']} |",
                f"| Calibration cases | {report['provider']} | {report['model']} | "
                f"{report['case_count']} |",
                f"| Model-judge label accuracy | {report['provider']} | {report['model']} | "
                f"{_pct(metrics['model_judge_label_accuracy'])} |",
                (
                    f"| Classifier / hosted judge agreement | {report['provider']} | "
                    f"{report['model']} | "
                    f"{_pct(metrics['classifier_model_judge_agreement_rate'])} |"
                ),
                (
                    f"| Average hosted judge confidence | {report['provider']} | "
                    f"{report['model']} | "
                    f"{_pct(metrics['average_model_judge_confidence'])} |"
                ),
                f"| Hosted judge disagreement count | {report['provider']} | {report['model']} | "
                f"{metrics['model_judge_disagreement_count']} |",
                f"| Publication gate decision | {report['provider']} | {report['model']} | "
                f"{_display_status(review['decision'])} |",
                f"| Unsafe misses | {report['provider']} | {report['model']} | "
                f"{review['unsafe_miss_count']} |",
                f"| Benign auto-blocks | {report['provider']} | {report['model']} | "
                f"{review['benign_auto_block_count']} |",
            ]
        )
    examples = [
        (
            report["provider"],
            example,
        )
        for report in reports
        for example in report.get("public_disagreement_examples", [])[:8]
    ]
    if examples:
        rows.extend(
            [
                "",
                "| Provider | Public disagreement case | Category | Human | Hosted judge | Error |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for provider, example in examples[:12]:
            rows.append(
                "| {provider} | {case_id} | {risk_category} | {human_label} | "
                "{model_judge_label} | {model_judge_error_type} |".format(
                    provider=provider,
                    **example,
                )
            )
    rows.extend(["", "| Hosted judge limitation |", "| --- |"])
    for report in reports:
        for limitation in report.get("limitations", []):
            rows.append(f"| {report['provider']}: {limitation} |")
    return "\n".join(rows)


def _model_judge_provider_comparison_table(report: dict[str, Any]) -> str:
    if report.get("report_type") != "reviewed_model_judge_provider_comparison":
        return "Reviewed model-judge provider comparison is not configured."
    metrics = report["comparison_metrics"]
    rows = [
        "| Reviewed provider comparison | Value |",
        "| --- | --- |",
        f"| Status | {_display_status(report['status'])} |",
        f"| Providers | {', '.join(report['providers'])} |",
        f"| Comparable cases | {report['case_count']} |",
        (
            "| Provider label agreement | "
            f"{_pct(metrics['provider_label_agreement_rate'])} |"
        ),
        (
            "| Provider decision agreement | "
            f"{_pct(metrics['provider_decision_agreement_rate'])} |"
        ),
        (
            "| Cross-provider label disagreements | "
            f"{metrics['cross_provider_label_disagreement_count']} |"
        ),
        (
            "| Any provider unsafe misses | "
            f"{metrics['any_provider_unsafe_miss_count']} |"
        ),
        (
            "| Any provider benign auto-blocks | "
            f"{metrics['any_provider_benign_auto_block_count']} |"
        ),
    ]
    rows.extend(
        [
            "",
            "| Provider | Model | Accuracy | Classifier agreement | Confidence | "
            "Unsafe misses | Benign auto-blocks |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for summary in report["provider_summaries"]:
        rows.append(
            "| {provider} | {model} | {accuracy} | {agreement} | {confidence} | "
            "{unsafe_miss_count} | {benign_auto_block_count} |".format(
                accuracy=_pct(summary["model_judge_label_accuracy"]),
                agreement=_pct(
                    summary["classifier_model_judge_agreement_rate"]
                ),
                confidence=_pct(summary["average_model_judge_confidence"]),
                **summary,
            )
        )
    if report["cross_provider_disagreement_cases"]:
        rows.extend(
            [
                "",
                "| Case | Category | Human | Classifier | Provider labels | Error pattern |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in report["cross_provider_disagreement_cases"][:8]:
            provider_labels = ", ".join(
                f"{result['provider']}={result['model_judge_label']}"
                for result in row["provider_results"]
            )
            error_pattern = ", ".join(
                f"{result['provider']}={result['model_judge_error_type']}"
                for result in row["provider_results"]
            )
            rows.append(
                "| {case_id} | {risk_category} | {human_label} | "
                "{classifier_label} | {provider_labels} | {error_pattern} |".format(
                    provider_labels=provider_labels,
                    error_pattern=error_pattern,
                    **row,
                )
            )
    rows.extend(["", f"Publication policy: {report['publication_policy']}"])
    return "\n".join(rows)


def _safety_threshold_table(report: dict[str, Any]) -> str:
    rows = [
        (
            "| Threshold | Policy | Recall | False positive | False negative | "
            "Review | High severity FN |"
        ),
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in safety_threshold_rows(report):
        rows.append(
            "| {threshold} | {policy_label} | {recall_pct} | "
            "{false_positive_rate_pct} | {false_negative_rate_pct} | "
            "{review_rate_pct} | {high_severity_false_negative_count} |".format(**row)
        )
    return "\n".join(rows)


def _safety_retuning_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    rows = [
        "| Safety retuning metric | Value |",
        "| --- | ---: |",
        f"| Legacy recall | {_pct(summary['legacy_recall'])} |",
        f"| Retuned recall | {_pct(summary['tuned_recall'])} |",
        f"| Recall lift | {_signed_pct(summary['recall_delta'])} |",
        f"| Legacy false negatives | {summary['legacy_false_negative_count']} |",
        f"| Retuned false negatives | {summary['tuned_false_negative_count']} |",
        f"| False-negative reduction | {summary['false_negative_reduction']} |",
        (
            "| Benign near-miss false positives | "
            f"{summary['benign_near_miss_false_positive_count']} |"
        ),
    ]
    rows.extend(
        [
            "",
            "| Category | Legacy recall | Retuned recall | Recall lift | FN reduction |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in safety_retuning_rows(report):
        rows.append(
            "| {risk_category} | {legacy_recall_pct} | {tuned_recall_pct} | "
            "{recall_delta_pct} | {false_negative_reduction} |".format(**row)
        )
    return "\n".join(rows)


def _safety_review_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    rows = [
        "| Human review simulation metric | Value |",
        "| --- | ---: |",
        f"| Queue cases | {summary['queue_count']} |",
        f"| Capacity utilization | {_pct(summary['capacity_utilization'])} |",
        f"| Disagreement rate | {_pct(summary['disagreement_rate'])} |",
        f"| Escalation rate | {_pct(summary['escalation_rate'])} |",
        f"| Unsafe caught by review | {summary['unsafe_caught_by_review']} |",
        f"| Human overblocks | {summary['human_overblock_count']} |",
        f"| SLA breaches | {summary['sla_breach_count']} |",
    ]
    examples = safety_review_case_rows(report, limit=5)
    if examples:
        rows.extend(
            [
                "",
                "| Review case | Category | Severity | Score | Final decision | Escalated |",
                "| --- | --- | --- | ---: | --- | --- |",
            ]
        )
        for row in examples:
            rows.append(
                "| {case_id} | {risk_category} | {risk_severity} | {score} | "
                "{final_decision} | {escalated} |".format(**row)
            )
    return "\n".join(rows)


def _safety_adjudication_notes_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    rows = [
        "| Human-authored adjudication notes metric | Value |",
        "| --- | ---: |",
        f"| Authored notes | {summary['adjudication_note_count']} |",
        f"| Medium-severity notes | {summary['medium_severity_note_count']} |",
        f"| Review-queue note coverage | {_pct(summary['review_queue_note_coverage'])} |",
        f"| Classifier disagreements | {summary['classifier_disagreement_count']} |",
        f"| Disagreement rate | {_pct(summary['classifier_disagreement_rate'])} |",
        f"| Unsafe cases found by notes | {summary['unsafe_cases_found_by_notes']} |",
    ]
    examples = safety_adjudication_note_rows(report, limit=5)
    if examples:
        rows.extend(
            [
                "",
                (
                    "| Adjudication case | Category | Severity | Classifier | "
                    "Recommended | Disagreed |"
                ),
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in examples:
            rows.append(
                "| {case_id} | {risk_category} | {risk_severity} | "
                "{classifier_decision} | {recommended_decision} | "
                "{classifier_disagreed} |".format(**row)
            )
    return "\n".join(rows)


def _safety_disagreement_slice_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    rows = [
        "| Reviewer disagreement slice metric | Value |",
        "| --- | ---: |",
        f"| Disagreement count | {summary['disagreement_count']} |",
        f"| Disagreement rate | {_pct(summary['disagreement_rate'])} |",
        f"| Benign review-to-allow overrides | {summary['benign_review_to_allow_count']} |",
        f"| Unsafe allow-to-block overrides | {summary['unsafe_allow_to_block_count']} |",
        f"| Top disagreement category | {summary['top_disagreement_category']} |",
        f"| Top disagreement source | {summary['top_disagreement_source']} |",
        "",
        "| Category slice | Notes | Disagreements | Rate | Benign allow overrides |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in report["by_category"][:5]:
        rows.append(
            "| {slice} | {note_count} | {disagreement_count} | {rate} | "
            "{benign_review_to_allow_count} |".format(
                rate=_pct(row["disagreement_rate"]),
                **row,
            )
        )
    return "\n".join(rows)


def _safety_secondary_review_band_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    policy = report["candidate_policy"]
    targeted_categories = ", ".join(summary["targeted_categories"]) or "None"
    rows = [
        "| Secondary review-band decision aid | Value |",
        "| --- | --- |",
        f"| Recommendation | {_display_status(summary['recommendation'])} |",
        (
            "| Global threshold change recommended | "
            f"{summary['global_threshold_change_recommended']} |"
        ),
        (
            "| Secondary review floor recommended | "
            f"{summary['secondary_review_floor_recommended']} |"
        ),
        f"| Secondary review floor | {policy['secondary_review_floor']} |",
        f"| Secondary review ceiling | {policy['secondary_review_ceiling']} |",
        f"| Benign intent guard | {policy['benign_intent_guard']} |",
        f"| Targeted categories | {targeted_categories} |",
        f"| Unsafe allow-to-block overrides | {summary['unsafe_allow_to_block_count']} |",
        f"| Benign review-to-allow overrides | {summary['benign_review_to_allow_count']} |",
    ]
    if report["category_actions"]:
        rows.extend(
            [
                "",
                "| Category | Unsafe overrides | Recommended action |",
                "| --- | ---: | --- |",
            ]
        )
        for row in report["category_actions"]:
            rows.append(
                "| {risk_category} | {unsafe_allow_to_block_count} | "
                "{recommended_action} |".format(
                    **{**row, "recommended_action": _display_status(row["recommended_action"])}
                )
            )
    return "\n".join(rows)


def _safety_secondary_review_validation_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    policy = report["validation_policy"]
    rows = [
        "| Secondary review-floor validation | Value |",
        "| --- | ---: |",
        f"| Validation cases | {summary['validation_case_count']} |",
        f"| Unsafe cases | {summary['unsafe_case_count']} |",
        f"| Benign cases | {summary['benign_case_count']} |",
        f"| Multi-turn cases | {summary['multi_turn_case_count']} |",
        f"| Multi-turn unsafe capture rate | {_pct(summary['multi_turn_unsafe_capture_rate'])} |",
        f"| Multi-turn benign cases | {summary['multi_turn_benign_case_count']} |",
        (
            "| Multi-turn benign new review rate | "
            f"{_pct(summary['multi_turn_benign_new_review_rate'])} |"
        ),
        f"| Baseline unsafe allowed | {summary['baseline_unsafe_allowed_count']} |",
        f"| Floor unsafe allowed | {summary['floor_unsafe_allowed_count']} |",
        f"| Unsafe capture rate | {_pct(summary['unsafe_capture_rate'])} |",
        f"| Benign new review count | {summary['benign_new_review_count']} |",
        f"| Benign new review rate | {_pct(summary['benign_new_review_rate'])} |",
        f"| Reviewer label coverage | {_pct(summary['reviewer_label_coverage'])} |",
        (
            "| Reviewer label disagreements | "
            f"{summary['reviewer_label_disagreement_count']} |"
        ),
        f"| Floor reviewer precision | {_pct(summary['floor_reviewer_precision'])} |",
        f"| Rubric label coverage | {_pct(summary['rubric_label_coverage'])} |",
        (
            "| Rubric/reviewer disagreements | "
            f"{summary['rubric_reviewer_disagreement_count']} |"
        ),
        f"| Floor rubric precision | {_pct(summary['floor_rubric_precision'])} |",
        (
            "| Capacity sensitivity floor reviews | "
            f"{summary['capacity_sensitivity_floor_review_count']} |"
        ),
        (
            "| Capacity sensitivity max utilization | "
            f"{_pct(summary['capacity_sensitivity_max_utilization'])} |"
        ),
        (
            "| Capacity sensitivity max backlog days | "
            f"{summary['capacity_sensitivity_max_backlog_days']} |"
        ),
        f"| Benign intent guard | {policy['benign_intent_guard']} |",
        f"| Recommendation | {_display_status(summary['recommendation'])} |",
        "",
        (
            "| Reviewer daily capacity | Floor reviews | Utilization | "
            "Backlog days | Status |"
        ),
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in report["capacity_sensitivity"]:
        rows.append(
            "| {reviewer_daily_capacity} | {floor_review_count} | {utilization} | "
            "{estimated_backlog_days} | {capacity_status} |".format(
                utilization=_pct(row["capacity_utilization"]),
                **{**row, "capacity_status": _display_status(row["capacity_status"])},
            )
        )
    rows.extend(
        [
            "",
        (
            "| Category | Cases | Unsafe | Baseline unsafe allowed | "
            "Floor unsafe allowed | Benign new review |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["category_results"]:
        rows.append(
            "| {risk_category} | {case_count} | {unsafe_case_count} | "
            "{baseline_unsafe_allowed_count} | {floor_unsafe_allowed_count} | "
            "{benign_new_review_count} |".format(**row)
        )
    return "\n".join(rows)


def _safety_operating_recommendation_table(report: dict[str, Any]) -> str:
    summary = report["summary"]
    rows = [
        "| Secondary review operating recommendation | Value |",
        "| --- | --- |",
        f"| Recommendation | {_display_status(summary['recommendation'])} |",
        f"| Decision | {summary['decision']} |",
        f"| Staffing assumption | {summary['staffing_assumption']} |",
        f"| Review SLA hours | {summary['review_sla_hours']} |",
        f"| Floor review count | {summary['floor_review_count']} |",
        (
            "| Minimum reviewer daily capacity | "
            f"{summary['minimum_reviewer_daily_capacity']} |"
        ),
        (
            "| Minimum total daily capacity | "
            f"{summary['minimum_total_daily_capacity']} |"
        ),
        (
            "| Recommended capacity utilization | "
            f"{_pct(summary['recommended_capacity_utilization'])} |"
        ),
        f"| Capacity buffer cases | {summary['capacity_buffer_cases']} |",
        f"| Capacity buffer rate | {_pct(summary['capacity_buffer_rate'])} |",
        "",
        (
            "| Reviewer daily capacity | Total capacity | Utilization | "
            "Buffer cases | Backlog days | Decision |"
        ),
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in safety_operating_recommendation_rows(report):
        rows.append(
            "| {reviewer_daily_capacity} | {total_daily_capacity} | "
            "{capacity_utilization_pct} | {capacity_buffer_cases} | "
            "{estimated_backlog_days} | {operating_decision} |".format(**row)
        )
    rows.extend(["", "| Operating controls |", "| --- |"])
    for item in report["operating_controls"]:
        rows.append(f"| {item} |")
    return "\n".join(rows)


def _safety_mitigation_table(report: dict[str, Any]) -> str:
    rows = [
        "| Scenario | Unsafe allowed | Unsafe intercepted | Overblocks | Manual touches |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in safety_mitigation_rows(report):
        rows.append(
            "| {scenario} | {unsafe_allowed} | {unsafe_intercepted} | "
            "{overblocks} | {manual_touches} |".format(**row)
        )
    return "\n".join(rows)


def _safety_decision_memo_table(report: dict[str, Any]) -> str:
    rows = [
        "| Threshold decision memo | Value |",
        "| --- | --- |",
        f"| Decision | {report['decision']} |",
        f"| Selected threshold | {report['selected_threshold']} |",
        f"| Review band | {report['review_band']['low']} to {report['review_band']['high']} |",
    ]
    for index, item in enumerate(report["rationale"], start=1):
        rows.append(f"| Rationale {index} | {item} |")
    return "\n".join(rows)


def _markdown_to_html_document(markdown: str) -> str:
    body = _markdown_to_body_html(markdown)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Agent Safety & Reliability Evaluation Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px auto; max-width: 1040px; "
            "line-height: 1.55; color: #1f2937; }",
            "h1, h2 { color: #111827; }",
            "table { border-collapse: collapse; width: 100%; margin: 16px 0 24px; }",
            "th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }",
            "th { background: #f3f4f6; }",
            "td:not(:first-child), th:not(:first-child) { text-align: right; }",
            "code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }",
            "</style>",
            "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
            "",
        ]
    )


def _markdown_to_pdf_document(markdown: str) -> bytes:
    lines = _markdown_to_pdf_lines(markdown)
    pages = _paginate_pdf_lines(lines)
    return _build_pdf(pages)


def _markdown_to_pdf_lines(markdown: str, width: int = 96) -> list[str]:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue
        if line.startswith("# "):
            lines.extend(_wrap_pdf_line(line[2:].upper(), width))
            lines.append("")
            continue
        if line.startswith("## "):
            lines.append("")
            lines.extend(_wrap_pdf_line(line[3:], width))
            lines.append("")
            continue
        if line.startswith("- "):
            lines.extend(_wrap_pdf_line(f"- {line[2:]}", width, subsequent_indent="  "))
            continue
        if line.startswith("|"):
            cells = _table_cells(line)
            if _is_markdown_table_divider(cells):
                continue
            lines.extend(_wrap_pdf_line(" | ".join(cells), width))
            continue
        lines.extend(_wrap_pdf_line(line, width))
    return lines


def _wrap_pdf_line(
    line: str,
    width: int,
    *,
    subsequent_indent: str = "",
) -> list[str]:
    return wrap(
        line,
        width=width,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]


def _is_markdown_table_divider(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell.replace(":", "")) <= {"-"} for cell in cells)


def _paginate_pdf_lines(lines: list[str], page_line_count: int = 52) -> list[list[str]]:
    if not lines:
        return [[""]]
    return [
        lines[index : index + page_line_count]
        for index in range(0, len(lines), page_line_count)
    ]


def _build_pdf(pages: list[list[str]]) -> bytes:
    objects: list[tuple[int, bytes]] = [
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (3, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
    ]
    page_object_ids: list[int] = []
    for page_index, page_lines in enumerate(pages):
        page_object_id = 4 + page_index * 2
        content_object_id = page_object_id + 1
        page_object_ids.append(page_object_id)
        content = _pdf_page_content(page_lines)
        objects.append(
            (
                page_object_id,
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << /F1 3 0 R >> >> "
                    f"/Contents {content_object_id} 0 R >>"
                ).encode("ascii"),
            )
        )
        objects.append(
            (
                content_object_id,
                (
                    f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
                    + content
                    + b"\nendstream"
                ),
            )
        )

    kids = " ".join(f"{object_id} 0 R" for object_id in page_object_ids)
    objects.append(
        (
            2,
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>".encode(
                "ascii"
            ),
        )
    )
    objects.sort(key=lambda item: item[0])

    max_object_id = max(object_id for object_id, _ in objects)
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {0: 0}
    for object_id, body in objects:
        offsets[object_id] = len(pdf)
        pdf.extend(f"{object_id} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {max_object_id + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for object_id in range(1, max_object_id + 1):
        pdf.extend(f"{offsets[object_id]:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {max_object_id + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def _pdf_page_content(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 10 Tf", "14 TL", "54 738 Td"]
    for line in lines:
        commands.append(f"({_escape_pdf_text(line)}) Tj")
        commands.append("T*")
    commands.append("ET")
    return "\n".join(commands).encode("latin-1", errors="replace")


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _markdown_to_body_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("# "):
            blocks.append(f"<h1>{escape(line[2:])}</h1>")
            index += 1
            continue
        if line.startswith("## "):
            blocks.append(f"<h2>{escape(line[3:])}</h2>")
            index += 1
            continue
        if line.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(f"<li>{escape(lines[index].strip()[2:])}</li>")
                index += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        if line.startswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            blocks.append(_markdown_table_to_html(table_lines))
            continue
        blocks.append(f"<p>{escape(line)}</p>")
        index += 1
    return "\n".join(blocks)


def _markdown_table_to_html(lines: list[str]) -> str:
    header = _table_cells(lines[0])
    rows = [_table_cells(line) for line in lines[2:]]
    html_rows = [
        "<thead><tr>"
        + "".join(f"<th>{escape(cell)}</th>" for cell in header)
        + "</tr></thead>"
    ]
    html_rows.append(
        "<tbody>"
        + "".join(
            "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        + "</tbody>"
    )
    return "<table>" + "".join(html_rows) + "</table>"


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"


def _display_status(status: object) -> str:
    labels = {
        "awaiting_labels": "Awaiting independent labels",
        "dry_run_ready": "Ready for credentialed run",
        "dry_run_preview": "Prepared preview",
        "not_configured": "Not available",
        "not_published": "Not yet published",
        "pass_with_warnings": "Pass with warnings",
        "pass": "Pass",
        "warn": "Warning",
        "blocking": "Blocking",
        "non_blocking": "Non-blocking",
        "publish_with_limitations": "Publish with limitations",
        "publish": "Publish",
        "publishable": "Publishable",
        "reviewed_partial_results": "Reviewed partial results",
        "reviewed_result_present": "Reviewed result present",
        "review_required": "Review required",
        "recommend_targeted_secondary_review_floor": (
            "Recommend targeted secondary review floor"
        ),
        "add_secondary_review_floor": "Add secondary review floor",
        "validate_with_monitoring": "Validate with monitoring",
        "capacity_breach": "Capacity breach",
        "within_capacity": "Within capacity",
        "adopt_targeted_floor_with_minimum_capacity": (
            "Adopt targeted floor with minimum capacity"
        ),
        "not_recommended_capacity_breach": "Not recommended: capacity breach",
        "recommended_minimum": "Recommended minimum",
        "acceptable_extra_buffer": "Acceptable extra buffer",
        "ready": "Ready",
        "completed": "Completed",
        "evaluated": "Evaluated",
    }
    value = str(status)
    if "_" not in value:
        return labels.get(value, value)
    return labels.get(value, value.replace("_", " ").title())
