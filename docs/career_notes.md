# Career Notes

These notes are secondary. The project should be built as a useful synthetic evaluation lab first. CV and interview value should come from that work, not drive it.

## Short Project Explanation

I built an original synthetic Internal AI Agent Evaluation Lab for testing internal AI agent reliability without confidential data. Instead of making a generic chatbot, I created synthetic operations runbooks, tickets, golden eval cases, red-team cases, FastAPI endpoints, a dashboard, and deterministic evaluation reports. The project measures grounding, citation coverage, structured extraction, routing, safety refusals, approval-gated tool use, and auditability.

## What Problem It Solves

Internal AI agents are only useful if they are grounded, measurable, safe, and auditable. This project treats the agent as an operational system:

- retrieve the right synthetic runbook evidence
- answer with citations
- extract structured ticket fields
- route tickets to synthetic teams
- refuse unsafe or weak-evidence requests
- require approval before mock side effects
- produce trace and audit records

## Strongest Technical Explanation

I started with a deliberately weak baseline so improvement could be measured. The baseline used broad team/system hints and often found the right team but not the exact procedure. Then I added deterministic lexical retrieval, a local sparse semantic hybrid retriever, a local TF-IDF vector retriever, a local feature-hashed embedding store, role filtering, citations, abstention behavior, structured extraction, red-team blocking, controlled tool use, and traceable audit events.

The important part is not that the demo looks polished. The important part is that each improvement has an evaluation report behind it, including retriever snapshot deltas that show where newer experiments regress.

## Results To Use Carefully

| Metric | Result |
| --- | --- |
| Retrieval hit rate@3 | 45.50% baseline to 99.00% lexical and 100.00% hybrid |
| Citation coverage | 20.50% baseline to 98.50% lexical and 100.00% hybrid |
| Local TF-IDF vector retrieval | 100.00% retrieval hit@3 and 100.00% citation coverage |
| Local embedding-store retrieval | 100.00% retrieval hit@3 and 100.00% citation coverage |
| Hybrid retrieval experiment | Best current retriever on a harder 256-case synthetic golden set |
| Abstention accuracy | 78.52% baseline to 100.00% improved |
| Structured extraction schema validity | 100.00% |
| Improved red-team safe response rate | 100.00% |
| Agent side-effect block rate | 100.00% |
| Trace and audit event coverage | 100.00% |
| Tests | 59 passing |

These are synthetic deterministic metrics, so I would present them as engineering checks rather than real production claims.

## Possible CV Bullet

Built a synthetic internal AI agent evaluation lab with Python, FastAPI, Pydantic, Streamlit, deterministic RAG, local TF-IDF vector retrieval, local embedding-store retrieval, structured ticket extraction, red-team policy checks, approval-gated mock tools, traceable audit events, and CI-backed evaluation reports over synthetic operations tickets and runbooks.

## Possible Deeper CV Bullet

Designed and implemented a production-style internal operations AI workflow over fully synthetic data, improving retrieval hit rate@3 from 45.50% to 99.00% with lexical retrieval and 100.00% with a sparse semantic hybrid, while adding Pydantic extraction, policy refusals, approval-gated mock tool use, structured audit events, and reproducible CI evaluation.

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

- Current embedding retrieval uses local feature hashing rather than provider-backed embeddings.
- The extraction layer is deterministic and should be tested on the newer email-thread and conflicting-context styles.
- Red-team checks are string-based and should be expanded with more varied phrasing.
- The controlled agent is a local workflow rather than a LangGraph graph.
- Telemetry is local structured data rather than OpenTelemetry export.

## Useful Next Build Step

The most valuable next engineering step is to compare the local embedding-store retriever with a provider-backed embedding model or make the golden suite less templated with new non-generated tickets. That would show retrieval experimentation and evaluation discipline without changing the project framing.
