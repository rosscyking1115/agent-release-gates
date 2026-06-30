from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass
from math import log
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.failure_taxonomy import labels_for_failure_reasons
from internal_ai_agent.io import read_jsonl, write_json, write_jsonl

WIXQA_QA_RAW_PATH = Path("data/public/wixqa_expertwritten_test.jsonl")
WIXQA_CORPUS_RAW_PATH = Path("data/public/wixqa_kb_corpus.jsonl")
WIXQA_SAMPLE_PATH = Path("data/public/wixqa_public_rag_sample.jsonl")
WIXQA_SUMMARY_PATH = Path("reports/wixqa_public_rag_summary.json")
WIXQA_CASES_PATH = Path("reports/wixqa_public_rag_cases.jsonl")
WIXQA_PROFILE_PATH = Path("reports/wixqa_public_benchmark_profile.json")
WIXQA_RETRIEVER_COMPARISON_PATH = Path("reports/wixqa_public_retriever_comparison.json")
WIXQA_RETRIEVER_CASES_PATH = Path("reports/wixqa_public_retriever_cases.jsonl")
WIXQA_DEFAULT_SAMPLE_LIMIT = 160
WIXQA_PRIMARY_RETRIEVER_ID = "local_tfidf_wixqa_retriever"
WIXQA_RETRIEVER_SYSTEMS = [
    {
        "system_id": "keyword_title_baseline",
        "label": "Keyword title baseline",
        "description": "Simple title-token overlap baseline over Wix public KB articles.",
    },
    {
        "system_id": WIXQA_PRIMARY_RETRIEVER_ID,
        "label": "Local TF-IDF WixQA retriever",
        "description": "Local TF-IDF retrieval with title boosts and exact phrase scoring.",
    },
]


@dataclass(frozen=True)
class WixQADocument:
    document_id: str
    title: str
    text: str
    article_type: str


@dataclass(frozen=True)
class WixQARetrievedDocument:
    document_id: str
    title: str
    score: float


@dataclass(frozen=True)
class WixQACaseResult:
    system_id: str
    system_label: str
    case_id: str
    expected_citation_ids: list[str]
    retrieved_citation_ids: list[str]
    expected_rank: int | None
    top_score: float
    retrieval_hit_at_3: bool
    top1_match: bool
    multi_article_required: bool
    failure_reasons: list[str]
    taxonomy_source: str
    taxonomy_labels: list[str]


def evaluate_wixqa_public(project_root: Path) -> dict[str, Any]:
    cases = load_wixqa_cases(project_root)
    if not cases:
        profile = _benchmark_profile(cases=[], results=[], metrics={}, status="not_configured")
        report = {
            "dataset": "Wix/WixQA expert-written",
            "benchmark_track": "external_public_enterprise_rag",
            "status": "not_configured",
            "case_count": 0,
            "metrics": {},
            "benchmark_profile": profile["summary"],
            "notes": [
                (
                    "Add data/public/wixqa_public_rag_sample.jsonl or run "
                    "scripts/prepare_wixqa_public_benchmark.py after downloading "
                    "the WixQA expert-written QA file and KB corpus."
                )
            ],
        }
        _write_all(project_root, report, profile, [], _empty_retriever_comparison())
        return report

    documents = _documents_from_cases(cases)
    results_by_system = {
        system["system_id"]: [
            _evaluate_case(case, documents, system=system) for case in cases
        ]
        for system in WIXQA_RETRIEVER_SYSTEMS
    }
    results = results_by_system[WIXQA_PRIMARY_RETRIEVER_ID]
    metrics = _summarize(results)
    retriever_comparison = _retriever_comparison(results_by_system)
    profile = _benchmark_profile(
        cases=cases,
        results=results,
        metrics=metrics,
        status="evaluated",
    )
    report = {
        "dataset": "Wix/WixQA expert-written",
        "benchmark_track": "external_public_enterprise_rag",
        "status": "evaluated",
        "source_url": "https://huggingface.co/datasets/Wix/WixQA",
        "license": "MIT",
        "sample_path": str(WIXQA_SAMPLE_PATH).replace("\\", "/"),
        "case_count": len(results),
        "document_count": len(documents),
        "multi_article_case_count": sum(row.multi_article_required for row in results),
        "primary_retriever": retriever_comparison["primary_retriever"],
        "metrics": metrics,
        "retriever_comparison": retriever_comparison["summary"],
        "retriever_systems": retriever_comparison["systems"],
        "benchmark_profile": profile["summary"],
        "failure_reasons": _failure_reason_counts(results),
        "taxonomy_labels": _taxonomy_label_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            (
                "This is a second external public-data benchmark track using real "
                "enterprise-support questions and public Wix Help Center articles."
            ),
            (
                "It complements TechQA and the controlled synthetic benchmark; it "
                "does not replace safety red-team cases or synthetic tool-use cases."
            ),
            "The report is deterministic and uses no paid API calls.",
        ],
    }
    _write_all(project_root, report, profile, results, retriever_comparison, results_by_system)
    return report


