# Internal AI Agent Evaluation Lab

A public synthetic evaluation lab for testing internal AI agent reliability across grounded retrieval, structured extraction, safe refusal, approval-gated tools, auditability, and observability.

This project is not a clone or critique of any real company's internal AI system. It uses fully synthetic runbooks, tickets, teams, procedures, and metrics so the work can be inspected and extended safely.

## Live Project

- Public site: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/
- Full evaluation report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.html
- Dataset profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/dataset_profile.json

## What This Project Demonstrates

Internal AI agents are only useful when their answers are grounded, measurable, access-aware, safe, and auditable. This lab treats the agent as an operational system rather than a generic chatbot:

- retrieves synthetic runbook evidence and answers with citations
- extracts structured fields from synthetic operations tickets
- routes tickets to synthetic owner teams
- refuses unsafe, weak-evidence, or policy-bypassing requests
- blocks prompt injection from both user prompts and retrieved documents
- requires approval before side-effecting mock tool calls
- records traces, audit events, monitoring snapshots, and OpenTelemetry-style spans
- publishes deterministic reports and a public benchmark profile

## Highlights

| Area | Implementation |
| --- | --- |
| Retrieval evaluation | Baseline, lexical, hybrid sparse semantic, local TF-IDF vector, and local hashed embedding-store retrievers |
| Structured extraction | Pydantic-validated ticket extraction and routing decisions |
| Safety testing | Red-team cases for prompt injection, leakage, weak evidence, excessive agency, access escalation, and tool misuse |
| Agent governance | Read-only tools plus approval-gated mock side effects |
| Observability | Trace IDs, audit events, monitoring snapshots, local span timeline, OTLP/HTTP export preview, and local collector smoke test |
| Deployment | Public GitHub Pages report site, Docker image, Docker Compose, CI workflow |

## Current Evaluation Snapshot

The current benchmark is synthetic and deterministic:

| Dataset | Rows |
| --- | ---: |
| Runbook sections | 24 |
| Synthetic operations tickets | 180 |
| Golden evaluation cases | 296 |
| Red-team cases | 60 |

| Metric | Baseline | Improved lexical | Hybrid sparse semantic | Local TF-IDF vector | Local embedding store |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.22% | 99.13% | 100.00% | 100.00% | 100.00% |
| Citation coverage | 20.00% | 98.70% | 100.00% | 100.00% | 100.00% |
| Issue category accuracy | 20.00% | 98.70% | 100.00% | 100.00% | 100.00% |
| Next action accuracy | 20.00% | 98.70% | 100.00% | 100.00% | 100.00% |
| Abstention accuracy | 78.38% | 100.00% | 100.00% | 100.00% | 100.00% |

Additional evaluation results:

| Evaluation | Result |
| --- | ---: |
| Structured extraction schema validity | 100.00% |
| Structured extraction routing accuracy | 100.00% |
| Improved red-team safe response rate | 100.00% |
| Improved red-team residual risk score | 0 |
| Agent side-effect block rate | 100.00% |
| Agent approval audit rate | 100.00% |
| Exported OTel-style spans | 1,154 |

These scores are engineering checks over synthetic data, not claims about real-world production performance.

## Benchmark Transparency

The project includes a dataset profile because high scores on synthetic cases are only meaningful when the benchmark mix is visible.

Current dataset-profile highlights:

- 40 manually authored golden cases
- 66 expected abstention cases
- 38 noise types and 15 task types
- explicit gap label: `manual_case_share_below_25_percent`
- all public benchmark data is synthetic and reproducible

The most important next data-quality step is adding more hand-authored cases before further retriever tuning.

## Architecture

```text
Synthetic data generator
  -> runbooks, tickets, golden cases, red-team cases

Evaluation runners
  -> retrieval, extraction, safety, controlled-agent, observability

Application surfaces
  -> FastAPI endpoints, Streamlit dashboard, generated reports

Delivery
  -> GitHub Pages static site, Docker, Docker Compose, GitHub Actions CI
```

## Tech Stack

- Python 3.12
- FastAPI
- Streamlit
- Pydantic
- pytest
- ruff
- Docker / Docker Compose
- GitHub Actions
- GitHub Pages

## Run Locally

Install dependencies and regenerate deterministic reports:

```powershell
uv sync
uv run python scripts/run_all_evals.py
```

Run the interactive dashboard:

```powershell
uv run streamlit run app/streamlit_app.py --server.port 8510
```

Run API and dashboard together with Docker Compose:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8510
http://localhost:8000/health
```

## Verification

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/run_all_evals.py
uv run python scripts/smoke_otel_collector.py
docker build -t internal-ai-agent-eval-lab:local .
```

CI runs linting, tests, deterministic report regeneration, OTLP collector smoke testing, and Docker build verification.

## Safety Boundaries

- no real company documents
- no customer or employee data
- no confidential workflows
- no brand-specific system claims
- no real financial or operational actions
- side-effecting tools are mock-only and approval-gated

## Current Limitations

- The benchmark is synthetic and still partly templated.
- The local embedding store uses deterministic feature hashing, not a provider-backed embedding model.
- Structured extraction is deterministic pattern matching, not LLM extraction.
- The controlled agent is a local workflow, not a LangGraph state machine.
- The public deployment is currently a static evidence/report site; the interactive Streamlit dashboard runs locally or through Docker.

## Useful Follow-Up Work

- Add more hand-authored golden cases and noisier synthetic tickets.
- Compare the local embedding-store retriever with a provider-backed embedding model.
- Deploy the interactive Streamlit dashboard publicly.
- Add a full OpenTelemetry Collector deployment check.
- Add an optional LLM extraction path with schema repair.
