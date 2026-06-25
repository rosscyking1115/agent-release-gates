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
        default=None,
        help=(
            "Optional policy-as-code JSON file with incident replay gate thresholds. "
            "When --incident-pack is used, an incident_release_policy.json file in "
            "the pack is used automatically if present."
        ),
    )
    parser.add_argument(
        "--incident-pack",
        default=None,
        help=(
            "Directory containing incident_cases.jsonl, trace_events.jsonl, and "
            "optional incident_release_policy.json files."
        ),
    )
    args = parser.parse_args()
    try:
        summary = write_incident_replay_suite(
            Path.cwd(),
            policy_path=Path(args.policy) if args.policy else None,
            incident_pack_path=Path(args.incident_pack) if args.incident_pack else None,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Incident replay configuration error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    metrics = summary["summary"]
    print("Incident replay suite complete")
    incident_pack = summary.get("incident_pack", {})
    if incident_pack:
        print(f"- incident pack: {incident_pack.get('source', 'built_in')}")
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
