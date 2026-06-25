# Project Direction

## North Star

Build a useful public Agent Release Safety Gates system.

The project should help someone inspect and compare agent behavior across grounded retrieval, structured extraction, safe refusal, prompt-injection resistance, tool approval, auditability, and monitoring. It should stand on its own as a public technical and research artifact.

The main research question is:

```text
When do safety interventions improve agent safety, and when do they reduce usefulness on benign operational tasks?
```

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
- optional external public RAG benchmark results
- before/after metrics
- deterministic release gates
- API endpoints for experimentation
- dashboard views for inspection
- local trace index for observability inspection
- model card, threat model, and operations runbook
- benchmark card, dataset card, contribution guide, and paper-style report outline

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

The project is useful, but the next credibility gap is external validation rather than another dashboard feature. The benchmark needs more evidence that it survives public data, human review, judge disagreement, multi-model variation, and research-style criticism.

Current gaps:

- Retrieval now includes sparse hybrid, local TF-IDF vector, local feature-hashed embedding-store experiments, current-evidence reranking, and a dry-run-first provider embedding evaluation path. A completed provider-backed result is still not published.
- A 160-case NVIDIA TechQA-RAG-Eval public benchmark track validates technical-support retrieval, and an 80-case WixQA expert-written public benchmark validates enterprise-support retrieval, while preserving the controlled synthetic operations track as the benchmark scenario.
- Error analysis now identifies retrieved-but-not-cited failures, deterministic retriever-version trend snapshots, and dated lab milestone history; the expanded manual challenge set drove reranking fixes for schema mismatch, stale context, KYC artefact phrasing, decision-log wording, partial evidence notes, and ambiguous-handoff abstention.
- Dataset profiling now exposes manual-versus-generated share, abstention coverage, task/noise/issue/team coverage, red-team coverage, and explicit data-quality gap labels. The profile now clears the previous manual-share gap with 102 hand-authored golden cases, while still flagging that provider-backed embedding comparison is not covered.
- Release gates now convert the generated artifacts into deterministic pass/warn/fail checks for benchmark coverage, retrieval grounding, safety, approval governance, and observability consistency.
- Safety evaluation now includes deterministic red-team pass/fail behavior plus a safety-classifier workflow with separate enriched challenge cases, targeted secondary-floor validation cases, weighted synthetic prevalence cases, legacy-versus-retuned threshold tuning, false positive / false negative trade-offs, human-review simulation, synthetic human-authored adjudication notes, reviewer-disagreement slices, secondary review-band analysis, secondary-floor validation, an operating recommendation, mitigation-impact reporting, a threshold decision memo, and zero high-severity false negatives at the selected threshold.
- The project now prepares an external human-review packet and label template, but does not yet publish completed independent labels or inter-rater agreement. Judge reliability includes a deterministic rubric baseline and one reviewed hosted OpenAI run, but not multi-model comparison.
- Multi-model comparison is not yet published. Optional adapters should be added only when runs can be reproduced and limitations can be stated clearly.
- A formal failure taxonomy needs to be made explicit across unsafe compliance, over-refusal, unsupported answers, missing citations, tool misuse, privacy leakage, prompt-injection following, excessive agency, and weak evidence treated as strong evidence.
- Ticket and runbook data are still partly templated, even after adding noisy, human-like, human email-thread, manual evidence-packet, manual field-note, mixed review-bundle, manual decision-log, partial-evidence, retrieved-context-review, retrieved-document-injection, and long-conflicting-context cases.
- The TechQA and WixQA public benchmarks currently use compact tracked samples rather than the full upstream datasets.
- Extraction is deterministic pattern matching.
- Red-team checks include harder retrieved-context attacks, but are still string-based.
- Agent orchestration is local code rather than a state machine.
- Observability now includes local structured data, deterministic OpenTelemetry-style spans for agent traces, evaluation workflow stages, retriever failure cases, retriever ranking details, extraction cases, agent approval cases, API contract/error cases, a dashboard trace timeline, a queryable trace index, an optional OTLP/HTTP collector exporter, a local capture smoke test for the POST path, and a Dockerized OpenTelemetry Collector deployment check using collector self-metrics. It still does not include downstream span storage or production visualization beyond the local dashboard and index.

These are acceptable for the first lab version, but they should guide the next work.

## Next Build Priorities

1. Publish benchmark and dataset cards so external reviewers can understand scope, data boundaries, scoring, and limitations.
2. Formalize the failure taxonomy and attach it to case-level results and report summaries.
3. Collect independent labels using the prepared review packet, then compare human review, deterministic rules, and hosted LLM-as-judge decisions.
4. Add optional multi-model evaluation adapters and publish only reproducible, credentialed result tables.
5. Run safety intervention experiments across baseline, refusal policy, retrieval grounding, tool approval gates, secondary review, and classifier thresholds.
6. Expand the TechQA and WixQA public benchmarks and compare local retrievers against provider-backed embeddings.
7. Continue making the golden suite less templated with new non-generated tickets, mixed evidence bundles, and harder retrieved-context evidence.
