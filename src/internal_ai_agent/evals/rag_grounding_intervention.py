from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json

RAG_GROUNDING_REPORT_PATH = Path("reports/rag_grounding_intervention.json")
RAG_GROUNDING_REPORT_DOC = Path("reports/rag_grounding_intervention.md")

PRIMARY_SYSTEM_MARKERS = {
    "techqa": "local_tfidf_public_retriever",
    "wixqa": "local_tfidf_wixqa_retriever",
}

TRACK_THRESHOLDS = {
    "baseline_public_retriever": {"techqa": 15.0, "wixqa": 0.0},
    "citation_required_answering": {"techqa": 15.0, "wixqa": 0.0},
    "moderate_evidence_gate": {"techqa": 20.0, "wixqa": 12.0},
    "strict_grounding_gate": {"techqa": 25.0, "wixqa": 18.0},
    "strict_gate_with_review": {"techqa": 25.0, "wixqa": 18.0},
}


def write_rag_grounding_intervention(project_root: Path) -> dict[str, Any]:
    rows = _load_primary_public_rag_rows(project_root)
    report = _report(rows)
    write_json(project_root / RAG_GROUNDING_REPORT_PATH, report)
    _write_text(project_root / RAG_GROUNDING_REPORT_DOC, _markdown(report))
    return report


def _load_primary_public_rag_rows(project_root: Path) -> list[dict[str, Any]]:
    return [
        *_primary_rows(
            project_root / "reports/techqa_public_retriever_cases.jsonl",
            dataset="nvidia/TechQA-RAG-Eval",
            track_id="techqa",
            primary_marker=PRIMARY_SYSTEM_MARKERS["techqa"],
        ),
        *_primary_rows(
            project_root / "reports/wixqa_public_retriever_cases.jsonl",
            dataset="Wix/WixQA expert-written",
            track_id="wixqa",
            primary_marker=PRIMARY_SYSTEM_MARKERS["wixqa"],
        ),
    ]


def _primary_rows(
    path: Path,
    *,
    dataset: str,
    track_id: str,
    primary_marker: str,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for row in read_jsonl(path):
        if row.get("system_id") != primary_marker:
            continue
        rows.append({**row, "dataset": dataset, "track_id": track_id})
    return rows


def _report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "report_type": "rag_grounding_intervention",
            "status": "not_configured",
            "case_count": 0,
            "variants": [],
            "summary": {},
            "findings": [],
            "recommendations": [
                (
                    "Run the public TechQA and WixQA benchmarks before generating "
                    "the grounding intervention study."
                )
            ],
            "notes": [
                (
                    "This study requires public-data retriever case files and does "
                    "not use paid provider calls."
                )
            ],
        }

    variants = [_evaluate_variant(rows, variant_id) for variant_id in TRACK_THRESHOLDS]
    baseline = _variant_by_id(variants, "baseline_public_retriever")
    moderate = _variant_by_id(variants, "moderate_evidence_gate")
    strict = _variant_by_id(variants, "strict_grounding_gate")
    review = _variant_by_id(variants, "strict_gate_with_review")
    summary = {
        "dataset_count": len({row["dataset"] for row in rows}),
        "case_count": len(rows),
        "answerable_case_count": sum(not _is_impossible(row) for row in rows),
        "impossible_case_count": sum(_is_impossible(row) for row in rows),
        "baseline_unsupported_answer_rate": baseline["metrics"][
            "unsupported_answer_rate"
        ],
        "moderate_unsupported_answer_rate": moderate["metrics"][
            "unsupported_answer_rate"
        ],
        "strict_unsupported_answer_rate": strict["metrics"][
            "unsupported_answer_rate"
        ],
        "strict_review_burden_per_100": review["metrics"][
            "review_burden_per_100_cases"
        ],
        "moderate_useful_answer_rate": moderate["metrics"]["useful_answer_rate"],
        "strict_useful_answer_rate": strict["metrics"]["useful_answer_rate"],
        "recommended_variant": "moderate_evidence_gate",
    }
    return {
        "report_type": "rag_grounding_intervention",
        "status": "evaluated",
        "case_count": len(rows),
        "datasets": _dataset_counts(rows),
        "decision_policy": {
            "baseline_public_retriever": (
                "Use the existing public retriever decision threshold."
            ),
            "citation_required_answering": (
                "Do not publish an answer unless a retriever citation is present."
            ),
            "moderate_evidence_gate": (
                "Raise the evidence threshold modestly before answering."
            ),
            "strict_grounding_gate": (
                "Abstain on low-confidence retrieved evidence."
            ),
            "strict_gate_with_review": (
                "Route low-confidence evidence to review rather than publishing."
            ),
        },
        "thresholds": TRACK_THRESHOLDS,
        "variants": variants,
        "summary": summary,
        "findings": _findings(baseline, moderate, strict, review),
        "recommendations": _recommendations(),
        "limitations": [
            (
                "The intervention is deterministic and uses public benchmark labels "
                "only for scoring, not for making decisions."
            ),
            "The study measures answer/citation decisions, not natural-language answer quality.",
            (
                "Thresholds are intentionally simple so the result is reproducible "
                "in CI and public deployment."
            ),
        ],
        "notes": [
            "This report combines only public TechQA and WixQA retriever case files.",
            "It is separate from controlled synthetic operations safety and tool-use results.",
            "No paid provider calls are used.",
        ],
    }


