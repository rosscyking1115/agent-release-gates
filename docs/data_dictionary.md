# Data Dictionary

## `data/synthetic/raw_docs/runbooks.jsonl`

| Field | Description |
| --- | --- |
| `runbook_id` | Synthetic runbook family id. |
| `section_id` | Stable citation id for a runbook section. |
| `title` | Human-readable synthetic procedure title. |
| `team` | Synthetic team that owns the procedure. |
| `allowed_roles` | Roles allowed to retrieve the section in later phases. |
| `effective_date` | Synthetic procedure effective date. |
| `content` | Procedure text used for future retrieval and citations. |

## `data/synthetic/raw_tickets/tickets.jsonl`

| Field | Description |
| --- | --- |
| `ticket_id` | Stable synthetic ticket id. |
| `title` | Ticket title derived from the issue category. |
| `team` | Expected owning team. |
| `severity` | Synthetic severity: `low`, `medium`, or `high`. |
| `impacted_system` | Synthetic internal system name. |
| `issue_category` | Expected classification label. |
| `description` | Synthetic ticket description. |
| `expected_next_action` | Gold next action from the matching runbook. |
| `gold_citation_ids` | Expected runbook section citations. |

## `data/eval/golden_cases.jsonl`

| Field | Description |
| --- | --- |
| `case_id` | Stable evaluation case id. |
| `task_type` | Evaluation task category. |
| `user_role` | Role used for access-aware retrieval tests. |
| `input` | User-facing task prompt. |
| `expected_issue_category` | Gold issue category. |
| `expected_team` | Gold owning team. |
| `expected_next_action` | Gold next action. |
| `expected_citation_ids` | Gold citation ids that should support the answer. |
| `should_abstain` | Whether the agent should refuse due to weak evidence. |
| `noise_type` | Synthetic difficulty tag such as `clean_exact`, `paraphrase`, `abbreviated_ticket`, `missing_metadata`, `distractor_terms`, `typo_abbreviation`, `human_email_thread`, `manual_chat_fragment`, `manual_meeting_note`, `manual_screenshot_note`, `manual_desk_note`, `manual_conflicting_notes`, `manual_retrieved_injection`, `manual_ambiguous_note`, `manual_ops_chat_handoff`, `manual_shift_handoff`, `manual_control_room_note`, `manual_desk_paste`, `manual_redacted_fragment`, `manual_stale_thread`, `manual_conflicting_handoff`, `manual_retrieved_instruction_attack`, `manual_analyst_note`, `manual_csv_excerpt`, `manual_incident_timeline`, `manual_control_owner_note`, `manual_ambiguous_handoff`, `manual_evidence_packet`, `manual_evidence_packet_conflict`, `manual_review_bundle`, `manual_review_bundle_conflict`, `manual_decision_log`, `manual_decision_log_conflict`, `manual_partial_evidence`, `manual_partial_evidence_conflict`, `manual_retrieved_context_review`, `manual_retrieved_context_attack`, `manual_retrieved_context_conflict`, `adversarial_instruction`, `weak_evidence`, `conflicting_evidence`, or `long_conflicting_context`. |

Golden cases include exact ticket prompts, paraphrased prompts, noisy metadata prompts, false-lead prompts, typo/abbreviation prompts, human-like prompts, human email-thread prompts, manually authored chat/meeting/screenshot/desk-note/handoff/control-room/redacted/stale-thread prompts, evidence packets with stale side chatter and current-evidence cues, mixed review bundles combining screenshot/chat/table-style evidence, decision-log and partial-evidence notes, retrieved-context review packets, analyst-authored scratch notes, CSV excerpts, incident timelines, retrieved-document injection prompts, adversarial-instruction prompts, weak-evidence prompts where abstention is expected, and long conflicting-context prompts where the safest answer is to abstain.

## `data/eval/red_team_cases.jsonl`

| Field | Description |
| --- | --- |
| `case_id` | Stable red-team case id. |
| `risk_type` | Risk being tested. |
| `injection_location` | Whether the attack is in the prompt or retrieved document. |
| `user_role` | Role used for the test. |
| `input` | Adversarial or policy-challenging input. |
| `retrieved_section_id` | Synthetic section associated with the case. |
| `expected_behavior` | Required safe behavior. |
| `must_not` | Forbidden behavior labels for deterministic checks. |

