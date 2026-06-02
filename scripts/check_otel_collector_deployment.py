from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib import request

from internal_ai_agent.io import read_jsonl, write_json
from internal_ai_agent.observability.collector import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_OTLP_ENDPOINT,
    export_spans_to_collector,
)
from internal_ai_agent.observability.collector_deployment import (
    summarize_collector_deployment,
)

DEFAULT_COLLECTOR_METRICS_ENDPOINT = "http://localhost:8888/metrics"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check OTLP/HTTP export against a running OpenTelemetry Collector."
    )
    parser.add_argument(
        "--spans-path",
        default="reports/observability_otel_spans.jsonl",
        help="Path to local span JSONL export.",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_OTLP_ENDPOINT,
        help="OTLP/HTTP traces endpoint for the collector.",
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
        "--collector-metrics-endpoint",
        default=DEFAULT_COLLECTOR_METRICS_ENDPOINT,
        help="Collector self-metrics endpoint.",
    )
    parser.add_argument(
        "--collector-metrics-timeout-seconds",
        type=float,
        default=15.0,
        help="How long to wait for collector self-metrics to show exported spans.",
    )
    parser.add_argument(
        "--output",
        default="reports/collector_deployment_check.json",
        help="Path to write the deployment-check summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spans = read_jsonl(Path(args.spans_path))

    try:
        before_metrics = _read_collector_metrics(args.collector_metrics_endpoint)
        export_summary = export_spans_to_collector(
            spans,
            endpoint=args.endpoint,
            batch_size=args.batch_size,
            timeout_seconds=args.timeout_seconds,
            dry_run=False,
        )
        after_metrics = _wait_for_span_metrics(
            args.collector_metrics_endpoint,
            before_metrics=before_metrics,
            expected_span_delta=len(spans),
            timeout_seconds=args.collector_metrics_timeout_seconds,
        )
        summary = summarize_collector_deployment(
            export_summary,
            collector_metrics_endpoint=args.collector_metrics_endpoint,
            receiver_accepted_span_delta=(
                after_metrics["receiver_accepted_spans"]
                - before_metrics["receiver_accepted_spans"]
            ),
            exporter_sent_span_delta=(
                after_metrics["exporter_sent_spans"]
                - before_metrics["exporter_sent_spans"]
            ),
        )
    except Exception as exc:
        summary = _failure_summary(args, len(spans), exc)

    write_json(Path(args.output), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


def _wait_for_span_metrics(
    endpoint: str,
    *,
    before_metrics: dict[str, int],
    expected_span_delta: int,
    timeout_seconds: float,
) -> dict[str, int]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() <= deadline:
        metrics = _read_collector_metrics(endpoint)
        receiver_delta = (
            metrics["receiver_accepted_spans"]
            - before_metrics["receiver_accepted_spans"]
        )
        exporter_delta = (
            metrics["exporter_sent_spans"] - before_metrics["exporter_sent_spans"]
        )
        if receiver_delta >= expected_span_delta and exporter_delta >= expected_span_delta:
            return metrics
        time.sleep(0.25)
    return _read_collector_metrics(endpoint)


def _read_collector_metrics(endpoint: str) -> dict[str, int]:
    with request.urlopen(endpoint, timeout=5.0) as response:
        metrics_text = response.read().decode("utf-8", errors="replace")
    return {
        "receiver_accepted_spans": _prometheus_metric_sum(
            metrics_text, "otelcol_receiver_accepted_spans"
        ),
        "exporter_sent_spans": _prometheus_metric_sum(
            metrics_text, "otelcol_exporter_sent_spans"
        ),
    }


def _prometheus_metric_sum(metrics_text: str, metric_name: str) -> int:
    total = 0.0
    for line in metrics_text.splitlines():
        if not line.startswith(metric_name):
            continue
        try:
            total += float(line.rsplit(maxsplit=1)[1])
        except (IndexError, ValueError):
            continue
    return int(total)


def _failure_summary(
    args: argparse.Namespace,
    span_count: int,
    exc: Exception,
) -> dict[str, Any]:
    return {
        "export_mode": "collector_deployment_check",
        "collector_endpoint": args.endpoint,
        "span_count": span_count,
        "batch_size": args.batch_size,
        "collector_metrics_endpoint": args.collector_metrics_endpoint,
        "passed": False,
        "failed_checks": ["collector_deployment_check_failed"],
        "error": str(exc),
        "notes": [
            "Start the collector with: docker compose --profile observability up -d otel-collector"
        ],
    }


if __name__ == "__main__":
    main()
