"""Optional provider-backed embedding retrieval over the public RAG tracks.

The synthetic golden benchmark is saturated: local and provider embeddings both
reach 100% hit@3, so it cannot discriminate them. This module runs a hosted
provider embedding retriever over the harder public TechQA and WixQA tracks
(where the local retriever is well under 100%) so the comparison is meaningful.

It reuses each public track's own per-case scoring (via the injected `retrieve`
hook on `_evaluate_case`) so the provider system is measured identically to the
local retrievers. Retrieval metrics (hit@3, top-1 citation, MRR@3) are rank-based
and directly comparable; the abstention threshold is the local one and is not
recalibrated for provider score scales, so abstention figures are indicative only.
"""

from __future__ import annotations

from collections.abc import Callable
from math import sqrt
from pathlib import Path
from typing import Any

from internal_ai_agent.evals import techqa_public, wixqa_public

EmbedTexts = Callable[[list[str]], list[list[float]]]

_TRACKS: dict[str, dict[str, Any]] = {
    "techqa": {
        "module": techqa_public,
        "dataset": "nvidia/TechQA-RAG-Eval",
        "load_cases": techqa_public.load_techqa_cases,
        "documents_from_cases": techqa_public._documents_from_cases,
        "retrieved_cls": techqa_public.TechQARetrievedDocument,
        "primary_id": techqa_public.TECHQA_PRIMARY_RETRIEVER_ID,
        "primary_systems": techqa_public.TECHQA_RETRIEVER_SYSTEMS,
    },
    "wixqa": {
        "module": wixqa_public,
        "dataset": "Wix/WixQA expert-written",
        "load_cases": wixqa_public.load_wixqa_cases,
        "documents_from_cases": wixqa_public._documents_from_cases,
        "retrieved_cls": wixqa_public.WixQARetrievedDocument,
        "primary_id": wixqa_public.WIXQA_PRIMARY_RETRIEVER_ID,
        "primary_systems": wixqa_public.WIXQA_RETRIEVER_SYSTEMS,
    },
}


def available_tracks() -> list[str]:
    return list(_TRACKS)


def _document_text(document: Any) -> str:
    return f"{document.title}\n{document.text}".strip()


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def provider_embedding_input_estimate(project_root: Path, track: str) -> dict[str, int]:
    """Count embedding inputs a real run would make, without any API calls."""
    config = _TRACKS[track]
    cases = config["load_cases"](project_root)
    documents = config["documents_from_cases"](cases)
    unique_questions = {str(case["question"]) for case in cases}
    return {
        "case_count": len(cases),
        "document_count": len(documents),
        "unique_query_count": len(unique_questions),
        "embedding_inputs": len(documents) + len(unique_questions),
    }


def evaluate_public_rag_provider_embedding(
    project_root: Path,
    *,
    embed_texts: EmbedTexts,
    provider: str,
    model: str,
    track: str,
) -> dict[str, Any]:
    """Score a provider embedding retriever against the local primary on one track."""
    config = _TRACKS[track]
    module = config["module"]
    cases = config["load_cases"](project_root)
    if not cases:
        return {"track": track, "status": "not_configured", "case_count": 0}

    documents = config["documents_from_cases"](cases)

    # Embed every document once and every distinct query once (batched by the client).
    document_vectors = embed_texts([_document_text(document) for document in documents])
    vectors_by_document_id = {
        document.document_id: vector
        for document, vector in zip(documents, document_vectors, strict=True)
    }
    unique_questions = list(dict.fromkeys(str(case["question"]) for case in cases))
    vectors_by_question = dict(
        zip(unique_questions, embed_texts(unique_questions), strict=True)
    )

    retrieved_cls = config["retrieved_cls"]

    def provider_retrieve(question: str, docs: list[Any], *, top_k: int, system_id: str):
        query_vector = vectors_by_question[str(question)]
        ranked = []
        for document in docs:
            similarity = _cosine(query_vector, vectors_by_document_id[document.document_id])
            score = round(similarity * 100, 4)
            if score <= 0:
                continue
            ranked.append(
                retrieved_cls(document_id=document.document_id, title=document.title, score=score)
            )
        return sorted(ranked, key=lambda row: (-row.score, row.document_id))[:top_k]

    provider_system = {
        "system_id": f"provider_{provider}_embedding_{track}",
        "label": f"Provider {provider} embedding",
        "description": (
            f"Hosted {provider} {model} embedding retrieval over public {track} documents."
        ),
    }
    local_system = next(
        system
        for system in config["primary_systems"]
        if system["system_id"] == config["primary_id"]
    )

    provider_results = [
        module._evaluate_case(case, documents, system=provider_system, retrieve=provider_retrieve)
        for case in cases
    ]
    local_results = [
        module._evaluate_case(case, documents, system=local_system) for case in cases
    ]

    provider_metrics = module._summarize(provider_results)
    local_metrics = module._summarize(local_results)
    hit_key = "retrieval_hit_rate_at_3"
    return {
        "track": track,
        "status": "evaluated",
        "dataset": config["dataset"],
        "provider": provider,
        "model": model,
        "case_count": len(cases),
        "document_count": len(documents),
        "provider_system_id": provider_system["system_id"],
        "local_primary_system_id": config["primary_id"],
        "provider_metrics": provider_metrics,
        "local_primary_metrics": local_metrics,
        "hit_rate_delta": round(
            float(provider_metrics.get(hit_key, 0.0)) - float(local_metrics.get(hit_key, 0.0)),
            4,
        ),
    }
