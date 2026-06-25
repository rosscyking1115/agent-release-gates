from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from internal_ai_agent.evals.incident_replay import write_incident_replay_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the incident replay suite.")
    parser.add_argument(
        "--policy",
        default="config/incident_release_policy.json",
        help="Policy-as-code JSON file with incident replay gate thresholds.",
    )
    args = parser.parse_args()
    try:
        summary = write_incident_replay_suite(Path.cwd(), policy_path=Path(args.policy))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Incident replay configuration error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    metrics = summary["summary"]
    print("Incident replay suite complete")
    print(f"- policy: {summary['policy_id']} ({summary['policy_path']})")
    print(f"- cases: {summary['case_count']}")
    print(f"- gate status: {metrics['release_gate_status']}")
    print(f"- gate failures: {metrics['release_gate_fail_count']}")
    print(f"- expected behavior match: {metrics['expected_behavior_match_rate']:.4f}")
    print(f"- incident closure rate: {metrics['incident_closure_rate']:.4f}")
    if metrics["release_gate_fail_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
