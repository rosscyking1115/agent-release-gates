from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from math import log
from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json, write_jsonl

TECHQA_SAMPLE_PATH = Path("data/public/techqa_rag_eval_sample.jsonl")
TECHQA_RAW_PATH = Path("data/public/techqa_train.json")
TECHQA_SUMMARY_PATH = Path("reports/techqa_public_rag_summary.json")
TECHQA_CASES_PATH = Path("reports/techqa_public_rag_cases.jsonl")
TECHQA_PROFILE_PATH = Path("reports/techqa_public_benchmark_profile.json")
TECHQA_DEFAULT_SAMPLE_LIMIT = 160
ABSTENTION_SCORE_THRESHOLD = 15.0


@dataclass(frozen=True)
class TechQADocument:
    document_id: str
    title: str
    text: str


@dataclass(frozen=True)
class TechQARetrievedDocument:
    document_id: str
    title: str
    score: float


@dataclass(frozen=True)
class TechQACaseResult:
    case_id: str
    is_impossible: bool
    expected_citation_ids: list[str]
    retrieved_citation_ids: list[str]
    expected_rank: int | None
    top_score: float
    retrieval_hit_at_3: bool
    top1_match: bool
    predicted_abstain: bool
    abstention_correct: bool
    failure_reasons: list[str]


def evaluate_techqa_public(project_root: Path) -> dict[str, Any]:
    cases = load_techqa_cases(project_root)
    if not cases:
        profile = _benchmark_profile(
            cases=[],
            results=[],
            metrics={},
            status="not_configured",
        )
        report = {
            "dataset": "nvidia/TechQA-RAG-Eval",
            "benchmark_track": "external_public_rag",
            "status": "not_configured",
            "case_count": 0,
            "metrics": {},
            "benchmark_profile": profile["summary"],
            "notes": [
                (
                    "Add data/public/techqa_rag_eval_sample.jsonl or run "
                    "scripts/prepare_techqa_public_benchmark.py after downloading "
                    "data/public/techqa_train.json."
                )
            ],
        }
        write_json(project_root / TECHQA_SUMMARY_PATH, report)
        write_json(project_root / TECHQA_PROFILE_PATH, profile)
        write_jsonl(project_root / TECHQA_CASES_PATH, [])
        return report

    documents = _documents_from_cases(cases)
    results = [_evaluate_case(case, documents) for case in cases]
    metrics = _summarize(results)
    profile = _benchmark_profile(
        cases=cases,
        results=results,
        metrics=metrics,
        status="evaluated",
    )
    report = {
        "dataset": "nvidia/TechQA-RAG-Eval",
        "benchmark_track": "external_public_rag",
        "status": "evaluated",
        "source_url": "https://huggingface.co/datasets/nvidia/TechQA-RAG-Eval",
        "license": "Apache-2.0",
        "sample_path": str(TECHQA_SAMPLE_PATH).replace("\\", "/"),
        "case_count": len(results),
        "answerable_case_count": sum(not row.is_impossible for row in results),
        "impossible_case_count": sum(row.is_impossible for row in results),
        "document_count": len(documents),
        "abstention_score_threshold": ABSTENTION_SCORE_THRESHOLD,
        "metrics": metrics,
        "benchmark_profile": profile["summary"],
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            (
                "This is an external public-data benchmark track. It does not replace the "
                "controlled synthetic internal-operations benchmark."
            ),
            (
                "The evaluator measures retrieval/citation and impossible-question "
                "abstention over public technical-support questions."
            ),
            "The report is deterministic and uses no paid API calls.",
        ],
    }
    write_json(project_root / TECHQA_SUMMARY_PATH, report)
    write_json(project_root / TECHQA_PROFILE_PATH, profile)
    write_jsonl(project_root / TECHQA_CASES_PATH, (asdict(row) for row in results))
    return report


