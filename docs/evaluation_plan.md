# Evaluation Plan

## Purpose

The evaluation harness should show whether the internal AI agent is becoming more reliable, grounded, and safe over time.

## Datasets

- `golden_cases.jsonl`: expected answers, citations, ticket fields, and routing decisions.
- `red_team_cases.jsonl`: prompt injection, unsafe agency, leakage, and weak-evidence cases.
- `tickets.jsonl`: synthetic operations tickets used by extraction and routing tasks.
- `runbooks.jsonl`: synthetic runbook sections used by retrieval and citation tasks.

## Baseline Metrics

- retrieval hit-rate@k
- citation coverage
- abstention accuracy
- JSON schema validity
- field-level extraction accuracy
- routing accuracy
- prompt-injection block rate

## Deterministic Checks

- output is valid JSON when JSON is required
- cited source ids exist
- retrieved document team scope matches the user role
- tool calls match allowed schemas
- refusal appears when evidence is insufficient

## Reporting

Each evaluation run should save:

- timestamp
- system version
- dataset version
- metric values
- failed case ids
- notes on known limitations

The README should show real before/after numbers only after the eval runner has produced them.

The dashboard reads the saved report artifacts rather than recomputing metrics on page load:

- `reports/baseline_eval_summary.json`
- `reports/improved_eval_summary.json`
- `reports/hybrid_eval_summary.json`
- `reports/vector_eval_summary.json`
- `reports/embedding_eval_summary.json`
- `reports/retriever_comparison.json`
- `reports/retriever_metric_snapshots.json`
- `reports/eval_comparison.json`
- `reports/baseline_eval_cases.jsonl`
- `reports/improved_eval_cases.jsonl`
- `reports/vector_eval_cases.jsonl`
- `reports/agent_eval_summary.json`
- `reports/agent_eval_cases.jsonl`
- `reports/agent_trace_examples.jsonl`
- `reports/agent_otel_spans.jsonl`
- `reports/observability_otel_spans.jsonl`

## Baseline Version

The first baseline is `baseline_team_hint_retrieval`. It uses broad synthetic system and team keywords, then chooses the first matching runbook section. This is expected to find the correct team more often than the exact procedure, which creates useful baseline failures for later error analysis.

## Improved Lexical Version

The first improved version is `improved_lexical_retrieval`. It scores token overlap against runbook titles and content, then filters by the requesting role. This is still deterministic and local, but it gives the project a concrete before/after comparison before adding embeddings or a full vector store.

The current golden set includes exact, paraphrased, abbreviated, missing-metadata, false-lead, typo/abbreviation, human email-thread, manually authored chat/meeting/screenshot/desk-note/handoff/control-room/redacted/stale-thread fragments, adversarial-instruction, weak-evidence, conflicting-evidence, and long conflicting-context cases. Reports include grouped analysis by task type and noise type, plus failure-reason counts.

Known limitation: most golden cases are still generated from templates, even when they simulate email threads and contradictory context. The expanded manual challenge set is still small, but it now exposes residual final-selection failures; future eval sets should include more varied human-written phrasing, misleading system names, and adversarial retrieved text.

## Hybrid Sparse Semantic Version

The hybrid version is `hybrid_sparse_semantic_retrieval`. It combines lexical overlap with deterministic sparse semantic alias features for procedure concepts such as missing KYC documents, duplicate record clusters, and confirmation-pending trade exceptions.

This version is deliberately local and dependency-free. It is not a production embedding store; it is an experiment that shows whether synonym-aware retrieval reduces the known paraphrase and missing-metadata failures before adding pgvector or an embedding provider.

## Local TF-IDF Vector Version

The vector version is `local_tfidf_vector_retrieval`. It builds an IDF-weighted local vector index over runbook titles, content, team hints, procedure aliases, and character n-grams, then scores with cosine similarity plus a small keyword rerank.

This is a real local vector-space retrieval experiment, but it is not an embedding model, pgvector store, or paid provider. Its current value is comparison discipline: it reaches full retrieval hit@3 on the synthetic suite, while preserving a visible final-ranking failure for missing-metadata analysis.

## Local Embedding Store Version

The embedding-store version is `local_hashed_embedding_store_retrieval`. It builds a local store of dense, stable feature-hashed vectors over runbook titles, content, team hints, and procedure aliases, then searches with cosine similarity plus lightweight reranking.

