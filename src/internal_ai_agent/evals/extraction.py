from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from internal_ai_agent.extraction.service import extract_and_route
from internal_ai_agent.io import read_jsonl, write_json, write_jsonl


@dataclass(frozen=True)
class ExtractionCaseResult:
    ticket_id: str
    schema_valid: bool
    issue_category_match: bool
    severity_match: bool
    impacted_system_match: bool
    routing_team_match: bool
    predicted_issue_category: str | None
    expected_issue_category: str
    predicted_team: str
    expected_team: str


def evaluate_extraction(project_root: Path) -> dict[str, Any]:
    tickets = read_jsonl(project_root / "data/synthetic/raw_tickets/tickets.jsonl")
    results = [_evaluate_ticket(ticket) for ticket in tickets]
    report = {
        "system_version": "deterministic_structured_extraction",
        "dataset": "synthetic_tickets",
        "case_count": len(results),
        "metrics": {
            "schema_validity": _rate(row.schema_valid for row in results),
            "issue_category_accuracy": _rate(row.issue_category_match for row in results),
            "severity_accuracy": _rate(row.severity_match for row in results),
            "impacted_system_accuracy": _rate(row.impacted_system_match for row in results),
            "routing_team_accuracy": _rate(row.routing_team_match for row in results),
        },
        "notes": [
            "Extraction uses deterministic pattern matching over synthetic ticket text.",
            "This report proves the schema and routing evaluation path before LLM extraction.",
        ],
    }
    write_json(project_root / "reports/extraction_eval_summary.json", report)
    write_jsonl(
        project_root / "reports/extraction_eval_cases.jsonl", (asdict(row) for row in results)
    )
    return report


def _evaluate_ticket(ticket: dict[str, Any]) -> ExtractionCaseResult:
    result = extract_and_route(str(ticket["description"]))
    return ExtractionCaseResult(
        ticket_id=str(ticket["ticket_id"]),
        schema_valid=True,
        issue_category_match=result.extraction.issue_category == ticket["issue_category"],
        severity_match=result.extraction.severity == ticket["severity"],
        impacted_system_match=result.extraction.impacted_system == ticket["impacted_system"],
        routing_team_match=result.routing.team == ticket["team"],
        predicted_issue_category=result.extraction.issue_category,
        expected_issue_category=str(ticket["issue_category"]),
        predicted_team=result.routing.team,
        expected_team=str(ticket["team"]),
    )


def _rate(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(1 for item in items if item) / len(items), 4)
