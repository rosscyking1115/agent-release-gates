from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
PUBLIC_DIR = PROJECT_ROOT / "public"


def build_public_site(project_root: Path = PROJECT_ROOT) -> Path:
    reports_dir = project_root / "reports"
    public_dir = project_root / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    profile = _read_json(reports_dir / "dataset_profile.json")
    comparison = _read_json(reports_dir / "eval_comparison.json")
    security = _read_json(reports_dir / "security_eval_summary.json")
    collector = _read_json(reports_dir / "collector_export_preview.json")
    trace_index = _read_json(reports_dir / "observability_trace_index.json")
    gates = _read_json(reports_dir / "evaluation_gates.json")
    incident_replay = _read_optional_json(reports_dir / "incident_replay_summary.json")
    incident_release_gates = _read_optional_json(
        reports_dir / "incident_release_gates.json"
    )
    techqa_public = _read_optional_json(reports_dir / "techqa_public_rag_summary.json")
    techqa_profile = _read_optional_json(
        reports_dir / "techqa_public_benchmark_profile.json"
    )
    wixqa_public = _read_optional_json(reports_dir / "wixqa_public_rag_summary.json")
    wixqa_profile = _read_optional_json(
        reports_dir / "wixqa_public_benchmark_profile.json"
    )
    public_rag_findings = _read_optional_json(reports_dir / "public_rag_findings.json")
    public_rag_reranking = _read_optional_json(
        reports_dir / "public_rag_reranking_opportunity.json"
    )
    public_rag_reranker = _read_optional_json(reports_dir / "public_rag_reranker_eval.json")
    public_rag_model_reranker = _read_optional_json(
        reports_dir / "public_rag_model_reranker_adapter_status.json"
    )
    rag_grounding_intervention = _read_optional_json(
        reports_dir / "rag_grounding_intervention.json"
    )
    safety_classifier = _read_json(reports_dir / "safety_classifier_eval_summary.json")
    safety_retuning = _read_json(reports_dir / "safety_threshold_retuning.json")
    safety_review = _read_json(reports_dir / "safety_human_review_simulation.json")
    safety_adjudication = _read_json(reports_dir / "safety_adjudication_notes.json")
    safety_disagreements = _read_json(
        reports_dir / "safety_reviewer_disagreement_slices.json"
    )
    safety_mitigation = _read_json(reports_dir / "safety_mitigation_impact.json")
    safety_operating_recommendation = _read_json(
        reports_dir / "safety_secondary_review_operating_recommendation.json"
    )
    external_review = _read_optional_json(
        reports_dir / "external_human_review_summary.json"
    )
    intervention_study = _read_optional_json(
        reports_dir / "agent_safety_intervention_study.json"
    )
    memory_context_intervention = _read_optional_json(
        reports_dir / "memory_context_intervention.json"
    )
    goal_conflict_intervention = _read_optional_json(
        reports_dir / "goal_conflict_intervention.json"
    )

    shutil.copyfile(reports_dir / "evaluation_report.html", public_dir / "evaluation_report.html")
    shutil.copyfile(reports_dir / "evaluation_report.pdf", public_dir / "evaluation_report.pdf")
    shutil.copyfile(reports_dir / "dataset_profile.json", public_dir / "dataset_profile.json")
    shutil.copyfile(reports_dir / "evaluation_gates.json", public_dir / "evaluation_gates.json")
    shutil.copyfile(
        reports_dir / "safety_classifier_eval_summary.json",
        public_dir / "safety_classifier_eval_summary.json",
    )
    shutil.copyfile(
        reports_dir / "safety_threshold_sweep.json",
        public_dir / "safety_threshold_sweep.json",
    )
    shutil.copyfile(
        reports_dir / "safety_threshold_retuning.json",
        public_dir / "safety_threshold_retuning.json",
    )
    shutil.copyfile(
        reports_dir / "safety_human_review_simulation.json",
        public_dir / "safety_human_review_simulation.json",
    )
    shutil.copyfile(
        reports_dir / "safety_adjudication_notes.json",
        public_dir / "safety_adjudication_notes.json",
    )
    shutil.copyfile(
        reports_dir / "safety_reviewer_disagreement_slices.json",
        public_dir / "safety_reviewer_disagreement_slices.json",
    )
    shutil.copyfile(
        reports_dir / "safety_secondary_review_band_analysis.json",
        public_dir / "safety_secondary_review_band_analysis.json",
    )
    shutil.copyfile(
        reports_dir / "safety_secondary_review_floor_validation.json",
        public_dir / "safety_secondary_review_floor_validation.json",
    )
    shutil.copyfile(
        reports_dir / "safety_secondary_review_operating_recommendation.json",
        public_dir / "safety_secondary_review_operating_recommendation.json",
    )
    shutil.copyfile(
        reports_dir / "safety_mitigation_impact.json",
        public_dir / "safety_mitigation_impact.json",
    )
    shutil.copyfile(
        reports_dir / "safety_threshold_decision_memo.json",
        public_dir / "safety_threshold_decision_memo.json",
    )
    shutil.copyfile(
        reports_dir / "observability_trace_index.json",
        public_dir / "observability_trace_index.json",
    )
    for incident_artifact in [
        "incident_replay_summary.json",
        "incident_replay_runs.jsonl",
        "incident_release_gates.json",
        "incident_response_plan.json",
    ]:
        if (reports_dir / incident_artifact).exists():
            shutil.copyfile(
                reports_dir / incident_artifact,
                public_dir / incident_artifact,
            )
    for stale_memo_path in public_dir.glob("incident_memo_*.md"):
        stale_memo_path.unlink()
    for incident_memo_path in _current_incident_memo_paths(
        project_root,
        incident_replay,
    ):
        shutil.copyfile(
            incident_memo_path,
            public_dir / incident_memo_path.name,
        )
    incident_pack_schema = project_root / "schemas/incident_pack_v1.schema.json"
    if incident_pack_schema.exists():
        shutil.copyfile(
            incident_pack_schema,
            public_dir / incident_pack_schema.name,
        )
    candidate_results_schema = project_root / "schemas/candidate_results_v1.schema.json"
    if candidate_results_schema.exists():
        shutil.copyfile(
            candidate_results_schema,
            public_dir / candidate_results_schema.name,
        )
    if (reports_dir / "external_human_review_summary.json").exists():
        shutil.copyfile(
            reports_dir / "external_human_review_summary.json",
            public_dir / "external_human_review_summary.json",
        )
    if (reports_dir / "external_human_review_manifest.json").exists():
        shutil.copyfile(
            reports_dir / "external_human_review_manifest.json",
            public_dir / "external_human_review_manifest.json",
        )
    if (reports_dir / "multi_model_comparison_plan.json").exists():
        shutil.copyfile(
            reports_dir / "multi_model_comparison_plan.json",
            public_dir / "multi_model_comparison_plan.json",
        )
    if (reports_dir / "model_judge_provider_comparison.json").exists():
        shutil.copyfile(
            reports_dir / "model_judge_provider_comparison.json",
            public_dir / "model_judge_provider_comparison.json",
        )
    for intervention_artifact in [
        "baseline_v1_summary.json",
        "agent_safety_intervention_study.json",
        "instruction_hierarchy_intervention.json",
        "instruction_hierarchy_intervention.md",
        "action_gate_intervention.json",
        "action_gate_intervention.md",
        "safety_classifier_intervention_study.json",
        "safety_classifier_intervention_study.md",
        "memory_context_intervention.json",
        "memory_context_intervention.md",
        "goal_conflict_intervention.json",
        "goal_conflict_intervention.md",
    ]:
        if (reports_dir / intervention_artifact).exists():
            shutil.copyfile(
                reports_dir / intervention_artifact,
                public_dir / intervention_artifact,
            )
    for reviewed_summary_path in reports_dir.glob("model_judge_reviewed_summary*.json"):
        shutil.copyfile(
            reviewed_summary_path,
            public_dir / reviewed_summary_path.name,
        )
    if (project_root / "data/review/external_human_review_packet.csv").exists():
        shutil.copyfile(
            project_root / "data/review/external_human_review_packet.csv",
            public_dir / "external_human_review_packet.csv",
        )
    if (project_root / "data/review/external_human_review_label_template.csv").exists():
        shutil.copyfile(
            project_root / "data/review/external_human_review_label_template.csv",
            public_dir / "external_human_review_label_template.csv",
        )
    if (project_root / "data/review/external_human_review_reviewer_guide.md").exists():
        shutil.copyfile(
            project_root / "data/review/external_human_review_reviewer_guide.md",
            public_dir / "external_human_review_reviewer_guide.md",
        )
    if (reports_dir / "techqa_public_rag_summary.json").exists():
        shutil.copyfile(
            reports_dir / "techqa_public_rag_summary.json",
            public_dir / "techqa_public_rag_summary.json",
        )
    if (reports_dir / "techqa_public_benchmark_profile.json").exists():
        shutil.copyfile(
            reports_dir / "techqa_public_benchmark_profile.json",
            public_dir / "techqa_public_benchmark_profile.json",
        )
    if (reports_dir / "techqa_public_retriever_comparison.json").exists():
        shutil.copyfile(
            reports_dir / "techqa_public_retriever_comparison.json",
            public_dir / "techqa_public_retriever_comparison.json",
        )
    if (reports_dir / "wixqa_public_rag_summary.json").exists():
        shutil.copyfile(
            reports_dir / "wixqa_public_rag_summary.json",
            public_dir / "wixqa_public_rag_summary.json",
        )
    if (reports_dir / "wixqa_public_benchmark_profile.json").exists():
        shutil.copyfile(
            reports_dir / "wixqa_public_benchmark_profile.json",
            public_dir / "wixqa_public_benchmark_profile.json",
        )
    if (reports_dir / "wixqa_public_retriever_comparison.json").exists():
        shutil.copyfile(
            reports_dir / "wixqa_public_retriever_comparison.json",
            public_dir / "wixqa_public_retriever_comparison.json",
        )
    if (reports_dir / "public_rag_findings.json").exists():
        shutil.copyfile(
            reports_dir / "public_rag_findings.json",
            public_dir / "public_rag_findings.json",
        )
    if (reports_dir / "public_rag_reranking_opportunity.json").exists():
        shutil.copyfile(
            reports_dir / "public_rag_reranking_opportunity.json",
            public_dir / "public_rag_reranking_opportunity.json",
        )
    if (reports_dir / "public_rag_reranker_eval.json").exists():
        shutil.copyfile(
            reports_dir / "public_rag_reranker_eval.json",
            public_dir / "public_rag_reranker_eval.json",
        )
    if (reports_dir / "public_rag_model_reranker_adapter_status.json").exists():
        shutil.copyfile(
            reports_dir / "public_rag_model_reranker_adapter_status.json",
            public_dir / "public_rag_model_reranker_adapter_status.json",
        )
    if (reports_dir / "public_rag_model_reranker_packet.jsonl").exists():
        shutil.copyfile(
            reports_dir / "public_rag_model_reranker_packet.jsonl",
            public_dir / "public_rag_model_reranker_packet.jsonl",
        )
    if (reports_dir / "rag_grounding_intervention.json").exists():
        shutil.copyfile(
            reports_dir / "rag_grounding_intervention.json",
            public_dir / "rag_grounding_intervention.json",
        )
    if (reports_dir / "rag_grounding_intervention.md").exists():
        shutil.copyfile(
            reports_dir / "rag_grounding_intervention.md",
            public_dir / "rag_grounding_intervention.md",
        )

    artifact_links = _public_artifact_links(project_root)

    (public_dir / "index.html").write_text(
        _index_html(
            profile=profile,
            comparison=comparison,
            security=security,
            collector=collector,
            trace_index=trace_index,
            gates=gates,
            incident_replay=incident_replay,
            incident_release_gates=incident_release_gates,
            techqa_public=techqa_public,
            techqa_profile=techqa_profile,
            wixqa_public=wixqa_public,
            wixqa_profile=wixqa_profile,
            public_rag_findings=public_rag_findings,
            public_rag_reranking=public_rag_reranking,
            public_rag_reranker=public_rag_reranker,
            public_rag_model_reranker=public_rag_model_reranker,
            rag_grounding_intervention=rag_grounding_intervention,
            safety_classifier=safety_classifier,
            safety_retuning=safety_retuning,
            safety_review=safety_review,
            safety_adjudication=safety_adjudication,
            safety_disagreements=safety_disagreements,
            safety_mitigation=safety_mitigation,
            safety_operating_recommendation=safety_operating_recommendation,
            external_review=external_review,
            intervention_study=intervention_study,
            memory_context_intervention=memory_context_intervention,
            goal_conflict_intervention=goal_conflict_intervention,
            artifact_links=artifact_links,
        ),
        encoding="utf-8",
    )
    (public_dir / "artifacts.html").write_text(
        _artifact_index_html(artifact_links),
        encoding="utf-8",
    )
    return public_dir


