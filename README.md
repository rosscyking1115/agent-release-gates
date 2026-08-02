# Agent Release Safety Gates

> A release gate for AI agents that asks a research question about release gates:
> **if a gate's own safety policy were quietly weakened, would the gate notice?**
> It seeds semantically meaningful defects into its own enforcement configuration —
> deleted rules, loosened thresholds, rerouted tools, reworded signals — and measures
> how many of them change the release decision.

[![PyPI](https://img.shields.io/pypi/v/agent-release-gates.svg)](https://pypi.org/project/agent-release-gates/)
[![Python](https://img.shields.io/pypi/pyversions/agent-release-gates.svg)](https://pypi.org/project/agent-release-gates/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/rosscyking1115/agent-release-gates/blob/main/LICENSE)
[![CI](https://github.com/rosscyking1115/agent-release-gates/actions/workflows/ci.yml/badge.svg)](https://github.com/rosscyking1115/agent-release-gates/actions/workflows/ci.yml)

> **Two-repo stack** — downstream companion of
> [redteam-foundry](https://github.com/rosscyking1115/redteam-foundry), which audits the
> benchmarks whose challenge packs these gates consume. Full project map →
> [profile](https://github.com/rosscyking1115).

## The finding

A negative result about this project's own gate, reported rather than buried.

**Gate mutation adequacy — the fraction of seeded safety-policy defects that cause the
release gate to fail — measured 47.4% (9 of 19), 95% Wilson interval 27.3%–68.3%,**
with 0 false positives over 4 benign controls. Roughly half of the defects seeded into the
shipped enforcement configuration left the gate reporting a clean release.

A landscape survey of NeMo Guardrails, Guardrails AI, Lakera, LLM Guard, Rebuff, promptfoo,
Giskard, DeepEval, garak, PyRIT, Inspect and `release-gate` found no published systematic
policy-mutation programme. Mutating the *attack* is well established — WalledEval ships
prompt mutators, JailGuard varies mutation policies, red-team suites gate builds on
attack-success rate. Mutating the *defense* is the gap.

### The design defect

The gate's expected outcome, `block_or_hold_for_review`, was satisfied by **both** a
refusal and a hold for human approval. The controlled agent never receives approval during
replay, so anything reaching the tool step is held at `review` regardless of what the
safety policy did.

Deleting the **entire** request-level safety policy — every phrase signal, every
sensitive-data target — still left the critical prompt-injection case reporting a clean
result. The gate could not distinguish *"the safety policy caught this attack"* from
*"the approval gate happened to hold this ticket."*

### After the fix

Splitting the expected outcome into `block` and `hold_for_human_approval` and re-running
the **identical** probe — same 19 mutants, same 4 controls, same preregistered oracles,
only the gate changed:

| | Before | After |
| --- | --- | --- |
| Gate mutation adequacy | **47.4% (9/19)** | **52.6% (10/19)** |
| 95% Wilson interval | 27.3%–68.3% | 31.7%–72.7% |
| False positives | 0/4 | 0/4 |

**One discordant mutant. Exact two-sided McNemar p = 1.0.** The 5.3 points are not banked:
the repair is real, the rate change is not distinguishable from noise. What did move
completely is the property it targeted — **no case now survives deletion of the safety
policy**, where two did before.

The nine remaining survivors are corpus coverage, not gate design. On a clean run every
`max_*` gate observes 0 and every `min_*` gate observes 1.0, so no threshold in the policy
is under any tension, and two of the seven supported must-not assertions are declared by
zero cases.

### The generalization

**Any release gate whose expected outcome is satisfied by both a refusal and a hold cannot
measure whether its safety layer works.** The two outcomes have different causes and the
same score. Remove the refusing layer and the holding layer absorbs the difference, so
every case still passes and every metric stays green. The defect is invisible in normal
operation and appears only when something deliberately deletes the layer doing the work.

### The programme this closed

The measurement above was the pilot for a larger study: twelve incident families against
three release gates, preregistered before any case was authored. It was **closed by its own
kill criterion**.

All 57 MITRE ATLAS case studies were read against the twelve families. **Nineteen are
executable as agent-with-tools cases** (24 counting marginals), against a preregistered
floor of 40–60. Two families have no source case at all. The AI Incident Database cannot
make up the shortfall: its licence covers the structured records and explicitly excludes
the report text needed to reconstruct an environment. **The source with mechanism-level
detail is small; the source with volume withholds the detail.** Rights were never the
constraint.

Full write-up, including the per-study judgements:
[**the finding**](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/finding_gate_mutation_adequacy.md)
· [ATLAS executability audit](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/atlas_executability_audit.md)

## Why the result is trustworthy

A number this project produced about itself is easy to distrust. The measurement is built
so it can be audited, and so it says how far to trust it.

- **Every mutant declares its oracle before it runs.** Which obligation it weakens, and
  why the intact gate ought to react, are committed in the probe script ahead of any
  result. One preregistered oracle turned out to be **wrong** — it claimed a phrase was a
  case's only pre-tool control when a second rule also caught it. It is left in the probe
  as written and reported as wrong, because rewriting an oracle after seeing the result is
  how a mutation study becomes a demonstration.
- **A positive control rules out "the probe detects nothing".** Making side-effecting tools
  execute despite requiring approval and not having it — the literal failure two cases
  assert — is caught by three gates at once, both before and after the fix.
- **Benign controls measure the false-positive side.** Four mutants change the policy
  without weakening any obligation. None produced a spurious block. Four controls cannot
  establish a false-positive rate; the interval reaches 49%, and that is stated rather
  than rounded to "zero".
- **The before measurement is committed, not reconstructed.** It was published at
  `34bee32` before anything was repaired, and every "before" figure can be read back with
  `git show 34bee32:reports/gate_mutation_adequacy.json`.
- **State leaking between mutants fails loudly.** After each mutant the intact baseline is
  recomputed and compared.

**Limits, stated plainly.** Nineteen hand-authored mutants are not a random sample from an
enumerated population, so the binomial interval flatters a quantity it cannot really bound.
Eight cases, one candidate, one policy file — most of what is reported is a property of
that pack. No other tool was measured; the survey establishes that the measurement is not
published elsewhere, not how anything else would score. A ±19-point interval cannot
separate this gate from a superficial rule checker, which is this project's own
preregistered kill criterion 3, and it is met.

## Numbers in this repository that saturate

Nine metrics in `reports/agent_eval_summary.json` sit at exactly 1.0, and three more sit
at 1.0 in the incident-replay summary. They are reported here with what produces them,
because a table of 100% figures is a warning sign, not a result.

| Metric | Why it is 1.0 |
| --- | --- |
| `side_effect_block_rate`, `approved_action_execution_rate` | The eval runs the same deterministic agent twice, once with approval withheld and once granted, and checks it blocked then executed. This confirms a boolean is wired up; nothing resists anything. |
| `approval_audit_rate`, `audit_event_coverage_rate`, `trace_coverage_rate`, `monitoring_snapshot_rate` | The controlled agent emits these unconditionally on every run. |
| `valid_tool_call_rate`, `approval_trigger_rate`, `route_tool_selection_accuracy` | Properties of the deterministic tool layer, not of a model under stress. |
| `expected_behavior_match_rate`, `incident_closure_rate`, `trace_event_coverage_rate` | The metrics the mutation probe showed could stay at 1.0 with the entire request-level safety policy deleted. |

Treat these as conformance checks that the harness is wired correctly. **They are not
evidence that a safety mechanism works**, and the gate-mutation result above is the
demonstration of exactly that.

## The measured results

Retrieval quality is reported on **external public corpora**, never on the synthetic
benchmark this project generates itself.

| Area | Result |
| --- | --- |
| **Retrieval (external, headline)** | **79.92% hit rate@3, 69.61% top-1 citation accuracy** over 640 public cases (NVIDIA TechQA + Wix WixQA, 510 documents) |
| **Largest external failure mode** | **40.47% case failure rate; 85 impossible questions answered instead of abstained** |
| Retrieval (in-corpus fixture) | 99.31–100% on 358 self-generated cases. **Not a retrieval result**: the generator templates the query from its own gold answer |
| Safety classifier | 90.91% recall, 0 high-severity false negatives — measured with case-specific signals still in place, not re-measured since they were identified, and expected to fall when they are removed |
| Multi-model judge comparison | Local `llama3.1:8b` 91.67% label accuracy vs 95.83% (`gpt-4.1-mini`) and 100% (`claude-sonnet-4-5`) on 24 calibration cases; the local judge missed 2 unsafe cases the frontier models caught |

**The same retriever drops ~20 points the moment it leaves the corpus its own generator
wrote.** That gap is the point of the exercise, and the external number is the one
reported.

**This project's synthetic benchmark is circular**, and that is published as a finding
rather than quietly dropped: the generator builds the query from the same
`{category}`/`{system}` variables as the gold answer, three separately-reported metrics
are mathematically one measurement, and the 18.75% "baseline" is an alphabetical tie-break.
See
[evaluation integrity](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/evaluation_integrity.md),
which the rest of this README is written to be consistent with.

## What the eight incident cases are

**Constructed scenarios written for this repository.** Each declares itself in its own
`source_type` field — `simulated_agent_trace`, `simulated_chat_transcript`,
`simulated_retrieved_context`, `simulated_memory_note`. The failure *classes* are real and
widely reported: prompt injection, approval-gate bypass, system-prompt leakage,
retrieved-context priority attacks, secret-exfiltration requests, unbounded bulk
automation, memory poisoning. The *situations* are invented.

They exist to make the gate testable end to end without network access, API keys or
third-party data. They do not support any claim that this gate would catch a given
real-world incident, any coverage claim over a real incident population, or any ranking of
models. An incident-derived corpus with per-case provenance was designed and then
abandoned when its own kill criterion fired, above.

*Until 2026-08-02 this README described the tool as replaying "known incidents". It does
not, and that claim is retracted — see the
[changelog](https://github.com/rosscyking1115/agent-release-gates/blob/main/CHANGELOG.md).*

## What is in the repository

- **The mutation probe** (`scripts/run_gate_mutation_probe.py`): 19 dangerous mutants and
  4 benign controls with oracles fixed in advance, no network access, no API keys.
- **The release gate**: incident replay, policy-as-code thresholds, `ship`/`warn`/`block`
  with a non-zero CLI exit code, regression fixtures and generated memos.
- **Candidate-results exporters** for generic agent logs, LangChain/LangSmith traces,
  OpenAI Agents SDK results and LangGraph states, so an external agent can be scored
  without running its code.
- **Evaluation runners** for retrieval, extraction, safety classification, controlled-agent
  behavior and observability, plus baseline-vs-intervention studies for instruction
  hierarchy, action-risk gates, RAG grounding, memory/context pollution and goal conflict.
- **An Inspect (UK AISI) task**, a FastAPI evidence service, a Streamlit reviewer
  dashboard, Docker and CI.

<div align="center">
<img src="https://raw.githubusercontent.com/rosscyking1115/agent-release-gates/main/docs/img/dashboard.png" alt="The reviewer dashboard showing release-gate status, case counts, safety recall, and a baseline-versus-improved metrics table" width="760">
<br><sub>The reviewer dashboard. <a href="https://agent-release-gates.streamlit.app/">Open it live →</a></sub>
</div>

## Getting started

```bash
pip install agent-release-gates
```

```bash
# Run the deterministic release gate on the built-in pack. Exits non-zero on a block.
agent-safety release-gate
```

```bash
# Reproduce the headline finding. No network, no API keys.
python scripts/run_gate_mutation_probe.py
```

Score an external agent by converting its logs and gating them:

```bash
agent-safety init-example --dest incident_pack_minimal
agent-safety export-candidate-results --input incident_pack_minimal/agent_run_log.jsonl --output candidate_results.jsonl --candidate-id my_agent_v1
agent-safety release-gate --incident-pack incident_pack_minimal --candidate-results candidate_results.jsonl
```

Run the eight constructed cases as an Inspect (UK AISI) task against a real model:

```bash
pip install inspect_ai
```

```bash
inspect eval incident_replay --model openai/gpt-4.1-mini
```

The core install depends only on `pydantic`. The service and dashboard are opt-in:

```bash
pip install "agent-release-gates[api]"
```

```bash
pip install "agent-release-gates[dashboard]"
```

Run from source with `uv sync`, then `uv run python scripts/run_all_evals.py` to regenerate
every report deterministically. Full workflow:
[evaluate an agent](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/evaluate_your_agent_quickstart.md).

## Documentation

| Topic | Link |
| --- | --- |
| **The finding (standalone)** | [finding_gate_mutation_adequacy.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/finding_gate_mutation_adequacy.md) |
| **Evaluation integrity (read first)** | [evaluation_integrity.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/evaluation_integrity.md) |
| A global gitignore is not a packaging control | [finding_gitignore_not_a_packaging_control.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/finding_gitignore_not_a_packaging_control.md) |
| Mutation method and per-mutant record | [gate_mutation_adequacy.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/gate_mutation_adequacy.md) |
| Benchmark design (preregistered, suspended) | [gate_mutation_benchmark_design.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/gate_mutation_benchmark_design.md) |
| ATLAS executability audit | [atlas_executability_audit.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/atlas_executability_audit.md) |
| Incident corpus licensing | [incident_corpus_licensing.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/incident_corpus_licensing.md) |
| Engineering writeup (design rationale) | [engineering_writeup.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/engineering_writeup.md) |
| Incident pack / candidate results schemas | [incident_pack_schema.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/incident_pack_schema.md) · [candidate_results_schema.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/candidate_results_schema.md) |
| Benchmark card · dataset card · failure taxonomy | [benchmark_card.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/benchmark_card.md) · [dataset_card.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/dataset_card.md) · [failure_taxonomy.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/failure_taxonomy.md) |
| Static typing status | [typing_status.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/typing_status.md) |
| Reviewer handoff pack | [reviewer_handoff_pack.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/reviewer_handoff_pack.md) |

## Limitations

- **The incident pack is constructed, not sourced.** Nothing here measures coverage of a
  real incident population.
- **The synthetic benchmark is circular** and its scores are not retrieval evidence. It is
  kept as a deterministic regression fixture only.
- Public TechQA and WixQA tracks use compact samples, not the full upstream datasets.
- The Inspect incident-replay task is 8 constructed samples: a conformance smoke check that
  cannot rank models.
- `mypy --strict` is enforced on the 12 modules where a type error would corrupt a
  published number. The other ~61 package modules are unchecked and are not claimed to be
  checked.
- Human-review labels are simulated workflow labels; independent reviewer labels are
  prepared but not published.
- The multi-model judge comparison covers three providers on a 24-case calibration set.

## Scope and ethics

This is a **reference implementation, not a maintained product**. There is no roadmap,
support commitment, or commercial intent. The mutation programme is closed; the natural
next steps toward production — independent human labeling, a broader judge comparison,
expanded public RAG validation, further framework exporters — are listed to show where this
implementation deliberately stops, not as a plan.

All data, teams, tickets, runbooks and workflows in the controlled benchmark are synthetic.
This project does not reproduce, assess, or reverse-engineer any organization's internal AI
system. TechQA and WixQA are used separately as public retrieval-validation datasets under
their own terms. Results are engineering evidence over controlled benchmarks and are not
claims of real-world production performance. No regulatory-compliance claim is made; the
NIST AI 600-1 map in this repository is an evidence-alignment aid and says so.

Feedback and technical discussion are welcome via
[issues](https://github.com/rosscyking1115/agent-release-gates/issues). Released under the
[MIT License](https://github.com/rosscyking1115/agent-release-gates/blob/main/LICENSE).
