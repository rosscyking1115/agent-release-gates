# Agent Safety & Reliability Evaluation Lab

A public evaluation system for testing whether AI-agent workflows remain grounded, safe, auditable, and useful under retrieval, refusal, prompt-injection, and approval-gated tool-use conditions.

This project is not a clone, assessment, or reverse-engineering attempt of any company's internal AI system. The controlled operations benchmark is synthetic by design; TechQA and WixQA are used separately as public retrieval-validation datasets.

## Live Project

- Interactive dashboard: https://agent-evaluation-lab.streamlit.app/
- Public project page: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/
- Full evaluation report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.html
- PDF report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.pdf

## What This Project Does

The lab evaluates an AI-agent workflow across four reliability questions:

- Does the agent retrieve the right evidence and cite it?
- Does it abstain or refuse when evidence is weak, unsafe, or prompt-injected?
- Does it require approval before mock side-effecting tool calls?
- Does it leave enough trace, audit, and monitoring evidence for review?

The result is a reproducible evaluation artifact rather than a one-off dashboard: deterministic eval runners, generated reports, CI checks, Dockerized local execution, a public Streamlit dashboard, and a GitHub Pages report site.

## Current Evidence Snapshot

| Area | Current result |
| --- | --- |
| Controlled benchmark | 358 synthetic golden cases, 60 red-team cases, 180 synthetic operations tickets |
| Retrieval | 100.00% synthetic retrieval hit rate@3 with local TF-IDF/vector-style retrievers |
| Public RAG validation | 160 TechQA cases and 80 WixQA cases evaluated separately from the synthetic benchmark |
| Safety | 90.91% classifier recall, 0 high-severity false negatives in the current challenge set |
| Agent governance | 100.00% mock side-effect block rate and approval audit rate |
| Intervention study | 3 deterministic before/after studies covering instruction hierarchy, action gates, and safety classifier review |
| Hosted judge calibration | Reviewed OpenAI and Anthropic judge runs with public-safe provider comparison |

These results are engineering evidence over controlled benchmarks. They are not claims of real-world production performance.

## Key Findings

- Safety metrics are not meaningful alone; the lab reports over-review cost, benign auto-blocks, weak-evidence handling, and unsafe misses beside the headline scores.
- Layered safeguards reduce selected prompt-injection, unsafe-action, and unsafe-request failures in controlled studies while making review burden visible.
- Public TechQA and WixQA retrieval tracks help test whether the RAG harness works beyond self-contained synthetic data.
- Synthetic operations data remains useful for controlled tests that would be unsafe or impractical to run on confidential real workflows.
- The next strongest validation step is independent human labelling, followed by broader multi-model comparison.

## What Is Included

- Evaluation runners for retrieval, extraction, safety classification, controlled-agent behavior, and observability.
- Baseline-vs-intervention studies for instruction hierarchy, action-risk gates, and safety classifier review policy.
- Public benchmark documentation, dataset boundaries, failure taxonomy, and external-review packet.
- Streamlit dashboard for interactive inspection.
- GitHub Pages report and PDF for public review.
- CI, Docker, Docker Compose, linting, tests, and deterministic report regeneration.

## Run Locally

```powershell
uv sync
uv run python scripts/run_all_evals.py
uv run streamlit run streamlit_app.py --server.port 8510
```

Open:

```text
http://localhost:8510
```

Run the API and dashboard together:

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:8510
http://localhost:8000/health
```

## Verification

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/run_all_evals.py
uv run python scripts/build_public_site.py
docker build -t internal-ai-agent-eval-lab:local .
```

CI runs linting, tests, deterministic report checks, local OpenTelemetry smoke testing, Dockerized collector verification, and Docker build verification.

## Review Materials

- Benchmark card: [docs/benchmark_card.md](docs/benchmark_card.md)
- Agent safety intervention study: [docs/agent_safety_intervention_study.md](docs/agent_safety_intervention_study.md)
- Dataset card: [docs/dataset_card.md](docs/dataset_card.md)
- Failure taxonomy: [docs/failure_taxonomy.md](docs/failure_taxonomy.md)
- External reviewer handoff pack: [docs/reviewer_handoff_pack.md](docs/reviewer_handoff_pack.md)
- Technical artifact index: [docs/technical_artifacts.md](docs/technical_artifacts.md)

## Current Limitations

- The controlled benchmark is synthetic and still partly templated.
- Public TechQA and WixQA tracks use compact samples, not the full upstream datasets.
- Human-review labels are currently simulated workflow labels; independent reviewer labels are prepared but not yet published.
- Hosted model evidence includes reviewed judge-calibration runs, not a broad multi-model agent comparison.
- Provider-backed embedding and reranker adapters are prepared, but credentialed hosted results are not claimed until reviewed.

## Roadmap

- Collect independent human labels using the prepared review packet.
- Add reproducible multi-model comparison across hosted and open-source models.
- Extend intervention studies to RAG grounding, memory/context pollution, and goal-conflict scenarios.
- Expand public RAG validation beyond the current compact TechQA and WixQA samples.
- Expand the paper-style intervention report with external reviewer disagreement analysis.
- Invite external review through issues and contribution guidelines.
