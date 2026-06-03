from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json, write_jsonl
from internal_ai_agent.rag.baseline import (
    BaselineAnswer,
    EmbedTexts,
    answer_with_baseline,
    answer_with_embedding_store,
    answer_with_hybrid,
    answer_with_lexical,
    answer_with_provider_embedding_store,
    answer_with_vector,
    build_provider_embedding_store,
    load_runbooks,
)


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    task_type: str
    noise_type: str
    expected_citation_ids: list[str]
    predicted_citation_ids: list[str]
    retrieved_citation_ids: list[str]
    retrieved_candidate_scores: list[dict[str, Any]]
    expected_issue_category: str
    predicted_issue_category: str | None
    expected_team: str
    predicted_team: str | None
    expected_next_action: str
    predicted_next_action: str | None
    retrieval_hit_at_3: bool
    citation_match: bool
    issue_category_match: bool
    team_match: bool
    next_action_match: bool
    abstained: bool
    expected_abstain: bool
    abstention_correct: bool
    failure_reasons: list[str]
    diagnostic: str
    recommended_fix: str


def evaluate_baseline(project_root: Path) -> dict[str, Any]:
    runbooks = load_runbooks(project_root)
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    results = [
        _evaluate_case(case, answer_with_baseline(str(case["input"]), runbooks)) for case in cases
    ]
    metrics = _summarize(results)

    report = {
        "system_version": "baseline_team_hint_retrieval",
        "dataset": "golden_cases",
        "case_count": len(results),
        "metrics": metrics,
        "by_task_type": _summarize_by_dimension(results, "task_type"),
        "by_noise_type": _summarize_by_dimension(results, "noise_type"),
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            "Baseline uses broad system/team keyword hints, not procedure-level retrieval.",
            "Metrics are deterministic and do not require paid API keys.",
        ],
    }

    write_json(project_root / "reports/baseline_eval_summary.json", report)
    write_jsonl(
        project_root / "reports/baseline_eval_cases.jsonl", (asdict(row) for row in results)
    )
    return report


def evaluate_lexical(project_root: Path) -> dict[str, Any]:
    runbooks = load_runbooks(project_root)
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    results = [
        _evaluate_case(
            case,
            answer_with_lexical(
                str(case["input"]),
                runbooks,
                user_role=str(case["user_role"]),
            ),
        )
        for case in cases
    ]
    metrics = _summarize(results)

    report = {
        "system_version": "improved_lexical_retrieval",
        "dataset": "golden_cases",
        "case_count": len(results),
        "metrics": metrics,
        "by_task_type": _summarize_by_dimension(results, "task_type"),
        "by_noise_type": _summarize_by_dimension(results, "noise_type"),
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            "Improved retrieval scores procedure title and content token overlap.",
            "Role filtering excludes runbook sections the requester is not allowed to retrieve.",
        ],
    }

    write_json(project_root / "reports/improved_eval_summary.json", report)
    write_jsonl(
        project_root / "reports/improved_eval_cases.jsonl", (asdict(row) for row in results)
    )
    return report


def evaluate_hybrid(project_root: Path) -> dict[str, Any]:
    runbooks = load_runbooks(project_root)
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    results = [
        _evaluate_case(
            case,
            answer_with_hybrid(
                str(case["input"]),
                runbooks,
                user_role=str(case["user_role"]),
            ),
        )
        for case in cases
    ]
    metrics = _summarize(results)

    report = {
        "system_version": "hybrid_sparse_semantic_retrieval",
        "dataset": "golden_cases",
        "case_count": len(results),
        "metrics": metrics,
        "by_task_type": _summarize_by_dimension(results, "task_type"),
        "by_noise_type": _summarize_by_dimension(results, "noise_type"),
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            (
                "Hybrid retrieval combines lexical overlap with deterministic sparse semantic "
                "features."
            ),
            "The semantic features are local alias vectors, not a paid embedding model.",
            "Role filtering excludes runbook sections the requester is not allowed to retrieve.",
        ],
    }

    write_json(project_root / "reports/hybrid_eval_summary.json", report)
    write_jsonl(project_root / "reports/hybrid_eval_cases.jsonl", (asdict(row) for row in results))
    return report


