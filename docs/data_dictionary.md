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

Golden cases include exact ticket prompts, paraphrased prompts, and weak-evidence prompts where abstention is expected.

## `data/eval/red_team_cases.jsonl`

| Field | Description |
| --- | --- |
| `case_id` | Stable red-team case id. |
| `risk_type` | Risk being tested. |
| `injection_location` | Whether the attack is in the prompt or retrieved document. |
| `user_role` | Role used for the test. |
| `noise_type` | Synthetic difficulty tag such as `clean_exact`, `paraphrase`, `abbreviated_ticket`, `missing_metadata`, `weak_evidence`, or `conflicting_evidence`. |
| `input` | Adversarial or policy-challenging input. |
| `retrieved_section_id` | Synthetic section associated with the case. |
| `expected_behavior` | Required safe behavior. |
| `must_not` | Forbidden behavior labels for deterministic checks. |

## `reports/extraction_eval_cases.jsonl`

| Field | Description |
| --- | --- |
| `ticket_id` | Synthetic ticket id. |
| `schema_valid` | Whether the structured output passed Pydantic validation. |
| `issue_category_match` | Whether predicted issue category matched gold. |
| `severity_match` | Whether predicted severity matched gold. |
| `impacted_system_match` | Whether predicted impacted system matched gold. |
| `routing_team_match` | Whether predicted routing team matched gold. |
