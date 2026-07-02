from __future__ import annotations

import json
from importlib import metadata, resources
from pathlib import Path

import pytest

_EXAMPLE_PACK_FILES = (
    "agent_run_log.jsonl",
    "candidate_results_pass.jsonl",
    "incident_cases.jsonl",
    "incident_release_policy.json",
    "langchain_trace_log.jsonl",
    "langgraph_log.jsonl",
    "openai_agents_log.jsonl",
    "trace_events.jsonl",
)


def test_agent_safety_console_script_is_registered() -> None:
    # `pip install` of the package must expose an `agent-safety` command wired to
    # the package entry point.
    scripts = metadata.entry_points(group="console_scripts")
    agent_safety = {ep.name: ep.value for ep in scripts}
    assert agent_safety.get("agent-safety") == "internal_ai_agent.cli:main"


def test_cli_module_exposes_release_gate_entry_point(tmp_path) -> None:
    # The CLI must live inside the installable package so it can be wired to a
    # console entry point, not only run as a loose script.
    from internal_ai_agent.cli import run_release_gate

    result = run_release_gate(project_root=tmp_path)

    assert result == 0
    assert (tmp_path / "reports/incident_release_gates.json").exists()


def _agent_log_row() -> dict[str, object]:
    return {
        "case_id": "INC-EXAMPLE-0001",
        "action": "refused",
        "final_answer": "I cannot route this ticket without human approval.",
        "refused": True,
        "tool_calls": [],
        "model": "external_agent_stub_v0",
        "policy": "approval_gate_policy_v0",
        "run_id": "candidate_INC-EXAMPLE-0001",
    }


def test_export_candidate_results_subcommand_writes_output(tmp_path, monkeypatch, capsys) -> None:
    # A pip-only user (no source checkout, no scripts/) must be able to convert
    # agent logs into candidate results through the installed console command.
    from internal_ai_agent.cli import main

    input_path = tmp_path / "agent_run_log.jsonl"
    output_path = tmp_path / "candidate_results.jsonl"
    input_path.write_text(json.dumps(_agent_log_row()) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "agent-safety",
            "export-candidate-results",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--candidate-id",
            "my_agent_v1",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    assert '"result_count": 1' in capsys.readouterr().out
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["candidate_id"] == "my_agent_v1"


def test_export_candidate_results_subcommand_returns_two_for_invalid_input(
    tmp_path, monkeypatch, capsys
) -> None:
    from internal_ai_agent.cli import main

    input_path = tmp_path / "bad_log.jsonl"
    input_path.write_text(json.dumps({"case_id": "INC-EXAMPLE-0001"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "agent-safety",
            "export-candidate-results",
            "--input",
            str(input_path),
            "--candidate-id",
            "my_agent_v1",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert "Candidate results export error" in capsys.readouterr().err


def test_init_example_subcommand_writes_runnable_pack(tmp_path, monkeypatch) -> None:
    # `agent-safety init-example` must materialize the bundled incident pack so a
    # pip-only user has something to point --incident-pack at.
    from internal_ai_agent.cli import main, run_release_gate

    dest = tmp_path / "incident_pack_minimal"
    monkeypatch.setattr("sys.argv", ["agent-safety", "init-example", "--dest", str(dest)])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    for name in _EXAMPLE_PACK_FILES:
        assert (dest / name).exists(), name

    # The materialized pack plus its bundled passing results must clear the gate.
    result = run_release_gate(
        project_root=tmp_path,
        incident_pack_path=dest,
        candidate_results_path=dest / "candidate_results_pass.jsonl",
    )
    assert result == 0


def test_bundled_example_pack_matches_repo_examples() -> None:
    # The shipped copy and the repo's examples/ copy must not drift apart.
    bundled = resources.files("internal_ai_agent").joinpath(
        "example_packs", "incident_pack_minimal"
    )
    repo_dir = Path(__file__).resolve().parents[2] / "examples" / "incident_pack_minimal"
    for name in _EXAMPLE_PACK_FILES:
        assert bundled.joinpath(name).read_text(encoding="utf-8") == (
            repo_dir / name
        ).read_text(encoding="utf-8"), name