def _evaluate_variant(rows: list[dict[str, Any]], variant_id: str) -> dict[str, Any]:
    decisions = [_decision(row, variant_id) for row in rows]
    metrics = _metrics(decisions)
    return {
        "variant_id": variant_id,
        "label": _variant_label(variant_id),
        "case_count": len(decisions),
        "metrics": metrics,
        "dataset_metrics": _dataset_metrics(decisions),
        "failure_examples": _failure_examples(decisions),
    }


def _decision(row: dict[str, Any], variant_id: str) -> dict[str, Any]:
    track_id = str(row["track_id"])
    top_score = float(row.get("top_score", 0.0))
    threshold = TRACK_THRESHOLDS[variant_id][track_id]
    has_citation = bool(row.get("retrieved_citation_ids", []))
    low_evidence = top_score < threshold
    decision = "answer"
    if variant_id == "citation_required_answering" and not has_citation:
        decision = "abstain"
    elif low_evidence:
        decision = "review" if variant_id == "strict_gate_with_review" else "abstain"

    answerable = not _is_impossible(row)
    top1_match = bool(row.get("top1_match", False))
    unsupported_answer = answerable and decision == "answer" and not top1_match
    useful_answer = answerable and decision == "answer" and top1_match
    false_abstention_or_review = answerable and decision in {"abstain", "review"}
    impossible_not_intercepted = (not answerable) and decision == "answer"
    return {
        "case_id": str(row["case_id"]),
        "dataset": row["dataset"],
        "track_id": track_id,
        "variant_id": variant_id,
        "decision": decision,
        "answerable": answerable,
        "is_impossible": not answerable,
        "top_score": top_score,
        "threshold": threshold,
        "top1_match": top1_match,
        "retrieval_hit_at_3": bool(row.get("retrieval_hit_at_3", False)),
        "unsupported_answer": unsupported_answer,
        "useful_answer": useful_answer,
        "false_abstention_or_review": false_abstention_or_review,
        "impossible_not_intercepted": impossible_not_intercepted,
    }


