from __future__ import annotations

from internal_ai_agent.evals.failure_taxonomy import (
    labels_for_classifier_result,
    labels_for_failure_reasons,
    labels_for_risk_category,
    summarize_taxonomy_rows,
)


def test_retrieval_failure_reasons_map_to_shared_taxonomy() -> None:
    labels = labels_for_failure_reasons(
        ["missing_or_wrong_citation", "wrong_next_action"]
    )

    assert labels == ["missing_citation", "unsupported_answer", "wrong_citation"]


def test_safety_classifier_result_adds_operating_error_labels() -> None:
    labels = labels_for_classifier_result(
        {
            "risk_category": "weak_evidence_pressure",
            "false_positive": False,
            "false_negative": True,
            "review_queue": False,
            "is_unsafe": True,
        }
    )

    assert labels == ["false_negative", "weak_evidence_treated_as_strong"]


def test_risk_category_maps_to_safety_taxonomy() -> None:
    assert labels_for_risk_category("retrieved_context_attack") == [
        "retrieved_document_instruction_following"
    ]


def test_taxonomy_summary_counts_labels_by_group_and_source() -> None:
    summary = summarize_taxonomy_rows(
        [
            {
                "taxonomy_source": "synthetic_retrieval",
                "case_id": "case-1",
                "taxonomy_labels": ["missing_citation", "wrong_citation"],
            },
            {
                "taxonomy_source": "synthetic_red_team",
                "case_id": "case-2",
                "taxonomy_labels": ["privacy_leakage"],
            },
        ]
    )

    assert summary.total_labeled_cases == 2
    assert summary.by_group == {"reliability": 2, "safety": 1}
    assert summary.by_source["synthetic_retrieval"]["missing_citation"] == 1
