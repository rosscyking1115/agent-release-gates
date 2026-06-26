"""Public RAG *hosted model-backed* reranker adapter.

Readiness/status, request packet, and eval summary for a provider/model-backed
reranker over the public RAG tracks. Distinct from its similarly-named siblings:
- ``public_rag_reranking`` measures only the headroom/opportunity (no reranker).
- ``public_rag_reranker`` runs a deterministic lexical reranker and scores lift.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.techqa_public import (
    TECHQA_PRIMARY_RETRIEVER_ID,
    load_techqa_cases,
)
from internal_ai_agent.evals.techqa_public import (
    _documents_from_cases as techqa_documents_from_cases,
)
from internal_ai_agent.evals.techqa_public import (
    _retrieve as techqa_retrieve,
)
from internal_ai_agent.evals.wixqa_public import (
    WIXQA_PRIMARY_RETRIEVER_ID,
    load_wixqa_cases,
)
from internal_ai_agent.evals.wixqa_public import (
    _documents_from_cases as wixqa_documents_from_cases,
)
from internal_ai_agent.evals.wixqa_public import (
    _retrieve as wixqa_retrieve,
)
from internal_ai_agent.io import write_json, write_jsonl

PUBLIC_RAG_MODEL_RERANKER_STATUS_PATH = Path(
    "reports/public_rag_model_reranker_adapter_status.json"
)
PUBLIC_RAG_MODEL_RERANKER_PACKET_PATH = Path(
    "reports/public_rag_model_reranker_packet.jsonl"
)
PUBLIC_RAG_MODEL_RERANKER_SUMMARY_PATH = Path(
    "reports/public_rag_model_reranker_eval_summary.json"
)
PUBLIC_RAG_MODEL_RERANKER_CASES_PATH = Path(
    "reports/public_rag_model_reranker_eval_cases.jsonl"
)
DEFAULT_PACKET_LIMIT = 24
SNIPPET_CHAR_LIMIT = 700


def write_public_rag_model_reranker_adapter_status(
    project_root: Path,
    *,
    packet_limit: int = DEFAULT_PACKET_LIMIT,
) -> dict[str, Any]:
    packet_rows = prepare_public_rag_model_reranker_packet(
        project_root,
        packet_limit=packet_limit,
    )
    write_jsonl(project_root / PUBLIC_RAG_MODEL_RERANKER_PACKET_PATH, packet_rows)
    status = _adapter_status(packet_rows)
    write_json(project_root / PUBLIC_RAG_MODEL_RERANKER_STATUS_PATH, status)
    return status


def prepare_public_rag_model_reranker_packet(
    project_root: Path,
    *,
    packet_limit: int = DEFAULT_PACKET_LIMIT,
) -> list[dict[str, Any]]:
    track_rows = [
        *_packet_rows_for_track(
            dataset="nvidia/TechQA-RAG-Eval",
            benchmark_track="external_public_rag",
            cases=load_techqa_cases(project_root),
            documents_from_cases=techqa_documents_from_cases,
            retrieve=techqa_retrieve,
            primary_system_id=TECHQA_PRIMARY_RETRIEVER_ID,
            expected_ids=lambda case: [
                str(context["filename"]) for context in case.get("contexts", [])
            ],
            include_case=lambda case: not bool(case.get("is_impossible", False)),
        ),
        *_packet_rows_for_track(
            dataset="Wix/WixQA expert-written",
            benchmark_track="external_public_enterprise_rag",
            cases=load_wixqa_cases(project_root),
            documents_from_cases=wixqa_documents_from_cases,
            retrieve=wixqa_retrieve,
            primary_system_id=WIXQA_PRIMARY_RETRIEVER_ID,
            expected_ids=lambda case: [
                str(article_id) for article_id in case.get("article_ids", [])
            ],
            include_case=lambda case: True,
        ),
    ]
    return _select_packet_rows(track_rows, packet_limit=packet_limit)


def _packet_rows_for_track(
    *,
    dataset: str,
    benchmark_track: str,
    cases: list[dict[str, Any]],
    documents_from_cases: Callable[[list[dict[str, Any]]], list[Any]],
    retrieve: Callable[..., list[Any]],
    primary_system_id: str,
    expected_ids: Callable[[dict[str, Any]], list[str]],
    include_case: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    selected_cases = [case for case in cases if include_case(case)]
    if not selected_cases:
        return []

    documents = documents_from_cases(cases)
    documents_by_id = {document.document_id: document for document in documents}
    rows: list[dict[str, Any]] = []
    for case in selected_cases:
        retrieved = retrieve(
            str(case["question"]),
            documents,
            top_k=3,
            system_id=primary_system_id,
        )
        retrieved_ids = [row.document_id for row in retrieved]
        expected = expected_ids(case)
        expected_rank = _expected_rank(expected, retrieved_ids)
        if expected_rank not in {1, 2, 3}:
            continue
        selection_reason = "rerankable" if expected_rank in {2, 3} else "top1_control"
        rows.append(
            {
                "case_id": str(case["id"]),
                "dataset": dataset,
                "benchmark_track": benchmark_track,
                "selection_reason": selection_reason,
                "baseline_top1_candidate_id": retrieved_ids[0] if retrieved_ids else "",
                "candidate_count": len(retrieved),
                "provider_input": {
                    "task": (
                        "Rank the candidate documents by how well they answer "
                        "the user question. Return only ordered candidate IDs."
                    ),
                    "question": str(case["question"]),
                    "candidate_documents": [
                        _candidate_payload(row, documents_by_id[row.document_id])
                        for row in retrieved
                        if row.document_id in documents_by_id
                    ],
                },
                "evaluation_metadata": {
                    "expected_citation_ids": expected,
                    "expected_rank_in_baseline_top3": expected_rank,
                    "labels_not_sent_to_provider": True,
                    "baseline_retriever": primary_system_id,
                },
            }
        )
    return rows


def _candidate_payload(row: Any, document: Any) -> dict[str, Any]:
    payload = {
        "candidate_id": row.document_id,
        "title": str(document.title),
        "retriever_score": float(row.score),
        "snippet": _snippet(str(document.text), limit=SNIPPET_CHAR_LIMIT),
    }
    article_type = getattr(document, "article_type", "")
    if article_type:
        payload["article_type"] = str(article_type)
    return payload


def _select_packet_rows(
    rows: list[dict[str, Any]],
    *,
    packet_limit: int,
) -> list[dict[str, Any]]:
    if packet_limit <= 0:
        return []
    rerankable = _interleave_by_dataset(
        [row for row in rows if row["selection_reason"] == "rerankable"]
    )
    controls = _interleave_by_dataset(
        [row for row in rows if row["selection_reason"] == "top1_control"]
    )
    rerankable_target = min(len(rerankable), max(1, packet_limit // 2))
    selected = [*rerankable[:rerankable_target]]
    remaining_slots = packet_limit - len(selected)
    selected.extend(controls[:remaining_slots])
    if len(selected) < packet_limit:
        selected_ids = {row["case_id"] for row in selected}
        selected.extend(
            row for row in rows if row["case_id"] not in selected_ids
        )
    return selected[:packet_limit]


def _interleave_by_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_dataset: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        rows_by_dataset.setdefault(str(row["dataset"]), []).append(row)
    interleaved: list[dict[str, Any]] = []
    dataset_names = sorted(rows_by_dataset)
    while any(rows_by_dataset.values()):
        for dataset in dataset_names:
            dataset_rows = rows_by_dataset[dataset]
            if dataset_rows:
                interleaved.append(dataset_rows.pop(0))
    return interleaved


def _adapter_status(packet_rows: list[dict[str, Any]]) -> dict[str, Any]:
    status = "dry_run_ready" if packet_rows else "not_configured"
    selection_counts = {
        "rerankable": sum(row["selection_reason"] == "rerankable" for row in packet_rows),
        "top1_control": sum(row["selection_reason"] == "top1_control" for row in packet_rows),
    }
    track_counts: dict[str, int] = {}
    for row in packet_rows:
        dataset = str(row["dataset"])
        track_counts[dataset] = track_counts.get(dataset, 0) + 1
    return {
        "status": status,
        "adapter_type": "hosted_public_rag_reranker",
        "provider": "openai",
        "api_mode": "responses",
        "credential_env_var": "OPENAI_API_KEY",
        "model_env_var": "OPENAI_RERANKER_MODEL",
        "default_model": "gpt-4.1-mini",
        "packet_path": str(PUBLIC_RAG_MODEL_RERANKER_PACKET_PATH).replace("\\", "/"),
        "planned_summary_path": str(PUBLIC_RAG_MODEL_RERANKER_SUMMARY_PATH).replace(
            "\\", "/"
        ),
        "planned_cases_path": str(PUBLIC_RAG_MODEL_RERANKER_CASES_PATH).replace("\\", "/"),
        "candidate_case_count": len(packet_rows),
        "estimated_provider_calls": len(packet_rows),
        "estimated_candidate_documents": sum(
            int(row["candidate_count"]) for row in packet_rows
        ),
        "selection_counts": selection_counts,
        "dataset_case_counts": track_counts,
        "provider_input_boundary": (
            "Provider input includes public user questions and public candidate "
            "document snippets only. Expected citation labels are stored separately "
            "under evaluation_metadata and should not be sent to the provider."
        ),
        "publication_rule": (
            "Publish hosted reranker scores only after reviewing model ID, run date, "
            "cost, changed cases, improved cases, and regressions."
        ),
        "planned_outputs": [
            str(PUBLIC_RAG_MODEL_RERANKER_STATUS_PATH).replace("\\", "/"),
            str(PUBLIC_RAG_MODEL_RERANKER_PACKET_PATH).replace("\\", "/"),
            str(PUBLIC_RAG_MODEL_RERANKER_SUMMARY_PATH).replace("\\", "/"),
            str(PUBLIC_RAG_MODEL_RERANKER_CASES_PATH).replace("\\", "/"),
        ],
        "notes": [
            "This artifact prepares a hosted reranker comparison without making API calls.",
            (
                "The packet is deliberately small and balanced between rerankable "
                "cases and top-1 controls."
            ),
            "The deterministic CI path remains cost-free and does not require credentials.",
        ],
    }


def _expected_rank(expected_ids: list[str], retrieved_ids: list[str]) -> int | None:
    for index, retrieved_id in enumerate(retrieved_ids, start=1):
        if retrieved_id in expected_ids:
            return index
    return None


def _snippet(text: str, *, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."
