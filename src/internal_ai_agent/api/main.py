import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

from internal_ai_agent.agent.workflow import run_controlled_agent
from internal_ai_agent.api.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    AskRequest,
    AskResponse,
    ExtractRequest,
    ExtractResponse,
    RetrievedSectionResponse,
)
from internal_ai_agent.data.synthetic import build_runbooks
from internal_ai_agent.extraction.service import extract_and_route
from internal_ai_agent.rag.baseline import (
    answer_with_baseline,
    answer_with_embedding_store,
    answer_with_hybrid,
    answer_with_lexical,
    answer_with_vector,
)

app = FastAPI(
    title="Internal AI Agent Evaluation Lab",
    description="Synthetic enterprise operations AI agent demo.",
    version="0.1.0",
)

PROJECT_ROOT = Path.cwd()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/reports/evaluation", response_class=PlainTextResponse)
def evaluation_report() -> str:
    return (PROJECT_ROOT / "reports/evaluation_report.md").read_text(encoding="utf-8")


@app.get("/reports/evaluation.html", response_class=HTMLResponse)
def evaluation_report_html() -> str:
    return (PROJECT_ROOT / "reports/evaluation_report.html").read_text(encoding="utf-8")


@app.get("/reports/evaluation.pdf")
def evaluation_report_pdf() -> Response:
    return Response(
        (PROJECT_ROOT / "reports/evaluation_report.pdf").read_bytes(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="internal_ai_agent_evaluation_report.pdf"'
            )
        },
    )


@app.get("/reports/evaluation/history", response_class=JSONResponse)
def evaluation_history() -> dict[str, object]:
    return json.loads(
        (PROJECT_ROOT / "reports/evaluation_history.json").read_text(encoding="utf-8")
    )


@app.get("/reports/agent/otel-spans", response_class=PlainTextResponse)
def agent_otel_spans() -> str:
    return (PROJECT_ROOT / "reports/agent_otel_spans.jsonl").read_text(encoding="utf-8")


@app.get("/reports/observability/otel-spans", response_class=PlainTextResponse)
def observability_otel_spans() -> str:
    return (PROJECT_ROOT / "reports/observability_otel_spans.jsonl").read_text(
        encoding="utf-8"
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    runbooks = [section.__dict__ for section in build_runbooks()]
    retriever_modes = {"baseline", "hybrid", "vector", "embedding"}
    mode = request.mode if request.mode in retriever_modes else "improved"
    if mode == "baseline":
        answer = answer_with_baseline(request.question, runbooks)
    elif mode == "hybrid":
        answer = answer_with_hybrid(request.question, runbooks, user_role=request.user_role)
    elif mode == "vector":
        answer = answer_with_vector(request.question, runbooks, user_role=request.user_role)
    elif mode == "embedding":
        answer = answer_with_embedding_store(
            request.question, runbooks, user_role=request.user_role
        )
    else:
        answer = answer_with_lexical(request.question, runbooks, user_role=request.user_role)
    return AskResponse(
        mode=mode,
        answer=answer.answer,
        issue_category=answer.issue_category,
        team=answer.team,
        next_action=answer.next_action,
        citations=answer.citations,
        retrieved_sections=[
            RetrievedSectionResponse(
                section_id=section.section_id,
                title=section.title,
                team=section.team,
                score=section.score,
            )
            for section in answer.retrieved_sections
        ],
        abstained=answer.abstained,
    )


@app.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    result = extract_and_route(request.text)
    return ExtractResponse(extraction=result.extraction, routing=result.routing)


@app.post("/agent/run", response_model=AgentRunResponse)
def agent_run(request: AgentRunRequest) -> AgentRunResponse:
    result = run_controlled_agent(
        request.question,
        ticket_text=request.ticket_text,
        user_role=request.user_role,
        approval_granted=request.approval_granted,
        trace_id=request.trace_id,
    )
    return AgentRunResponse(**result.model_dump())