def _index_html(
    *,
    profile: dict[str, Any],
    comparison: dict[str, Any],
    security: dict[str, Any],
    collector: dict[str, Any],
    trace_index: dict[str, Any],
    gates: dict[str, Any],
    incident_replay: dict[str, Any],
    incident_release_gates: dict[str, Any],
    techqa_public: dict[str, Any],
    techqa_profile: dict[str, Any],
    wixqa_public: dict[str, Any],
    wixqa_profile: dict[str, Any],
    public_rag_findings: dict[str, Any],
    public_rag_reranking: dict[str, Any],
    public_rag_reranker: dict[str, Any],
    public_rag_model_reranker: dict[str, Any],
    rag_grounding_intervention: dict[str, Any],
    safety_classifier: dict[str, Any],
    safety_retuning: dict[str, Any],
    safety_review: dict[str, Any],
    safety_adjudication: dict[str, Any],
    safety_disagreements: dict[str, Any],
    safety_mitigation: dict[str, Any],
    safety_operating_recommendation: dict[str, Any],
    external_review: dict[str, Any],
    intervention_study: dict[str, Any],
    memory_context_intervention: dict[str, Any],
    goal_conflict_intervention: dict[str, Any],
    artifact_links: list[tuple[str, str, str]],
) -> str:
    counts = profile["dataset_counts"]
    mix = profile["golden_case_mix"]
    metrics = comparison["metrics"]
    security_metrics = security["metrics"]
    safety_metrics = safety_classifier["metrics"]
    safety_prevalence = safety_classifier["weighted_prevalence"]
    incident_summary = incident_replay.get("summary", {})
    incident_gate_status = _display_status(
        incident_summary.get(
            "release_gate_status",
            incident_release_gates.get("overall_status", "not_configured"),
        )
    )
    external_status = _display_status(external_review.get("status", "not_configured"))
    intervention_count = intervention_study.get("experiment_count", 0)
    memory_summary = memory_context_intervention.get("summary", {})
    goal_summary = goal_conflict_intervention.get("summary", {})
    grounding_summary = rag_grounding_intervention.get("summary", {})
    risk_labels = "\n".join(
        f"<li>{escape(_humanize_label(label))}</li>" for label in profile["risk_labels"]
    )
    recommendations = "\n".join(
        f"<li>{escape(item)}</li>" for item in profile["recommended_next_data_work"]
    )
    artifact_count = len(artifact_links)
    repo_url = "https://github.com/rosscyking1115/agent-release-gates"
    streamlit_url = "https://agent-release-gates.streamlit.app/"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Release Safety Gates</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5f6b7a;
      --line: #d8dee8;
      --panel: #f7f9fc;
      --accent: #0f766e;
      --accent-2: #b42318;
      --bg: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 48px 0 64px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 28px;
      margin-bottom: 28px;
    }}
    h1 {{
      font-size: clamp(2rem, 5vw, 4.5rem);
      line-height: 1.02;
      margin: 0 0 18px;
      letter-spacing: 0;
    }}
    h2 {{
      font-size: 1.35rem;
      margin: 32px 0 12px;
    }}
    p {{
      max-width: 780px;
      margin: 0 0 14px;
      color: var(--muted);
    }}
    a {{ color: var(--accent); font-weight: 650; }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 22px;
    }}
    .button {{
      border: 1px solid var(--accent);
      color: var(--accent);
      border-radius: 6px;
      padding: 10px 14px;
      text-decoration: none;
      background: #ffffff;
    }}
    .button.primary {{
      background: var(--accent);
      color: #ffffff;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 12px;
      margin: 18px 0 28px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: var(--panel);
      min-height: 96px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 0.92rem;
      margin-bottom: 6px;
    }}
    .metric strong {{
      display: block;
      font-size: 1.55rem;
      line-height: 1.2;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin: 18px 0 28px;
    }}
    .summary-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: var(--panel);
    }}
    .summary-card h3 {{
      margin: 0 0 8px;
      font-size: 1rem;
    }}
    .summary-card p {{
      margin: 0;
      color: var(--muted);
    }}
    .section {{
      border-top: 1px solid var(--line);
      padding-top: 22px;
      margin-top: 26px;
    }}
    ul {{
      margin: 8px 0 0;
      padding-left: 20px;
      color: var(--muted);
    }}
    .artifact-list {{
      columns: 2;
      column-gap: 36px;
      max-width: 900px;
    }}
    .artifact-list li {{
      break-inside: avoid;
      margin-bottom: 8px;
    }}
    @media (max-width: 720px) {{
      .artifact-list {{
        columns: 1;
      }}
    }}
    code {{
      background: #edf2f7;
      border-radius: 4px;
      padding: 2px 5px;
    }}
    .warning {{
      border-left: 4px solid var(--accent-2);
      padding: 12px 14px;
      background: #fff7f5;
      color: var(--ink);
      margin-top: 18px;
      max-width: 900px;
    }}
    details {{
      max-width: 940px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
      background: var(--panel);
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Agent Release Safety Gates</h1>
      <p>
        A public release-readiness harness for measuring AI-agent reliability
        across incident replay, grounded retrieval, safe refusal,
        approval-gated mock tools, safety/usefulness trade-offs, audit events,
        and observability.
      </p>
      <p>
        This project does not reproduce, evaluate, or criticize any real
        company's internal AI system. All data, teams, tickets, runbooks,
        controlled benchmark metrics, and workflows are synthetic. TechQA and
        WixQA results are separate public-data RAG benchmarks.
      </p>
      <div class="actions">
        <a class="button primary" href="{streamlit_url}">Open Interactive Dashboard</a>
        <a class="button primary" href="evaluation_report.html">Open Full Report</a>
        <a class="button" href="evaluation_report.pdf">Download PDF</a>
        <a class="button" href="{repo_url}">GitHub Repo</a>
      </div>
    </header>

    <section>
      <h2>At a glance</h2>
      <div class="summary-grid">
        <div class="summary-card">
          <h3>What it is</h3>
          <p>
            A reproducible benchmark and dashboard for evaluating incident
            replay, grounded retrieval, safe refusal, approval-gated tools,
            and auditability in AI-agent workflows.
          </p>
        </div>
        <div class="summary-card">
          <h3>Why it matters</h3>
          <p>
            Agent safety work needs mitigation-aware measurement that reports
            both unsafe misses and usefulness costs, not only a single headline
            safety score.
          </p>
        </div>
        <div class="summary-card">
          <h3>Evidence available</h3>
          <p>
            Controlled synthetic operations tests are paired with public TechQA
            and WixQA RAG validation, safety trade-off analysis, and release
            gates.
          </p>
        </div>
        <div class="summary-card">
          <h3>Validation boundary</h3>
          <p>
            The controlled operations benchmark is synthetic. Independent human
            labels and broader multi-model comparison are the next validation
            steps.
          </p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Key findings</h2>
      <div class="summary-grid">
        <div class="summary-card">
          <h3>Safety needs trade-off reporting</h3>
          <p>
            Unsafe-request capture is useful only when reviewed alongside
            benign blocks, review load, weak-evidence handling, and false
            negative risk.
          </p>
        </div>
        <div class="summary-card">
          <h3>Public RAG checks strengthen the lab</h3>
          <p>
            TechQA and WixQA results show that retrieval evaluation is not
            limited to the controlled synthetic environment.
          </p>
        </div>
        <div class="summary-card">
          <h3>Intervention evidence</h3>
          <p>
            The current study compares frozen baseline behavior against layered
            safeguards for prompt injection, action gating, and safety
            classification.
          </p>
        </div>
        <div class="summary-card">
          <h3>Goal-conflict arbitration</h3>
          <p>
            The lab now measures when agents should redirect user goals that
            conflict with safety, evidence, privacy, or tool-risk boundaries.
          </p>
        </div>
        <div class="summary-card">
          <h3>Incident replay</h3>
          <p>
            Redacted synthetic incidents are replayed as regression tests before
            a release gate can pass.
          </p>
        </div>
        <div class="summary-card">
          <h3>Auditability is part of reliability</h3>
          <p>
            The project publishes release gates, trace summaries, and generated
            artifacts so reviewers can inspect how results were produced.
          </p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Evidence snapshot</h2>
      <div class="grid">
        {_metric("Synthetic golden cases", counts["golden_cases"])}
        {_metric("Red-team cases", counts["red_team_cases"])}
        {_metric("Intervention experiments", intervention_count)}
        {_metric("Incident replay cases", incident_replay.get("case_count", "Not configured"))}
        {_metric(
            "Incident closure rate",
            _incident_replay_metric(incident_replay, "incident_closure_rate"),
        )}
        {_metric("Incident gate status", incident_gate_status)}
        {_metric("Manual golden-case share", _pct(mix["manual_share"]))}
        {_metric(
            "Public RAG cases",
            _public_rag_summary_value(public_rag_findings, "total_case_count"),
        )}
        {_metric(
            "Public weighted RAG@3",
            _public_rag_metric(public_rag_findings, "weighted_retrieval_hit_rate_at_3"),
        )}
        {_metric("TechQA public RAG@3", _techqa_metric(techqa_public, "retrieval_hit_rate_at_3"))}
        {_metric("WixQA public RAG@3", _wixqa_metric(wixqa_public, "retrieval_hit_rate_at_3"))}
        {_metric(
            "Moderate grounding unsupported",
            _rag_grounding_metric(
                rag_grounding_intervention,
                "moderate_unsupported_answer_rate",
            ),
        )}
        {_metric(
            "Strict grounding review / 100",
            grounding_summary.get("strict_review_burden_per_100", "Not available"),
        )}
        {_metric("Synthetic citation coverage", _pct(metrics["citation_coverage"]["improved"]))}
        {_metric("Synthetic abstention accuracy", _pct(metrics["abstention_accuracy"]["improved"]))}
        {_metric(
            "Memory pollution follow rate",
            _memory_context_metric(
                memory_context_intervention,
                "scoped_review_polluted_memory_follow_rate",
            ),
        )}
        {_metric(
            "Memory review / 100",
            memory_summary.get(
                "scoped_review_review_burden_per_100_cases",
                "Not configured",
            ),
        )}
        {_metric(
            "Goal conflict unsafe compliance",
            _goal_conflict_metric(
                goal_conflict_intervention,
                "layered_unsafe_goal_compliance_rate",
            ),
        )}
        {_metric(
            "Goal conflict review / 100",
            goal_summary.get(
                "layered_review_burden_per_100_cases",
                "Not configured",
            ),
        )}
        {_metric("Safety classifier recall", _pct(safety_metrics["recall"]))}
        {_metric(
            "High-severity unsafe misses",
            safety_metrics["high_severity_false_negative_count"],
        )}
        {_metric("Synthetic unsafe prevalence", _pct(safety_prevalence["unsafe_prevalence"]))}
        {_metric("Red-team safe response rate", _pct(security_metrics["improved_safe_rate"]))}
        {_metric("Indexed observability traces", trace_index["trace_count"])}
        {_metric("Release gate status", _display_status(gates["overall_status"]))}
        {_metric("External review status", external_status)}
      </div>
      <p>
        These are engineering checks over controlled benchmarks. They should be
        read with the benchmark cards, dataset boundaries, and full report.
      </p>
    </section>

    <section class="section">
      <h2>Explore the project</h2>
      <div class="summary-grid">
        <div class="summary-card">
          <h3>Interactive dashboard</h3>
          <p>
            Explore metrics, cases, safety analysis, retrieval comparisons, and
            observability views in Streamlit.
          </p>
          <p><a href="{streamlit_url}">Open dashboard</a></p>
        </div>
        <div class="summary-card">
          <h3>Full evaluation report</h3>
          <p>
            Read the deeper method, metrics, limitations, and generated
            evaluation narrative.
          </p>
          <p><a href="evaluation_report.html">Open report</a></p>
        </div>
        <div class="summary-card">
          <h3>Evaluate your agent</h3>
          <p>
            Convert generic agent logs or LangChain/LangSmith traces into
            candidate results, then run the incident replay release gate.
          </p>
          <p>
            <a href="{repo_url}/blob/main/docs/evaluate_your_agent_quickstart.md">
              Open quickstart
            </a>
          </p>
        </div>
        <div class="summary-card">
          <h3>Reviewer handoff</h3>
          <p>
            Inspect the external-review packet, labelling workflow, and
            reviewer-facing instructions.
          </p>
          <p>
            <a href="{repo_url}/blob/main/docs/reviewer_handoff_pack.md">
              Open reviewer handoff
            </a>
          </p>
        </div>
        <div class="summary-card">
          <h3>Technical artifacts</h3>
          <p>
            View {artifact_count} generated JSON, CSV, report, and reproducibility
            artifacts on a separate technical page.
          </p>
          <p><a href="artifacts.html">Open artifact index</a></p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Benchmark transparency</h2>
      <p>
        High scores on synthetic cases are useful only when the benchmark mix is
        visible. This project keeps the synthetic benchmark, public RAG tracks,
        and remaining validation gaps separate.
      </p>
      <details>
        <summary>Current benchmark-quality labels</summary>
        <ul>{risk_labels}</ul>
      </details>
      <details>
        <summary>Recommended next data work</summary>
        <ul>{recommendations}</ul>
      </details>
    </section>

    <section class="section">
      <h2>Run locally</h2>
      <p>
        The FastAPI service and dashboard are containerized so the full stack
        can be run from the public repository.
      </p>
      <p><code>docker compose up --build</code></p>
      <p>
        Then open <code>http://localhost:8510</code> for the dashboard and
        <code>http://localhost:8000/health</code> for the API.
      </p>
    </section>
  </main>
</body>
</html>
"""


def _public_artifact_links(project_root: Path = PROJECT_ROOT) -> list[tuple[str, str, str]]:
    artifact_links = [
        ("Primary reports", "Full evaluation report", "evaluation_report.html"),
        ("Primary reports", "PDF evaluation report", "evaluation_report.pdf"),
        ("Primary reports", "Evaluation gates", "evaluation_gates.json"),
        ("Intervention study", "Baseline v1 summary", "baseline_v1_summary.json"),
        (
            "Intervention study",
            "Agent safety intervention study",
            "agent_safety_intervention_study.json",
        ),
        (
            "Intervention study",
            "Instruction hierarchy intervention",
            "instruction_hierarchy_intervention.json",
        ),
        (
            "Intervention study",
            "Instruction hierarchy report",
            "instruction_hierarchy_intervention.md",
        ),
        (
            "Intervention study",
            "Action gate intervention",
            "action_gate_intervention.json",
        ),
        (
            "Intervention study",
            "Action gate report",
            "action_gate_intervention.md",
        ),
        (
            "Intervention study",
            "Safety classifier intervention study",
            "safety_classifier_intervention_study.json",
        ),
        (
            "Intervention study",
            "Safety classifier intervention report",
            "safety_classifier_intervention_study.md",
        ),
        (
            "Intervention study",
            "Memory context intervention study",
            "memory_context_intervention.json",
        ),
        (
            "Intervention study",
            "Memory context intervention report",
            "memory_context_intervention.md",
        ),
        (
            "Intervention study",
            "Goal conflict intervention study",
            "goal_conflict_intervention.json",
        ),
        (
            "Intervention study",
            "Goal conflict intervention report",
            "goal_conflict_intervention.md",
        ),
        ("Benchmark profile", "Dataset profile", "dataset_profile.json"),
        ("Public RAG", "TechQA public RAG summary", "techqa_public_rag_summary.json"),
        (
            "Public RAG",
            "TechQA public benchmark profile",
            "techqa_public_benchmark_profile.json",
        ),
        (
            "Public RAG",
            "TechQA public retriever comparison",
            "techqa_public_retriever_comparison.json",
        ),
        ("Public RAG", "WixQA public RAG summary", "wixqa_public_rag_summary.json"),
        (
            "Public RAG",
            "WixQA public benchmark profile",
            "wixqa_public_benchmark_profile.json",
        ),
        (
            "Public RAG",
            "WixQA public retriever comparison",
            "wixqa_public_retriever_comparison.json",
        ),
        ("Public RAG", "Cross-public RAG findings", "public_rag_findings.json"),
        (
            "Public RAG",
            "Public RAG reranking opportunity",
            "public_rag_reranking_opportunity.json",
        ),
        ("Public RAG", "Public RAG reranker evaluation", "public_rag_reranker_eval.json"),
        (
            "Public RAG",
            "RAG grounding intervention study",
            "rag_grounding_intervention.json",
        ),
        ("Public RAG", "RAG grounding intervention report", "rag_grounding_intervention.md"),
        (
            "Public RAG",
            "Hosted public RAG reranker adapter",
            "public_rag_model_reranker_adapter_status.json",
        ),
        ("Public RAG", "Hosted reranker packet", "public_rag_model_reranker_packet.jsonl"),
        (
            "Model comparison",
            "Multi-model comparison plan",
            "multi_model_comparison_plan.json",
        ),
        (
            "Model comparison",
            "Reviewed provider comparison",
            "model_judge_provider_comparison.json",
        ),
        (
            "Model comparison",
            "Reviewed OpenAI judge summary",
            "model_judge_reviewed_summary.json",
        ),
        (
            "Model comparison",
            "Reviewed Anthropic judge summary",
            "model_judge_reviewed_summary_anthropic.json",
        ),
        (
            "Safety evaluation",
            "Safety classifier summary",
            "safety_classifier_eval_summary.json",
        ),
        ("Safety evaluation", "Safety threshold sweep", "safety_threshold_sweep.json"),
        (
            "Safety evaluation",
            "Safety threshold retuning",
            "safety_threshold_retuning.json",
        ),
        (
            "Safety evaluation",
            "Safety human review simulation",
            "safety_human_review_simulation.json",
        ),
        (
            "Safety evaluation",
            "Safety adjudication notes",
            "safety_adjudication_notes.json",
        ),
        (
            "Safety evaluation",
            "Safety reviewer disagreement slices",
            "safety_reviewer_disagreement_slices.json",
        ),
        (
            "Safety evaluation",
            "Safety secondary review-band analysis",
            "safety_secondary_review_band_analysis.json",
        ),
        (
            "Safety evaluation",
            "Safety secondary review-floor validation",
            "safety_secondary_review_floor_validation.json",
        ),
        (
            "Safety evaluation",
            "Safety secondary review operating recommendation",
            "safety_secondary_review_operating_recommendation.json",
        ),
        ("Safety evaluation", "Safety mitigation impact", "safety_mitigation_impact.json"),
        (
            "Safety evaluation",
            "Safety threshold decision memo",
            "safety_threshold_decision_memo.json",
        ),
        (
            "Human review",
            "External human review summary",
            "external_human_review_summary.json",
        ),
        (
            "Human review",
            "External human review manifest",
            "external_human_review_manifest.json",
        ),
        ("Human review", "External review packet", "external_human_review_packet.csv"),
        (
            "Human review",
            "External review label template",
            "external_human_review_label_template.csv",
        ),
        ("Human review", "External reviewer guide", "external_human_review_reviewer_guide.md"),
        ("Observability", "Observability trace index", "observability_trace_index.json"),
        ("Incident replay", "Incident replay summary", "incident_replay_summary.json"),
        ("Incident replay", "Incident replay runs", "incident_replay_runs.jsonl"),
        ("Incident replay", "Incident release gates", "incident_release_gates.json"),
        ("Incident replay", "Incident response plan", "incident_response_plan.json"),
        ("Incident replay", "Incident pack schema", "incident_pack_v1.schema.json"),
        (
            "Incident replay",
            "Candidate results schema",
            "candidate_results_v1.schema.json",
        ),
    ]
    incident_replay = _read_optional_json(
        project_root / "reports/incident_replay_summary.json"
    )
    for memo_path in _current_incident_memo_paths(project_root, incident_replay):
        incident_id = memo_path.stem.replace("incident_memo_", "")
        artifact_links.append(
            (
                "Incident replay",
                f"Incident memo {incident_id}",
                memo_path.name,
            )
        )
    return artifact_links


def _current_incident_memo_paths(
    project_root: Path,
    incident_replay: dict[str, Any],
) -> list[Path]:
    reports_dir = (project_root / "reports").resolve()
    memo_paths = incident_replay.get("memo_paths", [])
    if not isinstance(memo_paths, list):
        return []

    current_paths: list[Path] = []
    for memo_path in memo_paths:
        if not isinstance(memo_path, str):
            continue
        path = (project_root / memo_path).resolve()
        if (
            path.parent == reports_dir
            and path.name.startswith("incident_memo_")
            and path.suffix == ".md"
            and path.exists()
        ):
            current_paths.append(path)
    return sorted(current_paths)


def _artifact_index_html(artifact_links: list[tuple[str, str, str]]) -> str:
    grouped: dict[str, list[tuple[str, str]]] = {}
    for category, label, href in artifact_links:
        grouped.setdefault(category, []).append((label, href))

    sections = "\n".join(
        f"""
        <section class="section">
          <h2>{escape(category)}</h2>
          <ul>
            {"".join(
                f'<li><a href="{escape(href)}">{escape(label)}</a></li>'
                for label, href in links
            )}
          </ul>
        </section>
        """
        for category, links in grouped.items()
    )

    repo_url = "https://github.com/rosscyking1115/agent-release-gates"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Technical Artifacts - Agent Release Safety Gates</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5f6b7a;
      --line: #d8dee8;
      --panel: #f7f9fc;
      --accent: #0f766e;
      --bg: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      width: min(980px, calc(100% - 32px));
      margin: 0 auto;
      padding: 42px 0 64px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 24px;
      margin-bottom: 24px;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3.5rem);
      line-height: 1.06;
      margin: 0 0 14px;
      letter-spacing: 0;
    }}
    h2 {{
      font-size: 1.15rem;
      margin: 0 0 10px;
    }}
    p {{
      max-width: 760px;
      margin: 0 0 14px;
      color: var(--muted);
    }}
    a {{ color: var(--accent); font-weight: 650; }}
    .section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 16px;
      margin: 14px 0;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
      columns: 2;
      column-gap: 32px;
      color: var(--muted);
    }}
    li {{
      break-inside: avoid;
      margin-bottom: 8px;
    }}
    @media (max-width: 720px) {{
      ul {{ columns: 1; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p><a href="index.html">Back to project overview</a></p>
      <h1>Technical Artifact Index</h1>
      <p>
        Generated reports and machine-readable outputs for reviewers who want
        to inspect the evidence behind the public summary.
      </p>
      <p>
        Source documentation lives in the
        <a href="{repo_url}/tree/main/docs">repository docs folder</a>.
      </p>
    </header>
    {sections}
  </main>
</body>
</html>
"""


def _metric(label: str, value: object) -> str:
    escaped_label = escape(label)
    escaped_value = escape(str(value))
    return (
        '<div class="metric">'
        f"<span>{escaped_label}</span>"
        f"<strong>{escaped_value}</strong>"
        "</div>"
    )


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return _read_json(path)
    return {"status": "not_configured", "metrics": {}}


def _techqa_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("metrics", {}).get(metric, 0.0)))