def write_techqa_sample(
    project_root: Path,
    *,
    limit: int = TECHQA_DEFAULT_SAMPLE_LIMIT,
    max_context_chars: int = 2400,
) -> Path:
    raw_path = project_root / TECHQA_RAW_PATH
    if not raw_path.exists():
        raise FileNotFoundError(
            "Expected data/public/techqa_train.json. Download it from "
            "https://huggingface.co/datasets/nvidia/TechQA-RAG-Eval/resolve/main/train.json"
        )

    raw_cases = json.loads(raw_path.read_text(encoding="utf-8"))
    selected = _select_sample_cases(raw_cases, limit=limit)
    sample_rows = [_compact_case(row, max_context_chars=max_context_chars) for row in selected]
    output_path = project_root / TECHQA_SAMPLE_PATH
    write_jsonl(output_path, sample_rows)
    return output_path


def load_techqa_cases(project_root: Path) -> list[dict[str, Any]]:
    sample_path = project_root / TECHQA_SAMPLE_PATH
    if sample_path.exists():
        return read_jsonl(sample_path)

    raw_path = project_root / TECHQA_RAW_PATH
    if not raw_path.exists():
        return []

    raw_cases = json.loads(raw_path.read_text(encoding="utf-8"))
    return [_compact_case(row, max_context_chars=2400) for row in _select_sample_cases(raw_cases)]


def _select_sample_cases(
    raw_cases: list[dict[str, Any]],
    *,
    limit: int = TECHQA_DEFAULT_SAMPLE_LIMIT,
) -> list[dict[str, Any]]:
    answerable = [row for row in raw_cases if not bool(row.get("is_impossible", False))]
    impossible = [row for row in raw_cases if bool(row.get("is_impossible", False))]
    impossible_target = max(1, limit // 5)
    answerable_target = max(1, limit - impossible_target)
    return [*answerable[:answerable_target], *impossible[:impossible_target]]


def _benchmark_profile(
    *,
    cases: list[dict[str, Any]],
    results: list[TechQACaseResult],
    metrics: dict[str, float],
    status: str,
) -> dict[str, Any]:
    answerable_cases = [case for case in cases if not bool(case.get("is_impossible"))]
    impossible_cases = [case for case in cases if bool(case.get("is_impossible"))]
    context_counts = [len(case.get("contexts", [])) for case in cases]
    unique_documents = {
        str(context["filename"])
        for case in cases
        for context in case.get("contexts", [])
    }
    failed_cases = [row for row in results if row.failure_reasons]
    summary = {
        "status": status,
        "dataset": "nvidia/TechQA-RAG-Eval",
        "benchmark_track": "external_public_rag",
        "license": "Apache-2.0",
        "source_url": "https://huggingface.co/datasets/nvidia/TechQA-RAG-Eval",
        "sample_path": str(TECHQA_SAMPLE_PATH).replace("\\", "/"),
        "sample_case_count": len(cases),
        "answerable_case_count": len(answerable_cases),
        "impossible_case_count": len(impossible_cases),
        "impossible_case_share": _rate(case.get("is_impossible", False) for case in cases),
        "unique_document_count": len(unique_documents),
        "average_contexts_per_case": round(sum(context_counts) / len(context_counts), 4)
        if context_counts
        else 0.0,
        "answerable_context_coverage": _rate(
            bool(case.get("contexts")) for case in answerable_cases
        ),
        "tracked_sample_default_limit": TECHQA_DEFAULT_SAMPLE_LIMIT,
        "sample_selection_policy": "first_answerable_plus_first_impossible_20pct",
        "sample_scope": "tracked_compact_public_sample",
        "provider_backed_embedding_result_published": False,
        "failed_case_count": len(failed_cases),
        "failure_rate": _rate(bool(row.failure_reasons) for row in results),
    }
    if metrics:
        summary["retrieval_hit_rate_at_3"] = metrics["retrieval_hit_rate_at_3"]
        summary["top1_citation_accuracy"] = metrics["top1_citation_accuracy"]
        summary["impossible_abstention_rate"] = metrics["impossible_abstention_rate"]
    return {
        "report_type": "techqa_public_benchmark_profile",
        "summary": summary,
        "coverage_notes": [
            (
                "The TechQA track is external public technical-support data and is "
                "reported separately from the synthetic internal-operations benchmark."
            ),
            (
                "The tracked sample is deterministic so CI, Streamlit, and GitHub "
                "Pages can reproduce the public-data metrics without downloading "
                "the upstream dataset."
            ),
            (
                "Provider-backed embedding comparison remains optional and is not "
                "claimed until a credentialed run publishes a separate result."
            ),
        ],
    }


def _compact_case(row: dict[str, Any], *, max_context_chars: int) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "question": str(row["question"]).strip(),
        "answer": str(row.get("answer", "")).strip(),
        "is_impossible": bool(row.get("is_impossible", False)),
        "contexts": [
            {
                "filename": str(context["filename"]),
                "text": str(context["text"]).strip()[:max_context_chars],
            }
            for context in row.get("contexts", [])
        ],
    }


