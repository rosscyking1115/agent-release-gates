# Internal AI Agent Evaluation Lab

A public synthetic evaluation lab for testing internal AI agent reliability across grounded retrieval, structured extraction, safe refusal, approval-gated tools, auditability, and observability.

This project is not a clone or critique of any real company's internal AI system. Its internal-operations environment uses fully synthetic runbooks, tickets, teams, procedures, and benchmark metrics so the work can be inspected and extended safely.

## Live Project

- Interactive dashboard: https://agent-evaluation-lab.streamlit.app/
- Public project page: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/
- Full evaluation report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.html
- PDF report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.pdf

## What This Project Demonstrates

Internal AI agents are only useful when their answers are grounded, measurable, access-aware, safe, and auditable. This lab treats the agent as an operational system rather than a generic chatbot:

- retrieves synthetic runbook evidence and answers with citations
- validates the retrieval harness on a 160-case public TechQA-RAG-Eval sample
- extracts structured fields from synthetic operations tickets
- routes tickets to synthetic owner teams
- refuses unsafe, weak-evidence, or policy-bypassing requests
- blocks prompt injection from both user prompts and retrieved documents
- requires approval before side-effecting mock tool calls
- records traces, audit events, monitoring snapshots, and OpenTelemetry-style spans
- publishes deterministic release gates for benchmark, safety, governance, and observability checks
- publishes deterministic reports and a public benchmark profile

## Highlights

| Area | Implementation |
| --- | --- |
| Retrieval evaluation | Baseline, lexical, hybrid sparse semantic, local TF-IDF vector, and local hashed embedding-store retrievers |
| External benchmark | 160-case NVIDIA TechQA-RAG-Eval public technical-support RAG sample |
| Structured extraction | Pydantic-validated ticket extraction and routing decisions |
| Safety testing | Red-team cases plus classifier threshold tuning, sampled prevalence estimation, human review simulation, synthetic adjudication notes, reviewer-disagreement slices, secondary review-band analysis, secondary-floor validation, operating recommendation, mitigation impact, and decision memo |
| Agent governance | Read-only tools plus approval-gated mock side effects |
| Evaluation gates | Deterministic pass/warn/fail gates for release-readiness checks |
| Observability | Trace IDs, audit events, monitoring snapshots, local span timeline, queryable trace index, OTLP/HTTP export preview, local capture smoke test, and Dockerized OpenTelemetry Collector check |
| Deployment | Public Streamlit dashboard, GitHub Pages report site, Docker image, Docker Compose, CI workflow |

## Current Evaluation Snapshot

The current benchmark is synthetic and deterministic:

| Dataset | Rows |
| --- | ---: |
| Runbook sections | 24 |
| Synthetic operations tickets | 180 |
| Golden evaluation cases | 358 |
| Red-team cases | 60 |
| Safety classifier challenge cases | 40 |
| Safety secondary-floor validation cases | 39 |
| Safety prevalence sampled cases | 80 |

| Metric | Baseline | Improved lexical | Hybrid sparse semantic | Local TF-IDF vector | Local embedding store |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retrieval hit rate@3 | 44.79% | 99.31% | 100.00% | 100.00% | 100.00% |
| Citation coverage | 18.75% | 98.26% | 99.65% | 100.00% | 100.00% |
| Issue category accuracy | 18.75% | 98.26% | 99.65% | 100.00% | 100.00% |
| Next action accuracy | 18.75% | 98.26% | 99.65% | 100.00% | 100.00% |
| Abstention accuracy | 81.28% | 100.00% | 100.00% | 100.00% | 100.00% |

Additional evaluation results:

| Evaluation | Result |
| --- | ---: |
| Structured extraction schema validity | 100.00% |
| Improved red-team safe response rate | 100.00% |
| Safety classifier recall | 90.91% |
| Safety high-severity false negatives | 0 |
| Secondary review-floor unsafe capture | 100.00% |
| Secondary review-floor multi-turn unsafe capture | 100.00% |
| Secondary review-floor benign new review rate | 9.52% |
| Secondary review-floor benign multi-turn new review rate | 0.00% |
| Secondary review-floor reviewer precision | 88.24% |
| Secondary review-floor rubric precision | 88.24% |
| Secondary review-floor capacity sensitivity max utilization | 212.50% |
| Secondary review-floor minimum recommended capacity | 16 cases/reviewer/day |
| Secondary review-floor recommended utilization | 53.12% |
| Synthetic unsafe-request prevalence estimate | 10.02% |
| Agent side-effect block rate | 100.00% |
| Agent approval audit rate | 100.00% |
| Evaluation gate status | pass with warnings |
| Evaluation gate failures | 0 |
| Indexed observability traces | 21 |

These scores are engineering checks over synthetic data, not claims about real-world production performance.

External public RAG benchmark:

| Dataset | Cases | Retrieval hit rate@3 | Top-1 citation | Impossible-question abstention |
| --- | ---: | ---: | ---: | ---: |
| NVIDIA TechQA-RAG-Eval sample | 160 | 87.50% | 77.34% | 34.38% |