This is not a paid embedding provider or production vector database. It exercises the same evaluation contract an embedding-backed vector store would need: index build, query embedding, top-k retrieval, final answer selection, citation checking, and failure analysis. In the current synthetic suite it reaches full retrieval hit@3 but has more final-selection failures than the TF-IDF vector retriever, which is useful evidence that embeddings do not remove the need for reranking and answer-grounding checks.

The retriever comparison report saves a five-system table:

- baseline team hints
- improved lexical retrieval
- hybrid sparse semantic retrieval
- local TF-IDF vector retrieval
- local embedding-store retrieval

The public report and dashboard also surface retriever failure analysis. The overview counts failed cases, cases where the expected section was retrieved but not finally cited, abstention mismatches, and the top failure reason for each retriever. The example table keeps the diagnostic and recommended fix attached to concrete case ids.

## Retriever Metric Snapshots

The snapshot report is `retriever_metric_snapshots.json`. It records the ordered retriever versions as deterministic snapshots rather than timestamped run history. This keeps CI reproducible while making metric regressions visible.

Each snapshot stores citation coverage, retrieval hit rate@3, next-action accuracy, abstention accuracy, failed-case count, deltas from the previous retriever, and regression flags. A regression is flagged when citation coverage decreases or failed-case count increases compared with the previous snapshot.

## Structured Extraction Version

The first extraction version is `deterministic_structured_extraction`. It validates a `TicketExtraction` schema and a `RoutingDecision` schema over synthetic ticket descriptions. It reports schema validity, issue-category accuracy, severity accuracy, impacted-system accuracy, and routing-team accuracy.

Known limitation: the current extraction cases are templated. Future eval sets should include abbreviated tickets, missing fields, misspellings, and conflicting evidence.

## Controlled Agent Version

The first controlled-agent version is `controlled_agent_approval_gate`. It uses deterministic read-only tools for runbook search, ticket extraction, and escalation-note drafting, then requires explicit approval before running `route_ticket_mock`.

It reports trace coverage rate, audit event coverage rate, approval audit rate, monitoring snapshot rate, valid tool-call rate, approval trigger rate, side-effect block rate, approved action execution rate, route-tool selection accuracy, and unnecessary tool-call rate. It also exports deterministic trace examples, OpenTelemetry-style spans for representative blocked and approved mock route runs, and case-level approval-decision spans for every synthetic ticket.

Known limitation: this is a deterministic local workflow rather than a LangGraph runtime. The shape is intentionally close to a future state machine so the approval and audit contract can be tested before adding orchestration dependencies.

## Observability Version

The first observability version adds trace ids, structured audit events, and monitoring snapshots to each controlled-agent run. It also writes deterministic OpenTelemetry-style span rows for representative blocked and approved tool routes. The full orchestration run adds an evaluation-level trace covering data generation, retriever comparison, extraction evaluation, security evaluation, agent evaluation, and report/API artifact export. Retriever failures are exported as case-level spans with expected, predicted, and retrieved citation attributes. Local vector and embedding-store retriever rankings are exported as case-level spans with top-candidate score components and winning margins. Extraction outcomes are exported as case-level spans with schema, issue-category, severity, impacted-system, and routing-team attributes. Agent approval outcomes are exported as case-level spans with approval, blocking, execution, audit, and tool-validity attributes. API contracts are exported as endpoint and expected-error spans for health, report, span-export, ask, extract, agent-run, validation-error, and not-found behavior. These spans are normalized into the local dashboard trace timeline. This makes the project easier to debug and gives the dashboard measurable operational controls rather than only answer-quality metrics.

Known limitation: the span export is local JSONL rather than a live OpenTelemetry collector pipeline. Future versions should add optional live collector export.

## Security Red-Team Version

The first security version evaluates `red_team_cases.jsonl` against baseline and improved behavior. It reports explicit policy block rate and safe response rate across prompt injection, grounding bypass, excessive agency, access-control bypass, retrieved-document injection, sensitive-data requests, weak evidence, tool misuse, system-prompt leakage, and unbounded consumption.

Known limitation: current red-team checks are deterministic string-based cases. Future versions should include more varied phrasing and retrieved-document attacks embedded inside runbook content.
