from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json

MANUAL_PREFIXES = ("MANUAL-",)


def write_dataset_profile(project_root: Path) -> dict[str, Any]:
    profile = dataset_profile(
        golden_cases=read_jsonl(project_root / "data/eval/golden_cases.jsonl"),
        red_team_cases=read_jsonl(project_root / "data/eval/red_team_cases.jsonl"),
        tickets=read_jsonl(project_root / "data/synthetic/raw_tickets/tickets.jsonl"),
        runbooks=read_jsonl(project_root / "data/synthetic/raw_docs/runbooks.jsonl"),
    )
    write_json(project_root / "reports/dataset_profile.json", profile)
    return profile


def dataset_profile(
    *,
    golden_cases: list[dict[str, Any]],
    red_team_cases: list[dict[str, Any]],
    tickets: list[dict[str, Any]],
    runbooks: list[dict[str, Any]],
) -> dict[str, Any]:
    manual_cases = [
        case for case in golden_cases if str(case["case_id"]).startswith(MANUAL_PREFIXES)
    ]
    abstention_cases = [case for case in golden_cases if case["should_abstain"]]
    answerable_cases = [case for case in golden_cases if not case["should_abstain"]]
    noise_counts = _counts(golden_cases, "noise_type")
    task_counts = _counts(golden_cases, "task_type")
    issue_counts = _counts(
        [case for case in golden_cases if case["expected_issue_category"]],
        "expected_issue_category",
    )
    team_counts = _counts(
        [case for case in golden_cases if case["expected_team"]],
        "expected_team",
    )
    red_team_risk_counts = _counts(red_team_cases, "risk_type")
    red_team_channel_counts = _counts(red_team_cases, "injection_location")

    manual_share = _ratio(len(manual_cases), len(golden_cases))
    abstention_share = _ratio(len(abstention_cases), len(golden_cases))
    risk_labels = _dataset_risk_labels(
        manual_share=manual_share,
        abstention_share=abstention_share,
        noise_type_count=len(noise_counts),
        issue_count=len(issue_counts),
        team_count=len(team_counts),
    )
    return {
        "profile_type": "synthetic_dataset_profile",
        "dataset_counts": {
            "runbooks": len(runbooks),
            "tickets": len(tickets),
            "golden_cases": len(golden_cases),
            "red_team_cases": len(red_team_cases),
        },
        "golden_case_mix": {
            "manual_cases": len(manual_cases),
            "generated_cases": len(golden_cases) - len(manual_cases),
            "manual_share": manual_share,
            "answerable_cases": len(answerable_cases),
            "expected_abstentions": len(abstention_cases),
            "abstention_share": abstention_share,
            "noise_type_count": len(noise_counts),
            "task_type_count": len(task_counts),
            "issue_category_count": len(issue_counts),
            "team_count": len(team_counts),
        },
        "golden_coverage": {
            "by_noise_type": noise_counts,
            "by_task_type": task_counts,
            "by_issue_category": issue_counts,
            "by_team": team_counts,
        },
        "red_team_coverage": {
            "by_risk_type": red_team_risk_counts,
            "by_attack_channel": red_team_channel_counts,
        },
        "top_manual_noise_types": _top_counts(
            _counts(manual_cases, "noise_type"),
            limit=8,
        ),
        "risk_labels": risk_labels,
        "recommended_next_data_work": _recommended_next_data_work(risk_labels),
    }


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[key]) for row in rows).items()))


def _top_counts(counts: dict[str, int], *, limit: int) -> list[dict[str, Any]]:
    return [
        {"value": value, "case_count": count}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[
            :limit
        ]
    ]


def _dataset_risk_labels(
    *,
    manual_share: float,
    abstention_share: float,
    noise_type_count: int,
    issue_count: int,
    team_count: int,
) -> list[str]:
    labels: list[str] = []
    if manual_share < 0.25:
        labels.append("manual_case_share_below_25_percent")
    if abstention_share < 0.15:
        labels.append("abstention_share_below_15_percent")
    if noise_type_count < 30:
        labels.append("noise_type_coverage_below_30")
    if issue_count < 20:
        labels.append("issue_category_coverage_below_20")
    if team_count < 4:
        labels.append("team_coverage_below_4")
    labels.append("provider_backed_embedding_comparison_not_covered")
    labels.append("real_company_data_intentionally_excluded")
    return labels


def _recommended_next_data_work(risk_labels: list[str]) -> list[str]:
    recommendations = []
    if "manual_case_share_below_25_percent" in risk_labels:
        recommendations.append("Add more hand-authored golden cases before more reranking.")
    if "abstention_share_below_15_percent" in risk_labels:
        recommendations.append("Add more weak-evidence and ownership-conflict abstention cases.")
    if "provider_backed_embedding_comparison_not_covered" in risk_labels:
        recommendations.append("Compare local retrieval with a provider-backed embedding option.")
    recommendations.append("Keep all public benchmark data synthetic and reproducible.")
    return recommendations


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
