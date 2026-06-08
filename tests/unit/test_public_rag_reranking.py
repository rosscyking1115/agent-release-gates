from pathlib import Path

from internal_ai_agent.evals.public_rag_reranking import (
    write_public_rag_reranking_opportunity,
)
from internal_ai_agent.io import write_jsonl


def test_public_rag_reranking_writes_not_configured_report(tmp_path: Path) -> None:
    report = write_public_rag_reranking_opportunity(tmp_path)

    assert report["status"] == "not_configured"
    assert report["summary"]["evaluated_track_count"] == 0
    assert (tmp_path / "reports/public_rag_reranking_opportunity.json").exists()


def test_public_rag_reranking_summarizes_top3_opportunity(tmp_path: Path) -> None:
    write_jsonl(
        tmp_path / "reports/techqa_public_rag_cases.jsonl",
        [
            _case("TECH-1", rank=1, is_impossible=False),
            _case("TECH-2", rank=2, is_impossible=False),
            _case("TECH-3", rank=None, is_impossible=False),
            _case("TECH-4", rank=None, is_impossible=True),
        ],
    )
    write_jsonl(
        tmp_path / "reports/wixqa_public_rag_cases.jsonl",
        [
            _case("WIX-1", rank=1),
            _case("WIX-2", rank=3),
            _case("WIX-3", rank=None),
        ],
    )

    report = write_public_rag_reranking_opportunity(tmp_path)

    summary = report["summary"]
    assert report["status"] == "evaluated"
    assert summary["evaluated_track_count"] == 2
    assert summary["total_case_count"] == 6
    assert summary["current_top1_correct_count"] == 2
    assert summary["rerankable_case_count"] == 2
    assert summary["not_retrieved_case_count"] == 2
    assert summary["current_weighted_top1_citation_accuracy"] == 0.3333
    assert summary["oracle_top3_rerank_ceiling"] == 0.6667
    assert summary["possible_weighted_top1_lift"] == 0.3333
    assert summary["residual_retrieval_gap"] == 0.3333
    assert "top-3 reranking could lift" in report["findings"][0]


def _case(
    case_id: str,
    *,
    rank: int | None,
    is_impossible: bool = False,
) -> dict[str, object]:
    expected = ["doc-expected"]
    if rank == 1:
        retrieved = ["doc-expected", "doc-other", "doc-third"]
    elif rank == 2:
        retrieved = ["doc-other", "doc-expected", "doc-third"]
    elif rank == 3:
        retrieved = ["doc-other", "doc-third", "doc-expected"]
    else:
        retrieved = ["doc-other", "doc-third", "doc-fourth"]
    return {
        "case_id": case_id,
        "is_impossible": is_impossible,
        "expected_citation_ids": expected,
        "retrieved_citation_ids": retrieved,
        "expected_rank": rank,
        "top1_match": rank == 1,
        "failure_reasons": [] if rank == 1 else ["expected_document_not_retrieved_at_3"],
    }
