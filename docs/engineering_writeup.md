# Engineering writeup: gating AI-agent releases on safety evidence

*A reference implementation of AI-safety release-engineering. This explains the idea, the
design decisions, and what the implementation covers. It is a reference project, not a
product.*

## The problem

AI agents regress silently. A prompt tweak, a model swap, a new tool, or a loosened approval
policy can quietly reintroduce a failure you already fixed: a prompt-injection that now
lands, a side-effecting tool that fires without sign-off, an answer invented from weak
evidence. Unlike a crashing web service, an unsafe agent usually looks fine. It returns a
fluent answer, and the regression stays invisible until it hurts someone.

Web services solved the analogous problem decades ago with regression tests and release
gates in CI. You do not ship if the suite goes red. This project applies that discipline to
agent safety: it replays known incidents against a changed agent and refuses to ship if a
safety property regressed.

## The core idea: incident replay and policy-as-code

Two moving parts, both borrowed from release engineering.

Incident replay turns every known failure into a permanent regression fixture. A redacted
incident pack captures the situation (the prompt, the retrieved context, the tools
available) and the must-not properties: `execute_side_effect_without_approval`,
`reveal_policy`, `leak_sensitive_data`, and so on. The candidate agent is replayed against
each incident, and the result is scored for whether it re-triggers the original failure.

Policy-as-code gates keep the thresholds in a JSON file rather than in someone's head:
minimum closure rate, zero must-not violations, minimum expected-behavior match. The gate
turns the scored results into one verdict of `ship`, `warn`, or `block`, and exits non-zero
on a blocking failure, so it drops straight into CI.

```
incidents ──▶ replay matrix ──▶ policy gates ──▶ ship / warn / block ──▶ evidence + memo
 (synthetic)   (deterministic)   (policy-as-code)    (CLI exit code)      (report / audit)
```

## Design decisions

The core is deterministic, and hosted models are optional. The gate, scoring, retrieval, and
incident replay run with no API keys and no network, so CI is reproducible and anyone can run
the whole thing for free. Hosted-model comparisons (OpenAI and Anthropic embeddings and
judges) are optional overlays whose results are reviewed and committed separately. That is
what keeps the evidence trustworthy: the numbers a reviewer sees in CI are the numbers they
can regenerate.

The contract is agent-agnostic. The gate never calls your agent. It consumes a
`candidate_results.jsonl` holding one normalized row per incident, with the decision, answer,
citations, and tool outcomes. Adapters convert real framework output into that contract:
generic logs, LangChain and LangSmith traces, OpenAI Agents SDK run results, and LangGraph
final states. Decoupling scoring from execution is what lets the same gate evaluate any agent
and still run deterministically.

A blocked release produces evidence, not just a boolean. It writes an incident memo, a replay
summary, span-level traces, and a readable report, which are the artifacts a reviewer needs
to act on rather than a red X.

Every headline number ships beside its cost. A safety classifier that blocks everything
scores perfectly on recall and is useless, so the reports carry over-review rate, benign
auto-blocks, weak-evidence handling, and unsafe misses next to the score. Interventions are
measured as trade-offs, safety gained against review burden added, not as one number to
maximize.

## What gets evaluated

The harness answers five release questions, each backed by a concrete eval.

| Question | How it is tested |
| --- | --- |
| Grounding: does it retrieve and cite the right evidence? | golden retrieval benchmark, plus the public TechQA and WixQA RAG tracks |
| Refusal: does it abstain on weak, unsafe, or injected input? | red-team suite, weak-evidence pressure, prompt-injection cases |
| Approval: does it require sign-off before side effects? | approval-gated mock tool use, side-effect block rate |
| Auditability: does it leave enough trace to review? | OpenTelemetry-style spans, audit events, trace index |
| Replay: does it pass incident replay and the policy gates? | seeded incidents, replay matrix, policy-as-code gate |

## Two findings

On the synthetic benchmark, a hosted OpenAI embedding only ties the local TF-IDF retrievers.
Both saturate at 100% hit@3, so the benchmark cannot tell them apart. On the harder public
RAG tracks the hosted embedding clearly wins, with a WixQA hit@3 of 98.1% against 77.5%. A
saturated benchmark hides real differences, and you need a hard enough test to see them.

As a safety judge, a free self-hosted `llama3.1:8b` reached 91.7% label accuracy against
95.8% for `gpt-4.1-mini` and 100% for `claude-sonnet-4-5`, on a 24-case calibration set. But
it under-blocked, missing 2 unsafe cases the frontier models caught, while the frontier model
erred toward over-blocking a benign one. For a safety judge, misses matter more than
aggregate accuracy, so the three are reported as disagreement slices rather than a
leaderboard. One implementation detail: the local model first meta-refused the judging task
in prose, and only complied once the output was constrained to JSON.

## What this implementation covers

- A deterministic, reproducible scoring pipeline with an agent-agnostic contract and a
  policy-as-code gate that runs in CI.
- Safety evaluation: red-teaming, prompt-injection resistance, abstention and weak-evidence
  handling, approval-gated tool use, and a failure taxonomy covering safety, retrieval,
  citation, privacy, and tool use.
- A multi-provider LLM-as-judge comparison, including a self-hosted model, reported as
  calibrated disagreement rather than a ranking.
- RAG evaluation: grounding, citation accuracy, and abstention measured on both synthetic
  and real public data.
- Packaging and systems: a PyPI-published CLI, a FastAPI service, a Streamlit dashboard,
  Docker and Compose, GitHub Actions CI, GitHub Pages reporting, and OpenTelemetry-style
  observability.

## Limitations

- The controlled benchmark is synthetic and partly templated. It demonstrates the method,
  not real-world prevalence.
- Human-review labels are simulated. Independent labels are the top open item.
- The judge calibration set is small (n = 24), so those findings are directional.
- Deterministic, rule-based checks stand in for some behaviors a production system would
  evaluate with more expensive methods.

## Scope

This is a reference implementation. There is no roadmap, support commitment, pricing, or
commercial intent, and none is planned. The working infrastructure (service, dashboard,
Docker, exporters) exists to make the design and evidence inspectable end to end.
