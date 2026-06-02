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

    shutil.copyfile(reports_dir / "evaluation_report.html", public_dir / "evaluation_report.html")
    shutil.copyfile(reports_dir / "evaluation_report.pdf", public_dir / "evaluation_report.pdf")
    shutil.copyfile(reports_dir / "dataset_profile.json", public_dir / "dataset_profile.json")

    (public_dir / "index.html").write_text(
        _index_html(
            profile=profile,
            comparison=comparison,
            security=security,
            collector=collector,
        ),
        encoding="utf-8",
    )
    return public_dir


def _index_html(
    *,
    profile: dict[str, Any],
    comparison: dict[str, Any],
    security: dict[str, Any],
    collector: dict[str, Any],
) -> str:
    counts = profile["dataset_counts"]
    mix = profile["golden_case_mix"]
    metrics = comparison["metrics"]
    security_metrics = security["metrics"]
    risk_labels = "\n".join(
        f"<li>{escape(label)}</li>" for label in profile["risk_labels"]
    )
    recommendations = "\n".join(
        f"<li>{escape(item)}</li>" for item in profile["recommended_next_data_work"]
    )
    repo_url = "https://github.com/rosscyking1115/internal-ai-agent-eval-lab"
    streamlit_url = "https://agent-evaluation-lab.streamlit.app/"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Internal AI Agent Evaluation Lab</title>
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
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Internal AI Agent Evaluation Lab</h1>
      <p>
        A public synthetic lab for evaluating internal AI agent reliability across
        grounded retrieval, structured extraction, safety refusals,
        approval-gated mock tools, audit events, and observability.
      </p>
      <p>
        This project does not reproduce, evaluate, or criticize any real
        company's internal AI system. All data, teams, tickets, runbooks,
        metrics, and workflows are synthetic.
      </p>
      <div class="actions">
        <a class="button primary" href="{streamlit_url}">Open Interactive Dashboard</a>
        <a class="button primary" href="evaluation_report.html">Open Full Report</a>
        <a class="button" href="evaluation_report.pdf">Download PDF</a>
        <a class="button" href="dataset_profile.json">Dataset Profile JSON</a>
        <a class="button" href="{repo_url}">GitHub Repo</a>
      </div>
    </header>

    <section>
      <h2>Current Synthetic Benchmark</h2>
      <div class="grid">
        {_metric("Runbook sections", counts["runbooks"])}
        {_metric("Synthetic tickets", counts["tickets"])}
        {_metric("Golden cases", counts["golden_cases"])}
        {_metric("Red-team cases", counts["red_team_cases"])}
        {_metric("Manual golden cases", mix["manual_cases"])}
        {_metric("Manual share", _pct(mix["manual_share"]))}
        {_metric("Expected abstentions", mix["expected_abstentions"])}
        {_metric("Noise types", mix["noise_type_count"])}
      </div>
    </section>

    <section class="section">
      <h2>Evaluation Snapshot</h2>
      <div class="grid">
        {_metric("Baseline citation coverage", _pct(metrics["citation_coverage"]["baseline"]))}
        {_metric("Improved citation coverage", _pct(metrics["citation_coverage"]["improved"]))}
        {_metric("Improved abstention accuracy", _pct(metrics["abstention_accuracy"]["improved"]))}
        {_metric("Improved red-team safe rate", _pct(security_metrics["improved_safe_rate"]))}
        {_metric("Collector spans", collector["span_count"])}
        {_metric("Collector payloads", collector["payload_count"])}
      </div>
    </section>

    <section class="section">
      <h2>Benchmark Gaps Are Visible</h2>
      <p>
        The lab reports benchmark-quality risks alongside model and retriever
        scores. That is deliberate: high scores on synthetic data are only useful
        when the data mix is inspectable.
      </p>
      <div class="warning">
        <strong>Current data-quality labels</strong>
        <ul>{risk_labels}</ul>
      </div>
      <h2>Recommended Next Data Work</h2>
      <ul>{recommendations}</ul>
    </section>

    <section class="section">
      <h2>Use The Interactive Lab</h2>
      <p>
        The Streamlit dashboard is deployed publicly for exploration. The
        FastAPI service and dashboard are also containerized so the full stack
        can be run locally from the public repo.
      </p>
      <p><a href="{streamlit_url}">Open the public Streamlit dashboard</a></p>
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


if __name__ == "__main__":
    output_dir = build_public_site()
    print(f"Public site written to {output_dir}")
