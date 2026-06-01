from pathlib import Path

from internal_ai_agent.evals.runner import (
    evaluate_baseline,
    evaluate_comparison,
    evaluate_hybrid,
    evaluate_vector,
)
from internal_ai_agent.rag.baseline import (
    answer_with_baseline,
    answer_with_hybrid,
    answer_with_lexical,
    answer_with_vector,
)


def test_baseline_answers_with_citation_for_known_system() -> None:
    runbooks = [
        {
            "section_id": "RB-PAYMENTS_OPS-01",
            "title": "File Validation Failed",
            "team": "payments_ops",
            "content": (
                "When Payments Operations receives a file validation failed ticket. "
                "Recommended next action: Validate file schema. "
                "If the evidence is incomplete, ask for clarification."
            ),
        }
    ]

    answer = answer_with_baseline("Aurora Payment Gateway has a failed file.", runbooks)

    assert answer.abstained is False
    assert answer.citations == ["RB-PAYMENTS_OPS-01"]
    assert answer.issue_category == "file_validation_failed"


def test_baseline_abstains_without_matching_system() -> None:
    answer = answer_with_baseline("A completely unknown synthetic platform failed.", [])

    assert answer.abstained is True
    assert answer.citations == []


def test_improved_lexical_retrieval_finds_specific_procedure() -> None:
    from internal_ai_agent.data.synthetic import build_runbooks

    runbooks = [section.__dict__ for section in build_runbooks()]
    answer = answer_with_lexical(
        "Confirmation Pending observed in Helios Trade Exceptions. What should I do next?",
        runbooks,
    )

    assert answer.issue_category == "confirmation_pending"
    assert answer.citations == ["RB-TRADE_SUPPORT-02"]


def test_hybrid_retrieval_uses_semantic_aliases_for_paraphrase() -> None:
    from internal_ai_agent.data.synthetic import build_runbooks

    runbooks = [section.__dict__ for section in build_runbooks()]
    answer = answer_with_hybrid(
        (
            "Several records look duplicated and need stewardship review in "
            "Atlas Data Controls. Which procedure applies?"
        ),
        runbooks,
    )

    assert answer.issue_category == "duplicate_record_cluster"
    assert answer.citations == ["RB-DATA_QUALITY-04"]


def test_hybrid_retrieval_penalizes_negated_false_leads() -> None:
    from internal_ai_agent.data.synthetic import build_runbooks

    runbooks = [section.__dict__ for section in build_runbooks()]
    answer = answer_with_hybrid(
        (
            "Triage note with a false lead: this is not confirmation pending even though "
            "that term appears in the chat. The actual evidence says several records look "
            "duplicated and need stewardship review on Atlas Data Controls."
        ),
        runbooks,
    )

    assert answer.issue_category == "duplicate_record_cluster"
    assert answer.citations == ["RB-DATA_QUALITY-04"]


def test_hybrid_retrieval_prefers_specific_phrase_over_generic_status_terms() -> None:
    from internal_ai_agent.data.synthetic import build_runbooks

    runbooks = [section.__dict__ for section in build_runbooks()]
    answer = answer_with_hybrid(
        (
            "New ticket without a stable id yet. The parties disagree on the trade date "
            "shown in the exception. The affected platform is Helios Trade Exceptions. "
            "Generated control output and workflow status are present."
        ),
        runbooks,
    )

    assert answer.issue_category == "trade_date_dispute"
    assert answer.citations == ["RB-TRADE_SUPPORT-04"]


def test_vector_retrieval_handles_typo_tolerant_paraphrase() -> None:
    from internal_ai_agent.data.synthetic import build_runbooks

    runbooks = [section.__dict__ for section in build_runbooks()]
    answer = answer_with_vector(
        (
            "The ops note says severl recrods look duplicated and need stewardship "
            "review in Atlas Data Controls. Which runbook applies?"
        ),
        runbooks,
    )

    assert answer.issue_category == "duplicate_record_cluster"
    assert answer.citations == ["RB-DATA_QUALITY-04"]


def test_baseline_eval_writes_report(tmp_path: Path) -> None:
    from internal_ai_agent.data.synthetic import generate_all

    generate_all(tmp_path, ticket_count=24)
    report = evaluate_baseline(tmp_path)

    assert report["case_count"] == 120
    assert "retrieval_hit_rate_at_3" in report["metrics"]
    assert "by_noise_type" in report
    assert "failure_reasons" in report
    assert (tmp_path / "reports/baseline_eval_summary.json").exists()
    assert (tmp_path / "reports/baseline_eval_cases.jsonl").exists()


def test_hybrid_eval_writes_report(tmp_path: Path) -> None:
    from internal_ai_agent.data.synthetic import generate_all

    generate_all(tmp_path, ticket_count=24)
    report = evaluate_hybrid(tmp_path)

    assert report["case_count"] == 120
    assert report["system_version"] == "hybrid_sparse_semantic_retrieval"
    assert (tmp_path / "reports/hybrid_eval_summary.json").exists()
    assert (tmp_path / "reports/hybrid_eval_cases.jsonl").exists()


def test_vector_eval_writes_report(tmp_path: Path) -> None:
    from internal_ai_agent.data.synthetic import generate_all

    generate_all(tmp_path, ticket_count=24)
    report = evaluate_vector(tmp_path)

    assert report["case_count"] == 120
    assert report["system_version"] == "local_tfidf_vector_retrieval"
    assert (tmp_path / "reports/vector_eval_summary.json").exists()
    assert (tmp_path / "reports/vector_eval_cases.jsonl").exists()


def test_eval_comparison_writes_before_after_report(tmp_path: Path) -> None:
    from internal_ai_agent.data.synthetic import generate_all

    generate_all(tmp_path, ticket_count=24)
    report = evaluate_comparison(tmp_path)

    assert report["case_count"] == 120
    assert (
        report["metrics"]["citation_coverage"]["improved"]
        >= report["metrics"]["citation_coverage"]["baseline"]
    )
    assert (tmp_path / "reports/eval_comparison.json").exists()
