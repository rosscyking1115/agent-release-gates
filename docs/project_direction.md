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
- safety prevalence and classifier-evaluation cases
- repeatable eval scripts
- before/after metrics
- deterministic release gates
- API endpoints for experimentation
- dashboard views for inspection
- local trace index for observability inspection
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

- Retrieval now includes sparse hybrid, local TF-IDF vector, local feature-hashed embedding-store experiments, current-evidence reranking, and a dry-run-first provider embedding evaluation path. A completed provider-backed result is still not published.
- Error analysis now identifies retrieved-but-not-cited failures, deterministic retriever-version trend snapshots, and dated lab milestone history; the expanded manual challenge set drove reranking fixes for schema mismatch, stale context, KYC artefact phrasing, and ambiguous-handoff abstention.
- Dataset profiling now exposes manual-versus-generated share, abstention coverage, task/noise/issue/team coverage, red-team coverage, and explicit data-quality gap labels. The profile now clears the previous manual-share gap with 94 hand-authored golden cases, while still flagging that provider-backed embedding comparison is not covered.
- Release gates now convert the generated artifacts into deterministic pass/warn/fail checks for benchmark coverage, retrieval grounding, safety, approval governance, and observability consistency.
- Safety evaluation now includes deterministic red-team pass/fail behavior plus a safety-classifier workflow with separate enriched challenge cases, targeted secondary-floor validation cases, weighted synthetic prevalence cases, legacy-versus-retuned threshold tuning, false positive / false negative trade-offs, human-review simulation, synthetic human-authored adjudication notes, reviewer-disagreement slices, secondary review-band analysis, secondary-floor validation, mitigation-impact reporting, a threshold decision memo, and zero high-severity false negatives at the selected threshold.
- Ticket and runbook data are still partly templated, even after adding noisy, human-like, human email-thread, manual evidence-packet, manual field-note, mixed review-bundle, retrieved-context-review, retrieved-document-injection, and long-conflicting-context cases.
- Extraction is deterministic pattern matching.
- Red-team checks include harder retrieved-context attacks, but are still string-based.
- Agent orchestration is local code rather than a state machine.
- Observability now includes local structured data, deterministic OpenTelemetry-style spans for agent traces, evaluation workflow stages, retriever failure cases, retriever ranking details, extraction cases, agent approval cases, API contract/error cases, a dashboard trace timeline, a queryable trace index, an optional OTLP/HTTP collector exporter, a local capture smoke test for the POST path, and a Dockerized OpenTelemetry Collector deployment check using collector self-metrics. It still does not include downstream span storage or production visualization beyond the local dashboard and index.

These are acceptable for the first lab version, but they should guide the next work.

## Next Build Priorities

1. Convert secondary review-floor capacity sensitivity into an operating recommendation with staffing assumptions.
2. Run and review the provider-backed embedding comparison when API access and cost are acceptable.
3. Continue making the golden suite less templated with new non-generated tickets, mixed evidence bundles, and harder retrieved-context evidence.
4. Extend the local trace index or OpenTelemetry Collector setup with optional downstream storage or visualization.
5. Add model-assisted adversarial review for the red-team suite after the deterministic scoring contract remains stable.
6. Add an optional LLM extraction path with schema repair once noisier tickets are in place.

## Secondary Use

The lab can support a career story, but only as a consequence of building something real and useful:

```text
I built a synthetic evaluation lab that helps test internal AI agent reliability, safety, and governance without using confidential data.
```

That story is stronger than building something only to look impressive.