def _documents_from_cases(cases: list[dict[str, Any]]) -> list[TechQADocument]:
    documents_by_id: dict[str, TechQADocument] = {}
    for case in cases:
        for context in case.get("contexts", []):
            document_id = str(context["filename"])
            if document_id in documents_by_id:
                continue
            text = str(context["text"])
            documents_by_id[document_id] = TechQADocument(
                document_id=document_id,
                title=_title_from_context(text, fallback=document_id),
                text=text,
            )
    return sorted(documents_by_id.values(), key=lambda document: document.document_id)


def _evaluate_case(
    case: dict[str, Any],
    documents: list[TechQADocument],
) -> TechQACaseResult:
    retrieved = _retrieve(str(case["question"]), documents, top_k=3)
    retrieved_ids = [document.document_id for document in retrieved]
    expected_ids = [str(context["filename"]) for context in case.get("contexts", [])]
    is_impossible = bool(case.get("is_impossible", False))
    top_score = retrieved[0].score if retrieved else 0.0
    expected_rank = _expected_rank(expected_ids, retrieved_ids)
    predicted_abstain = top_score < ABSTENTION_SCORE_THRESHOLD
    retrieval_hit_at_3 = bool(expected_rank is not None and expected_rank <= 3)
    top1_match = expected_rank == 1
    failure_reasons = _failure_reasons(
        is_impossible=is_impossible,
        predicted_abstain=predicted_abstain,
        retrieval_hit_at_3=retrieval_hit_at_3,
        top1_match=top1_match,
    )
    return TechQACaseResult(
        case_id=str(case["id"]),
        is_impossible=is_impossible,
        expected_citation_ids=expected_ids,
        retrieved_citation_ids=retrieved_ids,
        expected_rank=expected_rank,
        top_score=top_score,
        retrieval_hit_at_3=retrieval_hit_at_3,
        top1_match=top1_match,
        predicted_abstain=predicted_abstain,
        abstention_correct=predicted_abstain == is_impossible,
        failure_reasons=failure_reasons,
    )


def _retrieve(
    question: str,
    documents: list[TechQADocument],
    *,
    top_k: int,
) -> list[TechQARetrievedDocument]:
    if not documents:
        return []

    doc_features = [_document_features(document) for document in documents]
    idf = _inverse_document_frequency(doc_features)
    query_tokens = _token_sequence(question)
    query_vector = _tfidf_vector(_query_features(question), idf)
    retrieved: list[TechQARetrievedDocument] = []

    for document, features in zip(documents, doc_features, strict=True):
        document_vector = _tfidf_vector(features, idf)
        cosine_score = _cosine_similarity(query_vector, document_vector) * 100
        title_score = len(set(query_tokens) & set(_token_sequence(document.title))) * 2.5
        exact_phrase_score = _exact_phrase_score(question, document.title)
        score = round(cosine_score + title_score + exact_phrase_score, 4)
        if score <= 0:
            continue
        retrieved.append(
            TechQARetrievedDocument(
                document_id=document.document_id,
                title=document.title,
                score=score,
            )
        )
    return sorted(retrieved, key=lambda row: (-row.score, row.document_id))[:top_k]


def _summarize(results: list[TechQACaseResult]) -> dict[str, float]:
    answerable = [row for row in results if not row.is_impossible]
    impossible = [row for row in results if row.is_impossible]
    return {
        "retrieval_hit_rate_at_3": _rate(row.retrieval_hit_at_3 for row in answerable),
        "top1_citation_accuracy": _rate(row.top1_match for row in answerable),
        "mean_reciprocal_rank_at_3": _mean_reciprocal_rank(answerable),
        "abstention_accuracy": _rate(row.abstention_correct for row in results),
        "impossible_abstention_rate": _rate(row.predicted_abstain for row in impossible),
        "answerable_false_abstention_rate": _rate(row.predicted_abstain for row in answerable),
    }


