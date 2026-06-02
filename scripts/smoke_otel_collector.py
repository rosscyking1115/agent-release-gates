from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.io import read_jsonl, write_json
from internal_ai_agent.observability.collector import DEFAULT_BATCH_SIZE
from internal_ai_agent.observability.collector_smoke import run_local_collector_smoke


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke test OTLP/HTTP export against a local capture endpoint."
    )
    parser.add_argument(
        "--spans-path",
        default="reports/observability_otel_spans.jsonl",
        help="Path to local span JSONL export.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Number of spans per OTLP payload.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="HTTP timeout for each smoke-test request.",
    )
    parser.add_argument(
        "--output",
        default="reports/collector_export_smoke.json",
        help="Path to write the smoke-test summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spans = read_jsonl(Path(args.spans_path))
    summary = run_local_collector_smoke(
        spans,
        batch_size=args.batch_size,
        timeout_seconds=args.timeout_seconds,
    )
    write_json(Path(args.output), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
