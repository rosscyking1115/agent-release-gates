from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.io import read_jsonl, write_json
from internal_ai_agent.observability.collector import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_OTLP_ENDPOINT,
    export_spans_to_collector,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export local OpenTelemetry-style spans to an OTLP/HTTP collector."
    )
    parser.add_argument(
        "--spans-path",
        default="reports/observability_otel_spans.jsonl",
        help="Path to local span JSONL export.",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_OTLP_ENDPOINT,
        help="OTLP/HTTP traces endpoint, usually http://host:4318/v1/traces.",
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
        help="HTTP timeout for each collector request.",
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="POST to the collector. Omit this flag for a safe dry run.",
    )
    parser.add_argument(
        "--output",
        default="reports/collector_export_result.json",
        help="Path to write the export summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spans = read_jsonl(Path(args.spans_path))
    summary = export_spans_to_collector(
        spans,
        endpoint=args.endpoint,
        batch_size=args.batch_size,
        timeout_seconds=args.timeout_seconds,
        dry_run=not args.post,
    )
    write_json(Path(args.output), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
