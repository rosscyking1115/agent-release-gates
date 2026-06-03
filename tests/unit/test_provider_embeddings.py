from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.data.synthetic import build_runbooks, generate_all
from internal_ai_agent.evals.runner import evaluate_provider_embedding_store
from internal_ai_agent.providers.openai_embeddings import (
    OpenAIEmbeddingClient,
    OpenAIEmbeddingConfig,
)
from internal_ai_agent.rag.baseline import (
    answer_with_provider_embedding_store,
    build_provider_embedding_store,
)


def test_openai_embedding_client_posts_batches_and_parses_embeddings() -> None:
    calls = []

    def fake_post(
        endpoint: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> str:
        payload = json.loads(body)
        calls.append((endpoint, payload, headers, timeout_seconds))
        return json.dumps(
            {
                "data": [
                    {"index": index, "embedding": [float(index), 1.0]}
                    for index, _ in enumerate(payload["input"])
                ]
            }
        )

    client = OpenAIEmbeddingClient(
        OpenAIEmbeddingConfig(
            api_key="test-key",
            model="text-embedding-3-small",
            batch_size=2,
            timeout_seconds=4,
        ),
        http_post=fake_post,
    )

    embeddings = client.embed_texts(["one", "two", "three"])

    assert embeddings == [[0.0, 1.0], [1.0, 1.0], [0.0, 1.0]]
    assert len(calls) == 2
    assert calls[0][0] == "https://api.openai.com/v1/embeddings"
    assert calls[0][1]["model"] == "text-embedding-3-small"
    assert calls[0][1]["encoding_format"] == "float"
    assert calls[0][2]["Authorization"] == "Bearer test-key"
    assert calls[0][3] == 4


def test_provider_embedding_retrieval_uses_supplied_vectors() -> None:
    runbooks = [section.__dict__ for section in build_runbooks()]
    store = build_provider_embedding_store(
        runbooks,
        embed_texts=_fake_embed_texts,
        user_role="operations_analyst",
    )

    answer = answer_with_provider_embedding_store(
        "The counterparty confirmation has not arrived for Helios Trade Exceptions.",
        store,
        embed_texts=_fake_embed_texts,
    )

    assert answer.issue_category == "confirmation_pending"
    assert answer.citations == ["RB-TRADE_SUPPORT-02"]
    assert answer.retrieved_sections[0].score_breakdown
    assert "provider_embedding" in answer.retrieved_sections[0].score_breakdown


def test_provider_embedding_eval_writes_optional_report(tmp_path: Path) -> None:
    generate_all(tmp_path, ticket_count=24)

    report = evaluate_provider_embedding_store(
        tmp_path,
        embed_texts=_fake_embed_texts,
        provider_name="test_provider",
        model="test-embedding-model",
    )

    assert report["case_count"] == 120
    assert report["system_version"] == "provider_embedding_store_test_provider"
    assert report["model"] == "test-embedding-model"
    assert (tmp_path / "reports/provider_embedding_eval_summary.json").exists()
    assert (tmp_path / "reports/provider_embedding_eval_cases.jsonl").exists()


def _fake_embed_texts(texts: list[str]) -> list[list[float]]:
    return [_fake_embedding(text) for text in texts]


def _fake_embedding(text: str) -> list[float]:
    normalized = text.lower()
    return [
        _indicator(normalized, ("confirmation", "counterparty", "helios")),
        _indicator(normalized, ("duplicate", "duplicated", "atlas")),
        _indicator(normalized, ("kyc", "nova", "artifact", "artefact")),
    ]


def _indicator(text: str, terms: tuple[str, ...]) -> float:
    return float(sum(1 for term in terms if term in text))
