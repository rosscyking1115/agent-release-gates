from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_run_all():
    script_path = Path(__file__).resolve().parents[2] / "scripts/run_all_evals.py"
    spec = importlib.util.spec_from_file_location("run_all_evals", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load run_all_evals.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_all


def test_run_all_evals_generates_reports(tmp_path) -> None:
    run_all = _load_run_all()
    summary = run_all(tmp_path)

    assert summary["dataset_counts"]["runbooks"] == 24
    assert summary["dataset_profile"]["golden_case_mix"]["manual_cases"] == 94
    assert summary["dataset_profile"]["golden_case_mix"]["noise_type_count"] >= 30
    assert summary["comparison"]["case_count"] == 350
    assert summary["retriever_comparison"]["case_count"] == 350
    assert len(summary["retriever_comparison"]["systems"]) == 5
    assert summary["extraction"]["metrics"]["schema_validity"] == 1.0
    assert summary["security"]["metrics"]["improved_safe_rate"] == 1.0
    assert summary["security"]["metrics"]["improved_weighted_safe_rate"] == 1.0
    assert summary["security"]["metrics"]["improved_residual_risk_score"] == 0
    assert summary["security"]["case_count"] == 60
    assert summary["agent"]["metrics"]["side_effect_block_rate"] == 1.0
    assert summary["evaluation_history"]["current_summary"]["best_retriever"] == (
        "Local TF-IDF vector"
    )
    assert len(summary["evaluation_history"]["milestones"]) == 5
    assert summary["collector_export_preview"]["export_mode"] == "dry_run_preview"
    assert summary["collector_export_preview"]["span_count"] > 0
    assert summary["collector_export_preview"]["payload_count"] > 0
    assert (tmp_path / "reports/eval_comparison.json").exists()
    assert (tmp_path / "reports/dataset_profile.json").exists()
    assert (tmp_path / "reports/retriever_comparison.json").exists()
    assert (tmp_path / "reports/retriever_metric_snapshots.json").exists()
    assert (tmp_path / "reports/evaluation_history.json").exists()
    assert (tmp_path / "reports/hybrid_eval_summary.json").exists()
    assert (tmp_path / "reports/vector_eval_summary.json").exists()
    assert (tmp_path / "reports/embedding_eval_summary.json").exists()
    assert (tmp_path / "reports/agent_eval_summary.json").exists()
    assert (tmp_path / "reports/agent_otel_spans.jsonl").exists()
    assert (tmp_path / "reports/observability_otel_spans.jsonl").exists()
    assert (tmp_path / "reports/collector_export_preview.json").exists()
    assert (tmp_path / "reports/evaluation_report.md").exists()
    assert (tmp_path / "reports/evaluation_report.html").exists()
    assert (tmp_path / "reports/evaluation_report.pdf").exists()
    assert (tmp_path / "reports/evaluation_report.pdf").read_bytes().startswith(b"%PDF-1.4")
    assert Path(summary["observability_spans_path"]).name == "observability_otel_spans.jsonl"
    assert Path(summary["public_report_path"]).name == "evaluation_report.md"
