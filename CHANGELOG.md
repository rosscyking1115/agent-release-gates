# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
  `C:/Users/leaff/AppData/Local/Temp/lg.jsonl` — an untracked machine-local
  temp file — and recorded a 1-case run of a LangGraph example against the
  minimal example pack, while the README and evaluation report next to it
  claimed 8 incidents against the built-in pack. Regenerated against the
  built-in controlled agent and the tracked pack: the artifact and the report
  now agree at 8 incidents under `incident_release_policy_v0`, and no path
  under `reports/` references a temporary directory. **The `INC-2026-0003`
  replay decision changes from `block` to `review`.** Closure rate,
  expected-behavior match rate, must-not violations (0) and the overall gate
  status (`pass`) are unchanged. The previous `block` was not evidence: a
  verdict whose declared input never existed on any other machine was never
  reproducible. Documented as Finding 6 in `docs/evaluation_integrity.md`.
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
