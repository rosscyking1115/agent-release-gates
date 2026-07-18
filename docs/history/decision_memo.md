# Decision Memo

## Decision

Use **Agent Safety & Reliability Evaluation Lab** as the public project identity.

Keep the synthetic internal-operations domain as the controlled benchmark scenario, but stop using "Internal AI Agent" as the headline. The public artifact should be framed as an evaluation harness for grounded retrieval, safe refusal, tool-use governance, observability, and safety/usefulness trade-off analysis.

## Context

The goal is to create a reusable public lab for testing AI-agent behavior without confidential data.

The project needs to be more than a chatbot demo. It should help people inspect a measurable agent workflow with retrieval, extraction, safety controls, approval gates, auditability, and reproducible evaluation.

The active research question is:

```text
When do safety interventions improve agent safety, and when do they reduce usefulness on benign operational tasks?
```

The public framing must stay clear:

- no real company system is reproduced
- no confidential or employer data is used
- no claim is made about the quality of any real internal system
- the internal operations benchmark uses synthetic workflows, teams, tickets, runbooks, and metrics
- external public benchmarks are clearly separated from the synthetic internal benchmark

## Options Considered

| Option | Pros | Cons |
| --- | --- | --- |
| Generic chatbot | Fast to build | Weak utility and hard to evaluate |
| Realistic internal AI clone | Could look relevant | Unsafe framing; risks implying access to real systems |
| Synthetic evaluation lab | Safe, measurable, reusable by others | Requires more engineering discipline and documentation |
| Public safety and reliability benchmark | Stronger research framing; easier for external reviewers to inspect | Requires clearer dataset cards, contribution process, and limitation language |

## Chosen Approach

Use a synthetic operations domain for the internal benchmark:

- synthetic runbooks
- synthetic operations tickets
- golden evaluation cases
- red-team cases
- local deterministic policies
- mock tools only

Use public technical-support data only as a separate retrieval benchmark:

- 160-case TechQA-RAG-Eval sample
- 80-case WixQA expert-written sample
- public dataset license attribution
- no claim that public support cases represent internal operations

The project is positioned as a responsible AI-agent safety and reliability evaluation lab. Its value comes from starting with a weak baseline, measuring failures, and then improving grounding, extraction, safety, approval control, observability, and trade-off reporting.

## Design Principles

- Measure before improving.
- Cite synthetic evidence for operational answers.
- Abstain when evidence is weak.
- Treat user prompts and retrieved documents as untrusted.
- Validate structured outputs with schemas.
- Require approval before side-effecting mock tools.
- Keep all data synthetic and safe to publish.
- Prefer deterministic tests before adding paid or stochastic model providers.
- Label planned research-grade features clearly until they are implemented and reproducible.

## Evidence Built So Far

- Synthetic data generator
- Baseline vs improved retrieval eval
- Local vector and embedding-store retrieval experiments
- TechQA public RAG benchmark
- WixQA public RAG benchmark
- Retriever metric snapshots
- Evaluation release gates
- Dataset profile and coverage gaps
- Citation and abstention metrics
- Structured extraction schemas
- Red-team policy suite
- Safety prevalence and classifier evaluation workflow (thresholding, synthetic prevalence estimation, false positive / false negative trade-off measurement, human-review simulation, reviewer-disagreement slicing, secondary review-band analysis, secondary-floor validation, operating recommendation, mitigation-impact reporting)
- Controlled agent workflow with tool governance and approval gates
- Trace and audit events
- OTel-style evaluation, trace timeline, local trace index, OTLP/HTTP export preview, local collector smoke test, and Dockerized OpenTelemetry Collector check
- FastAPI and Streamlit surfaces
- CI workflow and operations runbook

## Current Results

The improved lexical retrieval path raises citation coverage from 18.75% to 98.26% and retrieval hit rate@3 from 44.79% to 99.31% on the expanded 358-case synthetic golden suite. The sparse hybrid retriever reaches 100.00% retrieval hit@3 and 99.65% citation coverage; one manual field-note case exposes a final-selection weakness where a commission-code issue is retrieved but a booking-status section is cited. The local TF-IDF vector retriever and local feature-hashed embedding store reach 100.00% retrieval hit@3 and 100.00% citation coverage after failure-guided reranking for stale context, schema mismatch, KYC artefact phrasing, mixed evidence bundles, decision-log wording, partial evidence notes, field-note wording, and retrieved-context review packets.

The dataset profile now reports 102 manually authored golden cases, 70 expected abstentions, 46 noise types, 22 task types, and a 28.49% manual-case share. This clears the previous manual-share-below-25% gap while keeping the provider-backed embedding comparison gap visible.

