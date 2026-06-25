from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.incident_replay import write_incident_replay_suite


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.command == "release-gate":
        try:
            result = run_release_gate(
                project_root=Path(args.project_root),
                policy_path=Path(args.policy) if args.policy else None,
            )
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            print(f"Release gate configuration error: {exc}", file=sys.stderr)
            result = 2
        raise SystemExit(result)
    parser.error("A command is required.")


def run_release_gate(*, project_root: Path, policy_path: Path | None = None) -> int:
    summary = write_incident_replay_suite(project_root, policy_path=policy_path)
    metrics = summary["summary"]
    _print_release_gate_summary(summary, metrics)
    return 1 if int(metrics["release_gate_fail_count"]) else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-safety",
        description="Run deterministic AI-agent safety release gates.",
    )
    subparsers = parser.add_subparsers(dest="command")
    release_gate = subparsers.add_parser(
        "release-gate",
        help="Run incident replay release gates and exit non-zero on blocking failures.",
    )
    release_gate.add_argument(
        "--project-root",
        default=".",
        help="Repository root containing data, reports, and config directories.",
    )
    release_gate.add_argument(
        "--policy",
        default="config/incident_release_policy.json",
        help="Policy-as-code JSON file with incident replay gate thresholds.",
    )
    return parser


def _print_release_gate_summary(summary: dict[str, Any], metrics: dict[str, Any]) -> None:
    print("Agent safety release gate complete")
    print(f"- policy: {summary['policy_id']} ({summary['policy_path']})")
    print(f"- incidents: {summary['case_count']}")
    print(f"- gate status: {metrics['release_gate_status']}")
    print(f"- gate failures: {metrics['release_gate_fail_count']}")
    print(f"- incident closure rate: {metrics['incident_closure_rate']:.4f}")
    print(f"- expected behavior match: {metrics['expected_behavior_match_rate']:.4f}")


if __name__ == "__main__":
    main()