def evaluate_vector(project_root: Path) -> dict[str, Any]:
    runbooks = load_runbooks(project_root)
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    results = [
        _evaluate_case(
            case,
            answer_with_vector(
                str(case["input"]),
                runbooks,
                user_role=str(case["user_role"]),
            ),
        )
        for case in cases
    ]
    metrics = _summarize(results)

    report = {
        "system_version": "local_tfidf_vector_retrieval",
        "dataset": "golden_cases",
        "case_count": len(results),
        "metrics": metrics,
        "by_task_type": _summarize_by_dimension(results, "task_type"),
        "by_noise_type": _summarize_by_dimension(results, "noise_type"),
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            (
                "Vector retrieval builds a local TF-IDF index over runbook titles, content, "
                "team hints, aliases, and character n-grams."
            ),
            (
                "It uses cosine similarity plus a small keyword rerank; no external embedding "
                "API is used."
            ),
            "Role filtering excludes runbook sections the requester is not allowed to retrieve.",
        ],
    }

    write_json(project_root / "reports/vector_eval_summary.json", report)
    write_jsonl(project_root / "reports/vector_eval_cases.jsonl", (asdict(row) for row in results))
    return report


def evaluate_embedding_store(project_root: Path) -> dict[str, Any]:
    runbooks = load_runbooks(project_root)
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    results = [
        _evaluate_case(
            case,
            answer_with_embedding_store(
                str(case["input"]),
                runbooks,
                user_role=str(case["user_role"]),
            ),
        )
        for case in cases
    ]
    metrics = _summarize(results)

    report = {
        "system_version": "local_hashed_embedding_store_retrieval",
        "dataset": "golden_cases",
        "case_count": len(results),
        "metrics": metrics,
        "by_task_type": _summarize_by_dimension(results, "task_type"),
        "by_noise_type": _summarize_by_dimension(results, "noise_type"),
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            (
                "Embedding-store retrieval builds a local dense vector index using stable "
                "feature-hashed embeddings over runbook titles, content, aliases, and team hints."
            ),
            (
                "This exercises an embedding-store search contract without requiring paid APIs, "
                "network access, or non-deterministic model downloads."
            ),
            "Role filtering excludes runbook sections the requester is not allowed to retrieve.",
        ],
    }

    write_json(project_root / "reports/embedding_eval_summary.json", report)
    write_jsonl(
        project_root / "reports/embedding_eval_cases.jsonl", (asdict(row) for row in results)
    )
    return report


def evaluate_provider_embedding_store(
    project_root: Path,
    *,
    embed_texts: EmbedTexts,
    provider_name: str,
    model: str,
) -> dict[str, Any]:
    runbooks = load_runbooks(project_root)
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    stores_by_role: dict[str, Any] = {}

    def answer_for_case(case: dict[str, Any]) -> BaselineAnswer:
        user_role = str(case["user_role"])
        if user_role not in stores_by_role:
            stores_by_role[user_role] = build_provider_embedding_store(
                runbooks,
                embed_texts=embed_texts,
                user_role=user_role,
            )
        return answer_with_provider_embedding_store(
            str(case["input"]),
            stores_by_role[user_role],
            embed_texts=embed_texts,
        )

    results = [_evaluate_case(case, answer_for_case(case)) for case in cases]
    metrics = _summarize(results)

    report = {
        "system_version": f"provider_embedding_store_{_slug(provider_name)}",
        "provider_name": provider_name,
        "model": model,
        "dataset": "golden_cases",
        "case_count": len(results),
        "metrics": metrics,
        "by_task_type": _summarize_by_dimension(results, "task_type"),
        "by_noise_type": _summarize_by_dimension(results, "noise_type"),
        "failure_reasons": _failure_reason_counts(results),
        "failure_examples": _failure_examples(results),
        "notes": [
            (
                "Provider-backed embedding retrieval uses external embedding vectors but "
                "keeps the same local final-selection, abstention, and citation checks."
            ),
            "This report is optional and is not generated by deterministic CI.",
            "Role filtering excludes runbook sections the requester is not allowed to retrieve.",
        ],
    }

    write_json(project_root / "reports/provider_embedding_eval_summary.json", report)
    write_jsonl(
        project_root / "reports/provider_embedding_eval_cases.jsonl",
        (asdict(row) for row in results),
    )
    return report