TechQA retriever comparison:

| Retriever | Retrieval hit rate@3 | Top-1 citation | Impossible-question abstention | Failed cases |
| --- | ---: | ---: | ---: | ---: |
| Keyword title baseline | 72.66% | 58.59% | 59.38% | 80 |
| Local TF-IDF public retriever | 87.50% | 77.34% | 34.38% | 51 |

The TechQA track is public technical-support data under Apache-2.0. It is used as an external validation layer for retrieval and abstention behavior, not as a replacement for the controlled synthetic internal-operations benchmark.

## Benchmark Transparency

The project includes a dataset profile because high scores on synthetic cases are only meaningful when the benchmark mix is visible.

Current dataset-profile highlights:

- 102 manually authored golden cases
- 70 expected abstention cases
- 46 noise types and 22 task types
- manual share increased to 28.49%, clearing the previous manual-share gap label
- the internal-operations benchmark data is synthetic and reproducible
- the public TechQA track is separated so external validation does not blur the synthetic-lab boundary

The most important next retrieval step is comparing the local embedding-store retriever with a provider-backed embedding option. The repo now includes a dry-run-first provider embedding evaluation script for that comparison, but provider-backed results are not claimed until the script is run with credentials.

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

The repo includes a 160-case TechQA sample for the public benchmark. To refresh it from the upstream public dataset, download `train.json` from `nvidia/TechQA-RAG-Eval` into `data/public/techqa_train.json`, then run:

```powershell
uv run python scripts/prepare_techqa_public_benchmark.py
uv run python scripts/run_techqa_public_eval.py
```

Use `--limit` on the preparation script to intentionally change the tracked sample size.

Run the interactive dashboard:

```powershell
uv run streamlit run streamlit_app.py --server.port 8510
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
docker compose --profile observability up -d otel-collector
uv run python scripts/check_otel_collector_deployment.py
docker compose --profile observability down
uv run python scripts/run_provider_embedding_eval.py
docker build -t internal-ai-agent-eval-lab:local .
```

CI runs linting, tests, deterministic report regeneration, local OTLP smoke testing, Dockerized OpenTelemetry Collector verification, and Docker build verification.

## Technical Artifacts

The public project page keeps the main experience focused on the dashboard and evaluation report. These JSON artifacts remain available for technical review:

- Dataset profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/dataset_profile.json
- Evaluation gates: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_gates.json
- TechQA public RAG summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_rag_summary.json
- TechQA public benchmark profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_benchmark_profile.json
- TechQA public retriever comparison: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_retriever_comparison.json
- Safety classifier summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_classifier_eval_summary.json
- Safety threshold sweep: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_threshold_sweep.json
- Safety threshold retuning: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_threshold_retuning.json
- Safety human review simulation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_human_review_simulation.json
- Safety adjudication notes: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_adjudication_notes.json
- Safety reviewer disagreement slices: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_reviewer_disagreement_slices.json
- Safety secondary review-band analysis: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_secondary_review_band_analysis.json
- Safety secondary review-floor validation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_secondary_review_floor_validation.json
- Safety secondary review operating recommendation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_secondary_review_operating_recommendation.json
- Safety mitigation impact: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_mitigation_impact.json
- Safety threshold decision memo: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_threshold_decision_memo.json
- Observability trace index: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/observability_trace_index.json

## Streamlit Cloud Deployment

The interactive dashboard is deployed on Streamlit Community Cloud:

- https://agent-evaluation-lab.streamlit.app/

Deployment settings:

```text
Repository: rosscyking1115/internal-ai-agent-eval-lab
Branch: main
Main file path: streamlit_app.py
App URL: agent-evaluation-lab
```

The root `streamlit_app.py` entrypoint loads the dashboard from `app/streamlit_app.py`, and `requirements.txt` installs the local package plus dependencies.

## Safety Boundaries

- no real company documents
- no customer or employee data
- no confidential workflows
- no brand-specific system claims
- no real financial or operational actions
- side-effecting tools are mock-only and approval-gated

## Current Limitations

- The benchmark is synthetic and still partly templated.
- The TechQA public benchmark currently uses a 160-case compact sample, not the full upstream dataset.
- The local embedding store uses deterministic feature hashing, not a provider-backed embedding model.
- Provider-backed embedding evaluation is available as an optional script, but no provider-backed result is published yet.
- Structured extraction is deterministic pattern matching, not LLM extraction.
- The controlled agent is a local workflow, not a LangGraph state machine.

## Useful Follow-Up Work

- Add more hand-authored golden cases and noisier synthetic tickets, especially cases that challenge the remaining hybrid final-selection miss.
- Expand the TechQA public benchmark beyond the 160-case sample and compare the same retrievers on the larger dataset.
- Compare the local embedding-store retriever with a provider-backed embedding model.
- Extend the OpenTelemetry Collector setup with optional downstream storage or visualization beyond the local trace index.
- Add an optional LLM extraction path with schema repair.
