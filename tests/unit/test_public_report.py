from __future__ import annotations

from pathlib import Path

from internal_ai_agent.data.synthetic import generate_all
from internal_ai_agent.evals.agent import evaluate_agent
from internal_ai_agent.evals.dataset_profile import write_dataset_profile
from internal_ai_agent.evals.extraction import evaluate_extraction
from internal_ai_agent.evals.runner import (
    evaluate_comparison,
    evaluate_retriever_comparison,
    write_evaluation_history,
)
from internal_ai_agent.evals.security import evaluate_security
from internal_ai_agent.io import write_json
from internal_ai_agent.reporting.public_report import (
    generate_public_report,
    generate_public_report_html,
    generate_public_report_pdf,
    write_public_report,
)


def _prepare_reports(project_root: Path) -> None:
    generate_all(project_root)
    write_dataset_profile(project_root)
    evaluate_comparison(project_root)
    retriever_comparison = evaluate_retriever_comparison(project_root)
    extraction = evaluate_extraction(project_root)
    security = evaluate_security(project_root)
    agent = evaluate_agent(project_root)
    write_evaluation_history(
        project_root,
        retriever_report=retriever_comparison,
        extraction=extraction,
        security=security,
        agent=agent,
    )
    write_json(
        project_root / "reports/collector_export_preview.json",
        {
            "export_mode": "dry_run_preview",
            "collector_endpoint": "http://localhost:4318/v1/traces",
            "span_count": 42,
            "payload_count": 1,
            "batch_size": 200,
        },
    )


def test_generate_public_report_summarizes_core_metrics(tmp_path) -> None:
    _prepare_reports(tmp_path)

    report = generate_public_report(tmp_path)

    assert "# Internal AI Agent Evaluation Report" in report
    assert "Golden retrieval cases: 350" in report
    assert "Best current retriever: Local TF-IDF vector" in report
    assert "## Dataset Profile" in report
    assert "| Manual golden cases | 94 |" in report
    assert "| Manual share | 26.86% |" in report
    assert "manual_case_share_below_25_percent" not in report
    assert "| Hybrid sparse semantic | 100.00% | 99.65% | 99.65% | 100.00% | 1 |" in report
    assert "| Local TF-IDF vector |" in report
    assert "| Local embedding store |" in report
    assert "## Retriever Metric Snapshots" in report
    assert "004_local_tf_idf_vector" in report
    assert "citation_coverage_decreased" not in report
    assert "## Historical Evaluation Snapshots" in report
    assert "| 2026-06-02T11:00:00Z | Hybrid sparse semantic | 99.65% | 1 | +1.07% | -3 |" in report
    assert "## Retriever Failure Analysis" in report
    assert "MANUAL-FIELD-074" in report
    assert "| Local embedding store | 100.00% | 100.00% | 100.00% | 100.00% | 0 |" in report
    assert "MANUAL-CHAT-001" not in report
    assert "MANUAL-CONTROL-011" not in report
    assert "Top retrieved scores" in report
    assert "HUMAN-EMAIL-THREAD-004" not in report
    assert "| Citation coverage | 19.15% | 98.58% | +79.43% |" in report
    assert "MANUAL-AMBIGUOUS-024" not in report
    assert "| Safe response rate | 0.00% | 100.00% |" in report
    assert "| Weighted safe response rate | 0.00% | 100.00% |" in report
    assert "| Residual risk score |" in report
    assert "| retrieved_access_escalation |" in report
    assert "## Agent Trace Examples" in report
    assert "trace_eval_tck-" in report
    assert "## Observability Span Export" in report
    assert "| OTel-style spans |" in report
    assert "| Child spans |" in report
    assert "| OTLP payloads | 1 |" in report
    assert "translates this local JSONL into OTLP/HTTP JSON" in report
    assert "case-level retriever failure spans" in report
    assert "retriever ranking-detail spans" in report
    assert "case-level extraction spans" in report
    assert "case-level agent approval spans" in report
    assert "API contract and error-case spans" in report
    assert "fully synthetic evaluation lab" in report


def test_write_public_report_creates_markdown_artifact(tmp_path) -> None:
    _prepare_reports(tmp_path)

    output_path = write_public_report(tmp_path)

    assert output_path == tmp_path / "reports/evaluation_report.md"
    assert output_path.exists()
    assert "## Recommended Next Work" in output_path.read_text(encoding="utf-8")
    assert output_path.with_suffix(".html").exists()
    assert output_path.with_suffix(".pdf").exists()


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
    assert "<h2>Historical Evaluation Snapshots</h2>" in html
    assert "<h2>Dataset Profile</h2>" in html
    assert "<td>dry_run_preview</td>" in html
    assert "It does not use real company documents" in html


def test_generate_public_report_pdf_renders_shareable_artifact(tmp_path) -> None:
    _prepare_reports(tmp_path)

    pdf = generate_public_report_pdf(tmp_path)

    assert pdf.startswith(b"%PDF-1.4")
    assert b"INTERNAL AI AGENT EVALUATION REPORT" in pdf
    assert b"Golden retrieval cases: 350" in pdf
    assert b"%%EOF" in pdf
