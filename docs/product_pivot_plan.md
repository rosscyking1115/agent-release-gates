# Agent Release Safety Gates Pivot Plan

## Positioning

The project is pivoting from a broad evaluation lab into a release-readiness tool for AI-agent systems.

Public title:

```text
Agent Release Safety Gates
```

The goal is to help teams answer a practical release question:

```text
Can this agent change ship without reintroducing known unsafe, unreliable, or unreviewed behavior?
```

The current evaluation lab remains useful, but its role changes. It becomes the evidence engine behind a more company-like workflow: incident replay, policy gates, human review, audit trails, and release memos.

## What The Tool Should Do

The tool should support a repeatable safety and reliability workflow:

```text
agent change
-> run benchmark and incident replay
-> apply policy-as-code gates
-> inspect failures and review queue
-> produce ship / warn / block decision
-> generate release evidence and incident memos
```

The project should be useful to people who need to evaluate agent behavior before deployment, especially when agents can retrieve context, call tools, act on tickets, or handle unsafe and ambiguous requests.

## Why This Pivot

The earlier lab proved that deterministic evaluation, public RAG validation, safety classifiers, human-review simulation, and approval-gated tool workflows can be measured. The next level is to make those measurements operational.

The strongest product-shaped use case is release gating:

- replay known incidents before shipping a new agent or policy version
- block releases when high-severity cases violate `must_not` assertions
- preserve evidence through trace, audit, report, and memo artifacts
- separate safety improvement from usefulness cost
- turn each confirmed failure into a regression fixture

## First Module: Incident Replay Suite

The first v0 module should ingest or define incident cases, replay them against the current controlled agent workflow, and produce release-gate artifacts.

V0 inputs:

- `data/incidents/incident_cases.jsonl`
- `data/incidents/trace_events.jsonl`

V0 outputs:

- `reports/incident_replay_summary.json`
- `reports/incident_replay_runs.jsonl`
- `reports/incident_release_gates.json`
- `reports/incident_memo_INC-*.md`
- `data/eval_cases/incident_regression_cases.jsonl`
- `config/incident_release_policy.json`

V0 behavior:

- evaluate each incident against the current controlled agent
- load policy-as-code release thresholds from JSON
- detect side-effect tool execution without approval
- detect policy or system-prompt leakage patterns
- compare replay behavior with expected behavior
- create release gates over high-severity incident regressions
- generate lightweight incident memos for review

V0 command:

```powershell
uv run python scripts/agent_safety.py release-gate --policy config/incident_release_policy.json
```

## Public Boundary

This project must stay honest and public-safe.

- It does not use real company documents, tickets, customers, employees, or proprietary processes.
- It does not claim to reproduce any real external incident or exploit.
- Simulated incidents are clearly marked as synthetic fixtures.
- Public TechQA and WixQA tracks remain separate from controlled synthetic operations data.
- The project should claim evaluation infrastructure and release evidence, not production safety certification.

## Near-Term Roadmap

Completed:

1. Build Incident Replay Suite v0 with seeded synthetic incident fixtures.
2. Add an `agent-safety` CLI entry point for release-gate runs.
3. Add validated policy-as-code thresholds for incident gates.
4. Add Streamlit incident queue, trace timeline, replay matrix, and memo views.
5. Reframe README, GitHub Pages, and Streamlit around release readiness.

Next:

1. Add public or human-labelled incident-style cases where licensing and privacy are suitable.

## Success Criteria

The pivot is successful when a reviewer can run one command and understand:

- which incidents were replayed
- whether high-severity `must_not` assertions were violated
- what changed between original incident behavior and current candidate behavior
- whether the release should pass, warn, or fail
- what regression fixtures were generated
- what limitations remain
