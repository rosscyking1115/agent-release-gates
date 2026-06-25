from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from internal_ai_agent.evals.candidate_results_export import (
    export_candidate_results_from_agent_log,
)


def main() -> None:
    args = _parser().parse_args()
    try:
        summary = export_candidate_results_from_agent_log(
            input_path=Path(args.input),
            output_path=Path(args.output),
            candidate_id=args.candidate_id,
            default_model_version=args.model_version,
            default_policy_version=args.policy_version,
            source_format=args.source_format,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Candidate results export error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    print(json.dumps(summary, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert external-agent JSONL logs into candidate_results.jsonl "
            "for Agent Release Safety Gates. Supports generic rows and "
            "LangChain/LangSmith-style trace rows."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to an external agent JSONL run log.",
    )
    parser.add_argument(
        "--output",
        default="candidate_results.jsonl",
        help="Path to write normalized candidate results JSONL.",
    )
    parser.add_argument(
        "--candidate-id",
        required=True,
        help="Safe identifier for the agent or release candidate under test.",
    )
    parser.add_argument(
        "--model-version",
        default="external_candidate_result",
        help="Default model or runner version when the input row does not include one.",
    )
    parser.add_argument(
        "--policy-version",
        default="unknown",
        help="Default safety policy or prompt version when the input row does not include one.",
    )
    parser.add_argument(
        "--source-format",
        default="generic_agent_log",
        help=(
            "Input adapter format. Use 'langchain_trace' or 'langsmith_run' for "
            "LangChain-style traces; other labels are treated as generic rows."
        ),
    )
    return parser


if __name__ == "__main__":
    main()
