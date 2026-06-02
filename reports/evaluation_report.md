# Internal AI Agent Evaluation Report

## Executive Summary

This report summarizes a fully synthetic evaluation lab for internal AI agent workflows. It does not use real company documents, customer data, employee data, confidential processes, or real operational actions.

- Golden retrieval cases: 272
- Synthetic ticket extraction and agent cases: 180
- Red-team safety cases: 40
- Best current retriever: Hybrid sparse semantic retrieval
- Current vector experiments: local TF-IDF vector retrieval and local embedding-store retrieval

## Retrieval Evaluation

| System | Hit rate@3 | Citation coverage | Next action accuracy | Abstention accuracy | Failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline team hints | 45.97% | 20.38% | 20.38% | 78.31% | 227 |
| Improved lexical | 99.05% | 98.58% | 98.58% | 100.00% | 3 |
| Hybrid sparse semantic | 100.00% | 99.53% | 99.53% | 100.00% | 1 |
| Local TF-IDF vector | 100.00% | 99.05% | 99.05% | 100.00% | 2 |
| Local embedding store | 100.00% | 99.05% | 99.05% | 100.00% | 2 |

The retrieval experiment compares a deliberately weak baseline, a lexical retriever, a local hybrid sparse semantic retriever, a TF-IDF vector retriever, and a local embedding-store retriever. The embedding row uses stable feature-hashed vectors; it is not a paid provider model.

## Retriever Metric Snapshots

| Snapshot | System | Citation coverage | Failed cases | Citation delta | Failure delta | Regression | Reason |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 001_baseline_team_hints | Baseline team hints | 20.38% | 227 |  |  | False |  |
| 002_improved_lexical | Improved lexical | 98.58% | 3 | +78.20% | -224 | False |  |
| 003_hybrid_sparse_semantic | Hybrid sparse semantic | 99.53% | 1 | +0.95% | -2 | False |  |
| 004_local_tf_idf_vector | Local TF-IDF vector | 99.05% | 2 | -0.48% | +1 | True | citation_coverage_decreased, failed_case_count_increased |
| 005_local_embedding_store | Local embedding store | 99.05% | 2 | +0.00% | +0 | False |  |

## Retriever Failure Analysis

| System | Failed cases | Retrieved but not cited | Abstention mismatches | Top failure reason |
| --- | ---: | ---: | ---: | --- |
| Baseline team hints | 227 | 54 | 59 | missing_or_wrong_citation (168) |
| Improved lexical | 3 | 1 | 0 | missing_or_wrong_citation (3) |
| Hybrid sparse semantic | 1 | 1 | 0 | missing_or_wrong_citation (1) |
| Local TF-IDF vector | 2 | 2 | 0 | missing_or_wrong_citation (2) |
| Local embedding store | 2 | 2 | 0 | missing_or_wrong_citation (2) |

