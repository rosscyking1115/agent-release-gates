import pytest
from pydantic import ValidationError

from internal_ai_agent.api.main import (
    agent_otel_spans,
    agent_run,
    app,
    ask,
    evaluation_report,
    evaluation_report_html,
    evaluation_report_pdf,
    extract,
    health,
    observability_otel_spans,
)
from internal_ai_agent.api.schemas import AgentRunRequest, AskRequest, ExtractRequest


def test_health() -> None:
    assert health() == {"status": "ok"}


def test_evaluation_report_endpoint_returns_markdown() -> None:
    report = evaluation_report()

    assert "# Internal AI Agent Evaluation Report" in report
    assert "## Retrieval Evaluation" in report


def test_evaluation_report_html_endpoint_returns_html() -> None:
    report = evaluation_report_html()

    assert "<!doctype html>" in report
    assert "<h1>Internal AI Agent Evaluation Report</h1>" in report


def test_evaluation_report_pdf_endpoint_returns_pdf() -> None:
    response = evaluation_report_pdf()

    assert response.media_type == "application/pdf"
    assert response.body.startswith(b"%PDF-1.4")
    assert b"INTERNAL AI AGENT EVALUATION REPORT" in response.body


def test_agent_otel_spans_endpoint_returns_jsonl() -> None:
    report = agent_otel_spans()

    assert '"name": "agent.run"' in report
    assert '"span_id":' in report


def test_observability_otel_spans_endpoint_returns_jsonl() -> None:
    report = observability_otel_spans()

    assert '"name": "evaluation.run"' in report
    assert '"name": "retriever.case_failure"' in report
    assert '"name": "retriever.ranking_case"' in report
    assert '"name": "extraction.case_result"' in report
    assert '"name": "agent.approval_decision"' in report
    assert '"name": "api.error_case"' in report
    assert '"name": "agent.run"' in report
    assert '"span_id":' in report


def test_api_contract_rejects_invalid_requests() -> None:
    with pytest.raises(ValidationError):
        AskRequest(question="")
    with pytest.raises(ValidationError):
        ExtractRequest(text="")
    with pytest.raises(ValidationError):
        AgentRunRequest(question="")
    assert "/unknown" not in {route.path for route in app.routes}


def test_ask_endpoint_function_returns_improved_answer() -> None:
    response = ask(
        AskRequest(
            question=(
                "Ticket TCK-0002: File Validation Failed observed in Aurora Payment Gateway. "
                "What should I do next?"
            )
        )
    )

    assert response.mode == "improved"
    assert response.abstained is False
    assert response.citations
    assert response.retrieved_sections


def test_ask_endpoint_can_run_baseline_mode() -> None:
    response = ask(
        AskRequest(
            question=(
                "Ticket TCK-0001: Confirmation Pending observed in Helios Trade Exceptions. "
                "What should I do next?"
            ),
            mode="baseline",
        )
    )

    assert response.mode == "baseline"
    assert response.abstained is False


def test_ask_endpoint_can_run_hybrid_mode() -> None:
    response = ask(
        AskRequest(
            question=(
                "Several records look duplicated and need stewardship review in "
                "Atlas Data Controls. Which procedure applies?"
            ),
            mode="hybrid",
        )
    )

    assert response.mode == "hybrid"
    assert response.issue_category == "duplicate_record_cluster"
    assert response.citations == ["RB-DATA_QUALITY-04"]


def test_ask_endpoint_can_run_vector_mode() -> None:
    response = ask(
        AskRequest(
            question=(
                "Several records look duplicated and need stewardship review in "
                "Atlas Data Controls. Which procedure applies?"
            ),
            mode="vector",
        )
    )

    assert response.mode == "vector"
    assert response.issue_category == "duplicate_record_cluster"
    assert response.citations == ["RB-DATA_QUALITY-04"]


def test_ask_endpoint_can_run_embedding_mode() -> None:
    response = ask(
        AskRequest(
            question=(
                "New intake case without a ticket id. The client activation is paused because "
                "a required KYC artifact is absent from Nova Client Intake evidence."
            ),
            mode="embedding",
        )
    )

    assert response.mode == "embedding"
    assert response.issue_category == "missing_kyc_document"
    assert response.citations == ["RB-CLIENT_ONBOARDING-01"]


def test_extract_endpoint_function_returns_route() -> None:
    response = extract(
        ExtractRequest(
            text=(
                "Ticket TCK-0003: Settlement Delay observed in Aurora Payment Gateway. "
                "The synthetic event severity is high. Evidence includes generated control output, "
                "workflow status, and timestamp markers."
            )
        )
    )

    assert response.extraction.issue_category == "settlement_delay"
    assert response.routing.team == "payments_ops"


def test_agent_run_endpoint_requires_approval_for_mock_route() -> None:
    response = agent_run(
        AgentRunRequest(
            question=(
                "Ticket TCK-0003: Settlement Delay observed in Aurora Payment Gateway. "
                "What should I do next?"
            ),
            ticket_text=(
                "Ticket TCK-0003: Settlement Delay observed in Aurora Payment Gateway. "
                "The synthetic event severity is high. Evidence includes generated control output, "
                "workflow status, and timestamp markers."
            ),
            trace_id="trace_test_api",
        )
    )

    assert response.trace_id == "trace_test_api"
    route_tool = next(
        decision
        for decision in response.tool_decisions
        if decision.tool_name == "route_ticket_mock"
    )
    assert route_tool.requires_approval is True
    assert route_tool.executed is False
