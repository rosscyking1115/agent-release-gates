from pathlib import Path

from internal_ai_agent.evals.public_rag_reranker import (
    CandidateScore,
    _rerank,
    write_public_rag_reranker_eval,
)


def test_public_rag_reranker_writes_not_configured_report(tmp_path: Path) -> None:
    report = write_public_rag_reranker_eval(tmp_path)

    assert report["status"] == "not_configured"
    assert report["summary"]["evaluated_track_count"] == 0
    assert (tmp_path / "reports/public_rag_reranker_eval.json").exists()


def test_reranker_promotes_only_when_gate_passes() -> None:
    promoted, changed, decision = _rerank(
        ["doc-a", "doc-b", "doc-c"],
        [
            CandidateScore("doc-a", original_score=10.0, reranker_score=12.0),
            CandidateScore("doc-b", original_score=8.5, reranker_score=18.0),
            CandidateScore("doc-c", original_score=7.0, reranker_score=5.0),
        ],
    )

    assert changed
    assert promoted == ["doc-b", "doc-a", "doc-c"]
    assert decision["action"] == "promote_challenger"

    kept, changed, decision = _rerank(
        ["doc-a", "doc-b", "doc-c"],
        [
            CandidateScore("doc-a", original_score=10.0, reranker_score=12.0),
            CandidateScore("doc-b", original_score=5.0, reranker_score=30.0),
            CandidateScore("doc-c", original_score=4.0, reranker_score=5.0),
        ],
    )

    assert not changed
    assert kept == ["doc-a", "doc-b", "doc-c"]
    assert decision["action"] == "keep_original"
