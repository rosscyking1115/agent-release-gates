from __future__ import annotations

import argparse
from pathlib import Path

from internal_ai_agent.evals.wixqa_public import (
    WIXQA_DEFAULT_SAMPLE_LIMIT,
    write_wixqa_sample,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the tracked WixQA public enterprise RAG benchmark sample."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=WIXQA_DEFAULT_SAMPLE_LIMIT,
        help=f"Number of public WixQA cases to include. Default: {WIXQA_DEFAULT_SAMPLE_LIMIT}.",
    )
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=2400,
        help="Maximum characters to retain from each public support article.",
    )
    args = parser.parse_args()
    output_path = write_wixqa_sample(
        Path.cwd(),
        limit=args.limit,
        max_context_chars=args.max_context_chars,
    )
    print(f"WixQA public benchmark sample written to {output_path}")


if __name__ == "__main__":
    main()