| System | Case | Noise | Failure | Expected citation | Predicted citation | Retrieved but not cited | Top retrieved scores | Recommended fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline team hints | GOLD-TCK-0001 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-TRADE_SUPPORT-02 | RB-TRADE_SUPPORT-01 | True | RB-TRADE_SUPPORT-01 total=3; RB-TRADE_SUPPORT-02 total=3; RB-TRADE_SUPPORT-03 total=3 | Add within-team reranking using issue-category evidence and expected action terms. |
| Baseline team hints | GOLD-TCK-0003 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-03 | RB-PAYMENTS_OPS-01 | True | RB-PAYMENTS_OPS-01 total=4; RB-PAYMENTS_OPS-02 total=4; RB-PAYMENTS_OPS-03 total=4 | Add within-team reranking using issue-category evidence and expected action terms. |
| Baseline team hints | GOLD-TCK-0004 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-05 | RB-PAYMENTS_OPS-01 | False | RB-PAYMENTS_OPS-01 total=3; RB-PAYMENTS_OPS-02 total=3; RB-PAYMENTS_OPS-03 total=3 | Add within-team reranking using issue-category evidence and expected action terms. |
| Improved lexical | PARA-TCK-0028 | paraphrase | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-04 | RB-DATA_QUALITY-01 | False | RB-DATA_QUALITY-01 total=13.0; RB-CLIENT_ONBOARDING-02 total=11.0; RB-CLIENT_ONBOARDING-05 total=11.0 | Add semantic retrieval or synonym expansion for paraphrased procedure descriptions. |
| Improved lexical | PARA-TCK-0044 | paraphrase | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-04 | RB-DATA_QUALITY-01 | False | RB-DATA_QUALITY-01 total=13.0; RB-CLIENT_ONBOARDING-02 total=11.0; RB-CLIENT_ONBOARDING-05 total=11.0 | Add semantic retrieval or synonym expansion for paraphrased procedure descriptions. |
| Improved lexical | NOISY-MISSING-007 | missing_metadata | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-CLIENT_ONBOARDING-01 | RB-CLIENT_ONBOARDING-03 | True | RB-CLIENT_ONBOARDING-03 total=12.0; RB-CLIENT_ONBOARDING-01 total=11.0; RB-TRADE_SUPPORT-06 total=8.0 | Improve ranking so explicit procedure evidence beats generic workflow terms. |
| Hybrid sparse semantic | MANUAL-CONTROL-011 | manual_control_room_note | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-02 | RB-DATA_QUALITY-03 | True | RB-DATA_QUALITY-03 total=16.3489; RB-DATA_QUALITY-02 total=12.9651; RB-DATA_QUALITY-06 total=11.4391 | Add within-team reranking using issue-category evidence and expected action terms. |
| Local TF-IDF vector | MANUAL-CHAT-001 | manual_chat_fragment | missing_or_wrong_citation, wrong_issue_category, wrong_team, wrong_next_action | RB-CLIENT_ONBOARDING-01 | RB-TRADE_SUPPORT-06 | True | RB-TRADE_SUPPORT-06 total=24.7607 (alias=5, vector=19.7607); RB-CLIENT_ONBOARDING-01 total=22.9157 (alias=5, team_hint=1.25, vector=16.6657); RB-CLIENT_ONBOARDING-06 total=20.6146 (alias=5, team_hint=1.25, vector=14.3646) | Add hybrid retrieval and stronger metadata filters before final answer selection. |
| Local TF-IDF vector | MANUAL-STALE-014 | manual_stale_thread | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-06 | RB-PAYMENTS_OPS-03 | True | RB-PAYMENTS_OPS-03 total=64.9291 (alias=10, current_evidence=1.125, team_hint=1.0, title_phrase=6.0, vector=46.8041); RB-PAYMENTS_OPS-06 total=50.8913 (alias=10, current_evidence=13.875, team_hint=1.0, vector=26.0163); RB-DATA_QUALITY-01 total=36.1513 (alias=10, current_evidence=7.5, vector=18.6513) | Add within-team reranking using issue-category evidence and expected action terms. |
| Local embedding store | MANUAL-CHAT-001 | manual_chat_fragment | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-CLIENT_ONBOARDING-01 | RB-CLIENT_ONBOARDING-04 | True | RB-CLIENT_ONBOARDING-04 total=22.9824 (alias=6, embedding=15.7324, team_hint=1.25); RB-CLIENT_ONBOARDING-01 total=19.9999 (alias=6, embedding=12.7499, team_hint=1.25); RB-CLIENT_ONBOARDING-05 total=19.8496 (alias=6, embedding=12.5996, team_hint=1.25) | Add within-team reranking using issue-category evidence and expected action terms. |
| Local embedding store | MANUAL-STALE-014 | manual_stale_thread | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-06 | RB-PAYMENTS_OPS-03 | True | RB-PAYMENTS_OPS-03 total=66.4995 (alias=12, current_evidence=1.125, embedding=36.3745, team_hint=1.0, title_phrase=16.0); RB-PAYMENTS_OPS-06 total=55.9318 (alias=12, current_evidence=13.875, embedding=29.0568, team_hint=1.0); RB-DATA_QUALITY-01 total=45.4892 (alias=12, current_evidence=7.5, embedding=25.9892) | Add within-team reranking using issue-category evidence and expected action terms. |

## Baseline To Improved Delta

| Metric | Baseline | Improved lexical | Delta |
| --- | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.97% | 99.05% | +53.08% |
| Citation coverage | 20.38% | 98.58% | +78.20% |
| Issue category accuracy | 20.38% | 98.58% | +78.20% |
| Next action accuracy | 20.38% | 98.58% | +78.20% |
| Abstention accuracy | 78.31% | 100.00% | +21.69% |

