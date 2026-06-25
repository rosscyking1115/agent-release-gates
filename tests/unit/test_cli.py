from __future__ import annotations

from importlib import metadata


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