def _techqa_profile_value(report: dict[str, Any], key: str) -> object:
    summary = report.get("summary", {})
    if not summary or summary.get("status") != "evaluated":
        return "Not configured"
    return summary.get(key, "Not configured")


def _wixqa_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("metrics", {}).get(metric, 0.0)))


def _wixqa_profile_value(report: dict[str, Any], key: str) -> object:
    summary = report.get("summary", {})
    if not summary or summary.get("status") != "evaluated":
        return "Not configured"
    return summary.get(key, "Not configured")


def _public_rag_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("summary", {}).get(metric, 0.0)))


def _rag_grounding_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("summary", {}).get(metric, 0.0)))


def _memory_context_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("summary", {}).get(metric, 0.0)))


def _goal_conflict_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("summary", {}).get(metric, 0.0)))


def _incident_replay_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("summary", {}).get(metric, 0.0)))


def _public_rag_summary_value(report: dict[str, Any], key: str) -> object:
    if report.get("status") != "evaluated":
        return "Not configured"
    return report.get("summary", {}).get(key, "Not configured")


def _public_reranking_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    return _pct(float(report.get("summary", {}).get(metric, 0.0)))


def _public_reranking_summary_value(report: dict[str, Any], key: str) -> object:
    if report.get("status") != "evaluated":
        return "Not configured"
    return report.get("summary", {}).get(key, "Not configured")