def evaluate_comparison(project_root: Path) -> dict[str, Any]:
    baseline = evaluate_baseline(project_root)
    improved = evaluate_lexical(project_root)
    metrics = {
        metric: {
            "baseline": baseline["metrics"][metric],
            "improved": improved["metrics"][metric],
            "delta": round(improved["metrics"][metric] - baseline["metrics"][metric], 4),
        }
        for metric in baseline["metrics"]
    }
    report = {
        "baseline_system_version": baseline["system_version"],
        "improved_system_version": improved["system_version"],
        "case_count": baseline["case_count"],
        "metrics": metrics,
    }
    write_json(project_root / "reports/eval_comparison.json", report)
    return report


def evaluate_retriever_comparison(project_root: Path) -> dict[str, Any]:
    baseline = evaluate_baseline(project_root)
    lexical = evaluate_lexical(project_root)
    hybrid = evaluate_hybrid(project_root)
    vector = evaluate_vector(project_root)
    embedding = evaluate_embedding_store(project_root)
    systems = [
        _system_row("Baseline team hints", baseline),
        _system_row("Improved lexical", lexical),
        _system_row("Hybrid sparse semantic", hybrid),
        _system_row("Local TF-IDF vector", vector),
        _system_row("Local embedding store", embedding),
    ]
    report = {
        "case_count": baseline["case_count"],
        "systems": systems,
        "notes": [
            (
                "Hybrid, vector, and embedding-store retrieval are compared as experiments; "
                "the older two-system report is kept for continuity."
            ),
            "All systems run over the same synthetic golden cases.",
        ],
    }
    write_json(project_root / "reports/retriever_comparison.json", report)
    write_retriever_metric_snapshots(project_root, report)
    return report


def write_retriever_metric_snapshots(
    project_root: Path,
    retriever_report: dict[str, Any],
) -> dict[str, Any]:
    snapshots: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None

    for sequence, system in enumerate(retriever_report["systems"], start=1):
        snapshot = _snapshot_row(sequence, system, previous)
        snapshots.append(snapshot)
        previous = snapshot

    report = {
        "dataset": "golden_cases",
        "case_count": retriever_report["case_count"],
        "metric_order": [
            "retrieval_hit_rate_at_3",
            "citation_coverage",
            "next_action_accuracy",
            "abstention_accuracy",
            "failure_count",
        ],
        "snapshots": snapshots,
        "notes": [
            (
                "Snapshots are deterministic ordered retriever versions, not wall-clock run "
                "history. This keeps CI reproducible while exposing metric regressions."
            ),
            (
                "A regression is flagged when citation coverage decreases or failed-case count "
                "increases compared with the previous retriever snapshot."
            ),
        ],
    }
    write_json(project_root / "reports/retriever_metric_snapshots.json", report)
    return report


