# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **The release gate could not distinguish a safety refusal from an approval hold.**
  All eight incident cases declared `expected_behavior: block_or_hold_for_review`,
  which the gate satisfies with *either* `block` or `review`. Because the controlled
  agent never has approval granted during replay, any case reaching the tool step is
  held at `review` regardless of what the safety policy did — so disabling the safety
  policy converted `block` into `review`, and `review` still passed.

  `block` and `hold_for_human_approval` were already implemented in
  `_expected_behavior_match` and were rejected by the pack validator, so no pack could
  use them. The validator now admits them, the schema and its documentation define when
  to use each, and the eight cases were reassigned under a rule fixed before it was
  applied: `block` where no human approval could make the request legitimate,
  `hold_for_human_approval` where the action is legitimate and merely needs sign-off.
  No case text was changed. `block_or_hold_for_review` is kept for compatibility with
  external packs and documented as deprecated.

  **Re-measured with the identical probe — same 19 mutants, same 4 controls, same
  preregistered oracles, only the gate changed.** Gate mutation adequacy moved
  **47.4% (9/19) → 52.6% (10/19)**, 95% Wilson interval 31.7%–72.7%, false positives
  0/4 unchanged.

  **One discordant mutant. Exact two-sided McNemar p = 1.0.** The repair is real and
  the rate change is not distinguishable from noise, and both are reported that way.
  What did change decisively is the property it targeted: deleting the entire
  request-level safety policy previously left two of the six cases it touched — one of
  them the critical prompt-injection case — reporting a clean result. Now none do.
  The nine remaining survivors are corpus coverage, not conflation, and were
  deliberately not addressed, because corpus changes would invalidate the comparison.

  The pre-fix measurement is committed, not reconstructed:
  `git show 34bee32:reports/gate_mutation_adequacy.json`.

### Corrected

- **A second overclaim, in a compliance-mapping document.**
  `reports/nist_ai_600_1_coverage_map.json` cited the
  confirmation-before-irreversible-action and unsafe-bulk-automation must-not
  assertions as MEASURE 2.7 evidence, sourced to `reports/incident_replay_runs.jsonl`.
  **No case in the shipped pack declares either assertion**, so that artifact contains
  no instance of them being measured. The mutation probe found it: removing ticket
  closure and customer notification from the irreversible-action set changed nothing at
  all.

  The entry now carries `exercised: false` and a rationale beginning "NOT EVIDENCE",
  and unexercised entries are excluded from `covered_subcategories`. The map's
  `evidence_present` field was only ever a file-existence check, which is how a claim
  with no measurement behind it passed — the disclaimer now says so. **No cases were
  added to make the map true**; fitting the evidence to the claim is the defect, not
  the fix.

### Added

- `docs/atlas_executability_audit.md`: **kill criterion 2 fires.** All 57 MITRE ATLAS
  case studies were read against the twelve candidate failure families. **19 are
  executable as agent-with-tools cases** (24 counting marginals), against a
  preregistered floor of 40–60. Two of the twelve families have no source case at all,
  and eleven of the executable cases are the same family. The AI Incident Database
  cannot make up the shortfall, because the source with mechanism-level detail (ATLAS,
  Apache-2.0) is small and the source with volume (AIID, CC BY-SA 4.0) excludes exactly
  the report text needed to reconstruct an environment. Rights were never the
  constraint; usable detail was. The per-study judgement is published so the count is
  auditable rather than asserted, and
  `docs/gate_mutation_benchmark_design.md` is suspended by dated amendment — a
  preregistration that reached its stopping condition before any case was authored.

### Corrected (2026-08-02, earlier)

