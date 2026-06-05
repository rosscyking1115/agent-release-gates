from __future__ import annotations

import argparse
from pathlib import Path

from internal_ai_agent.evals.techqa_public import (
    TECHQA_DEFAULT_SAMPLE_LIMIT,
    write_techqa_sample,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the tracked TechQA public RAG benchmark sample."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=TECHQA_DEFAULT_SAMPLE_LIMIT,
        help=f"Number of public TechQA cases to include. Default: {TECHQA_DEFAULT_SAMPLE_LIMIT}.",
    )
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=2400,
        help="Maximum characters to retain from each public support context.",
    )
    args = parser.parse_args()
    output_path = write_techqa_sample(
        Path.cwd(),
        limit=args.limit,
        max_context_chars=args.max_context_chars,
    )
    print(f"TechQA public benchmark sample written to {output_path}")


if __name__ == "__main__":
    main()
