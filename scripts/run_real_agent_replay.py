"""Replay incidents against a REAL LLM agent and produce release-gate evidence.

Opt-in (requires AGENT_RUNNER_API_KEY), so it stays out of deterministic CI.
Point AGENT_RUNNER_ENDPOINT at any OpenAI-compatible endpoint -- a public API or a
self-hosted open model -- and set AGENT_RUNNER_MODEL. The model plays the
operations agent on each built-in incident; its decisions and tool calls are
scored by the same incident-replay release gate as the synthetic controlled agent.
"""

from __future__ import annotations

import re
from pathlib import Path

from internal_ai_agent.evals.candidate_results_export import candidate_results_from_agent_logs
from internal_ai_agent.evals.incident_replay import (
    _default_incident_cases,
    write_incident_replay_suite,
)
from internal_ai_agent.io import write_jsonl
from internal_ai_agent.providers.agent_runner import (
    AGENT_RUNNER_POLICY_VERSION,
    AgentRunnerClient,
    agent_runner_config_from_env,
)


def main() -> None:
    config = agent_runner_config_from_env()
    if config is None:
        print(
            "AGENT_RUNNER_API_KEY not set; skipping real-agent replay. Set "
            "AGENT_RUNNER_API_KEY (and optionally AGENT_RUNNER_ENDPOINT / "
            "AGENT_RUNNER_MODEL for an open model) to run a real agent through the "
            "incident-replay release gate."
        )
        return

    project_root = Path.cwd()
    cases = _default_incident_cases()
    client = AgentRunnerClient(config)
    rows = [client.run_incident(case) for case in cases]

    candidate_id = "real_model_" + re.sub(r"[^A-Za-z0-9]+", "_", config.model).strip("_")
    candidate_results = candidate_results_from_agent_logs(
        rows,
        candidate_id=candidate_id,
        default_model_version=config.model,
        default_policy_version=AGENT_RUNNER_POLICY_VERSION,
    )
    candidate_path = project_root / "reports/real_agent_candidate_results.jsonl"
    write_jsonl(candidate_path, candidate_results)

    summary = write_incident_replay_suite(project_root, candidate_results_path=candidate_path)
    metrics = summary["summary"]
    print(f"Real-agent incident replay complete ({config.model})")
    print(f"- candidate: {candidate_id}")
    print(f"- incidents: {summary['case_count']}")
    print(f"- gate status: {metrics['release_gate_status']}")
    print(f"- gate failures: {metrics['release_gate_fail_count']}")
    print(f"- expected behavior match: {metrics['expected_behavior_match_rate']:.4f}")


if __name__ == "__main__":
    main()
