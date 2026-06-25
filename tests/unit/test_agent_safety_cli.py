from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_agent_safety_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts/agent_safety.py"
    spec = importlib.util.spec_from_file_location("agent_safety_cli", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_release_gate_cli_runner_returns_zero_for_default_policy(tmp_path) -> None:
    module = _load_agent_safety_module()

    result = module.run_release_gate(project_root=tmp_path)

    assert result == 0
    assert (tmp_path / "reports/incident_release_gates.json").exists()


def test_release_gate_cli_runner_raises_for_missing_explicit_policy(tmp_path) -> None:
    module = _load_agent_safety_module()

    with pytest.raises(FileNotFoundError):
        module.run_release_gate(
            project_root=tmp_path,
            policy_path=tmp_path / "missing_policy.json",
        )


def test_release_gate_cli_runner_raises_for_invalid_policy_threshold(tmp_path) -> None:
    module = _load_agent_safety_module()
    policy_path = tmp_path / "invalid_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "policy_id": "invalid_cli_policy",
                "min_expected_behavior_match_rate": 1.01,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        module.run_release_gate(project_root=tmp_path, policy_path=policy_path)


def test_main_returns_two_for_missing_policy(tmp_path, monkeypatch, capsys) -> None:
    module = _load_agent_safety_module()
    monkeypatch.setattr(
        "sys.argv",
        [
            "agent-safety",
            "release-gate",
            "--project-root",
            str(tmp_path),
            "--policy",
            str(tmp_path / "missing_policy.json"),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        module.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "Release gate configuration error" in captured.err
