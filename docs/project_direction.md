# Project Direction

## North Star

Build a useful public evaluation lab for internal AI agent reliability.

The project should help someone inspect and compare agent behavior across grounded retrieval, structured extraction, safe refusal, tool approval, auditability, and monitoring. Career value can come from that work, but it should not drive shortcuts or shallow features.

## Intended Users

- AI builders who want a local synthetic testbed before using confidential documents.
- Data scientists who want to compare retrieval and extraction strategies with repeatable metrics.
- Security-minded engineers who want small red-team cases for internal agent workflows.
- Learners who want to study evaluation-first AI engineering without needing private data or paid APIs.

## Useful Outputs

The project should produce artifacts that are independently useful:

- synthetic operations datasets
- golden evaluation cases
- red-team cases
- repeatable eval scripts
- before/after metrics
- API endpoints for experimentation
- dashboard views for inspection
- model card, threat model, and operations runbook

## Quality Bar

Do not add a feature just because it sounds impressive. A feature should be added only when it improves one of these:

- reliability measurement
- safety or governance
- explainability or auditability
- reproducibility
- local usability
- extensibility for future experiments

## Non-Negotiables

- No real company documents or confidential workflows.
- No claims about real internal AI systems.
- No fake production claims.
- No real financial or operational actions.
- No metrics without a reproducible evaluation path.
- No dashboard-only feature that is not backed by data, API behavior, or tests.

## Current Gaps

The project is useful, but it is still too deterministic in several places:

- Retrieval now includes sparse hybrid and local TF-IDF vector experiments, but not an embedding-backed vector store.
- Ticket and runbook data are still partly templated, even after adding noisy, human-like, and retrieved-document-injection cases.
- Extraction is deterministic pattern matching.
- Red-team checks are string-based.
- Agent orchestration is local code rather than a state machine.
- Observability is local structured data rather than OpenTelemetry traces.

These are acceptable for the first lab version, but they should guide the next work.

## Next Build Priorities

1. Deepen error-analysis views with example-level explanations and remediation notes for every retriever version.
2. Compare the local TF-IDF vector retriever with an embedding-backed vector store.
3. Expand the noisy evaluation dataset with more human-written variants and longer contradictory context.
4. Add OpenTelemetry-style trace export or a local trace viewer.
5. Add optional LLM/provider adapters only after deterministic evaluation remains stable.

## Secondary Use

The lab can support a career story, but only as a consequence of building something real and useful:

```text
I built a synthetic evaluation lab that helps test internal AI agent reliability, safety, and governance without using confidential data.
```

That story is stronger than building something only to look impressive.
