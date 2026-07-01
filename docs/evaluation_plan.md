# Evaluation Plan

## Purpose

The evaluation harness should show whether an AI-agent workflow is becoming more reliable, grounded, safe, and useful over time.

The system uses a controlled synthetic operations domain for measurement, plus separate public-data tracks where external validation is available. The central research question is how safety interventions change both unsafe compliance risk and benign-task usefulness.

## Datasets

- `golden_cases.jsonl`: expected answers, citations, ticket fields, and routing decisions.
- `red_team_cases.jsonl`: prompt injection, unsafe agency, leakage, weak-evidence, and retrieved-context attack cases.
- `safety_challenge_cases.jsonl`: enriched synthetic safety classifier challenge cases.
- `safety_secondary_review_validation_cases.jsonl`: separate ambiguous medium-severity slice for validating the targeted secondary review floor.
- `safety_prevalence_cases.jsonl`: weighted sampled synthetic request stream for safety classifier and prevalence evaluation.
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
- safety classifier precision, recall, false positive rate, and false negative rate
- estimated unsafe-request prevalence and human-review load

## Research-Grade Extension Track

The next evaluation layer should turn the lab into a stronger public benchmark:

- formal failure taxonomy for unsafe compliance, over-refusal, unsupported answer, missing citation, tool misuse, privacy leakage, prompt-injection following, excessive agency, and weak evidence treated as strong evidence
- hand-authored evaluation cases that include benign controls, ambiguous requests, unsafe requests, prompt injection, weak evidence, excessive agency, and tool misuse
- human-labeled calibration sample with reviewer agreement and disagreement notes
- judge reliability comparison between deterministic rules, LLM-as-judge, and human review
- multi-model evaluation adapters with clearly separated unpublished, credentialed, and reproducible result states
- safety intervention matrix comparing baseline, refusal policy, retrieval grounding, tool approval gate, secondary review, and classifier threshold settings
- paper-style report with abstract, method, dataset, metrics, results, failure analysis, limitations, and future work

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
- `reports/techqa_public_rag_summary.json`
- `reports/techqa_public_benchmark_profile.json`
- `reports/techqa_public_retriever_comparison.json`
- `reports/techqa_public_rag_cases.jsonl`
- `reports/techqa_public_retriever_cases.jsonl`
- `reports/wixqa_public_rag_summary.json`
- `reports/wixqa_public_benchmark_profile.json`
- `reports/wixqa_public_retriever_comparison.json`
- `reports/wixqa_public_rag_cases.jsonl`
- `reports/wixqa_public_retriever_cases.jsonl`
- `reports/evaluation_history.json`
- `reports/evaluation_gates.json`
- `reports/eval_comparison.json`
- `reports/dataset_profile.json`
- `reports/baseline_eval_cases.jsonl`
- `reports/improved_eval_cases.jsonl`
- `reports/vector_eval_cases.jsonl`
- `reports/agent_eval_summary.json`
- `reports/agent_eval_cases.jsonl`
- `reports/agent_trace_examples.jsonl`
- `reports/agent_otel_spans.jsonl`
- `reports/observability_otel_spans.jsonl`
- `reports/observability_trace_index.json`
- `reports/collector_export_preview.json`
- `reports/safety_classifier_eval_summary.json`
- `reports/safety_classifier_eval_cases.jsonl`
- `reports/safety_threshold_sweep.json`
- `reports/safety_threshold_retuning.json`
- `reports/safety_human_review_simulation.json`
- `reports/safety_reviewer_disagreement_slices.json`
- `reports/safety_secondary_review_band_analysis.json`
- `reports/safety_secondary_review_floor_validation.json`
- `reports/safety_secondary_review_operating_recommendation.json`
- `reports/safety_mitigation_impact.json`
- `reports/safety_threshold_decision_memo.json`
- `reports/evaluation_report.md`
- `reports/evaluation_report.html`
- `reports/evaluation_report.pdf`

## Baseline Version

The first baseline is `baseline_team_hint_retrieval`. It uses broad synthetic system and team keywords, then chooses the first matching runbook section. This is expected to find the correct team more often than the exact procedure, which creates useful baseline failures for later error analysis.

## Improved Lexical Version

