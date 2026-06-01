from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high", "unknown"]
Team = Literal["payments_ops", "client_onboarding", "trade_support", "data_quality", "unknown"]


class TicketExtraction(BaseModel):
    ticket_id: str | None = None
    title: str | None = None
    severity: Severity = "unknown"
    impacted_system: str | None = None
    issue_category: str | None = None
    evidence_present: bool = False


class RoutingDecision(BaseModel):
    team: Team = "unknown"
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str


class ExtractAndRouteResult(BaseModel):
    extraction: TicketExtraction
    routing: RoutingDecision
