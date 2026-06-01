from __future__ import annotations

import re
from dataclasses import dataclass
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


@dataclass(frozen=True)
class BaselineAnswer:
    answer: str
    issue_category: str | None
    team: str | None
    next_action: str | None
    citations: list[str]
    retrieved_sections: list[RetrievedSection]
    abstained: bool


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
    "repair_queue_backlog": ["repair", "queue", "backlog", "triage", "growing"],
    "missing_kyc_document": ["missing", "kyc", "document", "artifact", "absent"],
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
    "schema_drift": ["schema", "drift", "shape", "version", "incoming"],
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

        title_tokens = _tokenize(str(section["title"]))
        content_tokens = _tokenize(str(section["content"]))
        score = (len(query_tokens & title_tokens) * 5) + len(query_tokens & content_tokens)
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
        negation_penalty = _negated_category_penalty(question, category)
        score = lexical_score + semantic_score + alias_score + phrase_score + team_score
        score -= negation_penalty

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


def _negated_category_penalty(question: str, category: str) -> float:
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


def _token_sequence(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS
    ]
