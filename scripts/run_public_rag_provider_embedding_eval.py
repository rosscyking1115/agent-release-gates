from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.evals.public_rag_provider_embedding import (
    available_tracks,
    evaluate_public_rag_provider_embedding,
    provider_embedding_input_estimate,
)
from internal_ai_agent.evals.public_rag_publish import PUBLISHED_PATH
from internal_ai_agent.io import write_json
from internal_ai_agent.providers.openai_embeddings import (
    DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE,
    DEFAULT_OPENAI_EMBEDDING_ENDPOINT,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
    OpenAIEmbeddingClient,
    OpenAIEmbeddingConfig,
    openai_embedding_config_from_env,
)

STATUS_PATH = "reports/public_rag_provider_embedding_status.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Optionally compare local retrieval with provider-backed embeddings on the "
            "public TechQA and WixQA RAG tracks."
        )
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Make provider API calls. Omit for a cost-free dry run.",
    )
    parser.add_argument(
        "--track",
        choices=[*available_tracks(), "both"],
        default="both",
        help="Which public track(s) to evaluate.",
    )
    parser.add_argument("--model", default=DEFAULT_OPENAI_EMBEDDING_MODEL)
    parser.add_argument("--endpoint", default=DEFAULT_OPENAI_EMBEDDING_ENDPOINT)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE)
    parser.add_argument("--dimensions", type=int, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    return parser.parse_args()


def _tracks(track: str) -> list[str]:
    return available_tracks() if track == "both" else [track]


def _finding(tracks: dict[str, dict]) -> str:
    parts = []
    for name, block in tracks.items():
        if block.get("status") != "evaluated":
            continue
        p = block["provider_metrics"]["retrieval_hit_rate_at_3"]
        local = block["local_primary_metrics"]["retrieval_hit_rate_at_3"]
        delta = block["hit_rate_delta"]
        verb = "beats" if delta > 0 else "ties" if delta == 0 else "trails"
        parts.append(
            f"On {name}, the provider embedding {verb} the local retriever on hit rate@3 "
            f"({p:.4f} vs {local:.4f}, delta {delta:+.4f})."
        )
    return " ".join(parts) if parts else "No tracks were evaluated."


def _dry_run(project_root: Path, args: argparse.Namespace) -> dict[str, object]:
    estimates = {
        track: provider_embedding_input_estimate(project_root, track)
        for track in _tracks(args.track)
    }
    return {
        "status": "dry_run",
        "provider": "openai",
        "model": args.model,
        "tracks": estimates,
        "total_embedding_inputs": sum(e["embedding_inputs"] for e in estimates.values()),
        "notes": [
            "No provider API calls were made.",
            "Set OPENAI_API_KEY and rerun with --run to create provider-backed results.",
        ],
    }


def main() -> None:
    args = parse_args()
    project_root = Path.cwd()

    if not args.run:
        status = _dry_run(project_root, args)
        write_json(Path(STATUS_PATH), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        return

    env_config = openai_embedding_config_from_env()
    if env_config is None:
        status = {
            **_dry_run(project_root, args),
            "status": "blocked",
            "reason": "OPENAI_API_KEY is not set.",
        }
        write_json(Path(STATUS_PATH), status)
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
    tracks = {
        track: evaluate_public_rag_provider_embedding(
            project_root,
            embed_texts=client.embed_texts,
            provider="openai",
            model=config.model,
            track=track,
        )
        for track in _tracks(args.track)
    }
    published = {
        "report_type": "public_rag_provider_embedding_published_result",
        "status": "published",
        "provider": "openai",
        "model": config.model,
        "run_type": "reviewed_single_credentialed_run",
        "tracks": tracks,
        "finding": _finding(tracks),
        "review_note": (
            "Single credentialed run, manually reviewed. Retrieval metrics (hit@3, top-1 "
            "citation, MRR@3) are rank-based and directly comparable to the local retriever; "
            "abstention uses the local threshold and is indicative only. Regenerate with "
            "scripts/run_public_rag_provider_embedding_eval.py --run and OPENAI_API_KEY."
        ),
    }
    write_json(Path(PUBLISHED_PATH), published)
    write_json(Path(STATUS_PATH), {"status": "completed", "tracks": list(tracks)})
    print(json.dumps(published, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
