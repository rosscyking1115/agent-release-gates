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

- Retrieval now includes sparse hybrid, local TF-IDF vector, local feature-hashed embedding-store experiments, and current-evidence reranking, but not a provider-backed embedding model.
- Error analysis now identifies retrieved-but-not-cited failures and deterministic retriever-version trend snapshots; the expanded manual challenge set drove reranking fixes for schema mismatch, stale context, and KYC artefact phrasing.
- Ticket and runbook data are still partly templated, even after adding noisy, human-like, human email-thread, retrieved-document-injection, and long-conflicting-context cases.
- Extraction is deterministic pattern matching.
- Red-team checks are string-based.
- Agent orchestration is local code rather than a state machine.
- Observability now includes local structured data, deterministic OpenTelemetry-style spans for agent traces, evaluation workflow stages, retriever failure cases, retriever ranking details, extraction cases, agent approval cases, and API contract/error cases, plus a dashboard trace timeline, but not a live collector.

These are acceptable for the first lab version, but they should guide the next work.

## Next Build Priorities

1. Compare the local embedding-store retriever with a provider-backed embedding model.
2. Make the golden suite less templated with new non-generated tickets and harder retrieved-context attacks.
3. Add timestamped historical snapshots once the deterministic report contract is stable.
4. Add optional live collector export for the OpenTelemetry-style spans.
5. Add the next batch of non-templated manual cases before tuning the retrievers again.

## Secondary Use

The lab can support a career story, but only as a consequence of building something real and useful:

```text
I built a synthetic evaluation lab that helps test internal AI agent reliability, safety, and governance without using confidential data.
```

That story is stronger than building something only to look impressive.
