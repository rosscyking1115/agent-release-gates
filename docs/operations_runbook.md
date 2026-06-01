# Operations Runbook

This runbook explains how to verify the synthetic internal AI agent lab locally.

## Local Verification

Run the full deterministic check:

```powershell
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/run_all_evals.py
```

Expected result:

- lint passes
- tests pass
- synthetic data is regenerated
- baseline, extraction, security, and controlled-agent reports are written to `reports/`

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
```

Expected response:

```json
{"status":"ok"}
```

## Safety Checks

Before sharing the project publicly, confirm:

- no real company documents are present
- no customer, employee, or confidential data is present
- report metrics come from synthetic datasets
- README framing says this is an original synthetic evaluation lab
