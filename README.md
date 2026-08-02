# Agent Release Safety Gates

Before shipping software, teams run a check that blocks the release if something is
broken. This project builds that check for AI agents — and then asks whether the check
itself can be trusted.

**The question.** If someone quietly weakened the safety rules inside the gate, would the
gate notice? Or would it keep saying *ship*?

**The answer.** Usually it would not notice. Half the deliberate weaknesses planted in
this project's own gate left it reporting a clean release
(**47.4%** caught, 9 of 19; 95% interval 27.3–68.3%).

[![PyPI](https://img.shields.io/pypi/v/agent-release-gates.svg)](https://pypi.org/project/agent-release-gates/)
[![Python](https://img.shields.io/pypi/pyversions/agent-release-gates.svg)](https://pypi.org/project/agent-release-gates/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/rosscyking1115/agent-release-gates/blob/main/LICENSE)
[![CI](https://github.com/rosscyking1115/agent-release-gates/actions/workflows/ci.yml/badge.svg)](https://github.com/rosscyking1115/agent-release-gates/actions/workflows/ci.yml)

<img src="https://raw.githubusercontent.com/rosscyking1115/agent-release-gates/main/docs/img/dashboard.png" alt="The reviewer dashboard: release-gate status, case counts, safety recall, and a metrics comparison table" width="820">

<sub>The reviewer dashboard — one screen showing whether a change may ship.
<a href="https://agent-release-gates.streamlit.app/">Open it live →</a></sub>

> **Status: concluded, not maintained.** A reference implementation and a research
> result, not a product. The research programme behind it was closed by its own stopping
> criterion — [see below](#the-result). There is no roadmap and no support commitment.
> Released under the [MIT Licence](https://github.com/rosscyking1115/agent-release-gates/blob/main/LICENSE).

## What this is for

Agents regress quietly. A prompt tweak, a model swap, or a loosened tool permission can
reintroduce a failure you already fixed, and unlike a crashing web service, an unsafe
agent still returns a fluent answer. Web services solved the analogous problem with
release gates in CI. This applies that idea to agent safety: replay a pack of safety
scenarios against a changed agent, apply thresholds kept in a config file, and emit
`ship` / `warn` / `block` with a non-zero exit code.

Read it if you build agent evaluation or release tooling, or if you want a worked example
of a project measuring — and publishing — the limits of its own instrument.

**Related work.** Several tools fail a build on evaluation thresholds: promptfoo,
DeepEval, Giskard, and `release-gate` among them. What none of them published, at the time
of the survey below, is a measurement of whether the gate notices its own rules being
weakened. That measurement is the contribution here; the gate itself is ordinary.
Upstream companion: [redteam-foundry](https://github.com/rosscyking1115/redteam-foundry).

## Try it

```bash
pip install agent-release-gates
```

```bash
agent-safety release-gate
```

That replays the built-in pack and exits non-zero on a block. To score your own agent,
convert its logs and gate them — see the
[quickstart](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/evaluate_your_agent_quickstart.md).

To reproduce the finding you need the repository, since the probe is a script rather than
part of the installed package:

```bash
git clone https://github.com/rosscyking1115/agent-release-gates && cd agent-release-gates
```

```bash
uv sync && uv run python scripts/run_gate_mutation_probe.py
```

No network access, no API keys, no cost.

## The result

**Gate mutation adequacy** is the measurement: seed a semantically meaningful defect into
the gate's own configuration — delete a rule, loosen a threshold, reroute a tool, reword a
signal to a synonym — and see whether the release decision changes. The fraction that
changes it is the score.

This gate scored **47.4% (9 of 19)**, with 0 false alarms across 4 controls that changed
the policy without weakening it.

The cause was a specific, nameable design defect. The gate's expected outcome was
satisfied by *either* a refusal *or* a hold for human approval — and because the agent
never receives approval during replay, anything that reached the tool step was held
anyway. Deleting the **entire** safety rule set still left the critical prompt-injection
case reporting clean, because the approval hold absorbed the difference.

Splitting those two outcomes apart fixed that specific hole: no case now survives deletion
of the safety rules. It moved the headline score to 52.6% — **one mutant, McNemar
p = 1.0, which is not distinguishable from noise**, and is reported as such rather than
banked.

**The generalisation, which outlives this repository:** any release gate whose expected
outcome is satisfied by both a refusal and a hold cannot measure whether its safety layer
works. Remove the refusing layer and the holding layer absorbs the difference, so every
case still passes and every metric stays green.

**The programme was then closed by its own kill criterion.** Scaling this across tools
needed 40–60 executable incident-derived cases; reading all 57 MITRE ATLAS case studies
produced 19. Rights were never the constraint — the source with mechanism-level detail is
small, and the source with volume withholds the detail.

→ [**The full finding**](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/finding_gate_mutation_adequacy.md), with method, controls,
and limits.

## Why the result is trustworthy

- **Every mutant declared its oracle before it ran** — which rule it weakens, and why the
  gate ought to react — committed in the script ahead of any result.
- **One of those oracles was wrong.** It claimed a rule was a case's only protection when
  a second rule also caught it. It is left in the script as written and reported as wrong.
- **A positive control** rules out "the probe detects nothing": disabling the approval
  hold outright is caught by three gates at once.
- **The before measurement is committed, not reconstructed** —
  `git show 34bee32:reports/gate_mutation_adequacy.json`.
- **Limits, plainly.** Nineteen hand-authored mutants are not a random sample, so the
  interval flatters itself. Eight cases, one candidate, one policy file. No other tool was
  measured. Four controls cannot establish a false-alarm rate.

## What is in this repository

| | |
| --- | --- |
| **The finding** | [finding_gate_mutation_adequacy.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/finding_gate_mutation_adequacy.md) |
| **Evaluation integrity** — this project's audit of its own benchmark | [evaluation_integrity.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/evaluation_integrity.md) |
| Measured results, and what produces them | [results.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/results.md) |
| What the eight incident cases are | [incident_cases.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/incident_cases.md) |
| Why the benchmark programme was closed | [atlas_executability_audit.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/atlas_executability_audit.md) |
| A packaging defect, generalised | [finding_gitignore_not_a_packaging_control.md](https://github.com/rosscyking1115/agent-release-gates/blob/main/docs/finding_gitignore_not_a_packaging_control.md) |
| Design rationale, schemas, cards, house style | [docs/](https://github.com/rosscyking1115/agent-release-gates/tree/main/docs/) |
| The probe, the runners, the release gate | [scripts/](https://github.com/rosscyking1115/agent-release-gates/tree/main/scripts/), [src/](https://github.com/rosscyking1115/agent-release-gates/tree/main/src/internal_ai_agent/) |

Also here: an Inspect (UK AISI) task, a FastAPI evidence service, the Streamlit dashboard
above, Docker, and CI.

## Limitations

- **The incident pack is constructed, not sourced** — eight scenarios written for this
  repository. Nothing here measures coverage of a real incident population.
- **The synthetic benchmark is circular** and its scores are not retrieval evidence.
  Retrieval is reported on external public data instead.
- `mypy --strict` covers the 12 modules where a type error would corrupt a published
  number, not the whole package.
- Human-review labels are simulated; independent reviewer labels are prepared, not
  published.

All benchmark data is synthetic. This project does not reproduce or assess any
organisation's internal AI system. Feedback via
[issues](https://github.com/rosscyking1115/agent-release-gates/issues).