## Security eval report files

Security evaluation writes `reports/security_eval_summary.json` and `reports/security_eval_cases.jsonl`.

| Field | Description |
| --- | --- |
| `risk_severity` | Deterministic severity band derived from risk type: `low`, `medium`, or `high`. |
| `attack_channel` | Attack source used in scoring, currently the red-team case `injection_location`. |
| `risk_weight` | Numeric severity weight used for weighted scoring. |
| `safe` | Whether the response explicitly refused, abstained, and avoided forbidden behavior. |
| `residual_risk_score` | Per-case risk weight when unsafe, otherwise zero. |
| `weighted_safe_rate` | Severity-weighted safe response rate. |
| `by_risk_type` | Improved-policy breakdown by red-team risk type. |
| `by_attack_channel` | Improved-policy breakdown by prompt or retrieved-document channel. |
| `by_risk_severity` | Improved-policy breakdown by deterministic severity band. |

## Safety prevalence and classifier files

The Safety Prevalence & Classifier Evaluation module keeps enriched challenge cases separate from sampled synthetic prevalence cases.

Inputs:

| File | Description |
| --- | --- |
| `config/safety_taxonomy.yaml` | Category definitions, severity, allowed/disallowed boundary, deterministic rule flags, and benign near-neighbor notes. |
| `data/eval/safety_challenge_cases.jsonl` | Enriched harmful, unsafe, adversarial, and benign-control cases used for classifier robustness checks. |
| `data/eval/safety_secondary_review_validation_cases.jsonl` | Separate ambiguous medium-severity validation slice used to test the targeted secondary review floor without changing challenge or prevalence metrics. |
| `data/eval/safety_prevalence_cases.jsonl` | Weighted sampled synthetic request stream used for prevalence estimation. |
| `data/eval/human_calibration_cases.jsonl` | Maintainer-labeled calibration cases with primary, secondary, and adjudicated labels for comparing classifier decisions against label and expected-action targets. |
| `data/eval_cases/instruction_hierarchy_cases.jsonl` | Synthetic intervention-study cases where lower-priority instructions appear in retrieved text, tool outputs, ticket comments, stale memory, or user text. |
| `data/eval_cases/memory_context_pollution_cases.jsonl` | Synthetic memory/context intervention cases covering stale policy memory, cross-user state bleed, retrieved/tool-output memory injection, and benign scoped memory controls. |
| `data/eval_cases/goal_conflict_cases.jsonl` | Synthetic goal-conflict intervention cases covering safety-policy, evidence-quality, privacy, instruction-hierarchy, and tool-risk arbitration. |
| `data/review/external_human_review_packet.csv` | Public packet of calibration cases for independent reviewer labeling. |
| `data/review/external_human_review_label_template.csv` | Blank reviewer-response template with allowed label, decision, confidence, rationale, and notes fields. |
| `data/review/external_human_review_reviewer_guide.md` | Reviewer-facing blind-labeling instructions generated with the external review packet. |
| `config/action_risk_policy.yaml` | Synthetic mock-action risk policy for low, medium, high, and blocked tool actions used by the action-gate intervention study. |

Reports:

| File | Description |
| --- | --- |
| `reports/safety_classifier_eval_summary.json` | Overall and category-level confusion matrices, precision, recall, specificity, false positive rate, false negative rate, PR-AUC, calibration, and selected threshold. |
| `reports/safety_classifier_eval_cases.jsonl` | Case-level true label, classifier score, threshold decision, review routing, mitigation applied, and final outcome. |
| `reports/safety_threshold_sweep.json` | Strict, balanced, permissive, and candidate per-category threshold settings with projected false positives, false negatives, and review load. |
| `reports/safety_threshold_retuning.json` | Legacy-versus-retuned signal and threshold comparison with recall lift, false-negative reduction, and category-level deltas. |
| `reports/safety_human_review_simulation.json` | Review queue volume, reviewer capacity, disagreement, adjudication, escalation, and residual risk summary. |
| `reports/safety_adjudication_notes.json` | Synthetic human-authored adjudication notes for review-queued cases, medium-severity challenge cases, and false-negative cases, including reviewer rationale and classifier-disagreement flags. |
| `reports/safety_reviewer_disagreement_slices.json` | Reviewer-disagreement slices by category, source, and recommended decision, including benign review-to-allow overrides and unsafe allow-to-block overrides. |
| `reports/safety_secondary_review_band_analysis.json` | Decision aid that uses reviewer-disagreement slices to recommend a targeted secondary review floor for selected medium-severity categories while avoiding a global threshold change. |
| `reports/safety_secondary_review_floor_validation.json` | Validation report comparing current classifier routing against the targeted secondary floor, including unsafe-capture rate and added benign review load. |
| `reports/safety_secondary_review_operating_recommendation.json` | Staffing and capacity recommendation for adopting the targeted secondary review floor under explicit reviewer-throughput assumptions. |
| `reports/safety_mitigation_impact.json` | Scenario comparison for no classifier, classifier-only hold, and classifier plus simulated human review. |
| `reports/safety_threshold_decision_memo.json` | Selected threshold, review band, decision rationale, decision metrics, and next threshold-tuning work. |
| `reports/baseline_v1_summary.json` | Frozen deterministic pre-intervention baseline summary used as the comparison point for new intervention studies. |
| `reports/agent_safety_intervention_study.json` | Aggregate before/after study covering instruction hierarchy, action gates, and safety classifier secondary review. |
| `reports/instruction_hierarchy_intervention.json` | Deterministic prompt-injection intervention comparison across baseline, hierarchy prompt, validator, and layered controls. |
| `reports/action_gate_intervention.json` | Deterministic action-risk gate comparison across baseline routing, confirmation, risk classification, and layered controls. |
| `reports/safety_classifier_intervention_study.json` | Formal safety-classifier mitigation study comparing no classifier, thresholding, severity-aware routing, secondary review, and release gate variants. |
| `reports/memory_context_intervention.json` | Memory/context pollution intervention study comparing baseline memory, recency filtering, source-trust filtering, scoped memory, and review-backed scoped memory variants. |
| `reports/memory_context_intervention.md` | Human-readable memory/context intervention report with polluted-memory following, cross-user leakage, current-evidence priority, benign usefulness, and review-burden trade-offs. |
| `reports/goal_conflict_intervention.json` | Goal-conflict intervention study comparing baseline goal following, policy-aware planning, evidence-priority planning, tool-risk-aware planning, and layered goal arbitration. |
| `reports/goal_conflict_intervention.md` | Human-readable goal-conflict intervention report with unsafe-goal compliance, conflict detection, safe alternatives, benign completion, and review-burden trade-offs. |
| `reports/safety_prevalence_report.md` | Weighted prevalence estimates, confidence intervals, sampling limitations, and distinction from challenge-set failure rates. |
| `reports/human_calibration_summary.json` | Maintainer-labeled calibration summary with reviewer agreement, classifier label accuracy, expected-action match rate, unsafe capture, and category slices. |
| `reports/human_calibration_cases.jsonl` | Case-level calibration comparison rows with human labels, classifier decision, classifier score, action/label match flags, and error type. |
| `reports/external_human_review_manifest.json` | Machine-readable readiness checklist for the independent review workflow, including artifact paths, target reviewer count, and publication requirements. |
| `reports/external_human_review_summary.json` | External-review status and agreement metrics. Reports `awaiting_labels` until completed labels are supplied. |
| `reports/external_human_review_cases.jsonl` | Case-level external-review comparison rows. Empty until completed reviewer labels are supplied. |
| `reports/judge_reliability_summary.json` | Local rubric-judge reliability report with pairwise agreement, Cohen kappa, judge/classifier accuracy, category slices, and disagreement examples. |
| `reports/judge_reliability_cases.jsonl` | Case-level local rubric-judge outputs compared against maintainer labels, classifier labels, and reviewer labels. |
| `reports/model_judge_adapter_status.json` | Deterministic dry-run-ready status for the optional hosted model-judge adapter. This is safe to publish because it makes no provider calls. |
| `reports/model_judge_eval_status.json` | Local-only status file written by the hosted judge script in dry-run, blocked, or completed mode, including the publication review when a credentialed run completes. |
| `reports/model_judge_eval_summary.json` | Optional local-only hosted model-judge result written only after a credentialed `--run`, with aggregate metrics, category slices, disagreement examples, and publication review. |
| `reports/model_judge_eval_cases.jsonl` | Optional local-only hosted model-judge case outputs with model labels, confidence, rationale, and agreement flags. |
| `reports/model_judge_reviewed_summary.json` | Sanitized public summary promoted from the reviewed OpenAI hosted model-judge run, excluding raw response IDs and full provider rationales. |
| `reports/model_judge_reviewed_summary_anthropic.json` | Sanitized public summary promoted from the reviewed Anthropic hosted model-judge run, excluding raw response IDs and full provider rationales. |
| `reports/model_judge_provider_comparison.json` | Public-safe reviewed provider comparison derived from sanitized hosted-judge summaries and calibration metadata, including provider agreement rates, cross-provider disagreement cases, and publication policy. |
| `reports/multi_model_comparison_plan.json` | Provider-neutral comparison plan for cross-model hosted and local judge runs, including target providers, credential settings, output contract, readiness summary, reviewed-provider count, and publication gates. |
| `reports/failure_taxonomy_summary.json` | Shared failure-taxonomy counts by label, group, and source across retrieval, public RAG, red-team, and safety-classifier outputs. |
| `reports/techqa_public_rag_summary.json` | External public TechQA-RAG-Eval retrieval and abstention summary over the tracked public sample. |
| `reports/techqa_public_benchmark_profile.json` | Public benchmark transparency profile with sample size, answerable/impossible mix, unique document count, context coverage, failure rate, and provider-result status. |
| `reports/techqa_public_retriever_comparison.json` | Public TechQA retriever comparison between the keyword-title baseline and the primary local TF-IDF public retriever, including retrieval, citation, abstention, and lift metrics. |
| `reports/techqa_public_rag_cases.jsonl` | Case-level TechQA retrieval results, expected/retrieved citations, abstention decision, and failure reasons. |
| `reports/techqa_public_retriever_cases.jsonl` | Case-level TechQA results for each compared public retriever system, including system id, retrieved citations, predicted citations, and failure reasons. |
| `reports/wixqa_public_rag_summary.json` | External public WixQA expert-written retrieval summary over the tracked public enterprise-support sample. |
| `reports/wixqa_public_benchmark_profile.json` | Public WixQA benchmark transparency profile with sample size, unique document count, multi-article share, article-type mix, failure rate, and provider-result status. |
| `reports/wixqa_public_retriever_comparison.json` | Public WixQA retriever comparison between the keyword-title baseline and the primary local TF-IDF WixQA retriever, including retrieval, citation, multi-article, and lift metrics. |
| `reports/wixqa_public_rag_cases.jsonl` | Case-level WixQA retrieval results, expected/retrieved article ids, ranking result, and failure reasons. |
| `reports/wixqa_public_retriever_cases.jsonl` | Case-level WixQA results for each compared public retriever system, including system id, retrieved citations, top scores, and failure reasons. |
| `reports/public_rag_findings.json` | Cross-public TechQA and WixQA findings summary with weighted public RAG metrics, top failure label, track-level lifts, findings, and recommended next experiments. |
| `reports/public_rag_reranking_opportunity.json` | Cross-public reranking opportunity analysis that separates current top-1 citation accuracy, oracle top-3 rerank ceiling, rerankable cases, and residual retrieval misses. |
| `reports/public_rag_reranker_eval.json` | Conservative deterministic query-document reranker evaluation with top-1 citation lift, changed cases, improved cases, regressed cases, and track-level examples. |
| `reports/rag_grounding_intervention.json` | Public TechQA/WixQA grounding and abstention intervention study comparing baseline retrieval, evidence gates, strict abstention, and review routing. |
| `reports/rag_grounding_intervention.md` | Human-readable report for the RAG grounding intervention study, including unsupported-answer, useful-answer, false-abstention/review, and review-burden trade-offs. |
| `reports/public_rag_model_reranker_adapter_status.json` | Dry-run hosted reranker adapter status with provider mode, packet size, estimated calls, selection mix, and publication rule. |
| `reports/public_rag_model_reranker_packet.jsonl` | Public RAG reranker packet with user question, top-3 candidate document snippets, and separate evaluation metadata for a future hosted reranker run. |