The first improved version is `improved_lexical_retrieval`. It scores token overlap against runbook titles and content, then filters by the requesting role. This is still deterministic and local, but it gives the project a concrete before/after comparison before adding embeddings or a full vector store.

The current golden set includes exact, paraphrased, abbreviated, missing-metadata, false-lead, typo/abbreviation, human email-thread, manually authored chat/meeting/screenshot/desk-note/handoff/control-room/redacted/stale-thread fragments, evidence packets, mixed review bundles, decision logs, partial evidence notes, analyst scratch notes, CSV extracts, incident timelines, control-owner notes, adversarial-instruction, weak-evidence, conflicting-evidence, and long conflicting-context cases. Reports include grouped analysis by task type and noise type, plus failure-reason counts.

The dataset profile should be regenerated with each full eval run. It records case counts, manual-versus-generated mix, abstention share, coverage by task/noise/issue/team, red-team risk coverage, and explicit gap labels so benchmark quality can be reviewed alongside model or retriever quality.

Known limitation: most golden cases are still generated from templates, even when they simulate email threads, evidence packets, mixed review bundles, and contradictory context. The expanded manual challenge set is still small; it exposed residual final-selection and ambiguous-handoff abstention failures that are now fixed and regression-tested. Future eval sets should include more varied human-written phrasing, misleading system names, and adversarial retrieved text.

## Hybrid Sparse Semantic Version

The hybrid version is `hybrid_sparse_semantic_retrieval`. It combines lexical overlap with deterministic sparse semantic alias features for procedure concepts such as missing KYC documents, duplicate record clusters, and confirmation-pending trade exceptions.

This version is deliberately local and dependency-free. It is not a production embedding store; it is an experiment that shows whether synonym-aware retrieval reduces the known paraphrase and missing-metadata failures before adding pgvector or an embedding provider.

## Local TF-IDF Vector Version

The vector version is `local_tfidf_vector_retrieval`. It builds an IDF-weighted local vector index over runbook titles, content, team hints, procedure aliases, and character n-grams, then scores with cosine similarity plus a small keyword rerank.

This is a real local vector-space retrieval experiment, but it is not an embedding model, pgvector store, or paid provider. Its current value is comparison discipline: it reaches full retrieval hit@3 and citation coverage on the current synthetic suite while still exposing ranking score components for future failures.

## Local Embedding Store Version

The embedding-store version is `local_hashed_embedding_store_retrieval`. It builds a local store of dense, stable feature-hashed vectors over runbook titles, content, team hints, and procedure aliases, then searches with cosine similarity plus lightweight reranking.

This is not a paid embedding provider or production vector database. It exercises the same evaluation contract an embedding-backed vector store would need: index build, query embedding, top-k retrieval, final answer selection, citation checking, and failure analysis. In the current synthetic suite it reaches full retrieval hit@3 and citation coverage after the same reranking checks used by the local vector retriever, which reinforces that embeddings still need answer-grounding checks.

The optional provider-backed embedding comparison uses `scripts/run_provider_embedding_eval.py`. It is dry-run-first and does not make network calls unless `--run` is supplied with provider credentials. When executed, it applies the same golden-case scoring, citation checks, abstention checks, and failure-analysis contract as the local retrievers. Provider-backed results are intentionally not generated by deterministic CI. A reviewed single credentialed run is published in `reports/provider_embedding_published_result.json`; it reaches 100% retrieval hit rate@3 and 100% citation coverage on the 358-case synthetic benchmark, matching the local TF-IDF vector and feature-hashed retrievers. Because the controlled benchmark is saturated, the provider embedding adds no measurable lift here, and the public TechQA/WixQA tracks remain the better discriminator. This published result clears the optional provider-embedding release gate.

## External Public TechQA Track

The TechQA public track uses a tracked 480-case sample from NVIDIA TechQA-RAG-Eval. It evaluates public technical-support retrieval separately from the controlled synthetic operations benchmark. The summary report records retrieval hit rate@3, top-1 citation accuracy, mean reciprocal rank@3, abstention accuracy, impossible-question abstention, and answerable false abstention. The benchmark profile records the sample size, answerable/impossible split, unique public document count, context coverage, failed-case rate, sample-selection policy, and whether a provider-backed embedding result has actually been published.

