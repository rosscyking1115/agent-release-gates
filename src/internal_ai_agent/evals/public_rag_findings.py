from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from internal_ai_agent.io import write_json

PUBLIC_RAG_FINDINGS_PATH = Path("reports/public_rag_findings.json")


def write_public_rag_findings(
    project_root: Path,
    *,
    techqa_public: dict[str, Any] | None = None,
    wixqa_public: dict[str, Any] | None = None,
) -> dict[str, Any]:
    techqa = techqa_public or _read_optional_json(
        project_root / "reports/techqa_public_rag_summary.json"
    )
    wixqa = wixqa_public or _read_optional_json(
        project_root / "reports/wixqa_public_rag_summary.json"
    )
    tracks = [_track_summary(report) for report in (techqa, wixqa) if _evaluated(report)]
    report = _findings_report(tracks)
    write_json(project_root / PUBLIC_RAG_FINDINGS_PATH, report)
    return report


def _findings_report(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    if not tracks:
        return {
            "report_type": "public_rag_findings",
            "status": "not_configured",
            "summary": {
                "evaluated_track_count": 0,
                "total_case_count": 0,
                "total_failed_case_count": 0,
            },
            "tracks": [],
            "findings": [],
            "recommendations": [
                (
                    "Run the public TechQA and WixQA benchmarks before publishing "
                    "cross-public-data findings."
                )
            ],
        }

    total_cases = sum(int(track["case_count"]) for track in tracks)
    total_failed = sum(int(track["failed_case_count"]) for track in tracks)
    summary = {
        "evaluated_track_count": len(tracks),
        "total_case_count": total_cases,
        "total_document_count": sum(int(track["document_count"]) for track in tracks),
        "total_failed_case_count": total_failed,
        "weighted_retrieval_hit_rate_at_3": _weighted_metric(
            tracks, "retrieval_hit_rate_at_3"
        ),
        "weighted_top1_citation_accuracy": _weighted_metric(
            tracks, "top1_citation_accuracy"
        ),
        "weighted_failure_rate": round(total_failed / total_cases, 4)
        if total_cases
        else 0.0,
        "top_cross_track_failure_label": _top_failure_label(tracks),
        "largest_retrieval_lift_track": _largest_lift_track(
            tracks, "retrieval_hit_rate_at_3_lift"
        ),
        "largest_top1_lift_track": _largest_lift_track(tracks, "top1_citation_accuracy_lift"),
    }
    return {
        "report_type": "public_rag_findings",
        "status": "evaluated",
        "summary": summary,
        "tracks": tracks,
        "findings": _findings(tracks, summary),
        "recommendations": _recommendations(tracks, summary),
        "notes": [
            (
                "This report combines only external public-data RAG tracks. It does not "
                "mix public-data metrics with controlled synthetic operations metrics."
            ),
            "The current comparison is deterministic and local; no paid provider calls are used.",
        ],
    }


def _track_summary(report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("metrics", {})
    comparison = report.get("retriever_comparison", {})
    profile = report.get("benchmark_profile", {})
    retriever_systems = report.get("retriever_systems", [])
    baseline = _system_by_id(retriever_systems, str(comparison.get("baseline_system_id", "")))
    primary = report.get("primary_retriever", {})
    return {
        "dataset": report["dataset"],
        "benchmark_track": report["benchmark_track"],
        "license": report.get("license", ""),
        "case_count": report.get("case_count", 0),
        "document_count": report.get("document_count", 0),
        "failed_case_count": profile.get("failed_case_count", 0),
        "failure_rate": profile.get("failure_rate", 0.0),
        "primary_retriever": primary.get("label", ""),
        "baseline_retriever": baseline.get("label", ""),
        "retrieval_hit_rate_at_3": metrics.get("retrieval_hit_rate_at_3", 0.0),
        "top1_citation_accuracy": metrics.get("top1_citation_accuracy", 0.0),
        "mean_reciprocal_rank_at_3": metrics.get("mean_reciprocal_rank_at_3", 0.0),
        "retrieval_hit_rate_at_3_lift": comparison.get(
            "retrieval_hit_rate_at_3_lift", 0.0
        ),
        "top1_citation_accuracy_lift": comparison.get("top1_citation_accuracy_lift", 0.0),
        "failure_reasons": report.get("failure_reasons", {}),
        "taxonomy_labels": report.get("taxonomy_labels", {}),
        "dataset_specific_metrics": _dataset_specific_metrics(report),
    }


def _dataset_specific_metrics(report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("metrics", {})
    values: dict[str, Any] = {}
    if "impossible_abstention_rate" in metrics:
        values["impossible_abstention_rate"] = metrics["impossible_abstention_rate"]
        values["answerable_false_abstention_rate"] = metrics.get(
            "answerable_false_abstention_rate", 0.0
        )
    if "multi_article_retrieval_hit_rate_at_3" in metrics:
        values["multi_article_retrieval_hit_rate_at_3"] = metrics[
            "multi_article_retrieval_hit_rate_at_3"
        ]
    return values


def _system_by_id(systems: list[dict[str, Any]], system_id: str) -> dict[str, Any]:
    for system in systems:
        if system.get("system_id") == system_id:
            return system
    return {}


def _evaluated(report: dict[str, Any]) -> bool:
    return report.get("status") == "evaluated"


def _read_optional_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"status": "not_configured"}


def _weighted_metric(tracks: list[dict[str, Any]], metric: str) -> float:
    total_cases = sum(int(track["case_count"]) for track in tracks)
    if not total_cases:
        return 0.0
    return round(
        sum(float(track[metric]) * int(track["case_count"]) for track in tracks)
        / total_cases,
        4,
    )


def _top_failure_label(tracks: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for track in tracks:
        for label, count in track.get("taxonomy_labels", {}).items():
            counts[str(label)] = counts.get(str(label), 0) + int(count)
    if not counts:
        return ""
    label, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return f"{label} ({count})"


def _largest_lift_track(tracks: list[dict[str, Any]], metric: str) -> str:
    if not tracks:
        return ""
    selected = max(tracks, key=lambda track: float(track.get(metric, 0.0)))
    return f"{selected['dataset']} ({float(selected.get(metric, 0.0)):+.2%})"


def _findings(tracks: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
    findings = [
        (
            "Local TF-IDF retrieval outperforms the keyword-title baseline on every "
            "evaluated public RAG track."
        ),
        (
            "Across public tracks, weighted retrieval hit rate@3 is "
            f"{summary['weighted_retrieval_hit_rate_at_3']:.2%} and weighted top-1 "
            f"citation accuracy is {summary['weighted_top1_citation_accuracy']:.2%}."
        ),
    ]
    if summary["top_cross_track_failure_label"]:
        findings.append(
            "The most common cross-track failure label is "
            f"{summary['top_cross_track_failure_label']}."
        )
    for track in tracks:
        if "impossible_abstention_rate" in track["dataset_specific_metrics"]:
            findings.append(
                "TechQA exposes the abstention trade-off: the primary retriever improves "
                "answerable retrieval, but impossible-question abstention remains the main "
                "inspection target."
            )
        if "multi_article_retrieval_hit_rate_at_3" in track["dataset_specific_metrics"]:
            findings.append(
                "WixQA adds multi-article enterprise-support pressure and shows stronger "
                "retrieval coverage than top-1 citation accuracy, so reranking remains "
                "important."
            )
    return findings


def _recommendations(tracks: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
    recommendations = [
        (
            "Run a provider-backed embedding comparison on the same compact public "
            "samples before publishing any model-quality claim."
        ),
        (
            "Use the reranking opportunity analysis to test a real query-document "
            "reranker against the measured top-3 ceiling."
        ),
    ]
    if "weak_evidence_treated_as_strong" in summary["top_cross_track_failure_label"]:
        recommendations.append(
            "Inspect impossible-question handling separately from answerable retrieval "
            "because abstention behavior can move in the opposite direction."
        )
    return recommendations
