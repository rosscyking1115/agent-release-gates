from __future__ import annotations

from pydantic import BaseModel, Field

from internal_ai_agent.agent.schemas import AgentRunResult
from internal_ai_agent.extraction.schemas import ExtractAndRouteResult


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    user_role: str = "operations_analyst"
    mode: str = "improved"


class RetrievedSectionResponse(BaseModel):
    section_id: str
    title: str
    team: str
    score: float


class AskResponse(BaseModel):
    mode: str
    answer: str
    issue_category: str | None
    team: str | None
    next_action: str | None
    citations: list[str]
    retrieved_sections: list[RetrievedSectionResponse]
    abstained: bool


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1)


class ExtractResponse(ExtractAndRouteResult):
    pass


class AgentRunRequest(BaseModel):
    question: str = Field(min_length=1)
    ticket_text: str = ""
    user_role: str = "operations_analyst"
    approval_granted: bool = False
    trace_id: str | None = None


class AgentRunResponse(AgentRunResult):
    pass
