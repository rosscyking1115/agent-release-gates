from __future__ import annotations

import argparse
import json
import sys
from importlib import resources
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.candidate_results_export import (
    export_candidate_results_from_agent_log,
)
from internal_ai_agent.evals.incident_replay import write_incident_replay_suite

# Files that make up the bundled minimal incident pack. Kept in sync with the
# repo's examples/incident_pack_minimal copy by a drift-guard test.
EXAMPLE_PACK_FILES = (
    "agent_run_log.jsonl",
    "candidate_results_pass.jsonl",
    "incident_cases.jsonl",
    "incident_release_policy.json",
    "langchain_trace_log.jsonl",
    "trace_events.jsonl",
)


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.command == "release-gate":
        try:
            result = run_release_gate(
                project_root=Path(args.project_root),
                policy_path=Path(args.policy) if args.policy else None,
                incident_pack_path=Path(args.incident_pack) if args.incident_pack else None,
                candidate_results_path=Path(args.candidate_results)
                if args.candidate_results
                else None,
            )
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            print(f"Release gate configuration error: {exc}", file=sys.stderr)
            result = 2
        raise SystemExit(result)
    if args.command == "export-candidate-results":
        result = run_export_candidate_results(
            input_path=Path(args.input),
            output_path=Path(args.output),
            candidate_id=args.candidate_id,
            model_version=args.model_version,
            policy_version=args.policy_version,
            source_format=args.source_format,
        )
        raise SystemExit(result)
    if args.command == "init-example":
        result = run_init_example(dest=Path(args.dest))
        raise SystemExit(result)
    parser.error("A command is required.")


def run_release_gate(
    *,
    project_root: Path,
    policy_path: Path | None = None,
    incident_pack_path: Path | None = None,
    candidate_results_path: Path | None = None,
) -> int:
    summary = write_incident_replay_suite(
        project_root,
        policy_path=policy_path,
        incident_pack_path=incident_pack_path,
        candidate_results_path=candidate_results_path,
    )
    metrics = summary["summary"]
    _print_release_gate_summary(summary, metrics)
    return 1 if int(metrics["release_gate_fail_count"]) else 0


def run_export_candidate_results(
    *,
    input_path: Path,
    output_path: Path,
    candidate_id: str,
    model_version: str = "external_candidate_result",
    policy_version: str = "unknown",
    source_format: str = "generic_agent_log",
) -> int:
    try:
        summary = export_candidate_results_from_agent_log(
            input_path=input_path,
            output_path=output_path,
            candidate_id=candidate_id,
            default_model_version=model_version,
            default_policy_version=policy_version,
            source_format=source_format,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Candidate results export error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def run_init_example(*, dest: Path) -> int:
    source = resources.files("internal_ai_agent").joinpath(
        "example_packs", "incident_pack_minimal"
    )
    dest.mkdir(parents=True, exist_ok=True)
    for name in EXAMPLE_PACK_FILES:
        (dest / name).write_text(
            source.joinpath(name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    print(f"Wrote example incident pack to {dest}")
    for name in EXAMPLE_PACK_FILES:
        print(f"- {name}")
    print(
        "\nNext: score the bundled passing results against the pack:\n"
        f"  agent-safety release-gate --incident-pack {dest} "
        f"--candidate-results {dest / 'candidate_results_pass.jsonl'}"
    )
    return 0


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
        default=None,
        help=(
            "Optional policy-as-code JSON file with incident replay gate thresholds. "
            "When --incident-pack is used, an incident_release_policy.json file in "
            "the pack is used automatically if present."
        ),
    )
    release_gate.add_argument(
        "--incident-pack",
        default=None,
        help=(
            "Directory containing incident_cases.jsonl, trace_events.jsonl, and "
            "optional incident_release_policy.json files."
        ),
    )
    release_gate.add_argument(
        "--candidate-results",
        default=None,
        help=(
            "Optional JSONL file containing one submitted candidate result per "
            "incident. This scores an external agent without executing its code."
        ),
    )

    export = subparsers.add_parser(
        "export-candidate-results",
        help="Convert external-agent JSONL logs into candidate_results.jsonl.",
    )
    export.add_argument(
        "--input",
        required=True,
        help="Path to an external agent JSONL run log.",
    )
    export.add_argument(
        "--output",
        default="candidate_results.jsonl",
        help="Path to write normalized candidate results JSONL.",
    )
    export.add_argument(
        "--candidate-id",
        required=True,
        help="Safe identifier for the agent or release candidate under test.",
    )
    export.add_argument(
        "--model-version",
        default="external_candidate_result",
        help="Default model or runner version when the input row does not include one.",
    )
    export.add_argument(
        "--policy-version",
        default="unknown",
        help="Default safety policy or prompt version when the input row does not include one.",
    )
    export.add_argument(
        "--source-format",
        default="generic_agent_log",
        help=(
            "Input adapter format. Use 'langchain_trace' or 'langsmith_run' for "
            "LangChain-style traces; other labels are treated as generic rows."
        ),
    )

    init_example = subparsers.add_parser(
        "init-example",
        help="Write the bundled minimal incident pack to a directory.",
    )
    init_example.add_argument(
        "--dest",
        default="incident_pack_minimal",
        help="Directory to write the example incident pack into.",
    )
    return parser


def _print_release_gate_summary(summary: dict[str, Any], metrics: dict[str, Any]) -> None:
    print("Agent safety release gate complete")
    incident_pack = summary.get("incident_pack", {})
    if incident_pack:
        print(f"- incident pack: {incident_pack.get('source', 'built_in')}")
    candidate_results = summary.get("candidate_results", {})
    if candidate_results:
        print(f"- candidate results: {candidate_results.get('source', 'built_in')}")
        print(f"- candidate id: {summary['candidate_id']}")
    print(f"- policy: {summary['policy_id']} ({summary['policy_path']})")
    print(f"- incidents: {summary['case_count']}")
    print(f"- gate status: {metrics['release_gate_status']}")
    print(f"- gate failures: {metrics['release_gate_fail_count']}")
    print(f"- incident closure rate: {metrics['incident_closure_rate']:.4f}")
    print(f"- expected behavior match: {metrics['expected_behavior_match_rate']:.4f}")


if __name__ == "__main__":
    main()
