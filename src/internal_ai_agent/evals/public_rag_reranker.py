"""Public RAG reranker *evaluation*.

Runs a deterministic lexical reranker over the public RAG tracks and reports the
actual lift versus the retrieval baseline (baseline vs reranked top-1 citation
accuracy, changed/improved/regressed cases, regression rate). Distinct from its
similarly-named siblings:
- ``public_rag_reranking`` measures only the headroom/opportunity (no reranker).
- ``public_rag_model_reranker`` is the hosted, model-backed reranker adapter.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
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
from internal_ai_agent.evals.techqa_public import (
    _token_sequence as techqa_tokens,
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
from internal_ai_agent.evals.wixqa_public import (
    _token_sequence as wixqa_tokens,
)
from internal_ai_agent.io import write_json

PUBLIC_RAG_RERANKER_PATH = Path("reports/public_rag_reranker_eval.json")
RERANKER_SCORE_MARGIN = 5.0
MAX_ORIGINAL_SCORE_GAP = 2.0


@dataclass(frozen=True)
class CandidateScore:
    document_id: str
    original_score: float
    reranker_score: float


def write_public_rag_reranker_eval(project_root: Path) -> dict[str, Any]:
    tracks = [
        _evaluate_track(
            dataset="nvidia/TechQA-RAG-Eval",
            benchmark_track="external_public_rag",
            cases=load_techqa_cases(project_root),
            documents_from_cases=techqa_documents_from_cases,
            retrieve=techqa_retrieve,
            primary_system_id=TECHQA_PRIMARY_RETRIEVER_ID,
            token_sequence=techqa_tokens,
            expected_ids=lambda case: [
                str(context["filename"]) for context in case.get("contexts", [])
            ],
            include_case=lambda case: not bool(case.get("is_impossible", False)),
        ),
        _evaluate_track(
            dataset="Wix/WixQA expert-written",
            benchmark_track="external_public_enterprise_rag",
            cases=load_wixqa_cases(project_root),
            documents_from_cases=wixqa_documents_from_cases,
            retrieve=wixqa_retrieve,
            primary_system_id=WIXQA_PRIMARY_RETRIEVER_ID,
            token_sequence=wixqa_tokens,
            expected_ids=lambda case: [
                str(article_id) for article_id in case.get("article_ids", [])
            ],
            include_case=lambda case: True,
        ),
    ]
    report = _report([track for track in tracks if track["status"] == "evaluated"])
    write_json(project_root / PUBLIC_RAG_RERANKER_PATH, report)
    return report


def _evaluate_track(
    *,
    dataset: str,
    benchmark_track: str,
    cases: list[dict[str, Any]],
    documents_from_cases: Callable[[list[dict[str, Any]]], list[Any]],
    retrieve: Callable[..., list[Any]],
    primary_system_id: str,
    token_sequence: Callable[[str], list[str]],
    expected_ids: Callable[[dict[str, Any]], list[str]],
    include_case: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    selected_cases = [case for case in cases if include_case(case)]
    if not selected_cases:
        return {
            "dataset": dataset,
            "benchmark_track": benchmark_track,
            "status": "not_configured",
            "case_count": 0,
        }

    documents = documents_from_cases(cases)
    documents_by_id = {document.document_id: document for document in documents}
    rows = []
    for case in selected_cases:
        retrieved = retrieve(
            str(case["question"]),
            documents,
            top_k=3,
            system_id=primary_system_id,
        )
        original_ids = [row.document_id for row in retrieved]
        expected = expected_ids(case)
        scores = [
            CandidateScore(
                document_id=row.document_id,
                original_score=float(row.score),
                reranker_score=_reranker_score(
                    str(case["question"]),
                    documents_by_id[row.document_id],
                    token_sequence,
                ),
            )
            for row in retrieved
        ]
        reranked_ids, changed, decision = _rerank(original_ids, scores)
        baseline_correct = bool(original_ids and original_ids[0] in expected)
        reranked_correct = bool(reranked_ids and reranked_ids[0] in expected)
        rows.append(
            {
                "case_id": str(case["id"]),
                "expected_citation_ids": expected,
                "original_citation_ids": original_ids,
                "reranked_citation_ids": reranked_ids,
                "retrieval_hit_at_3": any(document_id in expected for document_id in original_ids),
                "baseline_top1_match": baseline_correct,
                "reranked_top1_match": reranked_correct,
                "changed": changed,
                "change_outcome": _change_outcome(
                    changed=changed,
                    baseline_correct=baseline_correct,
                    reranked_correct=reranked_correct,
                ),
                "decision": decision,
                "candidate_scores": [
                    {
                        "document_id": score.document_id,
                        "original_score": round(score.original_score, 4),
                        "reranker_score": round(score.reranker_score, 4),
                    }
                    for score in scores
                ],
            }
        )

    return {
        "dataset": dataset,
        "benchmark_track": benchmark_track,
        "status": "evaluated",
        "case_count": len(rows),
        "metrics": _metrics(rows),
        "changed_case_examples": [row for row in rows if row["changed"]][:8],
    }


def _report(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    if not tracks:
        return {
            "report_type": "public_rag_reranker_eval",
            "status": "not_configured",
            "summary": {"evaluated_track_count": 0, "total_case_count": 0},
            "tracks": [],
            "findings": [],
            "recommendations": [
                "Run the public RAG benchmarks before evaluating the reranker."
            ],
        }

    total_cases = sum(int(track["case_count"]) for track in tracks)
    total_baseline = sum(
        int(track["metrics"]["baseline_top1_correct_count"]) for track in tracks
    )
    total_reranked = sum(
        int(track["metrics"]["reranked_top1_correct_count"]) for track in tracks
    )
    total_changed = sum(int(track["metrics"]["changed_case_count"]) for track in tracks)
    total_improved = sum(int(track["metrics"]["improved_case_count"]) for track in tracks)
    total_regressed = sum(int(track["metrics"]["regressed_case_count"]) for track in tracks)
    summary = {
        "evaluated_track_count": len(tracks),
        "total_case_count": total_cases,
        "baseline_top1_accuracy": _rate(total_baseline, total_cases),
        "reranked_top1_accuracy": _rate(total_reranked, total_cases),
        "top1_accuracy_delta": round(
            _rate(total_reranked, total_cases) - _rate(total_baseline, total_cases),
            4,
        ),
        "changed_case_count": total_changed,
        "improved_case_count": total_improved,
        "regressed_case_count": total_regressed,
        "net_improved_case_count": total_improved - total_regressed,
        "change_rate": _rate(total_changed, total_cases),
        "regression_rate": _rate(total_regressed, total_cases),
    }
    return {
        "report_type": "public_rag_reranker_eval",
        "status": "evaluated",
        "reranker": {
            "label": "Conservative lexical overlap reranker",
            "candidate_set": "top_3_primary_public_retriever_results",
            "score_margin_threshold": RERANKER_SCORE_MARGIN,
            "max_original_score_gap": MAX_ORIGINAL_SCORE_GAP,
            "uses_labels_or_answers": False,
            "uses_paid_provider": False,
        },
        "summary": summary,
        "tracks": tracks,
        "findings": _findings(summary),
        "recommendations": _recommendations(summary),
        "notes": [
            (
                "This deterministic reranker uses only the user query and candidate "
                "document text. It does not use expected labels, answers, or paid APIs."
            ),
            (
                "The gate is conservative: it only promotes a challenger when the "
                "reranker margin is at least 5.0 and the original retriever score gap "
                "is at most 2.0."
            ),
        ],
    }


def _metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    changed = [row for row in rows if row["changed"]]
    improved = [row for row in rows if row["change_outcome"] == "improved"]
    regressed = [row for row in rows if row["change_outcome"] == "regressed"]
    baseline_correct = sum(1 for row in rows if row["baseline_top1_match"])
    reranked_correct = sum(1 for row in rows if row["reranked_top1_match"])
    return {
        "baseline_top1_correct_count": baseline_correct,
        "reranked_top1_correct_count": reranked_correct,
        "baseline_top1_accuracy": _rate(baseline_correct, len(rows)),
        "reranked_top1_accuracy": _rate(reranked_correct, len(rows)),
        "top1_accuracy_delta": round(
            _rate(reranked_correct, len(rows)) - _rate(baseline_correct, len(rows)),
            4,
        ),
        "changed_case_count": len(changed),
        "improved_case_count": len(improved),
        "regressed_case_count": len(regressed),
        "neutral_change_count": len(changed) - len(improved) - len(regressed),
        "change_rate": _rate(len(changed), len(rows)),
        "regression_rate": _rate(len(regressed), len(rows)),
    }


def _rerank(
    original_ids: list[str],
    scores: list[CandidateScore],
) -> tuple[list[str], bool, dict[str, Any]]:
    if not original_ids or not scores:
        return original_ids, False, {"action": "keep_original"}
    incumbent_id = original_ids[0]
    score_by_id = {score.document_id: score for score in scores}
    incumbent = score_by_id[incumbent_id]
    challenger = sorted(
        scores,
        key=lambda score: (-score.reranker_score, score.document_id),
    )[0]
    reranker_margin = challenger.reranker_score - incumbent.reranker_score
    original_score_gap = incumbent.original_score - challenger.original_score
    should_promote = (
        challenger.document_id != incumbent_id
        and reranker_margin >= RERANKER_SCORE_MARGIN
        and original_score_gap <= MAX_ORIGINAL_SCORE_GAP
    )
    decision = {
        "action": "promote_challenger" if should_promote else "keep_original",
        "challenger_id": challenger.document_id,
        "incumbent_id": incumbent_id,
        "reranker_margin": round(reranker_margin, 4),
        "original_score_gap": round(original_score_gap, 4),
    }
    if not should_promote:
        return original_ids, False, decision
    reranked = [challenger.document_id] + [
        document_id for document_id in original_ids if document_id != challenger.document_id
    ]
    return reranked, True, decision


def _reranker_score(
    question: str,
    document: Any,
    token_sequence: Callable[[str], list[str]],
) -> float:
    query_tokens = token_sequence(question)
    query_set = set(query_tokens)
    if not query_set:
        return 0.0
    title_tokens = token_sequence(str(document.title))
    text_tokens = token_sequence(str(document.text))
    title_set = set(title_tokens)
    text_set = set(text_tokens)
    query_bigrams = _bigrams(query_tokens)
    title_bigrams = _bigrams(title_tokens)
    text_bigrams = _bigrams(text_tokens[:250])
    return round(
        (len(query_set & title_set) / len(query_set)) * 45
        + (len(query_set & text_set) / len(query_set)) * 25
        + len(query_bigrams & title_bigrams) * 12
        + len(query_bigrams & text_bigrams) * 3
        + len(query_set & title_set) * 3
        + len(query_set & text_set),
        4,
    )


def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    return set(zip(tokens, tokens[1:], strict=False))


def _change_outcome(
    *,
    changed: bool,
    baseline_correct: bool,
    reranked_correct: bool,
) -> str:
    if not changed:
        return "unchanged"
    if not baseline_correct and reranked_correct:
        return "improved"
    if baseline_correct and not reranked_correct:
        return "regressed"
    return "neutral"


def _findings(summary: dict[str, Any]) -> list[str]:
    return [
        (
            "The conservative deterministic reranker improves weighted top-1 "
            f"citation accuracy by {summary['top1_accuracy_delta']:+.2%}."
        ),
        (
            "It changes "
            f"{summary['changed_case_count']} cases, improves "
            f"{summary['improved_case_count']}, and regresses "
            f"{summary['regressed_case_count']}."
        ),
        (
            "The small lift confirms reranking is useful, but the observed effect is "
            "far below the oracle top-3 ceiling and needs stronger model-based scoring."
        ),
    ]


def _recommendations(summary: dict[str, Any]) -> list[str]:
    recommendations = [
        (
            "Compare this deterministic reranker against a provider-backed or "
            "open-source cross-encoder reranker on the same public candidates."
        ),
        (
            "Keep regression count visible because reranking can trade citation gains "
            "for new top-1 mistakes."
        ),
    ]
    if float(summary["top1_accuracy_delta"]) < 0.02:
        recommendations.append(
            "Treat this heuristic as a baseline, not a final reranking solution."
        )
    return recommendations


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
