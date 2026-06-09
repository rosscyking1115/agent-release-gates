# Technical Artifact Index

This page is for reviewers who want to inspect generated metrics, benchmark profiles, safety workflow outputs, and reproducibility files. The README and GitHub Pages homepage intentionally keep the public story concise.

## Primary Reports

- Public project page: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/
- Full evaluation report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.html
- PDF evaluation report: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_report.pdf
- Evaluation gates: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/evaluation_gates.json

## Benchmark Documentation

- Benchmark card: benchmark_card.md
- Dataset card: dataset_card.md
- Failure taxonomy: failure_taxonomy.md
- Research roadmap: research_roadmap.md
- External reviewer handoff pack: reviewer_handoff_pack.md
- Contributing guide: ../CONTRIBUTING.md
- Dataset profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/dataset_profile.json

## Public RAG Validation

- TechQA public RAG summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_rag_summary.json
- TechQA public benchmark profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_benchmark_profile.json
- TechQA public retriever comparison: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/techqa_public_retriever_comparison.json
- WixQA public RAG summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/wixqa_public_rag_summary.json
- WixQA public benchmark profile: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/wixqa_public_benchmark_profile.json
- WixQA public retriever comparison: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/wixqa_public_retriever_comparison.json
- Cross-public RAG findings: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/public_rag_findings.json
- Public RAG reranking opportunity: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/public_rag_reranking_opportunity.json
- Public RAG reranker evaluation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/public_rag_reranker_eval.json
- Hosted public RAG reranker adapter status: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/public_rag_model_reranker_adapter_status.json
- Hosted reranker packet: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/public_rag_model_reranker_packet.jsonl

## Safety Evaluation

- Safety classifier summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_classifier_eval_summary.json
- Safety threshold sweep: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_threshold_sweep.json
- Safety threshold retuning: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_threshold_retuning.json
- Safety human review simulation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_human_review_simulation.json
- Safety adjudication notes: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_adjudication_notes.json
- Safety reviewer disagreement slices: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_reviewer_disagreement_slices.json
- Safety secondary review-band analysis: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_secondary_review_band_analysis.json
- Safety secondary review-floor validation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_secondary_review_floor_validation.json
- Safety secondary review operating recommendation: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_secondary_review_operating_recommendation.json
- Safety mitigation impact: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_mitigation_impact.json
- Safety threshold decision memo: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/safety_threshold_decision_memo.json

## Model Comparison

- Multi-model comparison plan: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/multi_model_comparison_plan.json

## Human Review Packet

- External human review protocol: external_human_review_protocol.md
- External review packet: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_packet.csv
- External review label template: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_label_template.csv
- External reviewer guide: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_reviewer_guide.md
- External review manifest: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_manifest.json
- External human review summary: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/external_human_review_summary.json

## Observability

- Observability trace index: https://rosscyking1115.github.io/internal-ai-agent-eval-lab/observability_trace_index.json

## Local Regeneration

```powershell
uv run python scripts/run_all_evals.py
uv run python scripts/build_public_site.py
```
