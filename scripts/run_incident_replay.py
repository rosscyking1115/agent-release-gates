from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.incident_replay import write_incident_replay_suite


def main() -> None:
    summary = write_incident_replay_suite(Path.cwd())
    metrics = summary["summary"]
    print("Incident replay suite complete")
    print(f"- cases: {summary['case_count']}")
    print(f"- gate status: {metrics['release_gate_status']}")
    print(f"- gate failures: {metrics['release_gate_fail_count']}")
    print(f"- expected behavior match: {metrics['expected_behavior_match_rate']:.4f}")
    print(f"- incident closure rate: {metrics['incident_closure_rate']:.4f}")
    if metrics["release_gate_fail_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
