from __future__ import annotations

from typing import Any

ACCEPTED_COLLECTOR_STATUS_CODES = {200, 202}


def summarize_collector_deployment(
    export_summary: dict[str, Any],
    *,
    collector_metrics_endpoint: str,
    receiver_accepted_span_delta: int,
    exporter_sent_span_delta: int,
) -> dict[str, Any]:
    status_codes = list(export_summary.get("status_codes", []))
    payload_count = int(export_summary.get("payload_count", 0))
    posted_payload_count = int(export_summary.get("posted_payload_count", 0))
    failed_checks = _deployment_failed_checks(
        payload_count=payload_count,
        posted_payload_count=posted_payload_count,
        status_codes=status_codes,
        span_count=int(export_summary.get("span_count", 0)),
        receiver_accepted_span_delta=receiver_accepted_span_delta,
        exporter_sent_span_delta=exporter_sent_span_delta,
    )

    return {
        **export_summary,
        "export_mode": "collector_deployment_check",
        "collector_post_mode": export_summary.get("export_mode"),
        "collector_metrics_endpoint": collector_metrics_endpoint,
        "receiver_accepted_span_delta": receiver_accepted_span_delta,
        "exporter_sent_span_delta": exporter_sent_span_delta,
        "accepted_status_codes": sorted(ACCEPTED_COLLECTOR_STATUS_CODES),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
        "notes": [
            "Posts generated OTLP/HTTP payloads to a real OpenTelemetry Collector service.",
            (
                "Collector self-metrics must show the expected accepted and exported "
                "span deltas."
            ),
        ],
    }


def _deployment_failed_checks(
    *,
    payload_count: int,
    posted_payload_count: int,
    status_codes: list[int],
    span_count: int,
    receiver_accepted_span_delta: int,
    exporter_sent_span_delta: int,
) -> list[str]:
    failed_checks: list[str] = []
    if posted_payload_count != payload_count:
        failed_checks.append("posted_payload_count_mismatch")
    if len(status_codes) != payload_count:
        failed_checks.append("status_code_count_mismatch")
    if any(
        status_code not in ACCEPTED_COLLECTOR_STATUS_CODES
        for status_code in status_codes
    ):
        failed_checks.append("unexpected_status_code")
    if receiver_accepted_span_delta < span_count:
        failed_checks.append("receiver_accepted_span_delta_below_expected")
    if exporter_sent_span_delta < span_count:
        failed_checks.append("exporter_sent_span_delta_below_expected")
    return failed_checks