## Structured Extraction

| Metric | Score |
| --- | ---: |
| Schema validity | 100.00% |
| Issue category accuracy | 100.00% |
| Severity accuracy | 100.00% |
| Impacted system accuracy | 100.00% |
| Routing team accuracy | 100.00% |

Extraction currently uses deterministic synthetic ticket patterns. The value of this stage is the schema, routing contract, and evaluation harness rather than a claim that messy real tickets are solved.

## Safety Red-Team

| Metric | Baseline | Improved policy |
| --- | ---: | ---: |
| Policy block rate | 0.00% | 100.00% |
| Safe response rate | 0.00% | 100.00% |

Block rate requires an explicit policy refusal. Safe response rate checks that forbidden behavior is absent from the response.

## Controlled Agent Workflow

| Metric | Score |
| --- | ---: |
| Trace coverage | 100.00% |
| Audit event coverage | 100.00% |
| Approval audit coverage | 100.00% |
| Side-effect block rate | 100.00% |
| Approved action execution rate | 100.00% |
| Unnecessary tool-call rate | 0.00% |

The controlled workflow separates read-only tools from side-effecting actions. The mock ticket routing tool is prepared but blocked until approval is granted, and every run returns trace, audit, and monitoring fields.

## Agent Trace Examples

| Trace | Ticket | Approval | Route outcome | Tool calls | Executed | Blocked | Audit events |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| trace_eval_tck-0001_blocked | TCK-0001 | False | approval_required | 4 | 3 | 1 | 4 |
| trace_eval_tck-0001_approved | TCK-0001 | True | executed | 4 | 4 | 0 | 4 |
| trace_eval_tck-0002_blocked | TCK-0002 | False | approval_required | 4 | 3 | 1 | 4 |
| trace_eval_tck-0002_approved | TCK-0002 | True | executed | 4 | 4 | 0 | 4 |
| trace_eval_tck-0003_blocked | TCK-0003 | False | approval_required | 4 | 3 | 1 | 4 |
| trace_eval_tck-0003_approved | TCK-0003 | True | executed | 4 | 4 | 0 | 4 |
| trace_eval_tck-0004_blocked | TCK-0004 | False | approval_required | 4 | 3 | 1 | 4 |
| trace_eval_tck-0004_approved | TCK-0004 | True | executed | 4 | 4 | 0 | 4 |
| trace_eval_tck-0005_blocked | TCK-0005 | False | approval_required | 4 | 3 | 1 | 4 |
| trace_eval_tck-0005_approved | TCK-0005 | True | executed | 4 | 4 | 0 | 4 |

## Observability Span Export

| Export metric | Value |
| --- | ---: |
| OTel-style spans | 1096 |
| Exported traces | 21 |
| Root spans | 21 |
| Child spans | 1075 |
| Tool spans | 40 |

The combined export includes workflow-level spans, agent tool/audit spans, case-level retriever failure spans, retriever ranking-detail spans, case-level extraction spans, case-level agent approval spans, plus API contract and error-case spans for local inspection.

## What This Proves

- The project can generate synthetic enterprise operations data safely.
- Retrieval quality can be measured across exact, paraphrased, noisy, conflicting, and adversarial cases.
- Structured extraction, routing, refusal behavior, approval gates, and audit traces are evaluated as product behavior, not only as model output.
- The dashboard, API, Docker runtime, and CI workflow make the lab reproducible.

## Current Limitations

- The dataset is synthetic and templated.
- Extraction is deterministic rather than LLM-backed.
- The vector retriever is local TF-IDF, not an embedding model or vector database.
- The embedding-store retriever uses local feature-hashed embeddings, not a paid API.
- Scores should be read as regression-test results for this lab, not as claims about production accuracy.

## Recommended Next Work

- Add noisier, human-written ticket variants.
- Compare the local embedding-store retriever with a provider-backed embedding model.
- Add downloadable PDF report export.
- Add live collector export for the local OpenTelemetry-style spans.
- Add an optional LLM extraction path with schema repair and failure analysis.
