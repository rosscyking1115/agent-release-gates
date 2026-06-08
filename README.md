# Agent Safety & Reliability Evaluation Lab

A public evaluation harness for measuring AI-agent reliability under grounded retrieval, unsafe requests, weak evidence, prompt injection, and approval-gated tool-use conditions.

The core benchmark uses a fully synthetic internal-operations environment so safety, retrieval, and tool-governance behavior can be tested without confidential data. The project is not a clone, critique, or reverse-engineering attempt of any real company's internal AI system.

## Live Project

- Interactive dashboard: https://agent-evaluation-lab.streamlit.app/
- Public project page: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/
- Full evaluation report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.html
- PDF report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.pdf

## What This Project Demonstrates

AI agents are only useful when their answers are grounded, measurable, access-aware, safe, and auditable. This lab treats the agent as an operational system rather than a generic chatbot:

- retrieves synthetic runbook evidence and answers with citations
- validates the retrieval harness on a 160-case public TechQA-RAG-Eval sample
- validates enterprise-support retrieval on an 80-case public WixQA expert-written sample
- extracts structured fields from synthetic operations tickets
- routes tickets to synthetic owner teams
- refuses unsafe, weak-evidence, or policy-bypassing requests
- blocks prompt injection from both user prompts and retrieved documents
- requires approval before side-effecting mock tool calls
- records traces, audit events, monitoring snapshots, and OpenTelemetry-style spans
- publishes deterministic release gates for benchmark, safety, governance, and observability checks
- publishes deterministic reports and a public benchmark profile

## Research Framing

The working research question is:

```text
When do safety interventions improve agent safety, and when do they reduce usefulness on benign operational tasks?
```

The project is moving toward a research-grade public artifact, not just a dashboard. Current work covers a deterministic synthetic benchmark, public TechQA and WixQA retrieval tracks, safety classifier thresholding, human-review simulation, an external-review packet, a reviewed hosted model-judge run, and release gates. Planned work adds completed independent human labels, multi-model comparison, broader failure analysis, and public contribution workflows.

## Highlights

| Area | Implementation |
| --- | --- |
| Retrieval evaluation | Baseline, lexical, hybrid sparse semantic, local TF-IDF vector, and local hashed embedding-store retrievers |
| External benchmarks | 160-case NVIDIA TechQA-RAG-Eval sample and 80-case WixQA expert-written enterprise-support sample |
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
| External human-review packet | awaiting labels |
| Reviewed hosted model-judge label accuracy | 95.83% |
| Reviewed hosted model-judge unsafe misses | 0 |
| Agent side-effect block rate | 100.00% |
| Agent approval audit rate | 100.00% |
| Evaluation gate status | pass with warnings |
| Evaluation gate failures | 0 |
| Indexed observability traces | 21 |

These scores are engineering checks over synthetic data, not claims about real-world production performance.

External public RAG benchmark:

| Dataset | Cases | Retrieval hit rate@3 | Top-1 citation | Additional metric |
| --- | ---: | ---: | ---: | ---: |
| NVIDIA TechQA-RAG-Eval sample | 160 | 87.50% | 77.34% | 34.38% impossible-question abstention |
| WixQA expert-written sample | 80 | 88.75% | 75.00% | 95.65% multi-article retrieval@3 |

TechQA retriever comparison:

| Retriever | Retrieval hit rate@3 | Top-1 citation | Impossible-question abstention | Failed cases |
| --- | ---: | ---: | ---: | ---: |
| Keyword title baseline | 72.66% | 58.59% | 59.38% | 80 |
| Local TF-IDF public retriever | 87.50% | 77.34% | 34.38% | 51 |

WixQA retriever comparison:

| Retriever | Retrieval hit rate@3 | Top-1 citation | Multi-article retrieval@3 | Failed cases |
| --- | ---: | ---: | ---: | ---: |
| Keyword title baseline | 61.25% | 46.25% | 65.22% | 43 |
| Local TF-IDF WixQA retriever | 88.75% | 75.00% | 95.65% | 20 |

The TechQA track is public technical-support data under Apache-2.0. The WixQA track is public enterprise-support data under MIT. They are used as external validation layers for retrieval behavior, not as replacements for the controlled synthetic internal-operations benchmark.

