# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