def write_wixqa_sample(
    project_root: Path,
    *,
    limit: int = WIXQA_DEFAULT_SAMPLE_LIMIT,
    max_context_chars: int = 2400,
) -> Path:
    qa_path = project_root / WIXQA_QA_RAW_PATH
    corpus_path = project_root / WIXQA_CORPUS_RAW_PATH
    if not qa_path.exists() or not corpus_path.exists():
        raise FileNotFoundError(
            "Expected data/public/wixqa_expertwritten_test.jsonl and "
            "data/public/wixqa_kb_corpus.jsonl. Download them from "
            "https://huggingface.co/datasets/Wix/WixQA."
        )
    corpus_by_id = {str(row["id"]): row for row in read_jsonl(corpus_path)}
    sample_rows = []
    for index, row in enumerate(read_jsonl(qa_path), start=1):
        article_ids = [str(article_id) for article_id in row.get("article_ids", [])]
        contexts = [
            _compact_document(corpus_by_id[article_id], max_context_chars=max_context_chars)
            for article_id in article_ids
            if article_id in corpus_by_id
        ]
        if not article_ids or len(contexts) != len(article_ids):
            continue
        sample_rows.append(
            {
                "id": f"WIXQA-EXPERT-{index:04d}",
                "question": str(row["question"]).strip(),
                "answer": str(row.get("answer", "")).strip(),
                "article_ids": article_ids,
                "contexts": contexts,
            }
        )
        if len(sample_rows) >= limit:
            break
    output_path = project_root / WIXQA_SAMPLE_PATH
    write_jsonl(output_path, sample_rows)
    return output_path


def load_wixqa_cases(project_root: Path) -> list[dict[str, Any]]:
    sample_path = project_root / WIXQA_SAMPLE_PATH
    if sample_path.exists():
        return read_jsonl(sample_path)
    return []


def _write_all(
    project_root: Path,
    report: dict[str, Any],
    profile: dict[str, Any],
    results: list[WixQACaseResult],
    retriever_comparison: dict[str, Any],
    results_by_system: dict[str, list[WixQACaseResult]] | None = None,
) -> None:
    write_json(project_root / WIXQA_SUMMARY_PATH, report)
    write_json(project_root / WIXQA_PROFILE_PATH, profile)
    write_jsonl(project_root / WIXQA_CASES_PATH, (asdict(row) for row in results))
    write_json(project_root / WIXQA_RETRIEVER_COMPARISON_PATH, retriever_comparison)
    flattened = []
    for system_results in (results_by_system or {}).values():
        flattened.extend(asdict(row) for row in system_results)
    write_jsonl(project_root / WIXQA_RETRIEVER_CASES_PATH, flattened)


def _compact_document(row: dict[str, Any], *, max_context_chars: int) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "title": str(row.get("title", "")).strip(),
        "url": str(row.get("url", "")).strip(),
        "article_type": str(row.get("article_type", "")).strip(),
        "text": str(row.get("contents", "")).strip()[:max_context_chars],
    }


def _documents_from_cases(cases: list[dict[str, Any]]) -> list[WixQADocument]:
    documents_by_id: dict[str, WixQADocument] = {}
    for case in cases:
        for context in case.get("contexts", []):
            document_id = str(context["id"])
            if document_id in documents_by_id:
                continue
            documents_by_id[document_id] = WixQADocument(
                document_id=document_id,
                title=str(context.get("title", document_id)),
                text=str(context.get("text", "")),
                article_type=str(context.get("article_type", "")),
            )
    return sorted(documents_by_id.values(), key=lambda document: document.document_id)