The tracked sample keeps CI and GitHub Pages deterministic. To refresh or resize it, download the upstream `train.json` into `data/public/techqa_train.json`, then run `scripts/prepare_techqa_public_benchmark.py` with an explicit `--limit`.

The TechQA retriever comparison report saves the public-track systems separately from the controlled synthetic benchmark:

- keyword title baseline
- local TF-IDF public retriever

The current primary local TF-IDF public retriever improves TechQA retrieval hit rate@3 from 65.10% to 80.73% and top-1 citation accuracy from 55.21% to 72.40% versus the keyword-title baseline. The same comparison records the abstention trade-off: impossible-question abstention decreases from 39.58% to 11.46%, so future work should inspect whether the less conservative behavior is desirable before adding provider-backed embeddings.

## External Public WixQA Track

The WixQA public track uses a tracked 160-case sample from the expert-written split of Wix/WixQA. It evaluates real public enterprise-support retrieval separately from the controlled synthetic operations benchmark and from TechQA. The summary report records retrieval hit rate@3, top-1 citation accuracy, mean reciprocal rank@3, and multi-article retrieval@3. The benchmark profile records sample size, unique document count, multi-article share, article-type mix, failed-case rate, sample-selection policy, and whether a provider-backed embedding result has actually been published.

The tracked sample keeps CI and GitHub Pages deterministic. To refresh or resize it, download the upstream `wixqa_expertwritten/test.jsonl` and `wix_kb_corpus/wix_kb_corpus.jsonl` into `data/public/`, then run `scripts/prepare_wixqa_public_benchmark.py` with an explicit `--limit`.

The WixQA retriever comparison report saves the public-track systems separately from the controlled synthetic benchmark:

- keyword title baseline
- local TF-IDF WixQA retriever

The current primary local TF-IDF WixQA retriever improves retrieval hit rate@3 from 53.12% to 77.50% and top-1 citation accuracy from 36.88% to 61.25% versus the keyword-title baseline. It also reaches 88.64% retrieval hit@3 on multi-article cases, which makes it a useful complement to the TechQA impossible-question abstention track.

The public report and dashboard also surface retriever failure analysis. The overview counts failed cases, cases where the expected section was retrieved but not finally cited, abstention mismatches, and the top failure reason for each retriever. The example table keeps the diagnostic and recommended fix attached to concrete case ids.

## Retriever Metric Snapshots

The snapshot report is `retriever_metric_snapshots.json`. It records the ordered retriever versions as deterministic snapshots rather than timestamped run history. This keeps CI reproducible while making metric regressions visible.

Each snapshot stores citation coverage, retrieval hit rate@3, next-action accuracy, abstention accuracy, failed-case count, deltas from the previous retriever, and regression flags. A regression is flagged when citation coverage decreases or failed-case count increases compared with the previous snapshot.

The history report is `evaluation_history.json`. It records deterministic dated lab milestones over the same retriever versions, plus a current summary that combines the best retriever with extraction, security, and controlled-agent quality checks. The timestamps are stable milestone timestamps, not live production telemetry.

The release-gate report is `evaluation_gates.json`. It converts generated metrics into deterministic pass/warn/fail checks for benchmark coverage, retrieval grounding, abstention, extraction validity, red-team safety, approval governance, trace indexing, and collector-span consistency. Non-blocking warnings are allowed for useful but optional work that is not claimed as a published result, such as the provider-backed embedding comparison.

## Structured Extraction Version

The first extraction version is `deterministic_structured_extraction`. It validates a `TicketExtraction` schema and a `RoutingDecision` schema over synthetic ticket descriptions. It reports schema validity, issue-category accuracy, severity accuracy, impacted-system accuracy, and routing-team accuracy.

Known limitation: the current extraction cases are templated. Future eval sets should include abbreviated tickets, missing fields, misspellings, and conflicting evidence.

## Controlled Agent Version

The first controlled-agent version is `controlled_agent_approval_gate`. It uses deterministic read-only tools for runbook search, ticket extraction, and escalation-note drafting, then requires explicit approval before running `route_ticket_mock`.

It reports trace coverage rate, audit event coverage rate, approval audit rate, monitoring snapshot rate, valid tool-call rate, approval trigger rate, side-effect block rate, approved action execution rate, route-tool selection accuracy, and unnecessary tool-call rate. It also exports deterministic trace examples, OpenTelemetry-style spans for representative blocked and approved mock route runs, and case-level approval-decision spans for every synthetic ticket.