def _metrics(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    answerable = [row for row in decisions if row["answerable"]]
    impossible = [row for row in decisions if row["is_impossible"]]
    return {
        "case_count": len(decisions),
        "answerable_case_count": len(answerable),
        "impossible_case_count": len(impossible),
        "answer_attempt_rate": _rate(
            sum(row["decision"] == "answer" for row in decisions), len(decisions)
        ),
        "useful_answer_rate": _rate(
            sum(row["useful_answer"] for row in answerable), len(answerable)
        ),
        "unsupported_answer_rate": _rate(
            sum(row["unsupported_answer"] for row in answerable), len(answerable)
        ),
        "unsupported_answer_count": sum(row["unsupported_answer"] for row in answerable),
        "false_abstention_or_review_rate": _rate(
            sum(row["false_abstention_or_review"] for row in answerable),
            len(answerable),
        ),
        "false_abstention_or_review_count": sum(
            row["false_abstention_or_review"] for row in answerable
        ),
        "impossible_intercept_rate": _rate(
            sum(not row["impossible_not_intercepted"] for row in impossible),
            len(impossible),
        ),
        "impossible_miss_count": sum(row["impossible_not_intercepted"] for row in impossible),
        "review_burden_per_100_cases": round(
            100 * _rate(sum(row["decision"] == "review" for row in decisions), len(decisions)),
            2,
        ),
        "abstention_burden_per_100_cases": round(
            100
            * _rate(sum(row["decision"] == "abstain" for row in decisions), len(decisions)),
            2,
        ),
    }


def _dataset_metrics(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    datasets = sorted({str(row["dataset"]) for row in decisions})
    return [
        {"dataset": dataset, **_metrics([row for row in decisions if row["dataset"] == dataset])}
        for dataset in datasets
    ]


def _findings(
    baseline: dict[str, Any],
    moderate: dict[str, Any],
    strict: dict[str, Any],
    review: dict[str, Any],
) -> list[str]:
    baseline_metrics = baseline["metrics"]
    moderate_metrics = moderate["metrics"]
    strict_metrics = strict["metrics"]
    review_metrics = review["metrics"]
    moderate_delta = baseline_metrics["unsupported_answer_rate"] - moderate_metrics[
        "unsupported_answer_rate"
    ]
    strict_delta = baseline_metrics["unsupported_answer_rate"] - strict_metrics[
        "unsupported_answer_rate"
    ]
    return [
        (
            "A moderate evidence gate reduces unsupported public-RAG answer attempts "
            f"by {moderate_delta:.2%} absolute while keeping useful-answer rate at "
            f"{moderate_metrics['useful_answer_rate']:.2%}."
        ),
        (
            "A stricter grounding gate reduces unsupported answer attempts by "
            f"{strict_delta:.2%} absolute but increases false abstention/review to "
            f"{strict_metrics['false_abstention_or_review_rate']:.2%}."
        ),
        (
            "Routing strict low-evidence cases to review makes the operational cost "
            f"explicit: {review_metrics['review_burden_per_100_cases']:.2f} reviews "
            "per 100 public-RAG cases."
        ),
    ]


def _recommendations() -> list[str]:
    return [
        (
            "Use the moderate evidence gate as the default public-RAG release guard "
            "until a stronger reranker or model judge is validated."
        ),
        (
            "Keep the strict gate as a high-risk mode where unsupported answers are "
            "more costly than manual review or abstention."
        ),
        (
            "Evaluate the same thresholds against a provider-backed reranker before "
            "claiming model-level improvements."
        ),
    ]


def _markdown(report: dict[str, Any]) -> str:
    if report.get("status") != "evaluated":
        return "\n".join(
            [
                "# RAG Grounding Intervention Study",
                "",
                "Status: not configured",
                "",
                "Run the public TechQA and WixQA benchmarks before generating this study.",
                "",
            ]
        )
    variant_rows = "\n".join(
        "| {label} | {case_count} | {unsupported} | {useful} | {false_abs} | "
        "{intercept} | {review} |".format(
            label=variant["label"],
            case_count=variant["case_count"],
            unsupported=_pct(variant["metrics"]["unsupported_answer_rate"]),
            useful=_pct(variant["metrics"]["useful_answer_rate"]),
            false_abs=_pct(variant["metrics"]["false_abstention_or_review_rate"]),
            intercept=_pct(variant["metrics"]["impossible_intercept_rate"]),
            review=f"{variant['metrics']['review_burden_per_100_cases']:.2f}",
        )
        for variant in report["variants"]
    )
    findings = "\n".join(f"- {item}" for item in report["findings"])
    recommendations = "\n".join(f"- {item}" for item in report["recommendations"])
    limitations = "\n".join(f"- {item}" for item in report["limitations"])
    return "\n".join(
        [
            "# RAG Grounding Intervention Study",
            "",
            "## Abstract",
            "",
            (
                "This study evaluates deterministic grounding and abstention controls "
                "over public TechQA and WixQA RAG cases. It measures whether evidence "
                "thresholds reduce unsupported answer attempts and what usefulness or "
                "review burden they introduce."
            ),
            "",
            "## Results",
            "",
            "| Variant | Cases | Unsupported answer rate | Useful answer rate | "
            "False abstention/review | Impossible intercept | Review burden / 100 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            variant_rows,
            "",
            "## Findings",
            "",
            findings,
            "",
            "## Recommendations",
            "",
            recommendations,
            "",
            "## Limitations",
            "",
            limitations,
            "",
        ]
    )


def _failure_examples(decisions: list[dict[str, Any]], *, limit: int = 6) -> list[dict[str, Any]]:
    failures = [
        row
        for row in decisions
        if row["unsupported_answer"]
        or row["false_abstention_or_review"]
        or row["impossible_not_intercepted"]
    ]
    return [
        {
            "case_id": row["case_id"],
            "dataset": row["dataset"],
            "decision": row["decision"],
            "top_score": row["top_score"],
            "threshold": row["threshold"],
            "failure_type": _failure_type(row),
        }
        for row in failures[:limit]
    ]


def _failure_type(row: dict[str, Any]) -> str:
    if row["unsupported_answer"]:
        return "unsupported_answer_attempt"
    if row["false_abstention_or_review"]:
        return "answerable_low_evidence_intercepted"
    if row["impossible_not_intercepted"]:
        return "impossible_question_not_intercepted"
    return "none"


def _dataset_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        dataset = str(row["dataset"])
        counts[dataset] = counts.get(dataset, 0) + 1
    return dict(sorted(counts.items()))


def _is_impossible(row: dict[str, Any]) -> bool:
    return bool(row.get("is_impossible", False))


def _variant_by_id(rows: list[dict[str, Any]], variant_id: str) -> dict[str, Any]:
    for row in rows:
        if row["variant_id"] == variant_id:
            return row
    raise ValueError(f"Missing RAG grounding variant: {variant_id}")


def _variant_label(variant_id: str) -> str:
    return {
        "baseline_public_retriever": "Baseline public retriever",
        "citation_required_answering": "Citation-required answering",
        "moderate_evidence_gate": "Moderate evidence gate",
        "strict_grounding_gate": "Strict grounding gate",
        "strict_gate_with_review": "Strict gate with review",
    }[variant_id]


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
