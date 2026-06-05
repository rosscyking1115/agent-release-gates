# Decision Memo

## Decision

Build the project as a useful public Internal AI Agent Evaluation Lab rather than a clone or critique of any real company's internal AI system.

## Context

The goal is to create a reusable local lab for testing internal AI agent behavior without confidential data.

The project needs to be more than a chatbot demo. It should help people inspect a measurable internal AI workflow with retrieval, extraction, safety controls, approval gates, auditability, and reproducible evaluation.

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
- public dataset license attribution
- no claim that public support cases represent internal operations

The project is positioned as a responsible enterprise AI engineering lab. Its value comes from starting with a weak baseline, measuring failures, and then improving grounding, extraction, safety, approval control, and observability.

## Design Principles

- Measure before improving.
- Cite synthetic evidence for operational answers.
- Abstain when evidence is weak.
- Treat user prompts and retrieved documents as untrusted.
- Validate structured outputs with schemas.
- Require approval before side-effecting mock tools.
- Keep all data synthetic and safe to publish.
- Prefer deterministic tests before adding paid or stochastic model providers.

## Evidence Built So Far

| Evidence | Skill Signal |
| --- | --- |
| Synthetic data generator | Data design and privacy-aware development |
| Baseline vs improved retrieval eval | Measurement discipline |
| Local vector and embedding-store retrieval experiments | Retrieval experimentation and error analysis |
| TechQA public RAG benchmark | External validation over public technical-support data |
| Retriever metric snapshots | Regression tracking across retriever versions |
| Evaluation release gates | Deterministic quality bars before publishing results |
| Dataset profile and coverage gaps | Benchmark design honesty |
| Citation and abstention metrics | Grounded AI judgement |
| Structured extraction schemas | Document intelligence and validation |
| Red-team policy suite | AI security awareness |
| Safety prevalence and classifier evaluation workflow | Safety thresholding, synthetic prevalence estimation, false positive / false negative trade-off measurement, human-review simulation, reviewer-disagreement slicing, secondary review-band analysis, secondary-floor validation, operating recommendation, mitigation-impact reporting, and decision-support design |
| Controlled agent workflow | Tool governance and approval design |
| Trace and audit events | Observability and debugging |
| OTel-style evaluation, trace timeline, local trace index, OTLP/HTTP export preview, local collector smoke test, and Dockerized OpenTelemetry Collector check | Inspectable local observability artifact |
| FastAPI and Streamlit surfaces | Product delivery |
| CI workflow and operations runbook | Engineering reliability |

## Current Results

The improved lexical retrieval path raises citation coverage from 19.15% to 98.58% and retrieval hit rate@3 from 45.39% to 99.29% on the expanded 350-case synthetic golden suite. The sparse hybrid retriever reaches 100.00% retrieval hit@3 and 99.65% citation coverage; one manual field-note case exposes a final-selection weakness where a commission-code issue is retrieved but a booking-status section is cited. The local TF-IDF vector retriever and local feature-hashed embedding store reach 100.00% retrieval hit@3 and 100.00% citation coverage after failure-guided reranking for stale context, schema mismatch, KYC artefact phrasing, mixed evidence bundles, field-note wording, and retrieved-context review packets.

The dataset profile now reports 94 manually authored golden cases, 68 expected abstentions, 42 noise types, 18 task types, and a 26.86% manual-case share. This clears the previous manual-share-below-25% gap while keeping the provider-backed embedding comparison gap visible.

The retriever snapshot report records deterministic deltas between retriever versions, so regressions are visible even when every system is generated from the same local synthetic dataset.

The TechQA public RAG track evaluates 160 compact public technical-support cases with 87.50% retrieval hit rate@3, 77.34% top-1 citation accuracy, 81.51% mean reciprocal rank@3, and 34.38% impossible-question abstention for the primary local TF-IDF public retriever. The accompanying comparison shows that the local TF-IDF retriever improves retrieval hit rate@3 by 14.84 percentage points and top-1 citation accuracy by 18.75 percentage points versus a keyword-title baseline, while impossible-question abstention decreases by 25.00 percentage points. The benchmark profile records 128 answerable cases, 32 impossible cases, 119 unique public documents, and a 31.87% failed-case rate.

The controlled-agent workflow blocks side-effecting mock routes without approval and executes them only when approval is granted. The eval reports 100.00% side-effect block rate, approval audit rate, and valid tool-call rate.

The security red-team suite reports 100.00% improved explicit policy block rate, 100.00% improved safe response rate, 100.00% improved weighted safe response rate, and 0 improved residual risk score across 60 deterministic red-team cases, including harder retrieved-context attacks for priority inversion, approval-gate bypass, citation suppression, unsupported resolution, and access escalation.

The safety-classifier module separates enriched challenge cases, a targeted secondary-floor validation slice, and weighted synthetic prevalence cases. After adding harder medium-severity system-prompt-leakage, weak-evidence-pressure, unbounded-consumption, and benign governance near-miss cases, the retuned classifier reports 90.91% challenge-set recall, 0.00% false positive rate, 0 high-severity false negatives, and a 10.02% weighted synthetic unsafe-request prevalence estimate. The retuning comparison reduces challenge-set false negatives from 13 to 3 while keeping benign near-miss false positives at 0. The workflow includes deterministic human-review simulation, 31 synthetic human-authored adjudication notes, 19 reviewer-disagreement slices, secondary review-band analysis, secondary-floor validation, mitigation-impact comparison, operating recommendation, and a threshold decision memo so the output reads like an operating decision rather than just a model score. The expanded 39-case validation slice catches 100.00% of low-scoring unsafe targeted cases and 100.00% of multi-turn unsafe validation cases while moving 9.52% of benign validation cases into review after the benign-intent guard. Benign multi-turn governance cases add 0.00% new reviews. Synthetic reviewer labels and independent rubric labels cover 100.00% of validation cases and both estimate 88.24% precision when the secondary floor fires. Capacity sensitivity shows the floor stays within capacity at 16 or more cases per reviewer per day, but breaches at 4 or 8 cases per reviewer per day. The operating recommendation adopts the targeted secondary floor only when two reviewers can sustain at least 16 cases per reviewer per day for the current validation volume.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Project appears to imply a real organization system | README, model card, and docs clearly state the synthetic internal benchmark scope |
| Metrics look too perfect | Manual challenge failures were fixed and kept as regression tests, newer analyst-authored, field-note, mixed review-bundle, and retrieved-context review batches were added, and the report keeps the hybrid field-note miss visible instead of forcing every retriever to 100% |
| Agent appears to take real actions | Tool names include `mock`, and side effects require approval |
| Demo depends on paid APIs | Tests and evals are deterministic and local |
| System seems like only a dashboard | FastAPI endpoints, eval reports, CI, and docs show engineering depth |
| Public-data results blur the synthetic-lab boundary | TechQA is reported as a separate external benchmark track |

## Next Decisions

- Whether to compare the local embedding store with a provider-backed embedding model.
- Whether to expand the TechQA public benchmark beyond the 160-case compact sample.
- Whether to add a real LangGraph dependency or keep the local controlled workflow until evaluation cases become more varied.
- Whether to prioritize noisier data/error analysis or downstream trace-index and collector storage/visualization.
