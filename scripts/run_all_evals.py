from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.data.synthetic import generate_all
from internal_ai_agent.evals.agent import evaluate_agent
from internal_ai_agent.evals.extraction import evaluate_extraction
from internal_ai_agent.evals.runner import evaluate_comparison, evaluate_retriever_comparison
from internal_ai_agent.evals.security import evaluate_security
from internal_ai_agent.reporting.public_report import write_public_report


def run_all(project_root: Path) -> dict[str, Any]:
    dataset_counts = generate_all(project_root)
    comparison = evaluate_comparison(project_root)
    retriever_comparison = evaluate_retriever_comparison(project_root)
    extraction = evaluate_extraction(project_root)
    security = evaluate_security(project_root)
    agent = evaluate_agent(project_root)
    public_report_path = write_public_report(project_root)
    return {
        "dataset_counts": dataset_counts,
        "comparison": comparison,
        "retriever_comparison": retriever_comparison,
        "extraction": extraction,
        "security": security,
        "agent": agent,
        "public_report_path": str(public_report_path),
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
