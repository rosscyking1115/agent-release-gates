# Internal AI Agent Evaluation Report

## Executive Summary

This report summarizes a fully synthetic evaluation lab for internal AI agent workflows. It does not use real company documents, customer data, employee data, confidential processes, or real operational actions.

- Golden retrieval cases: 216
- Synthetic ticket extraction and agent cases: 180
- Red-team safety cases: 40
- Best current retriever: Hybrid sparse semantic retrieval
- Current strongest result: perfect hybrid citation coverage on the synthetic suite

## Retrieval Evaluation

| System | Hit rate@3 | Citation coverage | Next action accuracy | Abstention accuracy | Failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline team hints | 45.45% | 19.89% | 19.89% | 81.94% | 465 |
| Improved lexical | 98.30% | 97.73% | 97.73% | 100.00% | 13 |
| Hybrid sparse semantic | 100.00% | 100.00% | 100.00% | 100.00% | 0 |

The retrieval experiment compares a deliberately weak baseline, a lexical retriever, and a local hybrid sparse semantic retriever. The hybrid system adds synonym-aware scoring, phrase matching, and false-lead handling before the project introduces heavier vector infrastructure.

## Baseline To Improved Delta

| Metric | Baseline | Improved lexical | Delta |
| --- | ---: | ---: | ---: |
| Retrieval hit rate@3 | 45.45% | 98.30% | +52.85% |
| Citation coverage | 19.89% | 97.73% | +77.84% |
| Issue category accuracy | 19.89% | 97.73% | +77.84% |
| Next action accuracy | 19.89% | 97.73% | +77.84% |
| Abstention accuracy | 81.94% | 100.00% | +18.06% |

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
- The hybrid retriever is local and sparse; it is not yet a vector database.
- Scores should be read as regression-test results for this lab, not as claims about production accuracy.

## Recommended Next Work

- Add noisier, human-written ticket variants.
- Introduce a real embedding/vector retrieval experiment.
- Add downloadable PDF or HTML report export.
- Add OpenTelemetry-compatible trace export.
- Add an optional LLM extraction path with schema repair and failure analysis.
