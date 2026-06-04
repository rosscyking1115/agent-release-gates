# Operations Runbook

This runbook explains how to verify the synthetic internal AI agent lab locally.

## Local Verification

Run the full deterministic check:

```powershell
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/run_all_evals.py
uv run python scripts/smoke_otel_collector.py
docker compose --profile observability up -d otel-collector
uv run python scripts/check_otel_collector_deployment.py
docker compose --profile observability down
uv run python scripts/run_provider_embedding_eval.py
```

Expected result:

- lint passes
- tests pass
- synthetic data is regenerated
- baseline, extraction, security, controlled-agent, dataset-profile, history, release-gates, observability, local trace-index, collector-preview, Markdown, HTML, and PDF reports are written to `reports/`
- OTLP/HTTP payloads are posted to a temporary local capture endpoint and verified
- the same payloads are posted to a Dockerized OpenTelemetry Collector and verified through collector self-metrics

## Dashboard

Start the evaluation dashboard:

```powershell
uv run streamlit run C:\Files\Jobs\project-5-jpm_internal_ai_agent\app\streamlit_app.py --server.port 8510
```

Open:

```text
http://localhost:8510
```

The dashboard reads saved report artifacts. If metrics look stale, rerun:

```powershell
uv run python scripts/run_all_evals.py
```

## API Smoke Test

Start the FastAPI app:

```powershell
uv run uvicorn internal_ai_agent.api.main:app --host 127.0.0.1 --port 8000
```

Check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/reports/evaluation
http://127.0.0.1:8000/reports/evaluation/history
http://127.0.0.1:8000/reports/evaluation/gates
http://127.0.0.1:8000/reports/evaluation.html
http://127.0.0.1:8000/reports/evaluation.pdf
http://127.0.0.1:8000/reports/dataset-profile
http://127.0.0.1:8000/reports/observability/trace-index
http://127.0.0.1:8000/reports/observability/collector-preview
```

Expected response:

```json
{"status":"ok"}
```

## Collector Export

The deterministic eval run also writes `reports/observability_trace_index.json`. Use it when you want a local, queryable summary of traces, error spans, retriever failures, API error cases, approval decisions, ranking cases, and component health without running downstream observability storage.

The deterministic eval run writes `reports/collector_export_preview.json`. It describes
how many OTLP/HTTP payloads would be sent to the default collector endpoint without
making a network call.

Dry-run the export:

```powershell
uv run python scripts/export_otel_collector.py
```

Post to a collector only when one is running:

```powershell
uv run python scripts/export_otel_collector.py --endpoint http://localhost:4318/v1/traces --post
```

Smoke-test the live HTTP POST path without running an external collector:

```powershell
uv run python scripts/smoke_otel_collector.py
```

Expected result:

- a local capture endpoint starts on `127.0.0.1`
- each OTLP/HTTP payload is posted with `Content-Type: application/json`
- the received span count matches `reports/observability_otel_spans.jsonl`
- `reports/collector_export_smoke.json` is written locally and ignored by git

Run the Dockerized OpenTelemetry Collector deployment check:

```powershell
docker compose --profile observability up -d otel-collector
uv run python scripts/check_otel_collector_deployment.py
docker compose --profile observability down
```

Expected result:

- the collector accepts OTLP/HTTP trace payloads on `http://localhost:4318/v1/traces`
- `http://localhost:8888/metrics` shows accepted and exported span counters increasing by the expected span count
- `reports/collector_deployment_check.json` is written locally and ignored by git
- the check fails if payload counts, HTTP status codes, or collector span metrics are missing

## Container Verification

Build the local container image:

```powershell
docker build -t internal-ai-agent-eval-lab:local .
```

Run the API from the image:

```powershell
docker run --rm -p 8000:8000 internal-ai-agent-eval-lab:local
```

Check:

```text
http://127.0.0.1:8000/health
```

Run the API and dashboard together:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8510
```

## Provider Embedding Evaluation

The provider-backed embedding comparison is optional and dry-run-first. The default command estimates the evaluation shape without making network calls:

```powershell
uv run python scripts/run_provider_embedding_eval.py
```

Run the provider comparison only after setting a provider key:

```powershell
$env:OPENAI_API_KEY="..."
uv run python scripts/run_provider_embedding_eval.py --run
```

Optional controls:

```powershell
uv run python scripts/run_provider_embedding_eval.py --run --model text-embedding-3-small --batch-size 64
```

Expected provider-run result:

- `reports/provider_embedding_eval_summary.json` is written locally and ignored by git
- `reports/provider_embedding_eval_cases.jsonl` is written locally and ignored by git
- the same citation, abstention, routing, and failure-analysis checks are applied as the local retrievers
- the report should not be described as a project result until the provider-backed run has actually completed

## Safety Checks

Before sharing the project publicly, confirm:

- no real company documents are present
- no customer, employee, or confidential data is present
- report metrics come from synthetic datasets
- README framing says this is an original synthetic evaluation lab