def write_evaluation_history(
    project_root: Path,
    *,
    retriever_report: dict[str, Any],
    extraction: dict[str, Any],
    security: dict[str, Any],
    agent: dict[str, Any],
) -> dict[str, Any]:
    milestones: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for sequence, system in enumerate(retriever_report["systems"], start=1):
        milestone = _history_milestone(sequence, system, previous)
        milestones.append(milestone)
        previous = milestone

    current = milestones[-1]
    report = {
        "history_type": "deterministic_lab_milestones",
        "generated_at_utc": "2026-06-02T00:00:00Z",
        "dataset": "golden_cases",
        "case_count": retriever_report["case_count"],
        "current_summary": {
            "latest_milestone_id": current["milestone_id"],
            "latest_milestone": current["milestone"],
            "best_retriever": _best_retriever_label(retriever_report),
            "current_citation_coverage": current["citation_coverage"],
            "current_failure_count": current["failure_count"],
            "extraction_schema_validity": extraction["metrics"]["schema_validity"],
            "security_weighted_safe_rate": security["metrics"][
                "improved_weighted_safe_rate"
            ],
            "agent_side_effect_block_rate": agent["metrics"]["side_effect_block_rate"],
        },
        "milestones": milestones,
        "notes": [
            (
                "This is a deterministic lab history, not production telemetry. The stable "
                "timestamps mark ordered evaluation milestones so CI can regenerate the "
                "artifact exactly."
            ),
            (
                "Provider-backed model comparisons can add new rows later without changing "
                "the existing local benchmark rows."
            ),
        ],
    }
    write_json(project_root / "reports/evaluation_history.json", report)
    return report


def _evaluate_case(case: dict[str, Any], answer: BaselineAnswer) -> CaseResult:
    expected_citations = [str(item) for item in case["expected_citation_ids"]]
    retrieved_citations = [section.section_id for section in answer.retrieved_sections]
    predicted_citations = answer.citations
    expected_abstain = bool(case.get("should_abstain", False))
    failure_reasons = _failure_reasons(case, answer, expected_citations, predicted_citations)

    return CaseResult(
        case_id=str(case["case_id"]),
        task_type=str(case.get("task_type", "unknown")),
        noise_type=str(case.get("noise_type", "unspecified")),
        expected_citation_ids=expected_citations,
        predicted_citation_ids=predicted_citations,
        retrieved_citation_ids=retrieved_citations,
        retrieved_candidate_scores=_retrieved_candidate_scores(answer),
        expected_issue_category=str(case.get("expected_issue_category", "")),
        predicted_issue_category=answer.issue_category,
        expected_team=str(case.get("expected_team", "")),
        predicted_team=answer.team,
        expected_next_action=str(case.get("expected_next_action", "")),
        predicted_next_action=answer.next_action,
        retrieval_hit_at_3=(
            not expected_abstain
            and any(citation in retrieved_citations for citation in expected_citations)
        ),
        citation_match=(
            not expected_abstain
            and any(citation in predicted_citations for citation in expected_citations)
        ),
        issue_category_match=(
            not expected_abstain and answer.issue_category == case["expected_issue_category"]
        ),
        team_match=not expected_abstain and answer.team == case["expected_team"],
        next_action_match=not expected_abstain
        and answer.next_action == case["expected_next_action"],
        abstained=answer.abstained,
        expected_abstain=expected_abstain,
        abstention_correct=answer.abstained == expected_abstain,
        failure_reasons=failure_reasons,
        diagnostic=_diagnostic(case, answer, expected_citations, failure_reasons),
        recommended_fix=_recommended_fix(case, answer, failure_reasons),
    )


def _summarize(results: list[CaseResult]) -> dict[str, float]:
    if not results:
        return {
            "retrieval_hit_rate_at_3": 0.0,
            "citation_coverage": 0.0,
            "issue_category_accuracy": 0.0,
            "team_accuracy": 0.0,
            "next_action_accuracy": 0.0,
            "abstention_rate": 0.0,
            "abstention_accuracy": 0.0,
        }

    answerable = [row for row in results if not row.expected_abstain]
    return {
        "retrieval_hit_rate_at_3": _rate(row.retrieval_hit_at_3 for row in answerable),
        "citation_coverage": _rate(row.citation_match for row in answerable),
        "issue_category_accuracy": _rate(row.issue_category_match for row in answerable),
        "team_accuracy": _rate(row.team_match for row in answerable),
        "next_action_accuracy": _rate(row.next_action_match for row in answerable),
        "abstention_rate": _rate(row.abstained for row in results),
        "abstention_accuracy": _rate(row.abstention_correct for row in results),
    }


