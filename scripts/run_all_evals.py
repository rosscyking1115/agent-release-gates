from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.data.synthetic import generate_all
from internal_ai_agent.evals.agent import evaluate_agent
from internal_ai_agent.evals.extraction import evaluate_extraction
from internal_ai_agent.evals.runner import evaluate_comparison, evaluate_retriever_comparison
from internal_ai_agent.evals.security import evaluate_security
from internal_ai_agent.io import read_jsonl, write_jsonl
from internal_ai_agent.observability.otel import (
    otel_spans_from_agent_approval_cases,
    otel_spans_from_evaluation_run,
    otel_spans_from_extraction_cases,
    otel_spans_from_retriever_failures,
)
from internal_ai_agent.reporting.public_report import write_public_report


def run_all(project_root: Path) -> dict[str, Any]:
    dataset_counts = generate_all(project_root)
    comparison = evaluate_comparison(project_root)
    retriever_comparison = evaluate_retriever_comparison(project_root)
    extraction = evaluate_extraction(project_root)
    security = evaluate_security(project_root)
    agent = evaluate_agent(project_root)
    observability_spans_path = write_observability_spans(
        project_root=project_root,
        dataset_counts=dataset_counts,
        retriever_comparison=retriever_comparison,
        extraction=extraction,
        security=security,
        agent=agent,
    )
    public_report_path = write_public_report(project_root)
    return {
        "dataset_counts": dataset_counts,
        "comparison": comparison,
        "retriever_comparison": retriever_comparison,
        "extraction": extraction,
        "security": security,
        "agent": agent,
        "observability_spans_path": str(observability_spans_path),
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
    extraction_case_spans = otel_spans_from_extraction_cases(
        read_jsonl(project_root / "reports/extraction_eval_cases.jsonl")
    )
    agent_approval_spans = otel_spans_from_agent_approval_cases(
        read_jsonl(project_root / "reports/agent_eval_cases.jsonl")
    )
    output_path = project_root / "reports/observability_otel_spans.jsonl"
    write_jsonl(
        output_path,
        [
            *evaluation_spans,
            *retriever_failure_spans,
            *extraction_case_spans,
            *agent_approval_spans,
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
    print(
        f"- extraction_schema_validity: {summary['extraction']['metrics']['schema_validity']:.4f}"
    )
    print(
        f"- security_improved_safe_rate: {summary['security']['metrics']['improved_safe_rate']:.4f}"
    )
    print(
        "- agent_side_effect_block_rate: "
        f"{summary['agent']['metrics']['side_effect_block_rate']:.4f}"
    )
    print(f"Public report: {summary['public_report_path']}")


if __name__ == "__main__":
    main()
