# Agent Safety & Reliability Evaluation Lab Plan

## Purpose

Build a public evaluation lab for AI-agent safety and reliability without using
confidential company data. The lab uses a synthetic internal-operations
environment for controlled evaluation and a separate public TechQA benchmark for
external retrieval validation.

The project should demonstrate whether an agent workflow is grounded, safe,
access-aware, auditable, and reproducible. It should also measure where safety
interventions create false positives, false negatives, review load, or usefulness
loss. It should not claim to reproduce or assess any real company's internal
system.

This is a real, reusable tool meant for adoption by practitioners and teams that
ship agent changes, and for delivering practical value to the community and to
organizations evaluating agent safety — not a one-off demonstration. A core
design principle is that the evaluation stays runnable by anyone, including
without paid API keys and on self-hosted infrastructure: hosted-provider
comparisons are always optional add-ons over a free, self-hostable baseline. This
keeps the barrier to adoption low for the community and supports privacy- or
cost-constrained organizations (for example in regulated sectors) that cannot
send evaluation data to third-party APIs.

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
- safety/usefulness trade-offs across intervention settings
- failure taxonomy and judge-reliability analysis

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
used to validate retrieval behavior outside the synthetic benchmark. The tracked
sample currently contains 480 cases.

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
13. TechQA keyword baseline versus local TF-IDF retriever comparison
14. Manual decision-log and partial-evidence golden-case expansion

## Public Deliverables

- Streamlit dashboard
- GitHub Pages project page
- generated HTML/PDF evaluation report
- JSON evaluation artifacts
- deterministic test suite
- Docker and Docker Compose runtime
- model card, threat model, operations runbook, and architecture docs
- benchmark card, dataset card, research roadmap, and contribution guide

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
- The TechQA public benchmark uses a 480-case compact sample, not the full upstream dataset.
- Extraction is deterministic rather than LLM-backed.
- Red-team checks are deterministic and rule-based.
- Reviewed provider-backed embedding results are published for the synthetic benchmark and the public RAG tracks, where the hosted embedding beats the local retriever; a multi-model comparison is not published yet.
- Observability is local JSONL plus collector validation, not downstream production tracing.

## Next Priorities

1. Publish benchmark and dataset cards, plus contribution guidance for external review.
2. Formalize the failure taxonomy across safety, retrieval, citation, privacy, tool-use, and usefulness failures.
3. Add a human-labeled calibration sample and compare human review with deterministic rules and LLM-as-judge.
4. Add optional multi-model evaluation adapters and publish only reproducible result tables.
5. Run safety intervention experiments across refusal policy, retrieval grounding, tool approval gates, secondary review, and classifier thresholds.
6. Expand the TechQA public benchmark beyond 480 cases and compare local retrieval with provider embeddings.
