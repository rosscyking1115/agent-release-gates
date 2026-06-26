"""Public RAG reranking *opportunity* analysis.

Measures the headroom a perfect reranker could recover on the public RAG tracks
(oracle top-3 rerank ceiling and possible top-1 citation-accuracy lift). It does
NOT run a reranker. Distinct from its similarly-named siblings:
- ``public_rag_reranker`` runs a deterministic reranker and reports actual lift.
- ``public_rag_model_reranker`` is the hosted, model-backed reranker adapter.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json

PUBLIC_RAG_RERANKING_PATH = Path("reports/public_rag_reranking_opportunity.json")


def write_public_rag_reranking_opportunity(project_root: Path) -> dict[str, Any]:
    tracks = [
        _track_opportunity(
            dataset="nvidia/TechQA-RAG-Eval",
            benchmark_track="external_public_rag",
            case_path=project_root / "reports/techqa_public_rag_cases.jsonl",
            answerable_only=True,
        ),
        _track_opportunity(
            dataset="Wix/WixQA expert-written",
            benchmark_track="external_public_enterprise_rag",
            case_path=project_root / "reports/wixqa_public_rag_cases.jsonl",
            answerable_only=False,
        ),
    ]
    evaluated_tracks = [track for track in tracks if track["status"] == "evaluated"]
    report = _report(evaluated_tracks)
    write_json(project_root / PUBLIC_RAG_RERANKING_PATH, report)
    return report


def _track_opportunity(
    *,
    dataset: str,
    benchmark_track: str,
    case_path: Path,
    answerable_only: bool,
) -> dict[str, Any]:
    if not case_path.exists():
        return {
            "dataset": dataset,
            "benchmark_track": benchmark_track,
            "status": "not_configured",
            "case_count": 0,
        }
    rows = read_jsonl(case_path)
    if answerable_only:
        rows = [row for row in rows if not bool(row.get("is_impossible", False))]
    if not rows:
        return {
            "dataset": dataset,
            "benchmark_track": benchmark_track,
            "status": "not_configured",
            "case_count": 0,
        }

    top1_correct = [row for row in rows if bool(row.get("top1_match", False))]
    rerankable = [
        row
        for row in rows
        if _expected_rank(row) is not None and int(_expected_rank(row)) in {2, 3}
    ]
    retrieved_at_3 = [
        row for row in rows if _expected_rank(row) is not None and int(_expected_rank(row)) <= 3
    ]
    not_retrieved = [row for row in rows if _expected_rank(row) is None]
    return {
        "dataset": dataset,
        "benchmark_track": benchmark_track,
        "status": "evaluated",
        "case_count": len(rows),
        "current_top1_correct_count": len(top1_correct),
        "rerankable_case_count": len(rerankable),
        "not_retrieved_case_count": len(not_retrieved),
        "current_top1_citation_accuracy": _rate(len(top1_correct), len(rows)),
        "oracle_top3_rerank_ceiling": _rate(len(retrieved_at_3), len(rows)),
        "possible_top1_lift": _rate(len(rerankable), len(rows)),
        "residual_retrieval_gap": _rate(len(not_retrieved), len(rows)),
        "rerankable_case_examples": _case_examples(rerankable),
        "not_retrieved_case_examples": _case_examples(not_retrieved),
    }


def _report(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    if not tracks:
        return {
            "report_type": "public_rag_reranking_opportunity",
            "status": "not_configured",
            "summary": {
                "evaluated_track_count": 0,
                "total_case_count": 0,
            },
            "tracks": [],
            "findings": [],
            "recommendations": [
                "Run the public RAG benchmarks before publishing reranking opportunity results."
            ],
        }

    total_cases = sum(int(track["case_count"]) for track in tracks)
    total_top1 = sum(int(track["current_top1_correct_count"]) for track in tracks)
    total_rerankable = sum(int(track["rerankable_case_count"]) for track in tracks)
    total_not_retrieved = sum(int(track["not_retrieved_case_count"]) for track in tracks)
    summary = {
        "evaluated_track_count": len(tracks),
        "total_case_count": total_cases,
        "current_top1_correct_count": total_top1,
        "rerankable_case_count": total_rerankable,
        "not_retrieved_case_count": total_not_retrieved,
        "current_weighted_top1_citation_accuracy": _rate(total_top1, total_cases),
        "oracle_top3_rerank_ceiling": _rate(total_top1 + total_rerankable, total_cases),
        "possible_weighted_top1_lift": _rate(total_rerankable, total_cases),
        "residual_retrieval_gap": _rate(total_not_retrieved, total_cases),
        "largest_rerankable_track": _largest_track(tracks, "possible_top1_lift"),
        "largest_residual_gap_track": _largest_track(tracks, "residual_retrieval_gap"),
    }
    return {
        "report_type": "public_rag_reranking_opportunity",
        "status": "evaluated",
        "summary": summary,
        "tracks": tracks,
        "findings": _findings(summary),
        "recommendations": _recommendations(summary),
        "notes": [
            (
                "This is a reranking opportunity analysis, not an oracle production "
                "reranker. It measures the maximum top-1 citation lift available when "
                "the expected public document is already in the top 3."
            ),
            (
                "Residual retrieval gap measures cases a reranker cannot fix because "
                "the expected document was not retrieved into the candidate set."
            ),
        ],
    }


def _findings(summary: dict[str, Any]) -> list[str]:
    return [
        (
            "Across public RAG tracks, top-3 reranking could lift weighted top-1 "
            "citation accuracy from "
            f"{summary['current_weighted_top1_citation_accuracy']:.2%} to "
            f"{summary['oracle_top3_rerank_ceiling']:.2%}."
        ),
        (
            "The current compact public samples contain "
            f"{summary['rerankable_case_count']} rerankable cases and "
            f"{summary['not_retrieved_case_count']} residual retrieval misses."
        ),
        (
            "Reranking is worth testing, but retriever recall still needs separate "
            "work because reranking cannot recover documents outside the candidate set."
        ),
    ]


def _recommendations(summary: dict[str, Any]) -> list[str]:
    recommendations = [
        (
            "Add a query-document reranker over the top-3 or top-5 retrieved public "
            "documents and compare it against this opportunity ceiling."
        ),
        (
            "Track reranking lift separately from retrieval-hit@3 so ranking gains "
            "are not confused with candidate-generation gains."
        ),
    ]
    if float(summary["residual_retrieval_gap"]) > float(summary["possible_weighted_top1_lift"]):
        recommendations.append(
            "Prioritize candidate-generation changes alongside reranking because the "
            "residual retrieval gap is larger than the rerankable top-1 gap."
        )
    return recommendations


def _case_examples(rows: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row.get("case_id", ""),
            "expected_rank": _expected_rank(row),
            "expected_citation_ids": row.get("expected_citation_ids", []),
            "retrieved_citation_ids": row.get("retrieved_citation_ids", []),
            "failure_reasons": row.get("failure_reasons", []),
        }
        for row in rows[:limit]
    ]


def _expected_rank(row: dict[str, Any]) -> int | None:
    rank = row.get("expected_rank")
    if rank is None:
        return None
    return int(rank)


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def _largest_track(tracks: list[dict[str, Any]], metric: str) -> str:
    selected = max(tracks, key=lambda track: float(track.get(metric, 0.0)))
    return f"{selected['dataset']} ({float(selected.get(metric, 0.0)):+.2%})"
