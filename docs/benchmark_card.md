# Benchmark Card

## Name

Agent Release Safety Gates

## Purpose

This benchmark measures whether an AI-agent workflow is grounded, safe, useful, access-aware, auditable, and reproducible. It focuses on failure modes that appear in retrieval-augmented and tool-using agents:

- weak or missing evidence
- unsupported answers
- unsafe compliance
- over-refusal
- prompt injection
- retrieved-document instruction following
- approval-gate bypass
- tool misuse
- privacy leakage
- excessive agency

## Research Question

```text
When do safety interventions improve agent safety, and when do they reduce usefulness on benign operational tasks?
```

## Current Tracks

| Track | Status | Data source |
| --- | --- | --- |
| Controlled synthetic operations retrieval | Implemented | Local synthetic runbooks and golden cases |
| Structured ticket extraction | Implemented | Local synthetic tickets |
| Red-team safety cases | Implemented | Local synthetic risk cases |
| Safety classifier and prevalence evaluation | Implemented | Local synthetic challenge, validation, and sampled prevalence cases |
| Approval-gated mock tool use | Implemented | Local controlled-agent cases |
| Observability and release gates | Implemented | Local trace, audit, and report artifacts |
| Public TechQA retrieval validation | Implemented | 160-case compact NVIDIA TechQA-RAG-Eval sample |
| Public WixQA retrieval validation | Implemented | 80-case compact WixQA expert-written sample |
| Maintainer-labeled calibration | Implemented | 24-case calibration sample |
| External human-review packet | Implemented | Review packet and label template prepared; labels awaiting independent reviewers |
| Local rubric judge reliability | Implemented | Deterministic judge baseline against maintainer labels |
| Hosted model-judge adapters | Implemented | Dry-run-first OpenAI Responses API and Anthropic Messages API adapters |
| Reviewed hosted model-judge result | Implemented | gpt-4.1-mini calibration run published with one reviewed over-refusal limitation |
| Independent human review labels | Planned | To be collected and reported separately from maintainer labels |
| Multi-model comparison | In progress | OpenAI result reviewed; Anthropic adapter available but not yet run |
| Hosted LLM-as-judge reliability | Implemented | One reviewed OpenAI judge run; Anthropic adapter available for the next credentialed run |

## Current Metrics

The implemented benchmark reports retrieval hit rate, citation coverage, abstention accuracy, structured extraction validity, red-team safe response rate, safety-classifier precision and recall, false positive / false negative trade-offs, sampled synthetic prevalence, human-review queue simulation, side-effect block rate, approval audit rate, trace coverage, release-gate status, public TechQA retrieval metrics, and public WixQA retrieval metrics.

## Intended Use

Use this benchmark to:

- compare retrieval and abstention strategies under a fixed evaluation contract
- inspect safety and usefulness trade-offs before adding stochastic model providers
- test approval-gated tool-use governance
- review failure cases rather than only headline scores
- reproduce public report artifacts locally

## Out Of Scope

This benchmark should not be used as evidence of real production performance, real unsafe-request prevalence, or the quality of any real company's internal AI system. The controlled synthetic operations track is a test domain, not a real enterprise dataset.

## Known Limitations

- Synthetic cases are still partly templated.
- Human-review labels are simulated and deterministic; the external-review packet is prepared, but independent labels are not yet published.
- Public TechQA uses a compact 160-case sample, not the full upstream dataset.
- Public WixQA uses a compact 80-case expert-written sample, not the full upstream benchmark suite.
- Provider-backed embeddings and multi-model results are not yet published.
- Deterministic rules make the benchmark reproducible but do not replace adversarial human review.

## Reproducibility

Run:

```powershell
uv run python scripts/run_all_evals.py
uv run python scripts/build_public_site.py
uv run pytest
```

The generated report artifacts are written to `reports/` and `site/`.