## Retrieval eval case files

Retrieval case result files include `baseline_eval_cases.jsonl`, `improved_eval_cases.jsonl`, `hybrid_eval_cases.jsonl`, `vector_eval_cases.jsonl`, and `embedding_eval_cases.jsonl`.

| Field | Description |
| --- | --- |
| `case_id` | Golden case id. |
| `expected_citation_ids` | Gold supporting runbook sections. |
| `predicted_citation_ids` | Final cited sections from the retriever answer. |
| `retrieved_citation_ids` | Top retrieved sections before final answer selection. |
| `retrieved_candidate_scores` | Top retrieved sections with total score and optional component breakdown, such as vector similarity, embedding similarity, alias boost, team hint, current-evidence boost, and negation penalty. |
| `failure_reasons` | Deterministic failure labels used for error analysis. |
| `taxonomy_source` | Benchmark source used for shared failure-taxonomy reporting. |
| `taxonomy_labels` | Shared taxonomy labels normalized from track-specific failures or risk categories. |
| `human_primary_label` | First maintainer label for calibration cases. |
| `human_secondary_label` | Second maintainer label for calibration cases. |
| `human_adjudicated_label` | Final adjudicated calibration label used as the comparison target. |
| `classifier_action_match` | Whether the classifier decision exactly matches the case-level expected action. |
| `classifier_label_match` | Whether the classifier binary label matches the adjudicated human label. |
| `error_type` | Calibration disagreement category such as unsafe auto-allowed, benign auto-blocked, benign sent to review, or action mismatch. |
| `judge_label` | Local rubric-judge binary label for a calibration case. |
| `judge_decision` | Local rubric-judge recommended action: allow, review, or block. |
| `judge_confidence` | Deterministic confidence score assigned by the local rubric judge. |
| `judge_error_type` | Judge disagreement category relative to the adjudicated label. |
| `diagnostic` | Short explanation of the failure mode. |
| `recommended_fix` | Suggested retrieval or policy improvement. |

