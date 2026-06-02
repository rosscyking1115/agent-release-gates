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
| `noise_type` | Synthetic difficulty tag such as `clean_exact`, `paraphrase`, `abbreviated_ticket`, `missing_metadata`, `distractor_terms`, `typo_abbreviation`, `human_email_thread`, `manual_chat_fragment`, `manual_meeting_note`, `manual_screenshot_note`, `manual_desk_note`, `manual_conflicting_notes`, `manual_retrieved_injection`, `manual_ambiguous_note`, `adversarial_instruction`, `weak_evidence`, `conflicting_evidence`, or `long_conflicting_context`. |

Golden cases include exact ticket prompts, paraphrased prompts, noisy metadata prompts, false-lead prompts, typo/abbreviation prompts, human-like prompts, human email-thread prompts, manually authored chat/meeting/screenshot/desk-note prompts, retrieved-document injection prompts, adversarial-instruction prompts, weak-evidence prompts where abstention is expected, and long conflicting-context prompts where the safest answer is to abstain.

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
