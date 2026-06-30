from __future__ import annotations

import json

from internal_ai_agent.evals.business_impact import (
    business_impact_summary,
    write_business_impact_summary,
)


def _intervention_study() -> dict[str, object]:
    return {
        "experiment_count": 3,
        "experiments": [
            {
                "experiment_id": "instruction_hierarchy",
                "title": "Instruction hierarchy and prompt-injection controls",
                "primary_metric": "prompt_injection_attack_success_rate",
                "baseline_value": 0.75,
                "recommended_value": 0.0,
                "absolute_improvement": 0.75,
                "review_burden_per_100": 66.67,
                "case_count": 12,
                "recommended_variant": "Layered hierarchy agent",
            },
            {
                "experiment_id": "action_gate",
                "title": "Action-risk policy and confirmation gate",
                "primary_metric": "unsafe_action_attempt_rate",
                "baseline_value": 1.0,
                "recommended_value": 0.0,
                "absolute_improvement": 1.0,
                "review_burden_per_100": 25.0,
                "case_count": 12,
                "recommended_variant": "Layered action gate",
            },
            {
                "experiment_id": "safety_classifier",
                "title": "Safety classifier and secondary review",
                "primary_metric": "unsafe_recall",
                "baseline_value": 0.0,
                "recommended_value": 1.0,
                "absolute_improvement": 1.0,
                "review_burden_per_100": 12.5,
                "case_count": 40,
                "recommended_variant": "Classifier plus release gate",
            },
        ],
    }


def test_reducing_a_bad_rate_is_framed_as_prevention() -> None:
    summary = business_impact_summary(_intervention_study())
    action_gate = next(s for s in summary["safeguards"] if s["experiment_id"] == "action_gate")

    assert action_gate["direction"] == "reduces_unsafe_rate"
    assert action_gate["unsafe_outcomes_addressed_per_100"] == 100.0
    assert action_gate["extra_reviews_per_100"] == 25.0
    assert action_gate["reviews_per_unsafe_outcome"] == 0.25
    assert "prevents" in action_gate["impact_statement"]
    assert "unsafe-action attempt" in action_gate["impact_statement"]


def test_raising_a_capture_rate_is_framed_as_catching() -> None:
    summary = business_impact_summary(_intervention_study())
    classifier = next(
        s for s in summary["safeguards"] if s["experiment_id"] == "safety_classifier"
    )

    assert classifier["direction"] == "increases_capture_rate"
    assert classifier["reviews_per_unsafe_outcome"] == 0.12  # 12.5 / 100, rounded
    assert "catches" in classifier["impact_statement"]


def test_portfolio_indicator_and_boundary_are_present() -> None:
    summary = business_impact_summary(_intervention_study())

    assert summary["portfolio"]["safeguard_count"] == 3
    # Mean of 0.89, 0.25, 0.12 ≈ 0.42 — an indicator, not a sum.
    assert summary["portfolio"]["mean_reviews_per_unsafe_outcome"] == 0.42
    # The honest denominator caveat must travel with the numbers.
    assert "not per unit of production traffic" in summary["responsible_boundary"]


def test_empty_study_does_not_crash() -> None:
    summary = business_impact_summary({"experiments": []})
    assert summary["safeguards"] == []
    assert summary["portfolio"]["mean_reviews_per_unsafe_outcome"] is None


def test_write_emits_json_and_markdown(tmp_path) -> None:
    summary = write_business_impact_summary(
        tmp_path, intervention_study=_intervention_study()
    )

    written = json.loads((tmp_path / "reports/business_impact_summary.json").read_text())
    assert written == summary
    assert written["report_type"] == "business_impact_summary"

    md = (tmp_path / "reports/business_impact_summary.md").read_text(encoding="utf-8")
    assert "# Business Impact Summary" in md
    assert "Reviews per outcome" in md
    assert "Responsible boundary" in md