The dashboard and public report derive retriever error-analysis tables from these fields, including a `retrieved_but_not_cited` flag when the expected citation appears in the retrieved set but not in the final cited answer. Failure examples also show top retrieved scores so ranking mistakes can be inspected without rerunning the retriever.

## `reports/retriever_metric_snapshots.json`

| Field | Description |
| --- | --- |
| `snapshot_id` | Stable ordered id for the retriever version snapshot. |
| `label` | Display name for the retriever system. |
| `system_version` | Internal version string for the retriever implementation. |
| `citation_delta_from_previous` | Citation coverage change versus the previous snapshot. |
| `failure_delta_from_previous` | Failed-case count change versus the previous snapshot. |
| `regression` | Whether citation coverage decreased or failed-case count increased. |
| `regression_reasons` | Deterministic labels explaining the regression flag. |

## `reports/evaluation_history.json`

This file records deterministic dated lab milestones for evaluation history. It is not production telemetry; stable timestamps mark ordered local benchmark milestones so CI can regenerate the artifact exactly.

| Field | Description |
| --- | --- |
| `history_type` | History contract type, currently `deterministic_lab_milestones`. |
| `generated_at_utc` | Stable artifact generation timestamp used for deterministic report regeneration. |
| `current_summary` | Latest milestone, best retriever, current citation coverage, failure count, and cross-workflow quality checks. |
| `milestones` | Ordered retrieval milestone rows with milestone timestamp, system version, citation coverage, next-action accuracy, abstention accuracy, failure count, and deltas from the previous milestone. |

## `reports/evaluation_gates.json`

This file records deterministic release-readiness gates derived from the generated evaluation artifacts. It is not a production certification; it is a reproducible local quality bar for deciding whether the current synthetic benchmark run is safe to publish.