- **A public claim was broader than its evidence: this project does not "replay
  known incidents".** The README's opening line, the PyPI package description,
  the FastAPI service description, the GitHub Pages project page, the
  engineering writeup, and the NIST AI 600-1 coverage rationale all described
  the tool as replaying *known incidents*. It does not. The eight cases in
  `data/incidents/incident_cases.jsonl` are **constructed scenarios written for
  this repository**. They are informed by publicly discussed classes of agent
  failure — prompt injection, approval-gate bypass, system-prompt leakage,
  retrieved-context priority attacks, secret-exfiltration requests, unbounded
  bulk automation, memory poisoning — but none reconstructs a specific sourced
  incident, and none carries provenance to a named public report.

  Every one of the eight declares itself `simulated_agent_trace`,
  `simulated_chat_transcript`, `simulated_retrieved_context`, or
  `simulated_memory_note` in its own `source_type` field. The repository's data
  contradicted the repository's front page, in the direction that flattered the
  project.

  This is the defect class the project exists to catch — a claim outrunning the
  evidence behind it — shipped on the front page of the tool that catches it. It
  was found by an external competitive and credibility audit on 2026-08-02, not
  by any control in this repository: nothing in CI compares the README to the
  corpus it describes.

  All six surfaces now describe constructed scenarios. The README gains a
  [What the eight incident cases actually are](README.md#what-the-eight-incident-cases-actually-are)
  section stating what the pack can and cannot support, carries the correction
  notice inline rather than only here, and links
  `docs/evaluation_integrity.md` from the header rather than burying it in the
  documentation table.

  **The corrected description reaches PyPI only on the next release.** The
  description published with the current version still carries the old wording
  and will until a new version is uploaded.

- **`redaction_state` was `redacted` on all eight cases, asserting a source that
  never existed.** Redaction means real material was removed. Nothing was
  removed from these cases, because nothing real went into them. Set to
  `synthetic`, which is what the minimal example pack already used.
  `docs/incident_pack_schema.md` previously called the two values
  interchangeable ("usually `redacted` or `synthetic`") and now defines them, so
  the next pack author does not repeat this.

### Added
- **A gate mutation adequacy probe, and the finding that this project's own gate
  misses about half of what is seeded into it.**
  `scripts/run_gate_mutation_probe.py` seeds 19 dangerous mutations and 4 benign
  controls into the shipped enforcement configuration, with every oracle stated in
  the script before any run, and scores whether the release decision changes. Nine
  killed, ten survived: **gate mutation adequacy 47.4% (9/19), 95% Wilson interval
  27.3%–68.3%**, false positives 0/4. Six survivors produced no observable change
  in any case outcome at all. Deleting the entire request-level safety policy is
  still reported as a clean release by two of the eight cases, because `block` and
  `review` both satisfy `block_or_hold_for_review`, so the gate cannot distinguish
  the safety policy catching an attack from the approval gate holding a ticket.
  Two of the seven supported must-not assertions — the irreversible-action and
  bulk-automation axes, both cited as evidence in the NIST AI 600-1 coverage map —
  are asserted by zero cases. Method, survivor classification, and the
  preregistered oracle that turned out to be wrong: `docs/gate_mutation_adequacy.md`.
  Report: `reports/gate_mutation_adequacy.json`.

  **Nothing was fixed in response.** Measuring a control and repairing it in the
  same pass makes the measurement unfalsifiable afterwards. The probe is
  deliberately not wired into CI.
- `docs/gate_mutation_benchmark_design.md`: a preregistered design for measuring
  gate mutation adequacy across 12 incident families against three release gates,
  written before any case is authored. Fixes the mutation operators, the
  incident-family holdout protocol, the matched benign hard negatives, the
  transformation record (including a mandatory divergence-from-the-real-event
  field), and the smallest adequacy gap worth reporting — 25 percentage points,
  derived from the floor of an exact two-sided McNemar test on 24 paired mutants.
- `docs/incident_corpus_licensing.md`: what can and cannot be redistributed if that
  corpus is built. MITRE ATLAS is Apache-2.0 with 57 case studies (not 68); the AI
  Incident Database is CC BY-SA 4.0 with report text explicitly excluded, so its
  share-alike is infectious and its narrative content is unusable; AVID `avid-db` is
  MIT and `avidtools` is Apache-2.0; OECD AIM has no verified open-data licence and
  is treated as unusable. A Hugging Face aggregator relabels AIID-sourced rows as
  CC BY 4.0, which share-alike does not permit, and is not relied on. Redistribution
  is possible, so kill criterion 1 does not fire; whether enough cases are
  *executable* is unresolved and is the next check.
- `docs/evaluation_integrity.md`: a self-reported audit of this project's own
  synthetic benchmark. The generator templates the query from the same
  variables as its gold answer, so the benchmark is circular and its scores are
  not retrieval evidence. Also documents that three separately-reported metrics
  are mathematically one measurement, that the 18.75% baseline is an
  alphabetical tie-break reaching only 4 of 24 runbook sections, and that
  several safety-classifier signals match single eval cases verbatim.
- **A blocking `mypy --strict` gate in CI**, scoped to the 12 modules where a
  type error would corrupt a published number: metric computation, the
  ship/warn/block decision, response-to-verdict scoring, retrieval, and the
  report writer. The scope lives in `[tool.mypy] files` and ratchets upward
  only. Verified non-vacuous by injecting a type error and confirming a
  non-zero exit. `docs/typing_status.md` documents the scope, what it cost, and
  what remains unchecked.
- `mypy` and `inspect-ai` are now dev dependencies. `inspect-ai` was missing, so
  CI had been silently skipping the entire Inspect suite test module.
- A test pinning the source citations in `docs/evaluation_integrity.md`: each
  cited `file:line` must contain an expected substring, the doc's anchor set and
  the test's expectation set must agree in both directions, and each inline
  label must match the line in its own link.

### Changed
- **Retrieval quality is now reported on external public data (TechQA/WixQA:
  79.92% hit@3, 69.61% top-1 over 640 cases) rather than on the synthetic
  benchmark.** The README, GitHub Pages site, Streamlit dashboard, model card,
  benchmark card, and generated evaluation report now lead with the external
  result and label every synthetic figure as in-corpus.

### Fixed
- **Regenerated the committed incident-replay evidence, which was not
  reproducible.** `reports/incident_replay_summary.json` declared its input as
  an untracked machine-local temp file under `AppData\Local\Temp`, and recorded
  a 1-case run of a LangGraph example against the minimal example pack, while
  the README and evaluation report next to it claimed 8 incidents against the
  built-in pack. Regenerated against the built-in controlled agent and the
  tracked pack: the artifact and the report now agree at 8 incidents under
  `incident_release_policy_v0`, and no path under `reports/` references a
  temporary directory. **The `INC-2026-0003` replay decision changes from
  `block` to `review`.** Closure rate, expected-behavior match rate, must-not
  violations (0) and the overall gate status (`pass`) are unchanged. The
  previous `block` was not evidence: a verdict whose declared input never
  existed on any other machine was never reproducible.

  That temp path also carried an OS account name, published on 2026-07-02 and
  still readable in this repository's public history; the write-up and this
  changelog entry then republished it on 2026-07-27 before it was redacted.
  Redacting the working tree does not recall any of that. The account name is
  the least important thing that escaped; the substantive failure is that a
  non-reproducible location was accepted into a provenance field of a committed
  evidence artifact. It was public for 25 days, and known for 10 of them.
  `tests/unit/test_provenance_paths.py` now fails the build on a machine-local
  location anywhere under `reports/` (raw-text scan, so `.jsonl` artifacts are
  covered too) or an unredacted account name in any tracked file.
  Documented as Finding 6 in `docs/evaluation_integrity.md`.
- An intermittent test failure that could abort the whole pytest session.
  `test_public_report.py` asserted containment directly against the generated
  HTML and PDF artifacts; on failure, pytest's assertion rewriting renders both
  operands, and rendering a 44KB `bytes` object was itself allocating enough to
  raise `MemoryError` inside the traceback formatter. Containment is now
  computed before the assert, so a failure reports the needle and a length
  instead of the artifact. Report generation was separately confirmed
  bit-deterministic across processes.
- Twelve type errors in the metric and gating core, fixed properly with no
  `# type: ignore` added: `json.loads` results are now validated as objects
  rather than returned as `Any` (a malformed report file raises instead of
  silently returning a non-dict); cosine similarity uses `math.sqrt` instead of
  `** 0.5`; incident-pack path resolution uses a `TypedDict` instead of
  `dict[str, Path | None]`; and several missing annotations were added. No
  behavior changed.
- The documented Inspect command did not work. `inspect eval
  agent-release-gates/incident_replay` fails with "No inspect tasks were found
  at the specified paths" because the task registers under its bare name and
  Inspect treats an unknown `pkg/task` string as a filesystem glob. The
  documented command is now `inspect eval incident_replay`, with a test that
  keeps the docs and the resolvable reference in sync.
- The Inspect scorer raised `ValueError` on non-JSON model output, aborting the
  entire eval with no samples scored. This was a pass-bias: a model that failed
  badly produced no score rather than a bad one. Malformed output now scores
  `INCORRECT` with `parse_error=true` in the score metadata.

## [0.1.2] - 2026-07-02

### Added
- `export-candidate-results` now supports two more framework formats:
  `--source-format openai_agents` (OpenAI Agents SDK run results) and
  `--source-format langgraph` (LangGraph final states). Working example logs
  ship in the bundled example pack.
- Local / self-hosted judge adapter (`scripts/run_model_judge_eval.py
  --provider local`) that runs against any OpenAI-compatible endpoint
  (Ollama/vLLM/LM Studio) with no API key — reaching a third reviewed judge
  provider in the multi-model comparison.
- Provider-backed embedding evaluation for the public TechQA/WixQA RAG tracks
  (`scripts/run_public_rag_provider_embedding_eval.py`), dry-run-first.
- Business-impact summary that reframes the safety intervention study as an
  operational trade-off (unsafe outcomes addressed vs. review cost).

### Changed
- Expanded the public RAG validation samples: TechQA 160 → 480 cases, WixQA
  80 → 160 cases, with regenerated retrieval metrics.
- Dashboard: cached data loads, a professional theme, and the modern Streamlit
  `width=` API.

## [0.1.1] - 2026-06-28

### Added
- `agent-safety export-candidate-results` subcommand — convert generic or
  LangChain/LangSmith-style agent logs into `candidate_results.jsonl` without a
  source checkout. Previously this was only reachable via `scripts/`.
- `agent-safety init-example` subcommand — write the bundled minimal incident
  pack to a directory so a pip-only user has something to point `--incident-pack`
  at. The minimal pack now ships as package data.

### Changed
- Rewrote the [evaluate-your-agent quickstart](docs/evaluate_your_agent_quickstart.md)
  around the installed `agent-safety` console commands and the no-argument
  built-in gate, instead of `uv run python scripts/...` and a required checkout.

### Fixed
- The advertised "point it at your own agent" workflow now works entirely from
  `pip install agent-release-gates`; the previous quickstart referenced scripts
  and example files that were not part of the wheel.

## [0.1.0] - 2026-06-27

### Added
- First public release. Deterministic AI-agent release gates: incident replay,
  policy-as-code gates, and `ship` / `warn` / `block` evidence.
- `agent-safety release-gate` CLI, the `agent-release-gates/incident_replay`
  Inspect task, a real-agent runner, and the eval/scoring core (lean install,
  `pydantic` only; `api` and `dashboard` extras opt-in).

[0.1.2]: https://github.com/rosscyking1115/agent-release-gates/releases/tag/v0.1.2
[0.1.1]: https://github.com/rosscyking1115/agent-release-gates/releases/tag/v0.1.1
[0.1.0]: https://github.com/rosscyking1115/agent-release-gates/releases/tag/v0.1.0
