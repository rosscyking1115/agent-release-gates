from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.evals.public_rag_model_reranker import (
    DEFAULT_PACKET_LIMIT,
    write_public_rag_model_reranker_adapter_status,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the dry-run public RAG hosted-reranker packet."
    )
    parser.add_argument(
        "--packet-limit",
        type=int,
        default=DEFAULT_PACKET_LIMIT,
        help="Maximum public RAG cases to include in the hosted reranker packet.",
    )
    args = parser.parse_args()

    status = write_public_rag_model_reranker_adapter_status(
        Path.cwd(),
        packet_limit=args.packet_limit,
    )
    print(json.dumps(status, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
