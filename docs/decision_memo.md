# Decision Memo

## Decision

Build the project as a useful public synthetic Internal AI Agent Evaluation Lab rather than a clone, mimic, or critique of any real company's internal AI system.

## Context

The goal is to create a reusable local lab for testing internal AI agent behavior without confidential data. Any career story should be a result of the work being useful, measured, and well documented.

The project needs to be more than a chatbot demo. It should help people inspect a measurable internal AI workflow with retrieval, extraction, safety controls, approval gates, auditability, and reproducible evaluation.

The public framing must stay clear:

- no real company system is reproduced
- no confidential or employer data is used
- no claim is made about the quality of any real internal system
- all workflows, teams, tickets, runbooks, and metrics are synthetic

## Options Considered

| Option | Pros | Cons |
| --- | --- | --- |
| Generic chatbot | Fast to build | Weak utility and hard to evaluate |
| Realistic internal AI clone | Could look relevant | Unsafe framing; risks implying access to real systems |
| Synthetic evaluation lab | Safe, measurable, reusable by others | Requires more engineering discipline and documentation |

## Chosen Approach

Use a fully synthetic operations domain:

- synthetic runbooks
- synthetic operations tickets
- golden evaluation cases
- red-team cases
- local deterministic policies
- mock tools only

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
| Retriever metric snapshots | Regression tracking across retriever versions |
| Evaluation release gates | Deterministic quality bars before publishing results |
| Dataset profile and coverage gaps | Benchmark design honesty |
| Citation and abstention metrics | Grounded AI judgement |
| Structured extraction schemas | Document intelligence and validation |
| Red-team policy suite | AI security awareness |
| Controlled agent workflow | Tool governance and approval design |
| Trace and audit events | Observability and debugging |
| OTel-style evaluation, trace timeline, local trace index, OTLP/HTTP export preview, local collector smoke test, and Dockerized OpenTelemetry Collector check | Inspectable local observability artifact |
| FastAPI and Streamlit surfaces | Product delivery |
| CI workflow and operations runbook | Engineering reliability |

## Current Results

The improved lexical retrieval path raises citation coverage from 19.15% to 98.58% and retrieval hit rate@3 from 45.39% to 99.29% on the expanded 350-case synthetic golden suite. The sparse hybrid retriever reaches 100.00% retrieval hit@3 and 99.65% citation coverage; one manual field-note case exposes a final-selection weakness where a commission-code issue is retrieved but a booking-status section is cited. The local TF-IDF vector retriever and local feature-hashed embedding store reach 100.00% retrieval hit@3 and 100.00% citation coverage after failure-guided reranking for stale context, schema mismatch, KYC artefact phrasing, mixed evidence bundles, field-note wording, and retrieved-context review packets.

The dataset profile now reports 94 manually authored golden cases, 68 expected abstentions, 42 noise types, 18 task types, and a 26.86% manual-case share. This clears the previous manual-share-below-25% gap while keeping the provider-backed embedding comparison gap visible.

The retriever snapshot report records deterministic deltas between retriever versions, so regressions are visible even when every system is generated from the same local synthetic dataset.

The controlled-agent workflow blocks side-effecting mock routes without approval and executes them only when approval is granted. The eval reports 100.00% side-effect block rate, approval audit rate, and valid tool-call rate.

The security red-team suite reports 100.00% improved explicit policy block rate, 100.00% improved safe response rate, 100.00% improved weighted safe response rate, and 0 improved residual risk score across 60 deterministic red-team cases, including harder retrieved-context attacks for priority inversion, approval-gate bypass, citation suppression, unsupported resolution, and access escalation.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Project appears to mimic a real employer system | README, model card, and docs clearly state synthetic-only scope |
| Metrics look too perfect | Manual challenge failures were fixed and kept as regression tests, newer analyst-authored, field-note, mixed review-bundle, and retrieved-context review batches were added, and the report keeps the hybrid field-note miss visible instead of forcing every retriever to 100% |
| Agent appears to take real actions | Tool names include `mock`, and side effects require approval |
| Demo depends on paid APIs | Tests and evals are deterministic and local |
| System seems like only a dashboard | FastAPI endpoints, eval reports, CI, and docs show engineering depth |
| Project becomes external-signaling-first rather than useful | Product direction doc keeps the build focused on reusable lab value |

## Next Decisions

- Whether to compare the local embedding store with a provider-backed embedding model.
- Whether to add a real LangGraph dependency or keep the local controlled workflow until evaluation cases become more varied.
- Whether to prioritize noisier data/error analysis or downstream trace-index and collector storage/visualization.
