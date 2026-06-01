from __future__ import annotations

import re

from internal_ai_agent.data.synthetic import TEAMS
from internal_ai_agent.extraction.schemas import (
    ExtractAndRouteResult,
    RoutingDecision,
    TicketExtraction,
)

CATEGORY_TITLES = {
    category: category.replace("_", " ").title()
    for team in TEAMS.values()
    for category, _action in team["categories"]
}

SYSTEM_TO_TEAM = {team["system"].lower(): team_id for team_id, team in TEAMS.items()}


def extract_ticket(text: str) -> TicketExtraction:
    normalized = text.lower()
    issue_category = _find_issue_category(normalized)
    impacted_system = _find_impacted_system(normalized)
    return TicketExtraction(
        ticket_id=_find_ticket_id(text),
        title=CATEGORY_TITLES.get(issue_category),
        severity=_find_severity(normalized),
        impacted_system=impacted_system,
        issue_category=issue_category,
        evidence_present=_has_evidence(normalized),
    )


def route_ticket(extraction: TicketExtraction) -> RoutingDecision:
    if extraction.impacted_system:
        team = SYSTEM_TO_TEAM.get(extraction.impacted_system.lower(), "unknown")
    else:
        team = _team_for_category(extraction.issue_category)

    if team == "unknown":
        return RoutingDecision(
            team="unknown",
            confidence=0.2,
            rationale="No recognized synthetic system or issue category was found.",
        )

    confidence = 0.95 if extraction.issue_category and extraction.evidence_present else 0.65
    return RoutingDecision(
        team=team,
        confidence=confidence,
        rationale=f"Matched synthetic system or category to {team}.",
    )


def extract_and_route(text: str) -> ExtractAndRouteResult:
    extraction = extract_ticket(text)
    routing = route_ticket(extraction)
    return ExtractAndRouteResult(extraction=extraction, routing=routing)


def _find_ticket_id(text: str) -> str | None:
    match = re.search(r"\b(?:TCK|WEAK)-\d{3,4}\b", text, flags=re.IGNORECASE)
    return match.group(0).upper() if match else None


def _find_issue_category(normalized: str) -> str | None:
    for category, title in CATEGORY_TITLES.items():
        if title.lower() in normalized or category in normalized:
            return category
    return None


def _find_impacted_system(normalized: str) -> str | None:
    for system in SYSTEM_TO_TEAM:
        if system in normalized:
            return system.title()
    return None


def _find_severity(normalized: str) -> str:
    match = re.search(r"\bseverity is (low|medium|high)\b", normalized)
    if match:
        return match.group(1)
    match = re.search(r"\bseverity (low|medium|high)\b", normalized)
    return match.group(1) if match else "unknown"


def _has_evidence(normalized: str) -> bool:
    return "generated control output" in normalized and "workflow" in normalized


def _team_for_category(issue_category: str | None) -> str:
    if not issue_category:
        return "unknown"
    for team_id, team in TEAMS.items():
        if any(category == issue_category for category, _action in team["categories"]):
            return team_id
    return "unknown"