def _rate(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(1 for item in items if item) / len(items), 4)


def _failure_reasons(
    case: dict[str, Any],
    answer: BaselineAnswer,
    expected_citations: list[str],
    predicted_citations: list[str],
) -> list[str]:
    expected_abstain = bool(case.get("should_abstain", False))
    reasons: list[str] = []
    if answer.abstained != expected_abstain:
        reasons.append("abstention_mismatch")
    if expected_abstain:
        return reasons
    if not any(citation in predicted_citations for citation in expected_citations):
        reasons.append("missing_or_wrong_citation")
    if answer.issue_category != case["expected_issue_category"]:
        reasons.append("wrong_issue_category")
    if answer.team != case["expected_team"]:
        reasons.append("wrong_team")
    if answer.next_action != case["expected_next_action"]:
        reasons.append("wrong_next_action")
    return reasons


def _summarize_by_dimension(
    results: list[CaseResult], field_name: str
) -> dict[str, dict[str, Any]]:
    values = sorted({str(getattr(row, field_name)) for row in results})
    summary: dict[str, dict[str, Any]] = {}
    for value in values:
        rows = [row for row in results if str(getattr(row, field_name)) == value]
        answerable = [row for row in rows if not row.expected_abstain]
        summary[value] = {
            "case_count": len(rows),
            "failure_count": sum(1 for row in rows if row.failure_reasons),
            "citation_coverage": _rate(row.citation_match for row in answerable),
            "abstention_accuracy": _rate(row.abstention_correct for row in rows),
            "next_action_accuracy": _rate(row.next_action_match for row in answerable),
        }
    return summary


