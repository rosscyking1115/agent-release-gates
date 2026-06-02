from __future__ import annotations

from pathlib import Path

from internal_ai_agent.data.synthetic import generate_all
from internal_ai_agent.evals.agent import evaluate_agent
from internal_ai_agent.evals.extraction import evaluate_extraction
from internal_ai_agent.evals.runner import evaluate_comparison, evaluate_retriever_comparison
from internal_ai_agent.evals.security import evaluate_security
from internal_ai_agent.reporting.public_report import (
    generate_public_report,
    generate_public_report_html,
    write_public_report,
)


def _prepare_reports(project_root: Path) -> None:
    generate_all(project_root)
    evaluate_comparison(project_root)
    evaluate_retriever_comparison(project_root)
    evaluate_extraction(project_root)
    evaluate_security(project_root)
    evaluate_agent(project_root)


def test_generate_public_report_summarizes_core_metrics(tmp_path) -> None:
    _prepare_reports(tmp_path)

    report = generate_public_report(tmp_path)

    assert "# Internal AI Agent Evaluation Report" in report
    assert "Golden retrieval cases: 264" in report
    assert "| Hybrid sparse semantic | 100.00% | 100.00% | 100.00% | 100.00% | 0 |" in report
    assert "| Local TF-IDF vector |" in report
    assert "| Local embedding store |" in report
    assert "## Retriever Metric Snapshots" in report
    assert "citation_coverage_decreased" in report
    assert "## Retriever Failure Analysis" in report
    assert "NOISY-MISSING-007" in report
    assert "| Local embedding store | 100.00% | 99.51% | 99.51% | 100.00% | 1 |" in report
    assert "MANUAL-CHAT-001" in report
    assert "Top retrieved scores" in report
    assert "HUMAN-EMAIL-THREAD-004" not in report
    assert "| Citation coverage | 20.98% | 98.54% | +77.56% |" in report
    assert "| Safe response rate | 0.00% | 100.00% |" in report
    assert "## Agent Trace Examples" in report
    assert "trace_eval_tck-" in report
    assert "## OpenTelemetry-Style Span Export" in report
    assert "| OTel-style spans |" in report
    assert "fully synthetic evaluation lab" in report


def test_write_public_report_creates_markdown_artifact(tmp_path) -> None:
    _prepare_reports(tmp_path)

    output_path = write_public_report(tmp_path)

    assert output_path == tmp_path / "reports/evaluation_report.md"
    assert output_path.exists()
    assert "## Recommended Next Work" in output_path.read_text(encoding="utf-8")
    assert output_path.with_suffix(".html").exists()


def test_generate_public_report_html_renders_tables_and_safety_boundary(tmp_path) -> None:
    _prepare_reports(tmp_path)

    html = generate_public_report_html(tmp_path)

    assert "<!doctype html>" in html
    assert "<h1>Internal AI Agent Evaluation Report</h1>" in html
    assert "<table>" in html
    assert "<td>Hybrid sparse semantic</td>" in html
    assert "<td>Local TF-IDF vector</td>" in html
    assert "<td>Local embedding store</td>" in html
    assert "<h2>Retriever Metric Snapshots</h2>" in html
    assert "It does not use real company documents" in html
