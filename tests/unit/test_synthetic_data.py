from pathlib import Path

from internal_ai_agent.data.synthetic import (
    build_golden_cases,
    build_runbooks,
    build_tickets,
    generate_all,
)


def test_runbooks_are_synthetic_and_citable() -> None:
    runbooks = build_runbooks()

    assert len(runbooks) >= 10
    assert all(section.section_id.startswith("RB-") for section in runbooks)
    assert all("JPMorgan" not in section.content for section in runbooks)


def test_ticket_generation_is_reproducible() -> None:
    runbooks = build_runbooks()

    first = build_tickets(runbooks, count=5, seed=42)
    second = build_tickets(runbooks, count=5, seed=42)

    assert first == second
    assert all(ticket.gold_citation_ids for ticket in first)


def test_golden_cases_reference_ticket_expectations() -> None:
    runbooks = build_runbooks()
    tickets = build_tickets(runbooks, count=3, seed=1)
    cases = build_golden_cases(tickets, limit=3)

    assert len(cases) == 15
    assert cases[0]["expected_citation_ids"] == tickets[0].gold_citation_ids
    assert cases[0]["should_abstain"] is False
    assert any(case["noise_type"] == "abbreviated_ticket" for case in cases)


def test_full_golden_cases_include_harder_noise_types() -> None:
    runbooks = build_runbooks()
    tickets = build_tickets(runbooks, count=48, seed=7)
    cases = build_golden_cases(tickets)
    noise_types = {str(case["noise_type"]) for case in cases}

    assert len(cases) == 302
    assert "distractor_terms" in noise_types
    assert "typo_abbreviation" in noise_types
    assert "adversarial_instruction" in noise_types
    assert "human_colloquial" in noise_types
    assert "human_email_thread" in noise_types
    assert "manual_chat_fragment" in noise_types
    assert "manual_conflicting_notes" in noise_types
    assert "manual_control_room_note" in noise_types
    assert "manual_ops_chat_handoff" in noise_types
    assert "manual_retrieved_injection" in noise_types
    assert "manual_retrieved_instruction_attack" in noise_types
    assert "manual_stale_thread" in noise_types
    assert "manual_analyst_note" in noise_types
    assert "manual_csv_excerpt" in noise_types
    assert "manual_incident_timeline" in noise_types
    assert "manual_control_owner_note" in noise_types
    assert "manual_ambiguous_handoff" in noise_types
    assert "manual_evidence_packet" in noise_types
    assert "manual_evidence_packet_conflict" in noise_types
    assert "manual_review_bundle" in noise_types
    assert "manual_review_bundle_conflict" in noise_types
    assert "manual_field_note" in noise_types
    assert "primary_signal_with_secondary_chatter" in noise_types
    assert "retrieved_doc_injection" in noise_types
    assert "long_conflicting_context" in noise_types
    assert "manual_retrieved_context_review" in noise_types
    assert "manual_retrieved_context_attack" in noise_types
    assert "manual_retrieved_context_conflict" in noise_types


def test_generate_all_writes_expected_files(tmp_path: Path) -> None:
    counts = generate_all(tmp_path, ticket_count=12)

    assert counts == {
        "runbooks": 24,
        "tickets": 12,
        "golden_cases": 60,
        "red_team_cases": 60,
        "safety_challenge_cases": 40,
        "safety_secondary_review_validation_cases": 33,
        "safety_prevalence_cases": 80,
    }
    assert (tmp_path / "config/safety_taxonomy.yaml").exists()
    assert (tmp_path / "data/synthetic/raw_docs/runbooks.jsonl").exists()
    assert (tmp_path / "data/synthetic/raw_tickets/tickets.jsonl").exists()
    assert (tmp_path / "data/eval/golden_cases.jsonl").exists()
    assert (tmp_path / "data/eval/red_team_cases.jsonl").exists()
    assert (tmp_path / "data/eval/safety_challenge_cases.jsonl").exists()
    assert (tmp_path / "data/eval/safety_secondary_review_validation_cases.jsonl").exists()
    assert (tmp_path / "data/eval/safety_prevalence_cases.jsonl").exists()
