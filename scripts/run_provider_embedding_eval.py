from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.evals.runner import evaluate_provider_embedding_store
from internal_ai_agent.io import read_jsonl, write_json
from internal_ai_agent.providers.openai_embeddings import (
    DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE,
    DEFAULT_OPENAI_EMBEDDING_ENDPOINT,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
    OpenAIEmbeddingClient,
    OpenAIEmbeddingConfig,
    openai_embedding_config_from_env,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Optionally compare local retrieval with provider-backed embeddings."
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Make provider API calls. Omit for a cost-free dry run.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_OPENAI_EMBEDDING_MODEL,
        help="Embedding model id.",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_OPENAI_EMBEDDING_ENDPOINT,
        help="Embedding API endpoint.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE,
        help="Number of texts per embedding request.",
    )
    parser.add_argument(
        "--dimensions",
        type=int,
        default=None,
        help="Optional reduced embedding dimension count.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=30.0,
        help="HTTP timeout for each provider request.",
    )
    parser.add_argument(
        "--status-output",
        default="reports/provider_embedding_eval_status.json",
        help="Path to write run status.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path.cwd()

    if not args.run:
        status = _dry_run_status(project_root, args)
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        return

    env_config = openai_embedding_config_from_env()
    if env_config is None:
        status = {
            **_dry_run_status(project_root, args),
            "status": "blocked",
            "reason": "OPENAI_API_KEY is not set.",
        }
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1)

    config = OpenAIEmbeddingConfig(
        api_key=env_config.api_key,
        model=args.model,
        endpoint=args.endpoint,
        batch_size=args.batch_size,
        dimensions=args.dimensions,
        timeout_seconds=args.timeout_seconds,
    )
    client = OpenAIEmbeddingClient(config)
    report = evaluate_provider_embedding_store(
        project_root,
        embed_texts=client.embed_texts,
        provider_name="openai",
        model=config.model,
    )
    status = {
        "status": "completed",
        "provider": "openai",
        "model": config.model,
        "summary_path": "reports/provider_embedding_eval_summary.json",
        "cases_path": "reports/provider_embedding_eval_cases.jsonl",
        "case_count": report["case_count"],
        "metrics": report["metrics"],
    }
    write_json(Path(args.status_output), status)
    print(json.dumps(status, indent=2, sort_keys=True))


def _dry_run_status(project_root: Path, args: argparse.Namespace) -> dict[str, object]:
    cases = read_jsonl(project_root / "data/eval/golden_cases.jsonl")
    runbooks = read_jsonl(project_root / "data/synthetic/raw_docs/runbooks.jsonl")
    user_roles = sorted({str(case["user_role"]) for case in cases})
    return {
        "status": "dry_run",
        "provider": "openai",
        "model": args.model,
        "case_count": len(cases),
        "runbook_count": len(runbooks),
        "user_role_count": len(user_roles),
        "estimated_embedding_inputs": len(cases) + (len(runbooks) * len(user_roles)),
        "notes": [
            "No provider API calls were made.",
            "Set OPENAI_API_KEY and rerun with --run to create provider-backed results.",
        ],
    }


if __name__ == "__main__":
    main()
