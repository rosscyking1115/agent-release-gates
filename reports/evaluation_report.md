# Internal AI Agent Evaluation Report

## Executive Summary

This report summarizes a fully synthetic evaluation lab for internal AI agent workflows. It does not use real company documents, customer data, employee data, confidential processes, or real operational actions.

- Golden retrieval cases: 240
- Synthetic ticket extraction and agent cases: 180
- Red-team safety cases: 40
- Best current retriever: Hybrid sparse semantic retrieval
- Current vector experiments: local TF-IDF vector retrieval and local embedding-store retrieval

## Retrieval Evaluation

| System | Hit rate@3 | Citation coverage | Next action accuracy | Abstention accuracy | Failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline team hints | 45.83% | 20.83% | 20.83% | 80.42% | 199 |
| Improved lexical | 98.44% | 97.92% | 97.92% | 100.00% | 4 |
| Hybrid sparse semantic | 100.00% | 100.00% | 100.00% | 100.00% | 0 |
| Local TF-IDF vector | 100.00% | 99.48% | 99.48% | 100.00% | 1 |
| Local embedding store | 100.00% | 96.35% | 96.35% | 100.00% | 7 |

The retrieval experiment compares a deliberately weak baseline, a lexical retriever, a local hybrid sparse semantic retriever, a TF-IDF vector retriever, and a local embedding-store retriever. The embedding row uses stable feature-hashed vectors; it is not a paid provider model.

## Retriever Failure Analysis

| System | Failed cases | Retrieved but not cited | Abstention mismatches | Top failure reason |
| --- | ---: | ---: | ---: | --- |
| Baseline team hints | 199 | 48 | 47 | missing_or_wrong_citation (152) |
| Improved lexical | 4 | 1 | 0 | missing_or_wrong_citation (4) |
| Hybrid sparse semantic | 0 | 0 | 0 |  |
| Local TF-IDF vector | 1 | 1 | 0 | missing_or_wrong_citation (1) |
| Local embedding store | 7 | 7 | 0 | missing_or_wrong_citation (7) |

| System | Case | Noise | Failure | Expected citation | Predicted citation | Retrieved but not cited | Recommended fix |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline team hints | GOLD-TCK-0001 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-TRADE_SUPPORT-02 | RB-TRADE_SUPPORT-01 | True | Add within-team reranking using issue-category evidence and expected action terms. |
| Baseline team hints | GOLD-TCK-0003 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-03 | RB-PAYMENTS_OPS-01 | True | Add within-team reranking using issue-category evidence and expected action terms. |
| Baseline team hints | GOLD-TCK-0004 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-PAYMENTS_OPS-05 | RB-PAYMENTS_OPS-01 | False | Add within-team reranking using issue-category evidence and expected action terms. |
| Improved lexical | PARA-TCK-0028 | paraphrase | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-04 | RB-DATA_QUALITY-01 | False | Add semantic retrieval or synonym expansion for paraphrased procedure descriptions. |
| Improved lexical | PARA-TCK-0044 | paraphrase | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-DATA_QUALITY-04 | RB-DATA_QUALITY-01 | False | Add semantic retrieval or synonym expansion for paraphrased procedure descriptions. |
| Improved lexical | NOISY-MISSING-007 | missing_metadata | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-CLIENT_ONBOARDING-01 | RB-CLIENT_ONBOARDING-03 | True | Improve ranking so explicit procedure evidence beats generic workflow terms. |
| Local TF-IDF vector | NOISY-MISSING-007 | missing_metadata | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-CLIENT_ONBOARDING-01 | RB-CLIENT_ONBOARDING-03 | True | Improve ranking so explicit procedure evidence beats generic workflow terms. |
| Local embedding store | GOLD-TCK-0001 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-TRADE_SUPPORT-02 | RB-TRADE_SUPPORT-06 | True | Add within-team reranking using issue-category evidence and expected action terms. |
| Local embedding store | GOLD-TCK-0041 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-TRADE_SUPPORT-02 | RB-TRADE_SUPPORT-06 | True | Add within-team reranking using issue-category evidence and expected action terms. |
| Local embedding store | GOLD-TCK-0045 | clean_exact | missing_or_wrong_citation, wrong_issue_category, wrong_next_action | RB-TRADE_SUPPORT-02 | RB-TRADE_SUPPORT-06 | True | Add within-team reranking using issue-category evidence and expected action terms. |

## Baseline To Improved Delta

| Metric | Baseline | Improved lexical | Delta |
| --- | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.83% | 98.44% | +52.61% |
| Citation coverage | 20.83% | 97.92% | +77.09% |
| Issue category accuracy | 20.83% | 97.92% | +77.09% |
| Next action accuracy | 20.83% | 97.92% | +77.09% |
| Abstention accuracy | 80.42% | 100.00% | +19.58% |

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
- Add OpenTelemetry-compatible trace export.
- Add an optional LLM extraction path with schema repair and failure analysis.
