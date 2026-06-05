# Internal AI Agent Evaluation Lab Plan

## Purpose

Build a public evaluation lab for internal AI agent reliability without using
confidential company data. The lab uses a synthetic internal-operations
environment for controlled evaluation and a separate public TechQA benchmark for
external retrieval validation.

The project should demonstrate whether an agent workflow is grounded, safe,
access-aware, auditable, and reproducible. It should not claim to reproduce or
assess any real company's internal system.

## Scope

The lab evaluates:

- grounded retrieval over synthetic runbooks
- structured extraction from synthetic operations tickets
- safe refusal and weak-evidence abstention behavior
- prompt-injection and retrieved-context attack resistance
- approval-gated mock tool use
- audit events, traces, and OpenTelemetry-style span exports
- deterministic release gates and public reports
- external public technical-support retrieval on TechQA-RAG-Eval

## Data Boundary

Internal operations data remains synthetic:

- runbooks
- tickets
- owner teams
- workflow procedures
- golden evaluation labels
- safety and red-team cases
- approval and audit events

The TechQA track is explicitly separate. It is public technical-support data
used to validate retrieval behavior outside the synthetic benchmark.

## Current Milestones

1. Synthetic operations data generation
2. Golden retrieval benchmark
3. Baseline and improved lexical retrieval
4. Hybrid sparse semantic retrieval
5. Local TF-IDF vector retrieval
6. Local feature-hashed embedding-store retrieval
7. Structured extraction with schema validation
8. Red-team and safety classifier evaluation
9. Approval-gated agent workflow
10. OpenTelemetry-style observability and trace index
11. Docker, CI, Streamlit, and GitHub Pages deployment
12. TechQA public RAG benchmark integration

## Public Deliverables

- Streamlit dashboard
- GitHub Pages project page
- generated HTML/PDF evaluation report
- JSON evaluation artifacts
- deterministic test suite
- Docker and Docker Compose runtime
- model card, threat model, operations runbook, and architecture docs

## Quality Bar

Every public metric should have:

- a reproducible data source
- a deterministic evaluation path
- a clear limitation
- public-facing wording that avoids production claims

Every new feature should improve at least one of:

- reliability measurement
- safety and governance
- explainability and auditability
- reproducibility
- extensibility

## Current Limitations

- The internal benchmark is synthetic and still partly templated.
- The TechQA public benchmark uses a compact sample, not the full upstream dataset.
- Extraction is deterministic rather than LLM-backed.
- Red-team checks are deterministic and rule-based.
- Provider-backed embedding results are not published yet.
- Observability is local JSONL plus collector validation, not downstream production tracing.

## Next Priorities

1. Expand the TechQA public benchmark and compare local retrieval with provider embeddings.
2. Add more hand-authored, noisy synthetic tickets and evidence bundles.
3. Add optional downstream trace storage or visualization.
4. Add model-assisted adversarial review while preserving deterministic gates.
5. Add optional LLM extraction with schema repair and failure analysis.