| Field | Description |
| --- | --- |
| `gate_set_type` | Stable artifact type, currently `deterministic_evaluation_release_gates`. |
| `overall_status` | `pass`, `pass_with_warnings`, or `fail` based on blocking gate failures and non-blocking warnings. |
| `gate_count` | Total number of gate rows evaluated. |
| `pass_count` | Number of gates with `pass` status. |
| `warn_count` | Number of non-blocking warnings, such as optional provider-backed comparison not yet published. |
| `fail_count` | Number of blocking gates that missed their threshold. |
| `gates` | Gate rows with id, area, label, status, severity, observed value, threshold, value format, and rationale. |

## Public report artifacts

The report generator writes `reports/evaluation_report.md`, `reports/evaluation_report.html`, and `reports/evaluation_report.pdf` from the same deterministic Markdown source. The PDF is a dependency-free, paginated text export intended for quick sharing and review; the Markdown and HTML artifacts remain the easiest files to diff.

## `reports/dataset_profile.json`

This file summarizes the synthetic benchmark itself so evaluation scores can be interpreted with data-quality context. It is generated by the full evaluation runner and shown in the dashboard, API, and public report.

| Field | Description |
| --- | --- |
| `profile_type` | Stable artifact type, currently `synthetic_dataset_profile`. |
| `dataset_counts` | Row counts for runbooks, synthetic tickets, golden cases, and red-team cases. |
| `golden_case_mix` | Manual/generated case counts, answerable/abstention counts, shares, and coverage counts. |
| `golden_coverage` | Count breakdowns by golden-case noise type, task type, issue category, and expected team. |
| `red_team_coverage` | Count breakdowns by red-team risk type and injection location. |
| `top_manual_noise_types` | Manual-case noise types with the highest current coverage. |
| `risk_labels` | Data-quality gap labels, such as low manual-case share or intentionally excluded real-company data. |
| `recommended_next_data_work` | Concrete next data-quality improvements derived from the current profile. |

## `reports/extraction_eval_cases.jsonl`

| Field | Description |
| --- | --- |
| `ticket_id` | Synthetic ticket id. |
| `schema_valid` | Whether the structured output passed Pydantic validation. |
| `issue_category_match` | Whether predicted issue category matched gold. |
| `severity_match` | Whether predicted severity matched gold. |
| `impacted_system_match` | Whether predicted impacted system matched gold. |
| `routing_team_match` | Whether predicted routing team matched gold. |

## `reports/agent_trace_examples.jsonl`

| Field | Description |
| --- | --- |
| `trace_id` | Stable synthetic trace id for the sample run. |
| `ticket_id` | Synthetic ticket used to generate the trace. |
| `approval_granted` | Whether the side-effecting mock route was approved for that run. |
| `route_tool_outcome` | Final state of the `route_ticket_mock` tool: `approval_required`, `executed`, or `not_requested`. |
| `tool_decisions` | Ordered tool decisions with schema validity, approval requirement, execution state, rationale, and mock output. |
| `audit_events` | Ordered structured audit events for policy and tool actions. |
| `monitoring` | Monitoring snapshot with tool counts, citation count, and abstention state. |

## `reports/agent_otel_spans.jsonl`

Each row is an OpenTelemetry-style span derived from `reports/agent_trace_examples.jsonl`. The export is deterministic and local; it is intended for inspection and adapter development rather than a live collector.

| Field | Description |
| --- | --- |
| `trace_id` | Stable 32-character hex trace id derived from the synthetic lab trace id. |
| `span_id` | Stable 16-character hex span id. |
| `parent_span_id` | Parent span id for child tool/audit spans, or `null` for root agent spans. |
| `name` | Span name, such as `agent.run`, `search_runbook`, or `route_ticket_mock`. |
| `kind` | Span kind. Current export uses `INTERNAL`. |
| `start_time_unix_nano` | Deterministic synthetic span start timestamp in Unix nanoseconds. |
| `end_time_unix_nano` | Deterministic synthetic span end timestamp in Unix nanoseconds. |
| `status` | Span status object. Governance blocks are represented through attributes, not failed span status. |
| `attributes` | Flattened span attributes for lab trace id, ticket id, approval state, audit outcome, and tool metadata. |

## `reports/observability_otel_spans.jsonl`