Known limitation: this is a deterministic local workflow rather than a LangGraph runtime. The shape is intentionally close to a future state machine so the approval and audit contract can be tested before adding orchestration dependencies.

## Observability Version

The first observability version adds trace ids, structured audit events, and monitoring snapshots to each controlled-agent run. It also writes deterministic OpenTelemetry-style span rows for representative blocked and approved tool routes. The full orchestration run adds an evaluation-level trace covering data generation, retriever comparison, extraction evaluation, security evaluation, agent evaluation, and report/API artifact export. Retriever failures are exported as case-level spans with expected, predicted, and retrieved citation attributes. Local vector and embedding-store retriever rankings are exported as case-level spans with top-candidate score components and winning margins. Extraction outcomes are exported as case-level spans with schema, issue-category, severity, impacted-system, and routing-team attributes. Agent approval outcomes are exported as case-level spans with approval, blocking, execution, audit, and tool-validity attributes. API contracts are exported as endpoint and expected-error spans for health, report, span-export, trace-index, collector-preview, ask, extract, agent-run, validation-error, and not-found behavior. These spans are normalized into the local dashboard trace timeline and a local trace index with trace, component, error, and predefined-query summaries. The OTLP/HTTP collector adapter converts the local JSONL spans into collector payloads, and the evaluation runner writes a dry-run payload preview. A separate local capture smoke test starts a temporary OTLP/HTTP-compatible endpoint, posts real payloads, and verifies received request and span counts. The Docker Compose observability profile also runs an OpenTelemetry Collector with an OTLP/HTTP receiver and debug exporter; the deployment check posts the same payloads to that collector and verifies accepted and exported span deltas through collector self-metrics. This makes the project easier to debug and gives the dashboard measurable operational controls rather than only answer-quality metrics.

Known limitation: the Dockerized collector check verifies receiver acceptance and exporter throughput through collector self-metrics. The local trace index supports inspection and public sharing, but it is not a production observability backend.

## Security Red-Team Version

The security version evaluates `red_team_cases.jsonl` against baseline and improved behavior. It reports explicit policy block rate, safe response rate, weighted safe response rate, residual risk score, and breakdowns by risk type, attack channel, and severity band across prompt injection, grounding bypass, excessive agency, access-control bypass, retrieved-document injection, sensitive-data requests, weak evidence, tool misuse, system-prompt leakage, unbounded consumption, retrieved-context priority attacks, approval-gate bypass, citation suppression, unsupported resolution, and retrieved access escalation.

Known limitation: current red-team checks and severity weights are deterministic. Future versions should include more varied phrasing, retrieved-document attacks embedded inside generated runbook content, and model-assisted adversarial review.

## Safety Prevalence And Classifier Evaluation Version

The safety-classifier extension evaluates a deterministic safety classifier or rule layer over enriched challenge cases, a targeted secondary-floor validation slice, and a weighted synthetic sampled request stream. It adds simulated unsafe-request categories, benign near-miss requests, classifier scores, threshold decisions, false positive / false negative trade-offs, prevalence estimation, human-review simulation, secondary review-band analysis, secondary-floor validation, mitigation-impact reporting, and a threshold decision memo.

The module reports:

- confusion matrix by category and severity
- precision, recall, false positive rate, false negative rate, and weighted safety score
- prevalence estimate for unsafe categories in the sampled synthetic stream
- threshold sweep with candidate operating points
- legacy-versus-retuned signal and category-threshold comparison
- human-review queue volume, capacity use, disagreement, escalation, and final adjudication
- synthetic human-authored adjudication notes for review-queued cases, medium-severity challenge cases, and false negatives
- reviewer-disagreement slices by category, source, and reviewer override type
- secondary review-band decision aid for targeted medium-severity review floors
- secondary review-floor validation with unsafe-capture and benign-review-load metrics
- mitigation-impact scenarios comparing no classifier, classifier-only hold, and classifier plus simulated review
- threshold decision memo with selected operating point, rationale, and next threshold work

Known limitation: review decisions and adjudication notes are synthetic workflow labels, not real human decisions. The public report must state that prevalence is estimated from synthetic sampled cases, not real traffic.
