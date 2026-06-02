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
| `failure_reasons` | Deterministic failure labels used for error analysis. |
| `diagnostic` | Short explanation of the failure mode. |
| `recommended_fix` | Suggested retrieval or policy improvement. |

The dashboard and public report derive retriever error-analysis tables from these fields, including a `retrieved_but_not_cited` flag when the expected citation appears in the retrieved set but not in the final cited answer.

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