Each row is an OpenTelemetry-style span for the broader lab observability view. The file combines `reports/agent_otel_spans.jsonl` with one deterministic `evaluation.run` trace that describes the orchestration path for synthetic data generation, retriever comparison, extraction evaluation, security evaluation, controlled-agent evaluation, and report/API artifact export. It also includes retriever failure traces with one child span per failed case, retriever ranking-detail traces for local vector and embedding-store systems, an extraction trace with one child span per synthetic ticket, an agent approval trace with one child span per synthetic ticket, and an API contract trace with endpoint and expected-error spans. Concrete retrieval misses, ranking score components, extraction checks, approval-gate decisions, and API validation boundaries can be inspected from the same timeline surface.

Additional attributes may include:

| Field | Description |
| --- | --- |
| `lab.component` | Component represented by the span, such as `data`, `retrieval`, `extraction`, `security`, `agent`, `api`, or `evaluation`. |
| `eval.sequence` | Deterministic child-span order inside the evaluation trace. |
| `eval.case_count` | Number of cases evaluated by the component. |
| `retriever.best_system` | Best retriever label by citation coverage and failed-case count. |
| `retriever.failure_reasons` | Comma-separated deterministic failure labels for a failed retrieval case. |
| `retriever.expected_citation_ids` | Gold citation ids for a failed retrieval case. |
| `retriever.predicted_citation_ids` | Final citation ids selected by the retriever. |
| `retriever.retrieved_citation_ids` | Top retrieved citation ids before final answer selection. |
| `retriever.top_candidate_scores` | Compact top-candidate score summary for a failed case. |
| `retriever.winning_margin` | Score difference between the top two ranked candidates. |
| `retriever.top_*.section_id` | Ranked candidate section id, currently for the top three candidates. |
| `retriever.top_*.score` | Ranked candidate total score. |
| `retriever.top_*.score_breakdown` | Compact component breakdown such as alias, vector, embedding, team hint, title phrase, current evidence, and negation penalty. |
| `extraction.schema_valid` | Whether structured extraction passed schema validation. |
| `extraction.expected_issue_category` | Gold issue category for the synthetic ticket. |
| `extraction.predicted_issue_category` | Issue category returned by the extractor. |
| `extraction.issue_category_match` | Whether predicted issue category matched gold. |
| `extraction.expected_team` | Gold routing team for the synthetic ticket. |
| `extraction.predicted_team` | Routing team returned by the extractor. |
| `extraction.routing_team_match` | Whether predicted routing team matched gold. |
| `agent.approval_required` | Whether the synthetic case required approval before a side-effecting mock tool. |
| `agent.side_effect_blocked_without_approval` | Whether the side-effecting mock tool was blocked before approval. |
| `agent.approved_action_executed` | Whether the mock tool executed after approval was granted. |
| `agent.approval_audited` | Whether approval outcomes appeared in the audit trail. |
| `agent.unnecessary_tool_call` | Whether the agent called a tool unnecessarily. |
| `http.method` | HTTP method for an API contract or error-case span. |
| `http.route` | API route represented by the span. |
| `http.status_code` | Expected HTTP status code for the route or error case. |
| `api.operation` | Happy-path API operation represented by an endpoint contract span. |
| `api.error_type` | Expected API error family, such as request validation or route not found. |
| `api.scenario` | Named API error scenario, such as empty question rejection. |
| `http.route.*` | Local report/API routes represented by the artifact-export span. |

## `reports/observability_trace_index.json`

This file is a deterministic local query layer over `reports/observability_otel_spans.jsonl`. It keeps the raw span export available while adding trace, component, error, and predefined-query summaries for the dashboard, API, public report, and static site.

| Field | Description |
| --- | --- |
| `index_type` | Stable artifact type, currently `local_observability_trace_index`. |
| `span_count` | Number of spans indexed from the local OpenTelemetry-style JSONL export. |
| `trace_count` | Number of unique trace ids represented in the index. |
| `error_span_count` | Number of spans with non-OK status or explicit error status. |
| `component_count` | Number of unique `lab.component` values represented in the spans. |
| `components` | Per-component span count, root span count, and error span count. |
| `queries` | Predefined local query counts for error spans, retriever failures, API error cases, approval decisions, and ranking cases. |
| `error_spans` | Bounded list of error-span examples with trace, span, component, case, route, and diagnostic attributes. |
| `traces` | Per-trace summaries with root span, components, span count, duration, first error span, and first error case id. |

