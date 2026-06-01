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
- hybrid sparse semantic retrieval experiment
- noisy golden cases for abbreviations, missing metadata, and conflicting evidence
- structured ticket extraction and routing
- deterministic red-team policy checks
- controlled agent workflow with approval-gated mock tools
- trace IDs, audit events, and monitoring snapshots
- FastAPI service, Streamlit dashboard, Docker/Compose runtime, CI workflow, and operations runbook

## Tech Stack

- Python 3.12
- uv
- FastAPI
- Pydantic
- pytest
- ruff
- Docker

Later phases should add a true vector store, noisier evaluation data, richer red-team cases, OpenTelemetry export, and optional LangGraph orchestration.

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
| Golden eval cases | 216 |
| Red-team cases | 40 |

The baseline evaluation writes:

- `reports/baseline_eval_summary.json`
- `reports/baseline_eval_cases.jsonl`
- `reports/improved_eval_summary.json`
- `reports/improved_eval_cases.jsonl`
- `reports/hybrid_eval_summary.json`
- `reports/hybrid_eval_cases.jsonl`
- `reports/retriever_comparison.json`
- `reports/eval_comparison.json`
- `reports/extraction_eval_summary.json`
- `reports/extraction_eval_cases.jsonl`
- `reports/security_eval_summary.json`
- `reports/security_eval_cases.jsonl`
- `reports/agent_eval_summary.json`
- `reports/agent_eval_cases.jsonl`

The current baseline is intentionally simple: it uses broad system/team keyword hints rather than procedure-level retrieval. This gives the project a measurable starting point before improved retrieval is added.

Current deterministic evaluation:

| Metric | Baseline | Improved lexical | Hybrid sparse semantic |
| --- | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.45% | 98.30% | 100.00% |
| Citation coverage | 19.89% | 97.73% | 100.00% |
| Issue category accuracy | 19.89% | 97.73% | 100.00% |
| Next action accuracy | 19.89% | 97.73% | 100.00% |
| Abstention accuracy | 81.94% | 100.00% | 100.00% |

These are first-pass synthetic metrics across exact, paraphrased, noisy, distractor, typo, weak-evidence, conflicting-evidence, and adversarial-instruction cases. Later phases should add a true vector index, more adversarial retrieval cases, and red-team scoring.

The hybrid retriever is intentionally local and deterministic: it combines lexical scoring with sparse semantic alias features, negated false-lead handling, and phrase matching. It is useful for measuring the value of synonym-aware retrieval before introducing a vector database or paid embedding model.

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

## Dashboard

The Streamlit dashboard presents the evaluation outcome as an inspection surface:

- headline case counts
- baseline vs improved metric chart
- retriever experiment table comparing baseline, lexical, and hybrid retrieval
- before/after metric table
- noisy-case and failure-reason analysis
- controlled agent approval and tool-governance metrics
- trace and audit coverage metrics
- failed-case review tables

Run it with:

```powershell
uv run streamlit run C:\Files\Jobs\project-5-jpm_internal_ai_agent\app\streamlit_app.py --server.port 8510
```

The `/ask` API supports `baseline`, `improved`, and `hybrid` modes. The `hybrid` mode uses the local sparse semantic retriever; `improved` is kept as the lexical retriever for comparison.

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

GitHub Actions is configured in `.github/workflows/ci.yml` to run linting, tests, and deterministic eval report regeneration.

For operational commands and smoke checks, see `docs/operations_runbook.md`.

## Project Notes

- `docs/model_card.md` explains intended use, data boundaries, metrics, and limitations.
- `docs/decision_memo.md` explains why the project is synthetic and what trade-offs it makes.
- `docs/project_direction.md` defines the product standard, intended users, and next build priorities.
