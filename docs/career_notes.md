# Career Notes

These notes are secondary. The project should be built as a useful synthetic evaluation lab first. CV and interview value should come from that work, not drive it.

## Short Project Explanation

I built an original synthetic Internal AI Agent Evaluation Lab for testing internal AI agent reliability without confidential data. Instead of making a generic chatbot, I created synthetic operations runbooks, tickets, golden eval cases, red-team cases, dataset-profile reports, FastAPI endpoints, a dashboard, and deterministic evaluation reports. The project measures grounding, citation coverage, structured extraction, routing, safety refusals, approval-gated tool use, auditability, and benchmark coverage gaps.

## What Problem It Solves

Internal AI agents are only useful if they are grounded, measurable, safe, and auditable. This project treats the agent as an operational system:

- retrieve the right synthetic runbook evidence
- answer with citations
- extract structured ticket fields
- route tickets to synthetic teams
- refuse unsafe or weak-evidence requests
- require approval before mock side effects
- produce trace, audit, and local span timeline records

## Strongest Technical Explanation

I started with a deliberately weak baseline so improvement could be measured. The baseline used broad team/system hints and often found the right team but not the exact procedure. Then I added deterministic lexical retrieval, a local sparse semantic hybrid retriever, a local TF-IDF vector retriever, a local feature-hashed embedding store, role filtering, citations, abstention behavior, structured extraction, red-team blocking, controlled tool use, traceable audit events, and a local span timeline.

The important part is not that the demo looks polished. The important part is that each improvement has an evaluation report behind it, including retriever snapshot deltas that show where newer experiments regress.

## Results To Use Carefully

| Metric | Result |
| --- | --- |
| Retrieval hit rate@3 | 45.39% baseline to 99.29% lexical and 100.00% hybrid/vector/embedding-store |
| Citation coverage | 19.15% baseline to 98.58% lexical, 99.65% hybrid, and 100.00% vector/embedding-store |
| Local TF-IDF vector retrieval | 100.00% retrieval hit@3 and 100.00% citation coverage |
| Local embedding-store retrieval | 100.00% retrieval hit@3 and 100.00% citation coverage |
| Hybrid retrieval experiment | One visible field-note final-selection miss on the harder 350-case synthetic golden set |
| Dataset profile | 94 manual cases, 68 expected abstentions, 42 noise types, and 26.86% manual share |
| Abstention accuracy | 81.43% baseline to 100.00% improved |
| Structured extraction schema validity | 100.00% |
| Improved red-team safe response rate | 100.00% |
| Improved red-team weighted safe response rate | 100.00% |
| Improved red-team residual risk score | 0 |
| Agent side-effect block rate | 100.00% |
| Trace and audit event coverage | 100.00% |
| Tests | Local pytest suite passing |

These are synthetic deterministic metrics, so I would present them as engineering checks rather than real production claims.

## Possible CV Bullet

Built a synthetic internal AI agent evaluation lab with Python, FastAPI, Pydantic, Streamlit, deterministic RAG, local TF-IDF vector retrieval, local embedding-store retrieval, structured ticket extraction, dataset profiling, red-team policy checks, approval-gated mock tools, traceable audit events, local span timeline, OpenTelemetry Collector export checks, and CI-backed evaluation reports over synthetic operations tickets and runbooks.

## Possible Deeper CV Bullet

Designed and implemented a production-style internal operations AI workflow over fully synthetic data, improving retrieval hit rate@3 from 45.39% to 99.29% with lexical retrieval and 100.00% with local vector and embedding-store retrievers, while adding Pydantic extraction, policy refusals, approval-gated mock tool use, structured audit events, and reproducible CI evaluation.

## Technical Questions The Project Supports

- Why did I use synthetic data?
- Why measure a weak baseline first?
- Why are citations and abstention important in operations workflows?
- Why separate retrieval hit@3 from final citation correctness?
- Why did the local embedding-store retriever trail TF-IDF on final citation selection?
- Why track retriever-version snapshots instead of only latest metrics?
- How does the approval gate reduce excessive agency risk?
- How are prompt injection and system-prompt leakage handled?
- What would change if this became a real production system?
- Why did I keep the first version deterministic instead of using paid APIs?

## Honest Limitations

- Current published embedding retrieval uses local feature hashing rather than provider-backed embeddings. A provider-backed evaluation path exists, but provider-backed results should only be claimed after an actual credentialed run.
- The dataset is synthetic and still partly templated, although it now includes manual field notes, evidence packets, mixed review bundles, and retrieved-context review packets with stale side chatter, current-evidence cues, table extracts, and ownership-conflict abstentions.
- The previous manual-case share gap is cleared; the dataset profile now flags provider-backed embedding comparison as the clearest retrieval gap.
- The extraction layer is deterministic and should be tested on the newer evidence-packet, email-thread, and conflicting-context styles.
- Red-team checks are string-based and should be expanded with more varied phrasing.
- The controlled agent is a local workflow rather than a LangGraph graph.
- Telemetry is local JSONL, including OpenTelemetry-style agent spans, evaluation-stage spans, case-level retriever failure spans, retriever ranking-detail spans, case-level extraction spans, case-level agent approval spans, API contract/error spans, a dashboard trace timeline, an optional OTLP/HTTP collector exporter, a local capture smoke test for POST-path verification, and a Dockerized OpenTelemetry Collector deployment check verified through collector self-metrics. The remaining gap is downstream storage or production observability visualization.

## Useful Next Build Step

The most valuable next engineering step is to run the optional provider-backed embedding comparison or add model-assisted adversarial review for the red-team suite. That would show retrieval experimentation and evaluation discipline without changing the project framing.