def _evaluate_case(
    case: dict[str, Any],
    documents: list[WixQADocument],
    *,
    system: dict[str, str],
) -> WixQACaseResult:
    retrieved = _retrieve(
        str(case["question"]),
        documents,
        top_k=3,
        system_id=system["system_id"],
    )
    retrieved_ids = [document.document_id for document in retrieved]
    expected_ids = [str(article_id) for article_id in case.get("article_ids", [])]
    expected_rank = _expected_rank(expected_ids, retrieved_ids)
    retrieval_hit_at_3 = bool(expected_rank is not None and expected_rank <= 3)
    top1_match = expected_rank == 1
    failure_reasons = _failure_reasons(
        retrieval_hit_at_3=retrieval_hit_at_3,
        top1_match=top1_match,
    )
    return WixQACaseResult(
        system_id=system["system_id"],
        system_label=system["label"],
        case_id=str(case["id"]),
        expected_citation_ids=expected_ids,
        retrieved_citation_ids=retrieved_ids,
        expected_rank=expected_rank,
        top_score=retrieved[0].score if retrieved else 0.0,
        retrieval_hit_at_3=retrieval_hit_at_3,
        top1_match=top1_match,
        multi_article_required=len(expected_ids) > 1,
        failure_reasons=failure_reasons,
        taxonomy_source="public_wixqa_retrieval",
        taxonomy_labels=labels_for_failure_reasons(failure_reasons),
    )


def _retrieve(
    question: str,
    documents: list[WixQADocument],
    *,
    top_k: int,
    system_id: str,
) -> list[WixQARetrievedDocument]:
    if not documents:
        return []
    if system_id == "keyword_title_baseline":
        return _retrieve_keyword_title_baseline(question, documents, top_k=top_k)

    doc_features = [_document_features(document) for document in documents]
    idf = _inverse_document_frequency(doc_features)
    query_tokens = _token_sequence(question)
    query_vector = _tfidf_vector(_query_features(question), idf)
    retrieved = []
    for document, features in zip(documents, doc_features, strict=True):
        document_vector = _tfidf_vector(features, idf)
        cosine_score = _cosine_similarity(query_vector, document_vector) * 100
        title_score = len(set(query_tokens) & set(_token_sequence(document.title))) * 3.0
        exact_phrase_score = _exact_phrase_score(question, document.title)
        score = round(cosine_score + title_score + exact_phrase_score, 4)
        if score <= 0:
            continue
        retrieved.append(WixQARetrievedDocument(document.document_id, document.title, score))
    return sorted(retrieved, key=lambda row: (-row.score, row.document_id))[:top_k]


def _retrieve_keyword_title_baseline(
    question: str,
    documents: list[WixQADocument],
    *,
    top_k: int,
) -> list[WixQARetrievedDocument]:
    query_tokens = set(_token_sequence(question))
    retrieved = []
    for document in documents:
        title_tokens = set(_token_sequence(document.title))
        score = len(query_tokens & title_tokens) * 4.0
        if score <= 0:
            continue
        retrieved.append(WixQARetrievedDocument(document.document_id, document.title, score))
    return sorted(retrieved, key=lambda row: (-row.score, row.document_id))[:top_k]


def _benchmark_profile(
    *,
    cases: list[dict[str, Any]],
    results: list[WixQACaseResult],
    metrics: dict[str, float],
    status: str,
) -> dict[str, Any]:
    context_counts = [len(case.get("contexts", [])) for case in cases]
    article_types = Counter(
        str(context.get("article_type", "unknown"))
        for case in cases
        for context in case.get("contexts", [])
    )
    failed_cases = [row for row in results if row.failure_reasons]
    summary = {
        "status": status,
        "dataset": "Wix/WixQA expert-written",
        "benchmark_track": "external_public_enterprise_rag",
        "license": "MIT",
        "source_url": "https://huggingface.co/datasets/Wix/WixQA",
        "sample_path": str(WIXQA_SAMPLE_PATH).replace("\\", "/"),
        "sample_case_count": len(cases),
        "unique_document_count": len(
            {str(context.get("id")) for case in cases for context in case.get("contexts", [])}
        ),
        "multi_article_case_count": sum(len(case.get("article_ids", [])) > 1 for case in cases),
        "multi_article_case_share": _rate(
            len(case.get("article_ids", [])) > 1 for case in cases
        ),
        "average_grounding_documents_per_case": round(
            sum(context_counts) / len(context_counts), 4
        )
        if context_counts
        else 0.0,
        "article_type_counts": dict(sorted(article_types.items())),
        "tracked_sample_default_limit": WIXQA_DEFAULT_SAMPLE_LIMIT,
        "sample_selection_policy": "first_expertwritten_cases_with_all_articles_present",
        "sample_scope": "tracked_compact_public_sample",
        "provider_backed_embedding_result_published": False,
        "failed_case_count": len(failed_cases),
        "failure_rate": _rate(bool(row.failure_reasons) for row in results),
    }
    if metrics:
        summary["retrieval_hit_rate_at_3"] = metrics["retrieval_hit_rate_at_3"]
        summary["top1_citation_accuracy"] = metrics["top1_citation_accuracy"]
    return {
        "report_type": "wixqa_public_benchmark_profile",
        "summary": summary,
        "coverage_notes": [
            (
                "WixQA is reported as a separate public enterprise-support RAG track, "
                "not as controlled synthetic operations evidence."
            ),
            (
                "The compact tracked sample keeps CI and public deployment deterministic "
                "while preserving source attribution and license metadata."
            ),
        ],
    }


