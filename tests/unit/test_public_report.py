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
    assert "Golden retrieval cases: 216" in report
    assert "| Hybrid sparse semantic | 100.00% | 100.00% | 100.00% | 100.00% | 0 |" in report
    assert "| Citation coverage | 19.89% | 97.73% | +77.84% |" in report
    assert "| Safe response rate | 0.00% | 100.00% |" in report
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
    assert "It does not use real company documents" in html