def _public_reranker_signed_metric(report: dict[str, Any], metric: str) -> str:
    if report.get("status") != "evaluated":
        return "Not configured"
    value = float(report.get("summary", {}).get(metric, 0.0))
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"


def _hosted_reranker_status(report: dict[str, Any]) -> str:
    status = str(report.get("status", "not_configured"))
    return _display_status(status)


def _hosted_reranker_case_count(report: dict[str, Any]) -> object:
    if report.get("status") == "not_configured":
        return "Not available"
    return report.get("candidate_case_count", 0)


def _display_status(status: object) -> str:
    labels = {
        "awaiting_labels": "Awaiting independent labels",
        "dry_run_ready": "Ready for credentialed run",
        "dry_run_preview": "Prepared preview",
        "not_configured": "Not available",
        "not_published": "Not yet published",
        "pass_with_warnings": "Pass with warnings",
        "pass": "Pass",
        "warn": "Warning",
        "blocking": "Blocking",
        "non_blocking": "Non-blocking",
        "completed": "Completed",
        "evaluated": "Evaluated",
    }
    value = str(status)
    if "_" not in value:
        return labels.get(value, value)
    return labels.get(value, value.replace("_", " ").title())


def _humanize_label(label: str) -> str:
    labels = {
        "provider_backed_embedding_comparison_not_covered": (
            "Provider-backed embedding comparison is available as an optional "
            "credentialed run but is not published yet."
        ),
        "real_company_data_intentionally_excluded": (
            "Real company data is intentionally excluded; synthetic and public "
            "benchmarks are reported separately."
        ),
    }
    return labels.get(label, label.replace("_", " ").capitalize())


if __name__ == "__main__":
    output_dir = build_public_site()
    print(f"Public site written to {output_dir}")
