from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib import request

from internal_ai_agent.io import read_jsonl, write_json

DEFAULT_OTLP_ENDPOINT = "http://localhost:4318/v1/traces"
DEFAULT_SERVICE_NAME = "internal-ai-agent-eval-lab"
DEFAULT_SERVICE_VERSION = "0.1.0"
DEFAULT_BATCH_SIZE = 200


HttpPost = Callable[[str, bytes, Mapping[str, str], float], tuple[int, str]]


def write_collector_export_preview(
    project_root: Path,
    *,
    endpoint: str = DEFAULT_OTLP_ENDPOINT,
    batch_size: int = DEFAULT_BATCH_SIZE,
    service_name: str = DEFAULT_SERVICE_NAME,
    service_version: str = DEFAULT_SERVICE_VERSION,
) -> dict[str, Any]:
    spans_path = project_root / "reports/observability_otel_spans.jsonl"
    spans = read_jsonl(spans_path)
    preview = collector_export_preview(
        spans,
        endpoint=endpoint,
        batch_size=batch_size,
        service_name=service_name,
        service_version=service_version,
    )
    write_json(project_root / "reports/collector_export_preview.json", preview)
    return preview


def collector_export_preview(
    spans: list[dict[str, Any]],
    *,
    endpoint: str = DEFAULT_OTLP_ENDPOINT,
    batch_size: int = DEFAULT_BATCH_SIZE,
    service_name: str = DEFAULT_SERVICE_NAME,
    service_version: str = DEFAULT_SERVICE_VERSION,
) -> dict[str, Any]:
    payloads = otlp_trace_payloads(
        spans,
        batch_size=batch_size,
        service_name=service_name,
        service_version=service_version,
    )
    return {
        "export_mode": "dry_run_preview",
        "collector_endpoint": endpoint,
        "service_name": service_name,
        "service_version": service_version,
        "source_path": "reports/observability_otel_spans.jsonl",
        "span_count": len(spans),
        "trace_count": len({span["trace_id"] for span in spans}),
        "root_span_count": sum(1 for span in spans if span.get("parent_span_id") is None),
        "batch_size": batch_size,
        "payload_count": len(payloads),
        "first_payload_span_count": _payload_span_count(payloads[0]) if payloads else 0,
        "notes": [
            "Dry run only; no network call is made by the evaluation runner.",
            "Use scripts/export_otel_collector.py with --endpoint to POST OTLP JSON.",
        ],
    }


def export_spans_to_collector(
    spans: list[dict[str, Any]],
    *,
    endpoint: str = DEFAULT_OTLP_ENDPOINT,
    batch_size: int = DEFAULT_BATCH_SIZE,
    service_name: str = DEFAULT_SERVICE_NAME,
    service_version: str = DEFAULT_SERVICE_VERSION,
    timeout_seconds: float = 10.0,
    headers: Mapping[str, str] | None = None,
    dry_run: bool = True,
    http_post: HttpPost | None = None,
) -> dict[str, Any]:
    payloads = otlp_trace_payloads(
        spans,
        batch_size=batch_size,
        service_name=service_name,
        service_version=service_version,
    )
    base_summary: dict[str, Any] = {
        "export_mode": "dry_run" if dry_run else "posted",
        "collector_endpoint": endpoint,
        "service_name": service_name,
        "service_version": service_version,
        "span_count": len(spans),
        "trace_count": len({span["trace_id"] for span in spans}),
        "batch_size": batch_size,
        "payload_count": len(payloads),
    }
    if dry_run:
        return {
            **base_summary,
            "posted_payload_count": 0,
            "status_codes": [],
            "notes": ["Dry run only; no network call was made."],
        }

    request_headers = {"Content-Type": "application/json", **dict(headers or {})}
    post = http_post or _http_post
    status_codes: list[int] = []
    response_previews: list[str] = []
    for payload in payloads:
        status_code, response_text = post(
            endpoint,
            json.dumps(payload, sort_keys=True).encode("utf-8"),
            request_headers,
            timeout_seconds,
        )
        status_codes.append(status_code)
        if response_text:
            response_previews.append(response_text[:200])

    return {
        **base_summary,
        "posted_payload_count": len(payloads),
        "status_codes": status_codes,
        "response_previews": response_previews,
    }


def otlp_trace_payloads(
    spans: list[dict[str, Any]],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    service_name: str = DEFAULT_SERVICE_NAME,
    service_version: str = DEFAULT_SERVICE_VERSION,
) -> list[dict[str, Any]]:
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    return [
        otlp_trace_payload(
            spans[index : index + batch_size],
            service_name=service_name,
            service_version=service_version,
        )
        for index in range(0, len(spans), batch_size)
    ]


def otlp_trace_payload(
    spans: list[dict[str, Any]],
    *,
    service_name: str = DEFAULT_SERVICE_NAME,
    service_version: str = DEFAULT_SERVICE_VERSION,
) -> dict[str, Any]:
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        _attribute("service.name", service_name),
                        _attribute("service.version", service_version),
                        _attribute("deployment.environment", "local-synthetic-lab"),
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "internal_ai_agent.observability.collector",
                            "version": service_version,
                        },
                        "spans": [_otlp_span(span) for span in spans],
                    }
                ],
            }
        ]
    }


def _otlp_span(span: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "traceId": span["trace_id"],
        "spanId": span["span_id"],
        "name": span["name"],
        "kind": 1,
        "startTimeUnixNano": str(span["start_time_unix_nano"]),
        "endTimeUnixNano": str(span["end_time_unix_nano"]),
        "status": {"code": _status_code(span.get("status", {}).get("code", "UNSET"))},
        "attributes": [
            _attribute(key, value)
            for key, value in sorted(span.get("attributes", {}).items())
        ],
    }
    if span.get("parent_span_id"):
        payload["parentSpanId"] = span["parent_span_id"]
    return payload


def _attribute(key: str, value: Any) -> dict[str, Any]:
    return {"key": key, "value": _any_value(value)}


def _any_value(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"intValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if value is None:
        return {"stringValue": ""}
    return {"stringValue": str(value)}


def _status_code(status: str) -> int:
    if status == "OK":
        return 1
    if status == "ERROR":
        return 2
    return 0


def _payload_span_count(payload: dict[str, Any]) -> int:
    return sum(
        len(scope_spans.get("spans", []))
        for resource_spans in payload.get("resourceSpans", [])
        for scope_spans in resource_spans.get("scopeSpans", [])
    )


def _http_post(
    endpoint: str,
    body: bytes,
    headers: Mapping[str, str],
    timeout_seconds: float,
) -> tuple[int, str]:
    http_request = request.Request(
        endpoint,
        data=body,
        headers=dict(headers),
        method="POST",
    )
    with request.urlopen(http_request, timeout=timeout_seconds) as response:
        return response.status, response.read().decode("utf-8", errors="replace")