## `reports/collector_export_preview.json`

This file records the deterministic dry-run summary for exporting `reports/observability_otel_spans.jsonl` as OTLP/HTTP JSON. The evaluation runner writes this preview without making a network call; `scripts/export_otel_collector.py --post` is required to send payloads to a live collector.

| Field | Description |
| --- | --- |
| `export_mode` | Preview mode, currently `dry_run_preview` for the deterministic eval artifact. |
| `collector_endpoint` | OTLP/HTTP traces endpoint that would receive payloads. |
| `service_name` | Service name attached to the OTLP resource. |
| `service_version` | Service version attached to the OTLP resource and instrumentation scope. |
| `source_path` | Local JSONL span source used for the export preview. |
| `span_count` | Number of local spans prepared for export. |
| `trace_count` | Number of unique trace ids in the local span export. |
| `root_span_count` | Number of root spans in the local span export. |
| `batch_size` | Maximum spans per OTLP payload. |
| `payload_count` | Number of OTLP payloads that would be posted. |
| `first_payload_span_count` | Number of spans in the first generated OTLP payload. |
| `notes` | Human-readable notes clarifying dry-run behavior and POST usage. |

## `reports/collector_export_smoke.json`

This local-only file is written by `scripts/smoke_otel_collector.py` and ignored by git. The script starts a temporary OTLP/HTTP-compatible capture endpoint on `127.0.0.1`, posts the generated OTLP payloads to it, and verifies request count, content type, status codes, and received span count.

| Field | Description |
| --- | --- |
| `export_mode` | Smoke mode, currently `local_collector_smoke`. |
| `collector_endpoint` | Temporary local endpoint used during the smoke test. |
| `span_count` | Number of local spans submitted to the exporter. |
| `payload_count` | Number of OTLP payloads prepared for export. |
| `posted_payload_count` | Number of payloads posted by the exporter. |
| `received_request_count` | Number of requests captured by the local endpoint. |
| `received_span_count` | Number of spans decoded from received OTLP payloads. |

## `reports/collector_deployment_check.json`

This local-only file is written by `scripts/check_otel_collector_deployment.py` and ignored by git. The script expects the Docker Compose `observability` profile to be running, posts the generated OTLP/HTTP payloads to a real OpenTelemetry Collector, and verifies that collector self-metrics show accepted and exported span counters increasing by the expected span count.

| Field | Description |
| --- | --- |
| `export_mode` | Deployment-check mode, currently `collector_deployment_check`. |
| `collector_endpoint` | OTLP/HTTP traces endpoint used during the deployment check. |
| `payload_count` | Number of OTLP payloads prepared for export. |
| `posted_payload_count` | Number of payloads posted to the collector. |
| `status_codes` | HTTP status codes returned by the collector. |
| `collector_metrics_endpoint` | Collector metrics endpoint used to verify accepted and exported spans. |
| `receiver_accepted_span_delta` | Increase in collector receiver accepted-span counter during the check. |
| `exporter_sent_span_delta` | Increase in collector exporter sent-span counter during the check. |
| `passed` | Whether payload counts, status codes, and collector metric checks passed. |

## `reports/provider_embedding_eval_status.json`

This local-only file is written by `scripts/run_provider_embedding_eval.py` and ignored by git. In dry-run mode it records the planned provider-backed embedding comparison without making network calls. When run with `--run` and `OPENAI_API_KEY`, it records completion status and points to the optional provider-backed summary and case files.

| Field | Description |
| --- | --- |
| `status` | `dry_run`, `blocked`, or `completed`. |
| `provider` | Provider adapter used for the optional comparison. |
| `model` | Embedding model configured for the run. |
| `case_count` | Golden cases planned or evaluated. |
| `estimated_embedding_inputs` | Dry-run estimate of provider embedding inputs. |

## `reports/provider_embedding_eval_summary.json`

This optional local-only file is written only after `scripts/run_provider_embedding_eval.py --run` completes. It uses the same retrieval metric schema as the deterministic local retrievers, but its results are not committed by default because they depend on external provider credentials, model availability, and live API behavior.
