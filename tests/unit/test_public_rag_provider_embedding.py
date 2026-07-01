from __future__ import annotations

import hashlib
import json
from pathlib import Path

from internal_ai_agent.evals.public_rag_provider_embedding import (
    evaluate_public_rag_provider_embedding,
    provider_embedding_input_estimate,
)
from internal_ai_agent.evals.public_rag_publish import PUBLISHED_PATH, published_tracks


def _fake_embed(texts: list[str]) -> list[list[float]]:
    # Deterministic bag-of-words hashing embedder: shared tokens -> positive cosine.
    dim = 64
    vectors = []
    for text in texts:
        vector = [0.0] * dim
        for token in text.lower().split():
            vector[int(hashlib.md5(token.encode()).hexdigest(), 16) % dim] += 1.0
        vectors.append(vector)
    return vectors


def _write_techqa_fixture(project_root: Path) -> None:
    sample = project_root / "data/public/techqa_rag_eval_sample.jsonl"
    sample.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "id": "T1",
            "question": "find docalpha guidance",
            "answer": "",
            "is_impossible": False,
            "contexts": [{"filename": "docalpha", "text": "docalpha explains the alpha workflow"}],
        },
        {
            "id": "T2",
            "question": "find docbeta guidance",
            "answer": "",
            "is_impossible": False,
            "contexts": [{"filename": "docbeta", "text": "docbeta explains the beta workflow"}],
        },
    ]
    sample.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def test_provider_embedding_ranks_matching_document_first(tmp_path) -> None:
    _write_techqa_fixture(tmp_path)

    report = evaluate_public_rag_provider_embedding(
        tmp_path,
        embed_texts=_fake_embed,
        provider="fake",
        model="fake-64d",
        track="techqa",
    )

    assert report["status"] == "evaluated"
    assert report["case_count"] == 2
    # Each query shares its unique doc token with exactly its gold document.
    assert report["provider_metrics"]["retrieval_hit_rate_at_3"] == 1.0
    assert "retrieval_hit_rate_at_3" in report["local_primary_metrics"]
    assert report["provider_system_id"] == "provider_fake_embedding_techqa"


def test_input_estimate_counts_documents_plus_unique_queries(tmp_path) -> None:
    _write_techqa_fixture(tmp_path)

    estimate = provider_embedding_input_estimate(tmp_path, "techqa")

    assert estimate["case_count"] == 2
    assert estimate["document_count"] == 2
    assert estimate["unique_query_count"] == 2
    assert estimate["embedding_inputs"] == 4


def test_published_tracks_empty_without_file(tmp_path) -> None:
    assert published_tracks(tmp_path) == set()


def test_published_tracks_reads_committed_result(tmp_path) -> None:
    path = tmp_path / PUBLISHED_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "published",
                "tracks": {
                    "techqa": {"status": "evaluated"},
                    "wixqa": {"status": "not_configured"},
                },
            }
        ),
        encoding="utf-8",
    )

    assert published_tracks(tmp_path) == {"techqa"}
