# Engineering Writeup — Gating AI-Agent Releases on Safety Evidence

*A reference implementation of AI-safety release-engineering. This writeup explains the
idea, the design decisions, and what the implementation covers. It is a reference project,
not a product.*

## The problem

AI agents regress silently. A prompt tweak, a model swap, a new tool, or a loosened
approval policy can quietly reintroduce a failure you already fixed — a prompt-injection
that now lands, a side-effecting tool that fires without sign-off, an answer that gets
confidently invented from weak evidence. Unlike a crashing web service, an unsafe agent
often looks fine: it returns a fluent answer. The regression is invisible until it hurts
someone.

Web services solved the analogous problem decades ago: regression tests and release gates
in CI. You do not ship if the suite goes red. **This project applies that discipline to
agent safety** — it replays known incidents against a changed agent and refuses to "ship"
if a safety property regressed.

## The core idea: incident replay + policy-as-code

Two moving parts, borrowed directly from release engineering:

1. **Incident replay.** Every known failure becomes a permanent regression fixture. A
   redacted "incident pack" captures the situation (the prompt, the retrieved context, the
   tools available) and the *must-not* properties (`execute_side_effect_without_approval`,
   `reveal_policy`, `leak_sensitive_data`, …). The candidate agent is replayed against each
   incident, and the result is scored for whether it re-triggers the original failure.

2. **Policy-as-code gates.** Thresholds live in a JSON policy, not in someone's head:
   minimum closure rate, zero must-not violations, minimum expected-behavior match, and so
   on. The gate turns the scored results into a single **`ship` / `warn` / `block`** verdict
   and exits non-zero on a blocking failure — so it drops straight into CI.

```
incidents ──▶ replay matrix ──▶ policy gates ──▶ ship / warn / block ──▶ evidence + memo
 (synthetic)   (deterministic)   (policy-as-code)    (CLI exit code)      (report / audit)
```

## Design decisions worth calling out

**Deterministic core; hosted models are optional add-ons.** The gate, scoring, retrieval,
and incident replay run with no API keys and no network — so CI is reproducible and anyone
can run the whole thing for free. Hosted-model comparisons (OpenAI/Anthropic embeddings and
judges) are strictly *optional overlays* whose results are reviewed and committed
separately. This keeps the evidence trustworthy: the numbers a reviewer sees in CI are the
numbers they can regenerate.

**An agent-agnostic contract.** The gate never calls your agent. It consumes a
`candidate_results.jsonl` — one normalized row per incident (decision, answer, citations,
tool outcomes). Adapters convert real framework output into that contract: generic logs,
LangChain/LangSmith traces, **OpenAI Agents SDK** run results, and **LangGraph** final
states. Decoupling *scoring* from *execution* is what lets the same gate evaluate any agent
and run deterministically.

**Evidence, not just a boolean.** A blocked release emits an incident memo, a replay
summary, span-level traces, and a human-readable report — the artifacts a reviewer actually
needs to act, not just a red X.

**Report the cost of safety, not only the score.** A safety classifier that blocks
everything scores perfectly on recall and is useless. So every headline number ships beside
its cost: over-review rate, benign auto-blocks, weak-evidence handling, and unsafe misses.
Interventions are measured as *trade-offs* (safety gained vs. review burden added), not as a
single number to maximize.

## What gets evaluated

The harness answers five release questions, each backed by a concrete eval:

| Question | How it is tested |
| --- | --- |
| **Grounding** — retrieves and cites the right evidence? | golden retrieval benchmark + public TechQA/WixQA RAG tracks |
| **Refusal** — abstains on weak/unsafe/injected input? | red-team suite, weak-evidence pressure, prompt-injection cases |
| **Approval** — requires sign-off before side effects? | approval-gated mock tool use, side-effect block rate |
| **Auditability** — leaves enough trace to review? | OpenTelemetry-style spans, audit events, trace index |
| **Replay** — passes incident replay + policy gates? | seeded incidents, replay matrix, policy-as-code gate |

## Two findings that show the reasoning

The work is more convincing when the findings are honest and non-obvious. Two
examples the implementation produced:

- **Provider vs. local embeddings.** On the synthetic benchmark a hosted OpenAI embedding
  only *ties* the local TF-IDF retrievers — both saturate at 100% hit@3, so the benchmark
  can't tell them apart. On the harder *public* RAG tracks the hosted embedding clearly
  *wins* (WixQA hit@3 98.1% vs 77.5%). The lesson baked into the writeup: a saturated
  benchmark hides real differences; you need a hard enough test to discriminate.

- **Local vs. frontier safety judge.** A free self-hosted `llama3.1:8b` reached 91.7% label
  accuracy vs. 95.8% (`gpt-4.1-mini`) and 100% (`claude-sonnet-4-5`) on a 24-case
  calibration set — but it *under-blocked*, missing 2 unsafe cases the frontier models
  caught, while the frontier model erred toward *over-blocking* a benign one. For a safety
  judge, misses matter more than aggregate accuracy, so the three are reported as
  disagreement slices, not a leaderboard. (One implementation detail: the local model
  initially meta-refused the judging task in prose until output was constrained to JSON.)

## What this implementation covers

The implementation spans:

- **Eval-harness design** — a deterministic, reproducible scoring pipeline with a clean
  agent-agnostic contract and a policy-as-code gate that runs in CI.
- **Safety evaluation** — red-teaming, prompt-injection resistance, abstention/weak-evidence
  handling, approval-gated tool use, and a failure taxonomy across safety/retrieval/
  citation/privacy/tool-use dimensions.
- **LLM-as-judge with calibration** — a multi-provider judge comparison (including a
  self-hosted model) reported as calibrated disagreement, not rankings.
- **RAG evaluation** — grounding, citation accuracy, and abstention measured on both
  synthetic and real public data.
- **Systems / packaging** — a PyPI-published CLI, FastAPI service, Streamlit dashboard,
  Docker/Compose, GitHub Actions CI, GitHub Pages reporting, and OpenTelemetry-style
  observability.

## Honest limitations

- The controlled benchmark is **synthetic** and partly templated — it demonstrates the
  method, not real-world prevalence.
- Human-review labels are currently **simulated**; independent labels are the top open item.
- The judge calibration set is **small (n = 24)** — the judge findings are directional.
- Deterministic, rule-based checks stand in for some behaviors a production system would
  evaluate with more expensive methods.

## Scope

This is a **reference implementation**. There is no roadmap, support commitment, pricing, or
commercial intent, and none is planned. The working infrastructure (service, dashboard,
Docker, exporters) exists to make the design and evidence inspectable end to end — not to be
a product.