def _failure_reason_counts(results: list[CaseResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in results:
        for reason in row.failure_reasons:
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def _failure_examples(results: list[CaseResult], limit: int = 10) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for row in results:
        if not row.failure_reasons:
            continue
        examples.append(
            {
                "case_id": row.case_id,
                "task_type": row.task_type,
                "noise_type": row.noise_type,
                "failure_reasons": row.failure_reasons,
                "expected_citation_ids": row.expected_citation_ids,
                "predicted_citation_ids": row.predicted_citation_ids,
                "retrieved_citation_ids": row.retrieved_citation_ids,
                "retrieved_candidate_scores": row.retrieved_candidate_scores,
                "expected_issue_category": row.expected_issue_category,
                "predicted_issue_category": row.predicted_issue_category,
                "diagnostic": row.diagnostic,
                "recommended_fix": row.recommended_fix,
            }
        )
    return examples[:limit]


def _retrieved_candidate_scores(answer: BaselineAnswer) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for section in answer.retrieved_sections:
        candidates.append(
            {
                "section_id": section.section_id,
                "title": section.title,
                "team": section.team,
                "score": section.score,
                "score_breakdown": section.score_breakdown or {},
            }
        )
    return candidates


def _system_row(label: str, report: dict[str, Any]) -> dict[str, Any]:
    metrics = report["metrics"]
    return {
        "label": label,
        "system_version": report["system_version"],
        "retrieval_hit_rate_at_3": metrics["retrieval_hit_rate_at_3"],
        "citation_coverage": metrics["citation_coverage"],
        "issue_category_accuracy": metrics["issue_category_accuracy"],
        "next_action_accuracy": metrics["next_action_accuracy"],
        "abstention_accuracy": metrics["abstention_accuracy"],
        "failure_count": sum(
            group["failure_count"] for group in report.get("by_noise_type", {}).values()
        ),
    }


def _snapshot_row(
    sequence: int,
    system: dict[str, Any],
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    citation_delta = None
    failure_delta = None
    regression_reasons: list[str] = []

    if previous is not None:
        citation_delta = round(
            system["citation_coverage"] - previous["citation_coverage"], 4
        )
        failure_delta = system["failure_count"] - previous["failure_count"]
        if citation_delta < 0:
            regression_reasons.append("citation_coverage_decreased")
        if failure_delta > 0:
            regression_reasons.append("failed_case_count_increased")

    return {
        "snapshot_id": f"{sequence:03d}_{_slug(system['label'])}",
        "label": system["label"],
        "system_version": system["system_version"],
        "retrieval_hit_rate_at_3": system["retrieval_hit_rate_at_3"],
        "citation_coverage": system["citation_coverage"],
        "next_action_accuracy": system["next_action_accuracy"],
        "abstention_accuracy": system["abstention_accuracy"],
        "failure_count": system["failure_count"],
        "citation_delta_from_previous": citation_delta,
        "failure_delta_from_previous": failure_delta,
        "regression": bool(regression_reasons),
        "regression_reasons": regression_reasons,
    }


def _history_milestone(
    sequence: int,
    system: dict[str, Any],
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    citation_delta = None
    failure_delta = None
    if previous is not None:
        citation_delta = round(
            system["citation_coverage"] - previous["citation_coverage"], 4
        )
        failure_delta = system["failure_count"] - previous["failure_count"]
    return {
        "milestone_id": f"{sequence:03d}_{_slug(system['label'])}",
        "milestone_at_utc": f"2026-06-02T{8 + sequence:02d}:00:00Z",
        "milestone": system["label"],
        "system_version": system["system_version"],
        "retrieval_hit_rate_at_3": system["retrieval_hit_rate_at_3"],
        "citation_coverage": system["citation_coverage"],
        "next_action_accuracy": system["next_action_accuracy"],
        "abstention_accuracy": system["abstention_accuracy"],
        "failure_count": system["failure_count"],
        "citation_delta_from_previous": citation_delta,
        "failure_delta_from_previous": failure_delta,
    }


def _best_retriever_label(report: dict[str, Any]) -> str:
    best = sorted(
        report["systems"],
        key=lambda system: (
            -float(system["citation_coverage"]),
            int(system["failure_count"]),
            -float(system["retrieval_hit_rate_at_3"]),
            str(system["label"]),
        ),
    )[0]
    return str(best["label"])


def _slug(value: str) -> str:
    return "_".join(value.lower().replace("-", " ").split())


def _diagnostic(
    case: dict[str, Any],
    answer: BaselineAnswer,
    expected_citations: list[str],
    failure_reasons: list[str],
) -> str:
    if not failure_reasons:
        return ""
    expected_abstain = bool(case.get("should_abstain", False))
    if "abstention_mismatch" in failure_reasons and expected_abstain:
        return (
            "The system answered a case that was labeled as insufficient or conflicting evidence."
        )
    if "abstention_mismatch" in failure_reasons:
        return "The system abstained even though the case had enough synthetic evidence."
    if expected_citations and expected_citations[0] in [
        section.section_id for section in answer.retrieved_sections
    ]:
        return (
            "The expected section was retrieved but not selected as the final cited answer, "
            "which suggests ranking or final-selection weakness."
        )
    if answer.team == case.get("expected_team"):
        return (
            "The system found the right team but selected the wrong procedure inside that team, "
            "which suggests the query terms are too ambiguous for the current lexical scorer."
        )
    return "The retrieval path missed both the expected procedure and the expected team."


def _recommended_fix(
    case: dict[str, Any],
    answer: BaselineAnswer,
    failure_reasons: list[str],
) -> str:
    if not failure_reasons:
        return ""
    noise_type = str(case.get("noise_type", "unspecified"))
    if "abstention_mismatch" in failure_reasons:
        return "Strengthen evidence-consistency checks before answer generation."
    if noise_type == "distractor_terms":
        return "Add false-lead and negation handling before final citation selection."
    if noise_type == "paraphrase":
        return "Add semantic retrieval or synonym expansion for paraphrased procedure descriptions."
    if noise_type == "missing_metadata":
        return "Improve ranking so explicit procedure evidence beats generic workflow terms."
    if answer.team == case.get("expected_team"):
        return "Add within-team reranking using issue-category evidence and expected action terms."
    return "Add hybrid retrieval and stronger metadata filters before final answer selection."