def _retriever_comparison(
    results_by_system: dict[str, list[WixQACaseResult]],
) -> dict[str, Any]:
    systems = []
    primary_metrics = _summarize(results_by_system[WIXQA_PRIMARY_RETRIEVER_ID])
    baseline_metrics = _summarize(results_by_system["keyword_title_baseline"])
    for system in WIXQA_RETRIEVER_SYSTEMS:
        results = results_by_system[system["system_id"]]
        systems.append(
            {
                "system_id": system["system_id"],
                "label": system["label"],
                "description": system["description"],
                "case_count": len(results),
                "failed_case_count": sum(1 for row in results if row.failure_reasons),
                "metrics": _summarize(results),
            }
        )
    return {
        "report_type": "wixqa_public_retriever_comparison",
        "status": "evaluated",
        "dataset": "Wix/WixQA expert-written",
        "benchmark_track": "external_public_enterprise_rag",
        "primary_retriever": next(
            system for system in systems if system["system_id"] == WIXQA_PRIMARY_RETRIEVER_ID
        ),
        "summary": {
            "system_count": len(systems),
            "primary_system_id": WIXQA_PRIMARY_RETRIEVER_ID,
            "baseline_system_id": "keyword_title_baseline",
            "retrieval_hit_rate_at_3_lift": round(
                primary_metrics["retrieval_hit_rate_at_3"]
                - baseline_metrics["retrieval_hit_rate_at_3"],
                4,
            ),
            "top1_citation_accuracy_lift": round(
                primary_metrics["top1_citation_accuracy"]
                - baseline_metrics["top1_citation_accuracy"],
                4,
            ),
        },
        "systems": systems,
        "notes": [
            "This comparison is local and deterministic.",
            "Provider-backed embedding comparison remains optional.",
        ],
    }


def _empty_retriever_comparison() -> dict[str, Any]:
    return {
        "report_type": "wixqa_public_retriever_comparison",
        "status": "not_configured",
        "dataset": "Wix/WixQA expert-written",
        "benchmark_track": "external_public_enterprise_rag",
        "summary": {"system_count": 0},
        "systems": [],
        "notes": [],
    }


def _summarize(results: list[WixQACaseResult]) -> dict[str, float]:
    return {
        "retrieval_hit_rate_at_3": _rate(row.retrieval_hit_at_3 for row in results),
        "top1_citation_accuracy": _rate(row.top1_match for row in results),
        "mean_reciprocal_rank_at_3": _mean_reciprocal_rank(results),
        "multi_article_retrieval_hit_rate_at_3": _rate(
            row.retrieval_hit_at_3 for row in results if row.multi_article_required
        ),
    }


def _failure_reasons(*, retrieval_hit_at_3: bool, top1_match: bool) -> list[str]:
    if not retrieval_hit_at_3:
        return ["expected_document_not_retrieved_at_3"]
    if not top1_match:
        return ["expected_document_retrieved_but_not_top1"]
    return []


def _failure_reason_counts(results: list[WixQACaseResult]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in results:
        counts.update(row.failure_reasons)
    return dict(sorted(counts.items()))


def _taxonomy_label_counts(results: list[WixQACaseResult]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in results:
        counts.update(row.taxonomy_labels)
    return dict(sorted(counts.items()))


def _failure_examples(
    results: list[WixQACaseResult],
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row.case_id,
            "failure_reasons": row.failure_reasons,
            "taxonomy_labels": row.taxonomy_labels,
            "expected_citation_ids": row.expected_citation_ids,
            "retrieved_citation_ids": row.retrieved_citation_ids,
            "expected_rank": row.expected_rank,
            "top_score": row.top_score,
        }
        for row in results
        if row.failure_reasons
    ][:limit]


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


def _mean_reciprocal_rank(results: list[WixQACaseResult]) -> float:
    if not results:
        return 0.0
    score = 0.0
    for row in results:
        if row.expected_rank is not None and row.expected_rank <= 3:
            score += 1 / row.expected_rank
    return round(score / len(results), 4)


def _document_features(document: WixQADocument) -> list[str]:
    features = _vector_features(document.title, prefix="title") * 3
    features.extend(_vector_features(document.article_type, prefix="type") * 2)
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
    "can",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
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
    "wix",
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
