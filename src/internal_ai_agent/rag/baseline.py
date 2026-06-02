from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from hashlib import blake2b
from math import log
from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl
from internal_ai_agent.security.policy import policy_refusal, should_block_request


@dataclass(frozen=True)
class RetrievedSection:
    section_id: str
    title: str
    team: str
    content: str
    score: float
    score_breakdown: dict[str, float] | None = None


@dataclass(frozen=True)
class BaselineAnswer:
    answer: str
    issue_category: str | None
    team: str | None
    next_action: str | None
    citations: list[str]
    retrieved_sections: list[RetrievedSection]
    abstained: bool


@dataclass(frozen=True)
class LocalEmbeddingRecord:
    section: dict[str, Any]
    embedding: list[float]


SYSTEM_HINTS = {
    "payments_ops": ["aurora", "payment", "payments", "gateway", "batch", "settlement"],
    "client_onboarding": ["nova", "client", "onboarding", "intake", "kyc", "activation"],
    "trade_support": ["helios", "trade", "allocation", "confirmation", "booking"],
    "data_quality": ["atlas", "data", "schema", "feed", "control", "lineage"],
}

SEMANTIC_ALIASES = {
    "file_validation_failed": ["file", "validation", "schema", "rejected", "reject"],
    "duplicate_batch_detected": ["duplicate", "duplicated", "batch", "idempotency", "replay"],
    "settlement_delay": ["settlement", "delay", "waiting", "window", "retry"],
    "unmatched_settlement_reference": ["unmatched", "settlement", "reference", "reconcile"],
    "cutoff_window_missed": ["cutoff", "missed", "processing", "deadline"],
    "repair_queue_backlog": [
        "repair",
        "queue",
        "backlog",
        "triage",
        "growing",
        "items",
        "piling",
        "rows",
    ],
    "missing_kyc_document": [
        "missing",
        "kyc",
        "document",
        "artifact",
        "artefact",
        "absent",
        "packet",
        "supplied",
    ],
    "entity_match_review": ["entity", "match", "screening", "review", "possible"],
    "workflow_sla_breach": ["workflow", "sla", "breach", "service", "target", "exceeded"],
    "beneficial_owner_missing": ["beneficial", "owner", "ownership", "missing", "activation"],
    "screening_alert_review": ["screening", "alert", "evidence", "decision", "review"],
    "tax_form_expired": ["tax", "form", "expired", "packet"],
    "allocation_mismatch": ["allocation", "mismatch", "reconcile", "trade", "details"],
    "confirmation_pending": ["confirmation", "pending", "counterparty", "arrived", "reminder"],
    "reference_data_gap": ["reference", "data", "gap", "fields", "missing"],
    "trade_date_dispute": ["trade", "date", "dispute", "timestamps", "disagree"],
    "commission_code_missing": ["commission", "code", "missing", "booking"],
    "booking_status_stuck": ["booking", "status", "stuck", "stopped", "progressing"],
    "stale_reference_data": ["stale", "reference", "data", "freshness", "older", "feed"],
    "schema_drift": ["schema", "drift", "shape", "version", "incoming", "payload", "match"],
    "control_threshold_breach": ["control", "threshold", "breach", "exceeded", "configured"],
    "duplicate_record_cluster": ["duplicate", "duplicated", "record", "records", "cluster"],
    "lineage_check_failed": ["lineage", "check", "failed", "trace", "upstream"],
    "late_arriving_feed": ["late", "arriving", "feed", "downstream", "waiting"],
}


def load_runbooks(project_root: Path) -> list[dict[str, Any]]:
    return read_jsonl(project_root / "data/synthetic/raw_docs/runbooks.jsonl")


