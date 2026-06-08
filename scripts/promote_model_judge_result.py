from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.evals.model_judge_promotion import promote_model_judge_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a reviewed hosted model-judge result for public reporting."
    )
    parser.add_argument(
        "--reviewer",
        default="maintainer",
        help="Reviewer name or role recorded in the public summary.",
    )
    parser.add_argument(
        "--decision",
        default="publish_with_limitations",
        choices=["publish_with_limitations", "publish", "do_not_publish"],
        help="Manual publication decision after reviewing provider-backed results.",
    )
    parser.add_argument(
        "--note",
        default=(
            "Reviewed provider-backed result. Publish with limitation: one benign "
            "planning case was over-blocked by the hosted judge."
        ),
        help="Short review note included in the public summary.",
    )
    parser.add_argument(
        "--summary-input",
        default="reports/model_judge_eval_summary.json",
        help="Local ignored hosted model-judge summary input.",
    )
    parser.add_argument(
        "--cases-input",
        default="reports/model_judge_eval_cases.jsonl",
        help="Local ignored hosted model-judge cases input.",
    )
    parser.add_argument(
        "--output",
        default="reports/model_judge_reviewed_summary.json",
        help="Sanitized public summary output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path.cwd()
    output = promote_model_judge_result(
        project_root,
        summary_path=Path(args.summary_input),
        cases_path=Path(args.cases_input),
        output_path=Path(args.output),
        reviewer=args.reviewer,
        decision=args.decision,
        note=args.note,
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
