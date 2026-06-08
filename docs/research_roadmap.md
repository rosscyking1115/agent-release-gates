# Research Roadmap

## Public Artifact Goal

Turn the lab into a public benchmark and evaluation harness for AI-agent safety and reliability, with enough transparency for external reviewers to inspect data boundaries, scoring, limitations, and reproducibility.

## Research Question

```text
When do safety interventions improve agent safety, and when do they reduce usefulness on benign operational tasks?
```

## Current Evidence

- Synthetic internal-operations benchmark with retrieval, citation, abstention, extraction, safety, tool-governance, and observability checks.
- Public TechQA retrieval validation using a compact 160-case sample.
- Safety classifier evaluation with false positive / false negative trade-offs, sampled synthetic prevalence, simulated human review, mitigation impact, and threshold decision memo.
- Deterministic release gates, public reports, Docker runtime, CI, Streamlit dashboard, and GitHub Pages site.

## Stage 1: Public Benchmark Hygiene

- Maintain benchmark card and dataset card.
- Keep synthetic and public-data tracks separated.
- Publish clear limitation language.
- Keep report artifacts reproducible from local commands.
- Use GitHub issues for external review requests and benchmark gaps.

## Stage 2: Failure Taxonomy

Attach a formal failure taxonomy to case-level results and report summaries:

- unsafe compliance
- over-refusal
- unsupported answer
- missing citation
- weak evidence treated as strong evidence
- prompt-injection following
- retrieved-document instruction following
- privacy leakage
- tool misuse
- excessive agency

## Stage 3: Human And Judge Reliability

- Add a small human-labeled calibration sample.
- Record reviewer agreement and disagreement notes.
- Compare human review, deterministic rules, and LLM-as-judge on the same cases.
- Report false positives, false negatives, and disagreement slices.
- Document where automatic judging should not be trusted.

## Stage 4: Multi-Model Comparison

- Add optional adapters for provider or local model runs.
- Separate local unpublished runs from public published results.
- Publish result tables only when prompts, model ids, dates, settings, and limitations are recorded.
- Compare safety, usefulness, retrieval grounding, abstention, and tool-use governance under the same harness.

## Stage 5: Safety Intervention Experiments

Compare:

- baseline with no additional guardrail
- refusal policy
- retrieval grounding
- tool approval gate
- secondary review
- classifier threshold settings
- combined mitigations

Report both safety improvements and usefulness costs on benign or ambiguous tasks.

## Stage 6: Paper-Style Report

Prepare a technical report with:

- Abstract
- Motivation
- Method
- Dataset
- Metrics
- Results
- Failure Analysis
- Limitations
- Future Work

The report should produce a finding, not just describe the tool.
