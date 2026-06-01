from internal_ai_agent.evals.agent import evaluate_agent


def test_agent_eval_report_writes_tool_governance_metrics(tmp_path) -> None:
    data_dir = tmp_path / "data/synthetic/raw_tickets"
    reports_dir = tmp_path / "reports"
    data_dir.mkdir(parents=True)
    reports_dir.mkdir()
    (data_dir / "tickets.jsonl").write_text(
        (
            '{"ticket_id":"TCK-0003","title":"Settlement Delay",'
            '"description":"Ticket TCK-0003: Settlement Delay observed in Aurora Payment Gateway. '
            "The synthetic event severity is high. Evidence includes generated control output, "
            'workflow status, and timestamp markers.",'
            '"severity":"high","impacted_system":"Aurora Payment Gateway",'
            '"issue_category":"settlement_delay","team":"payments_ops"}\n'
        ),
        encoding="utf-8",
    )

    report = evaluate_agent(tmp_path)

    assert report["metrics"]["trace_coverage_rate"] == 1.0
    assert report["metrics"]["approval_audit_rate"] == 1.0
    assert report["metrics"]["valid_tool_call_rate"] == 1.0
    assert report["metrics"]["side_effect_block_rate"] == 1.0
    assert report["metrics"]["approved_action_execution_rate"] == 1.0
    assert (reports_dir / "agent_eval_summary.json").exists()