def _failure_reasons(
    *,
    is_impossible: bool,
    predicted_abstain: bool,
    retrieval_hit_at_3: bool,
    top1_match: bool,
) -> list[str]:
    reasons: list[str] = []
    if is_impossible:
        if not predicted_abstain:
            reasons.append("failed_to_abstain_impossible_question")
        return reasons
    if predicted_abstain:
        reasons.append("false_abstention_answerable_question")
    if not retrieval_hit_at_3:
        reasons.append("expected_document_not_retrieved_at_3")
    elif not top1_match:
        reasons.append("expected_document_retrieved_but_not_top1")
    return reasons


def _failure_reason_counts(results: list[TechQACaseResult]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in results:
        counts.update(row.failure_reasons)
    return dict(sorted(counts.items()))


def _failure_examples(
    results: list[TechQACaseResult],
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for row in results:
        if not row.failure_reasons:
            continue
        examples.append(
            {
                "case_id": row.case_id,
                "is_impossible": row.is_impossible,
                "failure_reasons": row.failure_reasons,
                "expected_citation_ids": row.expected_citation_ids,
                "retrieved_citation_ids": row.retrieved_citation_ids,
                "expected_rank": row.expected_rank,
                "top_score": row.top_score,
            }
        )
    return examples[:limit]


def _expected_rank(expected_ids: list[str], retrieved_ids: list[str]) -> int | None:
    for index, retrieved_id in enumerate(retrieved_ids, start=1):
        if retrieved_id in expected_ids:
            return index
    return None


def _rate(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(1 for item in items if item) / len(items), 4)


def _mean_reciprocal_rank(results: list[TechQACaseResult]) -> float:
    if not results:
        return 0.0
    score = 0.0
    for row in results:
        if row.expected_rank is not None and row.expected_rank <= 3:
            score += 1 / row.expected_rank
    return round(score / len(results), 4)


def _title_from_context(text: str, *, fallback: str) -> str:
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    if first_line.lower().startswith("title:"):
        return first_line.split(":", maxsplit=1)[1].strip()
    return fallback


def _document_features(document: TechQADocument) -> list[str]:
    features = _vector_features(document.title, prefix="title") * 3
    features.extend(_vector_features(document.text, prefix="body"))
    return features


def _query_features(question: str) -> list[str]:
    return _vector_features(question, prefix="query")


def _vector_features(text: str, *, prefix: str) -> list[str]:
    tokens = _token_sequence(text)
    features = [f"token:{token}" for token in tokens]
    features.extend(f"{prefix}:{token}" for token in tokens)
    features.extend(
        f"bigram:{left}_{right}" for left, right in zip(tokens, tokens[1:], strict=False)
    )
    return features


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "what",
    "when",
    "why",
    "with",
}


def _token_sequence(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS
    ]


def _inverse_document_frequency(doc_features: list[list[str]]) -> dict[str, float]:
    doc_count = len(doc_features)
    frequencies: Counter[str] = Counter()
    for features in doc_features:
        frequencies.update(set(features))
    return {
        feature: log((doc_count + 1) / (frequency + 1)) + 1
        for feature, frequency in frequencies.items()
    }


def _tfidf_vector(features: list[str], idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(features)
    if not counts:
        return {}
    max_count = max(counts.values())
    return {
        feature: (count / max_count) * idf.get(feature, 1.0)
        for feature, count in counts.items()
    }


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    overlap = set(left) & set(right)
    numerator = sum(left[key] * right[key] for key in overlap)
    left_norm = sum(value * value for value in left.values()) ** 0.5
    right_norm = sum(value * value for value in right.values()) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _exact_phrase_score(question: str, title: str) -> float:
    normalized_question = " ".join(_token_sequence(question))
    title_tokens = _token_sequence(title)
    score = 0.0
    for size in (2, 3):
        for index in range(0, max(0, len(title_tokens) - size + 1)):
            phrase = " ".join(title_tokens[index : index + size])
            if phrase and phrase in normalized_question:
                score += 4.0 if size == 2 else 8.0
    return score
