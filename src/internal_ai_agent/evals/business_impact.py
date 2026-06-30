"""Stakeholder-facing business-impact framing for the safety intervention study.

This module does not introduce new measurements. It re-expresses the existing
agent-safety intervention results as an operational trade-off: for every 100
requests that reach a safeguard's risk surface, how many unsafe outcomes it
addresses versus how many extra human reviews it costs. The denominator is
deliberately "in-scope requests" (the adversarial / risk cases the safeguard is
evaluated on), not all traffic, so the framing does not overclaim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.io import write_json

BUSINESS_IMPACT_PATH = "reports/business_impact_summary.json"
BUSINESS_IMPACT_DOC = "reports/business_impact_summary.md"

# Map an experiment's primary metric to the risk surface it is measured over, so
# the per-100 denominator reads as a concrete population rather than "cases".
_SCOPE_LABELS = {
    "prompt_injection_attack_success_rate": "prompt-injection attempt",
    "unsafe_action_attempt_rate": "unsafe-action attempt",
    "unsafe_recall": "unsafe request",
}

RESPONSIBLE_BOUNDARY = (
    "Rates are per 100 requests that reach each safeguard's risk surface in the "
    "controlled synthetic benchmark, not per unit of production traffic. These are "
    "engineering-evidence trade-offs, not production safety guarantees."
)


def _round(value: float, digits: int = 2) -> float:
    return round(float(value), digits)


def _safeguard_impact(experiment: dict[str, Any]) -> dict[str, Any]:
    baseline = float(experiment["baseline_value"])
    recommended = float(experiment["recommended_value"])
    improvement = float(experiment["absolute_improvement"])

    # Reducing a bad rate (e.g. attack success) "prevents"; raising a good rate
    # (e.g. unsafe recall) "captures".
    if recommended < baseline:
        direction, verb = "reduces_unsafe_rate", "prevents"
    else:
        direction, verb = "increases_capture_rate", "catches"

    scope = _SCOPE_LABELS.get(str(experiment.get("primary_metric")), "in-scope risk")
    outcomes_per_100 = _round(improvement * 100, 1)
    extra_reviews_per_100 = _round(float(experiment["review_burden_per_100"]), 1)
    reviews_per_outcome = (
        _round(extra_reviews_per_100 / outcomes_per_100) if outcomes_per_100 else None
    )

    cost_clause = (
        f"~{reviews_per_outcome:g} extra reviews per unsafe outcome"
        if reviews_per_outcome is not None
        else "no measured review cost"
    )
    statement = (
        f"Per 100 {scope} cases, {experiment['recommended_variant']} {verb} "
        f"{outcomes_per_100:g} unsafe outcomes at a cost of "
        f"{extra_reviews_per_100:g} extra human reviews ({cost_clause})."
    )

    return {
        "experiment_id": experiment["experiment_id"],
        "title": experiment["title"],
        "recommended_variant": experiment["recommended_variant"],
        "scope": scope,
        "direction": direction,
        "in_scope_cases": int(experiment["case_count"]),
        "unsafe_outcomes_addressed_per_100": outcomes_per_100,
        "extra_reviews_per_100": extra_reviews_per_100,
        "reviews_per_unsafe_outcome": reviews_per_outcome,
        "impact_statement": statement,
    }


def business_impact_summary(intervention_study: dict[str, Any]) -> dict[str, Any]:
    """Derive a stakeholder-facing impact framing from the intervention study."""
    safeguards = [
        _safeguard_impact(experiment)
        for experiment in intervention_study.get("experiments", [])
    ]
    ratios = [
        s["reviews_per_unsafe_outcome"]
        for s in safeguards
        if s["reviews_per_unsafe_outcome"] is not None
    ]
    portfolio = {
        "safeguard_count": len(safeguards),
        # Averaging cost-efficiency across safeguards; each has its own denominator,
        # so this is an indicator, not an additive total.
        "mean_reviews_per_unsafe_outcome": _round(sum(ratios) / len(ratios)) if ratios else None,
    }
    return {
        "report_type": "business_impact_summary",
        "basis": "agent_safety_intervention_study",
        "volume_basis": "per_100_in_scope_requests",
        "headline": _portfolio_headline(safeguards, portfolio),
        "safeguards": safeguards,
        "portfolio": portfolio,
        "responsible_boundary": RESPONSIBLE_BOUNDARY,
    }


def _portfolio_headline(safeguards: list[dict[str, Any]], portfolio: dict[str, Any]) -> str:
    if not safeguards:
        return "No safety interventions available to frame yet."
    mean_ratio = portfolio["mean_reviews_per_unsafe_outcome"]
    cost = (
        f"averaging ~{mean_ratio:g} extra reviews per unsafe outcome addressed"
        if mean_ratio is not None
        else "with review cost reported per safeguard"
    )
    return (
        f"{len(safeguards)} layered safeguards address unsafe outcomes on their risk "
        f"surfaces {cost}."
    )


def _markdown(summary: dict[str, Any]) -> str:
    header = (
        "| Safeguard | In-scope cases | Unsafe outcomes addressed / 100 | "
        "Extra reviews / 100 | Reviews per outcome |"
    )
    divider = "| --- | ---: | ---: | ---: | ---: |"
    rows = [
        "| {title} | {cases} | {outcomes:g} | {reviews:g} | {ratio} |".format(
            title=s["title"],
            cases=s["in_scope_cases"],
            outcomes=s["unsafe_outcomes_addressed_per_100"],
            reviews=s["extra_reviews_per_100"],
            ratio=(
                f"{s['reviews_per_unsafe_outcome']:g}"
                if s["reviews_per_unsafe_outcome"] is not None
                else "n/a"
            ),
        )
        for s in summary["safeguards"]
    ]
    statements = [f"- {s['impact_statement']}" for s in summary["safeguards"]]
    return "\n".join(
        [
            "# Business Impact Summary",
            "",
            "## What this reframes",
            "",
            (
                "This summary re-expresses the agent-safety intervention study as an "
                "operational trade-off for reviewers and release owners. It adds no new "
                "measurement; it pairs each safeguard's safety gain with its review cost."
            ),
            "",
            f"**{summary['headline']}**",
            "",
            "## Safety gain vs. review cost",
            "",
            header,
            divider,
            *rows,
            "",
            "## Plain-language impact",
            "",
            *statements,
            "",
            "## Responsible boundary",
            "",
            f"> {summary['responsible_boundary']}",
            "",
        ]
    )


def write_business_impact_summary(
    project_root: Path,
    *,
    intervention_study: dict[str, Any],
) -> dict[str, Any]:
    summary = business_impact_summary(intervention_study)
    write_json(project_root / BUSINESS_IMPACT_PATH, summary)
    (project_root / BUSINESS_IMPACT_DOC).write_text(_markdown(summary), encoding="utf-8")
    return summary
