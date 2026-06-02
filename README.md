# Internal AI Agent Evaluation Lab

A synthetic evaluation lab for testing how internal AI agents behave in enterprise operations workflows.

The lab provides generated runbooks, tickets, golden cases, red-team cases, API endpoints, evaluation reports, and a dashboard for studying grounded answers, structured extraction, safe refusal, approval-gated tools, and auditability.

This project does not reproduce, evaluate, or criticize any real company's internal AI system. It uses fully synthetic runbooks, tickets, teams, and procedures so the work can be used, inspected, and extended safely.

## Problem

Internal AI agents can be useful only when their answers are grounded, measurable, access-aware, and auditable. This lab treats the agent as an operational system rather than a generic chatbot:

- answer procedure questions with citations
- extract structured ticket fields
- route synthetic tickets to the right team
- refuse when evidence is insufficient
- block prompt injection from users and retrieved documents
- require approval before side-effecting tool calls
- log decisions for evaluation and audit

## Current Scope

The current version creates a local, reproducible lab:

- synthetic data generator
- baseline and improved retrieval evaluations
- hybrid sparse semantic, local TF-IDF vector, and local embedding-store retrieval experiments
- noisy golden cases for abbreviations, missing metadata, human email threads, and conflicting evidence
- structured ticket extraction and routing
- deterministic red-team policy checks
- controlled agent workflow with approval-gated mock tools
- trace IDs, audit events, monitoring snapshots, and OTel-style trace timeline
- FastAPI service, Streamlit dashboard, Docker/Compose runtime, CI workflow, and operations runbook

## Tech Stack

- Python 3.12
- uv
- FastAPI
- Pydantic
- pytest
- ruff
- Docker

Later phases should add provider-backed embeddings, noisier evaluation data, richer red-team cases, richer spans for additional workflows, and optional LangGraph orchestration.

## Quick Start

```powershell
uv sync
uv run python scripts/run_all_evals.py
uv run streamlit run C:\Files\Jobs\project-5-jpm_internal_ai_agent\app\streamlit_app.py --server.port 8510
uv run pytest
```

The generator writes synthetic data to:

- `data/synthetic/raw_docs/runbooks.jsonl`
- `data/synthetic/raw_tickets/tickets.jsonl`
- `data/eval/golden_cases.jsonl`
- `data/eval/red_team_cases.jsonl`

Current generated seed dataset:

| Dataset | Rows |
| --- | ---: |
| Runbook sections | 24 |
| Operations tickets | 180 |
| Golden eval cases | 272 |
| Red-team cases | 40 |

The baseline evaluation writes:

- `reports/baseline_eval_summary.json`
- `reports/baseline_eval_cases.jsonl`
- `reports/improved_eval_summary.json`
- `reports/improved_eval_cases.jsonl`
- `reports/hybrid_eval_summary.json`
- `reports/hybrid_eval_cases.jsonl`
- `reports/vector_eval_summary.json`
- `reports/vector_eval_cases.jsonl`
- `reports/embedding_eval_summary.json`
- `reports/embedding_eval_cases.jsonl`
- `reports/retriever_comparison.json`
- `reports/retriever_metric_snapshots.json`
- `reports/eval_comparison.json`
- `reports/extraction_eval_summary.json`
- `reports/extraction_eval_cases.jsonl`
- `reports/security_eval_summary.json`
- `reports/security_eval_cases.jsonl`
- `reports/agent_eval_summary.json`
- `reports/agent_eval_cases.jsonl`
- `reports/agent_trace_examples.jsonl`
- `reports/agent_otel_spans.jsonl`
- `reports/observability_otel_spans.jsonl`
- `reports/evaluation_report.md`
- `reports/evaluation_report.html`

The current baseline is intentionally simple: it uses broad system/team keyword hints rather than procedure-level retrieval. This gives the project a measurable starting point before improved retrieval is added.

The generated Markdown and HTML reports are the easiest static artifacts to share or review without running the dashboard.

Current deterministic evaluation:

| Metric | Baseline | Improved lexical | Hybrid sparse semantic | Local TF-IDF vector | Local embedding store |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.97% | 99.05% | 100.00% | 100.00% | 100.00% |
| Citation coverage | 20.38% | 98.58% | 100.00% | 100.00% | 100.00% |
| Issue category accuracy | 20.38% | 98.58% | 100.00% | 100.00% | 100.00% |
| Next action accuracy | 20.38% | 98.58% | 100.00% | 100.00% | 100.00% |
| Abstention accuracy | 78.41% | 100.00% | 100.00% | 100.00% | 100.00% |

These are first-pass synthetic metrics across exact, paraphrased, noisy, human-like, human email-thread, manually authored handoff/control-room/redacted/stale-thread cases, distractor, typo, weak-evidence, conflicting-evidence, long-conflicting-context, retrieved-document injection, and adversarial-instruction cases. Later phases should add provider-backed embedding comparison, more adversarial retrieval cases, and red-team scoring.