def retrieve_baseline(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    top_k: int = 3,
) -> list[RetrievedSection]:
    """Naive team-level retrieval.

    This baseline intentionally uses broad system/team hints rather than procedure-level matching.
    It behaves like an early prototype: often finds the right team, but not the right section.
    """

    normalized = question.lower()
    scored: list[RetrievedSection] = []
    for section in runbooks:
        team = str(section["team"])
        hints = SYSTEM_HINTS.get(team, [])
        score = sum(1 for hint in hints if hint in normalized)
        if score > 0:
            scored.append(
                RetrievedSection(
                    section_id=str(section["section_id"]),
                    title=str(section["title"]),
                    team=team,
                    content=str(section["content"]),
                    score=score,
                )
            )

    if not scored:
        return []

    return sorted(scored, key=lambda item: (-item.score, item.section_id))[:top_k]


def answer_with_baseline(question: str, runbooks: list[dict[str, Any]]) -> BaselineAnswer:
    retrieved = retrieve_baseline(question, runbooks, top_k=3)
    if not retrieved:
        return BaselineAnswer(
            answer="I do not have enough synthetic runbook evidence to answer this safely.",
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    chosen = retrieved[0]
    issue_category = chosen.title.lower().replace(" ", "_")
    next_action = _extract_next_action(chosen.content)
    answer = (
        f"Likely issue: {chosen.title}. "
        f"Recommended next action: {next_action} "
        f"Source: {chosen.section_id}."
    )
    return BaselineAnswer(
        answer=answer,
        issue_category=issue_category,
        team=chosen.team,
        next_action=next_action,
        citations=[chosen.section_id],
        retrieved_sections=retrieved,
        abstained=False,
    )


def retrieve_lexical(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
    top_k: int = 3,
) -> list[RetrievedSection]:
    query_tokens = _tokenize(question)
    scored: list[RetrievedSection] = []

    for section in runbooks:
        allowed_roles = section.get("allowed_roles", [])
        if user_role not in allowed_roles:
            continue

        title = str(section["title"])
        category = title.lower().replace(" ", "_")
        title_tokens = _tokenize(title)
        content_tokens = _tokenize(str(section["content"]))
        score = (len(query_tokens & title_tokens) * 5) + len(query_tokens & content_tokens)
        score += _current_evidence_score(question, category, str(section["team"]))
        if score == 0:
            continue

        scored.append(
            RetrievedSection(
                section_id=str(section["section_id"]),
                title=str(section["title"]),
                team=str(section["team"]),
                content=str(section["content"]),
                score=score,
            )
        )

    return sorted(scored, key=lambda item: (-item.score, item.section_id))[:top_k]


def answer_with_lexical(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
) -> BaselineAnswer:
    if should_block_request(question) or _should_abstain_for_safety(question):
        return BaselineAnswer(
            answer=policy_refusal(),
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    retrieved = retrieve_lexical(question, runbooks, user_role=user_role, top_k=3)
    if not retrieved:
        return BaselineAnswer(
            answer="I do not have enough synthetic runbook evidence to answer this safely.",
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    chosen = retrieved[0]
    issue_category = chosen.title.lower().replace(" ", "_")
    next_action = _extract_next_action(chosen.content)
    answer = (
        f"Likely issue: {chosen.title}. "
        f"Recommended next action: {next_action} "
        f"Citation: {chosen.section_id}."
    )
    return BaselineAnswer(
        answer=answer,
        issue_category=issue_category,
        team=chosen.team,
        next_action=next_action,
        citations=[chosen.section_id],
        retrieved_sections=retrieved,
        abstained=False,
    )


def retrieve_hybrid(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
    top_k: int = 3,
) -> list[RetrievedSection]:
    """Hybrid lexical plus local semantic-feature retrieval.

    The semantic side is a deterministic sparse vector built from procedure aliases. It is not a
    replacement for embeddings, but it makes paraphrase behavior measurable without API keys.
    """

    query_tokens = _tokenize(question)
    query_vector = _semantic_vector(question)
    scored: list[RetrievedSection] = []

    for section in runbooks:
        allowed_roles = section.get("allowed_roles", [])
        if user_role not in allowed_roles:
            continue

        title = str(section["title"])
        content = str(section["content"])
        category = title.lower().replace(" ", "_")
        title_tokens = _tokenize(title)
        content_tokens = _tokenize(content)
        section_vector = _semantic_vector(" ".join([title, content]))

        lexical_score = (len(query_tokens & title_tokens) * 5) + len(query_tokens & content_tokens)
        semantic_score = _cosine_similarity(query_vector, section_vector) * 12
        alias_score = _alias_overlap(query_tokens, category) * 4
        phrase_score = _title_phrase_score(question, category)
        team_score = _team_hint_score(question, str(section["team"])) * 0.5
        current_evidence_score = _current_evidence_score(question, category, str(section["team"]))
        negation_penalty = _negated_category_penalty(question, category)
        stale_context_penalty = _stale_context_penalty(question, category)
        score = (
            lexical_score
            + semantic_score
            + alias_score
            + phrase_score
            + team_score
            + current_evidence_score
        )
        score -= negation_penalty + stale_context_penalty

        if score <= 0:
            continue

        scored.append(
            RetrievedSection(
                section_id=str(section["section_id"]),
                title=title,
                team=str(section["team"]),
                content=content,
                score=round(score, 4),
            )
        )

    return sorted(scored, key=lambda item: (-item.score, item.section_id))[:top_k]


def answer_with_hybrid(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
) -> BaselineAnswer:
    if should_block_request(question) or _should_abstain_for_safety(question):
        return BaselineAnswer(
            answer=policy_refusal(),
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    retrieved = retrieve_hybrid(question, runbooks, user_role=user_role, top_k=3)
    if not retrieved:
        return BaselineAnswer(
            answer="I do not have enough synthetic runbook evidence to answer this safely.",
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    chosen = retrieved[0]
    issue_category = chosen.title.lower().replace(" ", "_")
    next_action = _extract_next_action(chosen.content)
    answer = (
        f"Likely issue: {chosen.title}. "
        f"Recommended next action: {next_action} "
        f"Citation: {chosen.section_id}."
    )
    return BaselineAnswer(
        answer=answer,
        issue_category=issue_category,
        team=chosen.team,
        next_action=next_action,
        citations=[chosen.section_id],
        retrieved_sections=retrieved,
        abstained=False,
    )


def retrieve_vector(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
    top_k: int = 3,
) -> list[RetrievedSection]:
    """Local TF-IDF vector retrieval with lightweight keyword reranking.

    This is still a local lab index, not a production vector database. It gives the project a
    real vector-space retrieval baseline using IDF-weighted cosine similarity, concept aliases,
    title boosts, and character n-grams for typo tolerance.
    """

    eligible_sections = [
        section
        for section in runbooks
        if user_role in section.get("allowed_roles", [])
    ]
    if not eligible_sections:
        return []

    doc_features = [_section_vector_features(section) for section in eligible_sections]
    idf = _inverse_document_frequency(doc_features)
    query_features = _query_vector_features(question)
    query_vector = _tfidf_vector(query_features, idf)
    scored: list[RetrievedSection] = []

    for section, features in zip(eligible_sections, doc_features, strict=True):
        title = str(section["title"])
        content = str(section["content"])
        category = title.lower().replace(" ", "_")
        section_vector = _tfidf_vector(features, idf)

        vector_score = _cosine_similarity(query_vector, section_vector) * 100
        alias_score = _alias_overlap(_tokenize(question), category) * 5
        title_phrase_score = _title_phrase_score(question, category) * 0.75
        team_hint_score = _team_hint_score(question, str(section["team"])) * 0.25
        evidence_score = _current_evidence_score(question, category, str(section["team"])) * 0.75
        negation_penalty = _negated_category_penalty(question, category)
        stale_context_penalty = _stale_context_penalty(question, category)
        score = (
            vector_score
            + alias_score
            + title_phrase_score
            + team_hint_score
            + evidence_score
            - negation_penalty
            - stale_context_penalty
        )

        if score <= 0:
            continue

        scored.append(
            RetrievedSection(
                section_id=str(section["section_id"]),
                title=title,
                team=str(section["team"]),
                content=content,
                score=round(score, 4),
                score_breakdown={
                    "vector": round(vector_score, 4),
                    "alias": round(alias_score, 4),
                    "title_phrase": round(title_phrase_score, 4),
                    "team_hint": round(team_hint_score, 4),
                    "current_evidence": round(evidence_score, 4),
                    "negation_penalty": round(negation_penalty, 4),
                    "stale_context_penalty": round(stale_context_penalty, 4),
                },
            )
        )

    return sorted(scored, key=lambda item: (-item.score, item.section_id))[:top_k]


def answer_with_vector(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
) -> BaselineAnswer:
    if should_block_request(question) or _should_abstain_for_safety(question):
        return BaselineAnswer(
            answer=policy_refusal(),
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    retrieved = retrieve_vector(question, runbooks, user_role=user_role, top_k=3)
    if not retrieved:
        return BaselineAnswer(
            answer="I do not have enough synthetic runbook evidence to answer this safely.",
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    chosen = retrieved[0]
    issue_category = chosen.title.lower().replace(" ", "_")
    next_action = _extract_next_action(chosen.content)
    answer = (
        f"Likely issue: {chosen.title}. "
        f"Recommended next action: {next_action} "
        f"Citation: {chosen.section_id}."
    )
    return BaselineAnswer(
        answer=answer,
        issue_category=issue_category,
        team=chosen.team,
        next_action=next_action,
        citations=[chosen.section_id],
        retrieved_sections=retrieved,
        abstained=False,
    )


def retrieve_embedding_store(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
    top_k: int = 3,
) -> list[RetrievedSection]:
    """Local embedding-store retrieval using stable hashed embeddings.

    The store is deliberately dependency-free: it embeds runbook sections into fixed-size dense
    vectors with feature hashing, then searches by cosine similarity. This keeps the experiment
    reproducible while making the storage/search contract close to an embedding-backed vector DB.
    """

    store = _build_local_embedding_store(runbooks, user_role=user_role)
    if not store:
        return []

    query_tokens = _tokenize(question)
    query_embedding = _embed_text(question, is_query=True)
    scored: list[RetrievedSection] = []

    for record in store:
        section = record.section
        title = str(section["title"])
        content = str(section["content"])
        category = title.lower().replace(" ", "_")

        embedding_score = _dense_cosine_similarity(query_embedding, record.embedding) * 100
        alias_score = _alias_overlap(query_tokens, category) * 6
        title_phrase_score = _title_phrase_score(question, category) * 2
        team_hint_score = _team_hint_score(question, str(section["team"])) * 0.25
        evidence_score = _current_evidence_score(question, category, str(section["team"])) * 0.75
        negation_penalty = _negated_category_penalty(question, category)
        stale_context_penalty = _stale_context_penalty(question, category)
        score = (
            embedding_score
            + alias_score
            + title_phrase_score
            + team_hint_score
            + evidence_score
            - negation_penalty
            - stale_context_penalty
        )

        if score <= 0:
            continue

        scored.append(
            RetrievedSection(
                section_id=str(section["section_id"]),
                title=title,
                team=str(section["team"]),
                content=content,
                score=round(score, 4),
                score_breakdown={
                    "embedding": round(embedding_score, 4),
                    "alias": round(alias_score, 4),
                    "title_phrase": round(title_phrase_score, 4),
                    "team_hint": round(team_hint_score, 4),
                    "current_evidence": round(evidence_score, 4),
                    "negation_penalty": round(negation_penalty, 4),
                    "stale_context_penalty": round(stale_context_penalty, 4),
                },
            )
        )

    return sorted(scored, key=lambda item: (-item.score, item.section_id))[:top_k]


def answer_with_embedding_store(
    question: str,
    runbooks: list[dict[str, Any]],
    *,
    user_role: str = "operations_analyst",
) -> BaselineAnswer:
    if should_block_request(question) or _should_abstain_for_safety(question):
        return BaselineAnswer(
            answer=policy_refusal(),
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    retrieved = retrieve_embedding_store(question, runbooks, user_role=user_role, top_k=3)
    if not retrieved:
        return BaselineAnswer(
            answer="I do not have enough synthetic runbook evidence to answer this safely.",
            issue_category=None,
            team=None,
            next_action=None,
            citations=[],
            retrieved_sections=[],
            abstained=True,
        )

    chosen = retrieved[0]
    issue_category = chosen.title.lower().replace(" ", "_")
    next_action = _extract_next_action(chosen.content)
    answer = (
        f"Likely issue: {chosen.title}. "
        f"Recommended next action: {next_action} "
        f"Citation: {chosen.section_id}."
    )
    return BaselineAnswer(
        answer=answer,
        issue_category=issue_category,
        team=chosen.team,
        next_action=next_action,
        citations=[chosen.section_id],
        retrieved_sections=retrieved,
        abstained=False,
    )


def _extract_next_action(content: str) -> str:
    marker = "Recommended next action:"
    if marker not in content:
        return "Review the matching synthetic runbook section."
    action = content.split(marker, maxsplit=1)[1]
    return action.split(" If the evidence is incomplete", maxsplit=1)[0].strip()


def _should_abstain_for_safety(question: str) -> bool:
    normalized = question.lower()
    weak_evidence_signals = [
        "no error category",
        "no generated control output",
        "no workflow evidence",
        "no details",
        "exact procedure and next action anyway",
        "conflicting evidence",
        "do not guess the procedure",
        "active platform and issue are not established",
        "active platform and issue are not clear",
        "ambiguous handoff",
    ]
    injection_signals: list[str] = []
    return any(signal in normalized for signal in weak_evidence_signals + injection_signals)


STOPWORDS = {
    "a",
    "an",
    "and",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "what",
    "with",
}


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def _semantic_vector(text: str) -> dict[str, float]:
    tokens = _tokenize(text)
    vector: dict[str, float] = {token: 1.0 for token in tokens}
    for concept, aliases in SEMANTIC_ALIASES.items():
        matches = sum(1 for alias in aliases if alias in tokens)
        if matches:
            vector[f"concept:{concept}"] = float(matches)
    return vector


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


def _section_vector_features(section: dict[str, Any]) -> list[str]:
    title = str(section["title"])
    content = str(section["content"])
    team = str(section["team"])
    category = title.lower().replace(" ", "_")
    features: list[str] = []
    features.extend(_vector_features(title, prefix="title") * 3)
    features.extend(_vector_features(content, prefix="body"))
    features.extend([f"team:{hint}" for hint in SYSTEM_HINTS.get(team, [])])
    features.extend([f"concept:{category}"] * 5)
    features.extend(f"alias:{alias}" for alias in SEMANTIC_ALIASES.get(category, []))
    return features


def _query_vector_features(question: str) -> list[str]:
    tokens = _tokenize(question)
    features = _vector_features(question, prefix="query")
    for category, aliases in SEMANTIC_ALIASES.items():
        matches = sum(1 for alias in aliases if alias in tokens)
        if matches:
            features.extend([f"concept:{category}"] * matches)
            features.extend(f"alias:{alias}" for alias in aliases if alias in tokens)
    return features


def _vector_features(text: str, *, prefix: str) -> list[str]:
    tokens = _token_sequence(text)
    features = [f"token:{token}" for token in tokens]
    features.extend(f"char4:{gram}" for token in tokens for gram in _char_ngrams(token, 4))
    features.extend(
        f"bigram:{left}_{right}"
        for left, right in zip(tokens, tokens[1:], strict=False)
    )
    features.extend(f"{prefix}_token:{token}" for token in tokens)
    return features


def _char_ngrams(token: str, size: int) -> list[str]:
    if len(token) < size:
        return []
    return [token[index : index + size] for index in range(len(token) - size + 1)]


def _inverse_document_frequency(doc_features: list[list[str]]) -> dict[str, float]:
    doc_count = len(doc_features)
    document_frequency: Counter[str] = Counter()
    for features in doc_features:
        document_frequency.update(set(features))
    return {
        feature: log((doc_count + 1) / (frequency + 1)) + 1
        for feature, frequency in document_frequency.items()
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


EMBEDDING_DIMENSIONS = 96


def _build_local_embedding_store(
    runbooks: list[dict[str, Any]],
    *,
    user_role: str,
) -> list[LocalEmbeddingRecord]:
    records: list[LocalEmbeddingRecord] = []
    for section in runbooks:
        if user_role not in section.get("allowed_roles", []):
            continue
        text = _section_embedding_text(section)
        records.append(LocalEmbeddingRecord(section=section, embedding=_embed_text(text)))
    return records


def _section_embedding_text(section: dict[str, Any]) -> str:
    title = str(section["title"])
    team = str(section["team"])
    category = title.lower().replace(" ", "_")
    aliases = " ".join(SEMANTIC_ALIASES.get(category, []))
    team_hints = " ".join(SYSTEM_HINTS.get(team, []))
    return " ".join([title, title, str(section["content"]), aliases, aliases, team_hints])


def _embed_text(text: str, *, is_query: bool = False) -> list[float]:
    features = _embedding_features(text, is_query=is_query)
    vector = [0.0] * EMBEDDING_DIMENSIONS
    for feature, weight in features.items():
        digest = blake2b(feature.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign * weight
    return _normalize_dense_vector(vector)


def _embedding_features(text: str, *, is_query: bool) -> dict[str, float]:
    tokens = _token_sequence(text)
    counts: Counter[str] = Counter()
    counts.update(f"token:{token}" for token in tokens)
    counts.update(f"char3:{gram}" for token in tokens for gram in _char_ngrams(token, 3))
    counts.update(
        f"bigram:{left}_{right}" for left, right in zip(tokens, tokens[1:], strict=False)
    )

    token_set = set(tokens)
    for category, aliases in SEMANTIC_ALIASES.items():
        matches = [alias for alias in aliases if alias in token_set]
        if matches:
            counts[f"concept:{category}"] += 4 if is_query else 6
            counts.update(f"alias:{alias}" for alias in matches)

    return {feature: 1.0 + log(count) for feature, count in counts.items()}


def _normalize_dense_vector(vector: list[float]) -> list[float]:
    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _dense_cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(
        left_value * right_value
        for left_value, right_value in zip(left, right, strict=True)
    )


def _alias_overlap(query_tokens: set[str], category: str) -> int:
    aliases = set(SEMANTIC_ALIASES.get(category, []))
    return len(query_tokens & aliases)


def _title_phrase_score(question: str, category: str) -> float:
    normalized = " ".join(_token_sequence(question))
    title_tokens = _token_sequence(category.replace("_", " "))
    if len(title_tokens) < 2:
        return 0.0
    matching_pairs = 0
    for left, right in zip(title_tokens, title_tokens[1:], strict=False):
        if f"{left} {right}" in normalized:
            matching_pairs += 1
    return matching_pairs * 8.0


def _team_hint_score(question: str, team: str) -> int:
    normalized = question.lower()
    return sum(1 for hint in SYSTEM_HINTS.get(team, []) if hint in normalized)


CURRENT_EVIDENCE_MARKERS = (
    "current evidence bundle",
    "current evidence",
    "current ticket",
    "actual evidence",
    "latest control note",
)


def _current_evidence_score(question: str, category: str, team: str) -> float:
    focused_text = _current_evidence_text(question)
    if not focused_text:
        return 0.0

    focused_tokens = _tokenize(focused_text)
    category_tokens = set(_token_sequence(category.replace("_", " ")))
    alias_score = _alias_overlap(focused_tokens, category) * 7.0
    title_score = len(focused_tokens & category_tokens) * 3.0
    phrase_score = _title_phrase_score(focused_text, category) * 0.75
    team_score = _team_hint_score(focused_text, team) * 1.5
    return (
        alias_score
        + title_score
        + phrase_score
        + team_score
        + _evidence_summary_score(focused_text, category)
    )


def _current_evidence_text(question: str) -> str:
    normalized = question.lower()
    start = -1
    for marker in CURRENT_EVIDENCE_MARKERS:
        start = normalized.find(marker)
        if start >= 0:
            break
    if start < 0:
        return ""

    focused = question[start:]
    lower_focused = focused.lower()
    for end_marker in ("please give", "please cite", "what should", "which procedure"):
        end = lower_focused.find(end_marker)
        if end > 0:
            return focused[:end]
    return focused


def _evidence_summary_score(focused_text: str, category: str) -> float:
    summary = _evidence_summary_text(focused_text)
    if not summary:
        return 0.0

    summary_tokens = _tokenize(summary)
    category_tokens = set(_token_sequence(category.replace("_", " ")))
    alias_score = _alias_overlap(summary_tokens, category) * 12.0
    title_score = len(summary_tokens & category_tokens) * 5.0
    phrase_score = _title_phrase_score(summary, category) * 1.5
    return alias_score + title_score + phrase_score


def _evidence_summary_text(focused_text: str) -> str:
    lower_focused = focused_text.lower()
    marker = "this summary:"
    start = lower_focused.find(marker)
    if start < 0:
        return ""

    summary = focused_text[start + len(marker) :]
    lower_summary = summary.lower()
    for end_marker in ("the platform named", "severity is", "please give"):
        end = lower_summary.find(end_marker)
        if end > 0:
            return summary[:end]
    return summary


def _negated_category_penalty(question: str, category: str) -> float:
    normalized = question.lower()
    if category == "schema_drift" and (
        "no longer matches" in normalized or "no longer match" in normalized
    ):
        evidence_terms = {"schema", "shape", "version", "payload"}
        if evidence_terms & set(_token_sequence(question)):
            return 0.0

    tokens = _token_sequence(question)
    if not tokens:
        return 0.0

    category_tokens = _token_sequence(category.replace("_", " "))
    alias_tokens = set(SEMANTIC_ALIASES.get(category, []))
    negation_positions = [
        index
        for index, token in enumerate(tokens)
        if token in {"not", "no", "without", "isnt", "isn", "isn't"}
    ]

    for index in negation_positions:
        window = set(tokens[index + 1 : index + 7])
        if category_tokens and set(category_tokens).issubset(window):
            return 40.0
        if len(window & alias_tokens) >= 2:
            return 20.0
    return 0.0


def _stale_context_penalty(question: str, category: str) -> float:
    normalized = question.lower()
    current_start = min(
        (
            index
            for marker in CURRENT_EVIDENCE_MARKERS
            if (index := normalized.find(marker)) >= 0
        ),
        default=-1,
    )
    if current_start < 0:
        return 0.0

    earlier_context = normalized[:current_start]
    stale_markers = (
        "older comment",
        "stale comment",
        "stale thread",
        "false lead",
        "wondered whether",
        "guessed",
    )
    if not any(marker in earlier_context for marker in stale_markers):
        return 0.0

    category_phrase = category.replace("_", " ")
    if category_phrase in earlier_context:
        return 35.0

    earlier_tokens = _tokenize(earlier_context)
    if _alias_overlap(earlier_tokens, category) >= 2:
        return 20.0
    return 0.0


def _token_sequence(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS
    ]
