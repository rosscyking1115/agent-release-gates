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

I started with a deliberately weak baseline so improvement could be measured. The baseline used broad team/system hints and often found the right team but not the exact procedure. Then I added deterministic lexical retrieval, a local sparse semantic hybrid retriever, role filtering, citations, abstention behavior, structured extraction, red-team blocking, controlled tool use, and traceable audit events.

The important part is not that the demo looks polished. The important part is that each improvement has an evaluation report behind it.

## Results To Use Carefully

| Metric | Result |
| --- | --- |
| Retrieval hit rate@3 | 45.45% baseline to 98.30% lexical and 100.00% hybrid |
| Citation coverage | 19.89% baseline to 97.73% lexical and 99.43% hybrid |
| Hybrid retrieval experiment | 1 remaining distractor-case failure on the current synthetic golden set |
| Abstention accuracy | 81.94% baseline to 100.00% improved |
| Structured extraction schema validity | 100.00% |
| Improved red-team safe response rate | 100.00% |
| Agent side-effect block rate | 100.00% |
| Trace and audit event coverage | 100.00% |
| Tests | 38 passing |

These are synthetic deterministic metrics, so I would present them as engineering checks rather than real production claims.

## Possible CV Bullet

Built a synthetic internal AI agent evaluation lab with Python, FastAPI, Pydantic, Streamlit, deterministic RAG, structured ticket extraction, red-team policy checks, approval-gated mock tools, traceable audit events, and CI-backed evaluation reports over synthetic operations tickets and runbooks.

## Possible Deeper CV Bullet

Designed and implemented a production-style internal operations AI workflow over fully synthetic data, improving retrieval hit rate@3 from 46.25% to 98.75% and citation coverage from 20.00% to 98.12%, while adding Pydantic extraction, policy refusals, approval-gated mock tool use, structured audit events, and reproducible CI evaluation.

## Technical Questions The Project Supports

- Why did I use synthetic data?
- Why measure a weak baseline first?
- Why are citations and abstention important in operations workflows?
- How does the approval gate reduce excessive agency risk?
- How are prompt injection and system-prompt leakage handled?
- What would change if this became a real production system?
- Why did I keep the first version deterministic instead of using paid APIs?

## Honest Limitations

- Current best retrieval is a deterministic sparse semantic hybrid rather than a true vector index.
- The extraction layer is deterministic and should be tested on noisier text.
- Red-team checks are string-based and should be expanded with more varied phrasing.
- The controlled agent is a local workflow rather than a LangGraph graph.
- Telemetry is local structured data rather than OpenTelemetry export.

## Useful Next Build Step

The most valuable next engineering step is to add a true vector retrieval layer and compare lexical, sparse hybrid, and vector retrieval using the same golden cases. That would show retrieval experimentation and evaluation discipline without changing the project framing.