The hybrid retriever is intentionally local and deterministic: it combines lexical scoring with sparse semantic alias features, negated false-lead handling, phrase matching, and current-evidence reranking for forwarded-thread cases. The local TF-IDF vector retriever adds an IDF-weighted cosine index with character n-grams and alias features. The local embedding-store retriever builds stable feature-hashed dense vectors and searches them with cosine similarity. The expanded 272-case suite exposed residual manual-case final-selection failures, then the reranker was updated with stale-context penalties, schema-mismatch handling, and KYC artefact vocabulary. Those recovered cases are regression-tested synthetic benchmarks, not claims that messy real tickets are solved.

Current structured extraction evaluation:

| Metric | Score |
| --- | ---: |
| Schema validity | 100.00% |
| Issue category accuracy | 100.00% |
| Severity accuracy | 100.00% |
| Impacted system accuracy | 100.00% |
| Routing team accuracy | 100.00% |

These extraction scores are deterministic over templated synthetic tickets. Later phases should add noisier ticket text and LLM-backed extraction with schema repair.

Current security red-team evaluation:

| Metric | Baseline | Improved policy |
| --- | ---: | ---: |
| Policy block rate | 0.00% | 100.00% |
| Safe response rate | 0.00% | 100.00% |

Block rate requires an explicit policy refusal, not only an accidental no-answer response.

Current controlled agent evaluation:

| Metric | Score |
| --- | ---: |
| Trace coverage rate | 100.00% |
| Audit event coverage rate | 100.00% |
| Approval audit rate | 100.00% |
| Monitoring snapshot rate | 100.00% |
| Valid tool-call rate | 100.00% |
| Approval trigger rate | 100.00% |
| Side-effect block rate | 100.00% |
| Approved action execution rate | 100.00% |
| Route-tool selection accuracy | 100.00% |
| Unnecessary tool-call rate | 0.00% |

Read-only tools can run automatically. The side-effecting `route_ticket_mock` tool is prepared but blocked until approval is granted. Each agent run returns a trace id, structured audit events, and a monitoring snapshot.

The agent eval exports deterministic OpenTelemetry-style spans to `reports/agent_otel_spans.jsonl`. The full orchestration run also writes `reports/observability_otel_spans.jsonl`, combining those agent spans with an evaluation-run trace for data generation, retriever comparison, extraction, security, agent evaluation, report/API artifact export, case-level retriever failure spans, retriever ranking-detail spans, case-level extraction spans, case-level agent approval spans, and API contract/error-case spans. These are local interoperability artifacts, not a live tracing backend.

## Dashboard

The Streamlit dashboard presents the evaluation outcome as an inspection surface:

- headline case counts
- baseline vs improved metric chart
- retriever experiment table comparing baseline, lexical, hybrid, vector, and embedding-store retrieval
- retriever metric snapshots showing citation deltas, failure deltas, and regression flags
- retriever failure analysis showing recovered evidence, final-citation misses, score breakdowns, and fixes
- before/after metric table
- noisy-case and failure-reason analysis
- controlled agent approval and tool-governance metrics
- trace and audit coverage metrics
- deterministic agent trace examples for blocked and approved mock routes
- OpenTelemetry-style observability summary, trace timeline, component rows, and span rows
- failed-case review tables

Run it with:

```powershell
uv run streamlit run C:\Files\Jobs\project-5-jpm_internal_ai_agent\app\streamlit_app.py --server.port 8510
```

The `/ask` API supports `baseline`, `improved`, `hybrid`, `vector`, and `embedding` modes. The `hybrid` mode uses the local sparse semantic retriever, `vector` uses the local TF-IDF vector retriever, `embedding` uses the local feature-hashed embedding store, and `improved` is kept as the lexical retriever for comparison.

The generated evaluation report is available from the dashboard and from:

```text
http://localhost:8000/reports/evaluation
http://localhost:8000/reports/evaluation.html
http://localhost:8000/reports/agent/otel-spans
http://localhost:8000/reports/observability/otel-spans
```

## Docker

Build the local image:

```powershell
docker build -t internal-ai-agent-eval-lab:local .
```

Run the API only:

```powershell
docker run --rm -p 8000:8000 internal-ai-agent-eval-lab:local
```

Run the API and dashboard together:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8000/health
http://localhost:8510
```

## Safety Boundaries

- No real bank documents
- No customer or employee data
- No confidential processes
- No brand-specific system claims
- No real financial actions

The public framing is a synthetic, reusable evaluation lab: no real confidential data, measurable engineering choices, and responsible internal AI design.

## Verification

The local and CI verification path is:

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/run_all_evals.py
```

GitHub Actions is configured in `.github/workflows/ci.yml` to run linting, tests, deterministic eval report regeneration, and Docker image build verification.

For operational commands and smoke checks, see `docs/operations_runbook.md`.

## Project Notes

- `docs/model_card.md` explains intended use, data boundaries, metrics, and limitations.
- `docs/decision_memo.md` explains why the project is synthetic and what trade-offs it makes.
- `docs/project_direction.md` defines the product standard, intended users, and next build priorities.
