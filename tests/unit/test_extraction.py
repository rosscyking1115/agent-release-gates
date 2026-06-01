from pathlib import Path

from internal_ai_agent.evals.extraction import evaluate_extraction
from internal_ai_agent.extraction.service import extract_and_route, extract_ticket


def test_extract_ticket_returns_valid_structured_fields() -> None:
    extraction = extract_ticket(
        "Ticket TCK-0002: File Validation Failed observed in Aurora Payment Gateway. "
        "The synthetic event severity is high. Evidence includes generated control output, "
        "workflow status, and timestamp markers."
    )

    assert extraction.ticket_id == "TCK-0002"
    assert extraction.issue_category == "file_validation_failed"
    assert extraction.severity == "high"
    assert extraction.impacted_system == "Aurora Payment Gateway"
    assert extraction.evidence_present is True


def test_extract_and_route_maps_ticket_to_team() -> None:
    result = extract_and_route(
        "Confirmation Pending observed in Helios Trade Exceptions. "
        "The synthetic event severity is medium. Evidence includes generated control output, "
        "workflow status, and timestamp markers."
    )

    assert result.routing.team == "trade_support"
    assert result.routing.confidence == 0.95


def test_extraction_eval_writes_report(tmp_path: Path) -> None:
    from internal_ai_agent.data.synthetic import generate_all

    generate_all(tmp_path, ticket_count=12)
    report = evaluate_extraction(tmp_path)

    assert report["case_count"] == 12
    assert report["metrics"]["schema_validity"] == 1.0
    assert (tmp_path / "reports/extraction_eval_summary.json").exists()
    assert (tmp_path / "reports/extraction_eval_cases.jsonl").exists()