The retriever snapshot report records deterministic deltas between retriever versions, so regressions are visible even when every system is generated from the same local synthetic dataset.

The TechQA public RAG track evaluates 160 compact public technical-support cases with 87.50% retrieval hit rate@3, 77.34% top-1 citation accuracy, 81.51% mean reciprocal rank@3, and 34.38% impossible-question abstention for the primary local TF-IDF public retriever. The accompanying comparison shows that the local TF-IDF retriever improves retrieval hit rate@3 by 14.84 percentage points and top-1 citation accuracy by 18.75 percentage points versus a keyword-title baseline, while impossible-question abstention decreases by 25.00 percentage points. The benchmark profile records 128 answerable cases, 32 impossible cases, 119 unique public documents, and a 31.87% failed-case rate.

The WixQA public RAG track evaluates 80 compact expert-written enterprise-support cases with 88.75% retrieval hit rate@3, 75.00% top-1 citation accuracy, 81.04% mean reciprocal rank@3, and 95.65% multi-article retrieval hit rate@3 for the primary local TF-IDF WixQA retriever. The accompanying comparison shows retrieval hit rate@3 improving by 27.50 percentage points and top-1 citation accuracy improving by 28.75 percentage points versus a keyword-title baseline. The benchmark profile records 96 unique public documents, 23 multi-article cases, and a 25.00% failed-case rate.

The controlled-agent workflow blocks side-effecting mock routes without approval and executes them only when approval is granted. The eval reports 100.00% side-effect block rate, approval audit rate, and valid tool-call rate.

The security red-team suite reports 100.00% improved explicit policy block rate, 100.00% improved safe response rate, 100.00% improved weighted safe response rate, and 0 improved residual risk score across 60 deterministic red-team cases, including harder retrieved-context attacks for priority inversion, approval-gate bypass, citation suppression, unsupported resolution, and access escalation.

The safety-classifier module separates enriched challenge cases, a targeted secondary-floor validation slice, and weighted synthetic prevalence cases. After adding harder medium-severity system-prompt-leakage, weak-evidence-pressure, unbounded-consumption, and benign governance near-miss cases, the retuned classifier reports 90.91% challenge-set recall, 0.00% false positive rate, 0 high-severity false negatives, and a 10.02% weighted synthetic unsafe-request prevalence estimate. The retuning comparison reduces challenge-set false negatives from 13 to 3 while keeping benign near-miss false positives at 0. The workflow includes deterministic human-review simulation, 31 synthetic human-authored adjudication notes, 19 reviewer-disagreement slices, secondary review-band analysis, secondary-floor validation, mitigation-impact comparison, operating recommendation, and a threshold decision memo so the output reads like an operating decision rather than just a model score. The expanded 39-case validation slice catches 100.00% of low-scoring unsafe targeted cases and 100.00% of multi-turn unsafe validation cases while moving 9.52% of benign validation cases into review after the benign-intent guard. Benign multi-turn governance cases add 0.00% new reviews. Synthetic reviewer labels and independent rubric labels cover 100.00% of validation cases and both estimate 88.24% precision when the secondary floor fires. Capacity sensitivity shows the floor stays within capacity at 16 or more cases per reviewer per day, but breaches at 4 or 8 cases per reviewer per day. The operating recommendation adopts the targeted secondary floor only when two reviewers can sustain at least 16 cases per reviewer per day for the current validation volume.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Project appears to imply a real organization system | README, model card, and docs clearly state the synthetic internal benchmark scope |
| Metrics look too perfect | Manual challenge failures were fixed and kept as regression tests, newer analyst-authored, field-note, mixed review-bundle, decision-log, partial-evidence, and retrieved-context review batches were added, and the report keeps the hybrid field-note miss visible instead of forcing every retriever to 100% |
| Agent appears to take real actions | Tool names include `mock`, and side effects require approval |
| Demo depends on paid APIs | Tests and evals are deterministic and local |
| System seems like only a dashboard | FastAPI endpoints, eval reports, CI, and docs provide programmatic access and reproducible artifacts beyond the dashboard |
| Public-data results blur the synthetic-lab boundary | TechQA and WixQA are reported as separate external benchmark tracks |

## Next Decisions

- How to attach a formal failure taxonomy to case-level results and summaries.
- How to collect and publish a small human-labeled calibration sample without overclaiming production validity.
- Which LLM-as-judge and multi-model adapters to support first, and how to separate unpublished local runs from public results.
- Whether to expand the TechQA and WixQA public benchmarks before or after provider-backed embedding comparison.
- How to invite external review through GitHub issues, contribution docs, benchmark cards, and a paper-style report.