## Benchmark Transparency

The project includes a dataset profile because high scores on synthetic cases are only meaningful when the benchmark mix is visible.

Current dataset-profile highlights:

- 102 manually authored golden cases
- 70 expected abstention cases
- 46 noise types and 22 task types
- manual share increased to 28.49%, clearing the previous manual-share gap label
- the internal-operations benchmark data is synthetic and reproducible
- the public TechQA and WixQA tracks are separated so external validation does not blur the synthetic-lab boundary

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

The repo also includes an 80-case WixQA expert-written sample for public enterprise-support retrieval. To refresh it from upstream, download `wixqa_expertwritten/test.jsonl` and `wix_kb_corpus/wix_kb_corpus.jsonl` from `Wix/WixQA` into `data/public/`, then run:

```powershell
uv run python scripts/prepare_wixqa_public_benchmark.py
uv run python scripts/run_wixqa_public_eval.py
```

`scripts/run_all_evals.py` also writes `reports/public_rag_findings.json`, a
cross-public summary that combines TechQA and WixQA without mixing those metrics
into the synthetic internal-operations benchmark.

The raw WixQA downloads are ignored by git; only the compact tracked benchmark sample and generated metrics are published.

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

- Benchmark card: https://github.com/rosscyking1115/internal-ai-agent-eval-lab/blob/main/docs/benchmark_card.md
- Dataset card: https://github.com/rosscyking1115/internal-ai-agent-eval-lab/blob/main/docs/dataset_card.md
- Failure taxonomy: https://github.com/rosscyking1115/internal-ai-agent-eval-lab/blob/main/docs/failure_taxonomy.md
- Research roadmap: https://github.com/rosscyking1115/internal-ai-agent-eval-lab/blob/main/docs/research_roadmap.md
- Contributing guide: https://github.com/rosscyking1115/internal-ai-agent-eval-lab/blob/main/CONTRIBUTING.md

- Dataset profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/dataset_profile.json
- Evaluation gates: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_gates.json
- External human review protocol: https://github.com/rosscyking1115/internal-ai-agent-eval-lab/blob/main/docs/external_human_review_protocol.md
- External review packet: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_packet.csv
- External review label template: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_label_template.csv
- External human review summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_summary.json
- TechQA public RAG summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_rag_summary.json
- TechQA public benchmark profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_benchmark_profile.json
- TechQA public retriever comparison: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_retriever_comparison.json
- WixQA public RAG summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/wixqa_public_rag_summary.json
- WixQA public benchmark profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/wixqa_public_benchmark_profile.json
- WixQA public retriever comparison: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/wixqa_public_retriever_comparison.json
- Cross-public RAG findings: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/public_rag_findings.json
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
- The WixQA public benchmark currently uses an 80-case compact sample, not the full upstream benchmark suite.
- The local embedding store uses deterministic feature hashing, not a provider-backed embedding model.
- Provider-backed embedding evaluation is available as an optional script, but no provider-backed result is published yet.
- Human-review labels are simulated workflow labels, not real independent human annotations.
- An external human-review packet and label template are prepared, but completed independent labels are not published yet.
- Hosted LLM-as-judge evidence is currently one reviewed OpenAI calibration run, not a multi-model comparison.
- Multi-model comparison is planned but not yet published.
- Structured extraction is deterministic pattern matching, not LLM extraction.
- The controlled agent is a local workflow, not a LangGraph state machine.

## Useful Follow-Up Work

- Formalize the failure taxonomy across unsafe compliance, over-refusal, unsupported answers, missing citations, tool misuse, privacy leakage, prompt-injection following, and weak evidence treated as strong evidence.
- Collect independent human labels using the prepared review packet and compare them with deterministic rules and hosted LLM-as-judge results.
- Add optional multi-model adapters and publish only credentialed, reproducible model comparison results.
- Run safety intervention experiments across baseline, refusal policy, retrieval grounding, tool approval gates, secondary review, and classifier thresholds.
- Expand the TechQA public benchmark beyond the 160-case sample and compare local retrieval with provider-backed embeddings.
- Expand the WixQA public benchmark and compare local retrieval with provider-backed embeddings.
