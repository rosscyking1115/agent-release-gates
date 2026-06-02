# Internal AI Agent Evaluation Report

## Executive Summary

This report summarizes a fully synthetic evaluation lab for internal AI agent workflows. It does not use real company documents, customer data, employee data, confidential processes, or real operational actions.

- Golden retrieval cases: 280
- Synthetic ticket extraction and agent cases: 180
- Red-team safety cases: 40
- Best current retriever: Hybrid sparse semantic retrieval
- Current vector experiments: local TF-IDF vector retrieval and local embedding-store retrieval

## Retrieval Evaluation

| System | Hit rate@3 | Citation coverage | Next action accuracy | Abstention accuracy | Failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline team hints | 45.41% | 20.18% | 20.18% | 78.57% | 234 |
| Improved lexical | 99.08% | 98.62% | 98.62% | 100.00% | 3 |
| Hybrid sparse semantic | 100.00% | 100.00% | 100.00% | 100.00% | 0 |
| Local TF-IDF vector | 100.00% | 100.00% | 100.00% | 100.00% | 0 |
| Local embedding store | 100.00% | 100.00% | 100.00% | 100.00% | 0 |

The retrieval experiment compares a deliberately weak baseline, a lexical retriever, a local hybrid sparse semantic retriever, a TF-IDF vector retriever, and a local embedding-store retriever. The embedding row uses stable feature-hashed vectors; it is not a paid provider model.

## Retriever Metric Snapshots

| Snapshot | System | Citation coverage | Failed cases | Citation delta | Failure delta | Regression | Reason |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 001_baseline_team_hints | Baseline team hints | 20.18% | 234 |  |  | False |  |
| 002_improved_lexical | Improved lexical | 98.62% | 3 | +78.44% | -231 | False |  |
| 003_hybrid_sparse_semantic | Hybrid sparse semantic | 100.00% | 0 | +1.38% | -3 | False |  |
| 004_local_tf_idf_vector | Local TF-IDF vector | 100.00% | 0 | +0.00% | +0 | False |  |
| 005_local_embedding_store | Local embedding store | 100.00% | 0 | +0.00% | +0 | False |  |

## Retriever Failure Analysis

| System | Failed cases | Retrieved but not cited | Abstention mismatches | Top failure reason |
| --- | ---: | ---: | ---: | --- |
| Baseline team hints | 234 | 55 | 60 | missing_or_wrong_citation (174) |
| Improved lexical | 3 | 1 | 0 | missing_or_wrong_citation (3) |
| Hybrid sparse semantic | 0 | 0 | 0 |  |
| Local TF-IDF vector | 0 | 0 | 0 |  |
| Local embedding store | 0 | 0 | 0 |  |

| System | Case | Noise | Failure | Expected citation | Predicted citation | Retrieved but not cited | Top retrieved scores | Recommended fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline team hints | GOLD-TCK-0001 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-TRADE_SUPPORT-02 | RB-TRADE_SUPPORT-01 | True | RB-TRADE_SUPPORT-01 total=3; RB-TRADE_SUPPORT-02 total=3; RB-TRADE_SUPPORT-03 total=3 | Add within-team reranking using issue-category evidence and expected action terms. |
| Baseline team hints | GOLD-TCK-0003 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-03 | RB-PAYMENTS_OPS-01 | True | RB-PAYMENTS_OPS-01 total=4; RB-PAYMENTS_OPS-02 total=4; RB-PAYMENTS_OPS-03 total=4 | Add within-team reranking using issue-category evidence and expected action terms. |
| Baseline team hints | GOLD-TCK-0004 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-05 | RB-PAYMENTS_OPS-01 | False | RB-PAYMENTS_OPS-01 total=3; RB-PAYMENTS_OPS-02 total=3; RB-PAYMENTS_OPS-03 total=3 | Add within-team reranking using issue-category evidence and expected action terms. |
| Improved lexical | PARA-TCK-0028 | paraphrase | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-04 | RB-DATA_QUALITY-01 | False | RB-DATA_QUALITY-01 total=13.0; RB-CLIENT_ONBOARDING-02 total=11.0; RB-CLIENT_ONBOARDING-05 total=11.0 | Add semantic retrieval or synonym expansion for paraphrased procedure descriptions. |
| Improved lexical | PARA-TCK-0044 | paraphrase | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-04 | RB-DATA_QUALITY-01 | False | RB-DATA_QUALITY-01 total=13.0; RB-CLIENT_ONBOARDING-02 total=11.0; RB-CLIENT_ONBOARDING-05 total=11.0 | Add semantic retrieval or synonym expansion for paraphrased procedure descriptions. |
| Improved lexical | NOISY-MISSING-007 | missing_metadata | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-CLIENT_ONBOARDING-01 | RB-CLIENT_ONBOARDING-03 | True | RB-CLIENT_ONBOARDING-03 total=12.0; RB-CLIENT_ONBOARDING-01 total=11.0; RB-TRADE_SUPPORT-06 total=8.0 | Improve ranking so explicit procedure evidence beats generic workflow terms. |

## Baseline To Improved Delta

| Metric | Baseline | Improved lexical | Delta |
| --- | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.41% | 99.08% | +53.67% |
| Citation coverage | 20.18% | 98.62% | +78.44% |
| Issue category accuracy | 20.18% | 98.62% | +78.44% |
| Next action accuracy | 20.18% | 98.62% | +78.44% |
| Abstention accuracy | 78.57% | 100.00% | +21.43% |

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
| OTel-style spans | 1112 |
| Exported traces | 21 |
| Root spans | 21 |
| Child spans | 1091 |
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
