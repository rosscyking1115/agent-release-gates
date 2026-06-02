from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from internal_ai_agent.observability.collector import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_SERVICE_NAME,
    DEFAULT_SERVICE_VERSION,
    export_spans_to_collector,
)


class _CaptureState:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []


def run_local_collector_smoke(
    spans: list[dict[str, Any]],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    service_name: str = DEFAULT_SERVICE_NAME,
    service_version: str = DEFAULT_SERVICE_VERSION,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    state = _CaptureState()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _capture_handler(state))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}/v1/traces"

    try:
        export_summary = export_spans_to_collector(
            spans,
            endpoint=endpoint,
            batch_size=batch_size,
            service_name=service_name,
            service_version=service_version,
            timeout_seconds=timeout_seconds,
            dry_run=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=timeout_seconds)

    received_span_count = sum(
        _payload_span_count(request_record["body"]) for request_record in state.requests
    )
    content_types = sorted(
        {
            request_record["content_type"]
            for request_record in state.requests
            if request_record["content_type"]
        }
    )
    failed_checks = _smoke_failed_checks(
        spans=spans,
        export_summary=export_summary,
        received_request_count=len(state.requests),
        received_span_count=received_span_count,
        content_types=content_types,
    )
    return {
        "export_mode": "local_collector_smoke",
        "collector_endpoint": endpoint,
        "span_count": len(spans),
        "batch_size": batch_size,
        "payload_count": export_summary["payload_count"],
        "posted_payload_count": export_summary["posted_payload_count"],
        "received_request_count": len(state.requests),
        "received_span_count": received_span_count,
        "status_codes": export_summary["status_codes"],
        "content_types": content_types,
        "passed": not failed_checks,
        "failed_checks": failed_checks,
        "notes": [
            "Started a local OTLP/HTTP-compatible capture endpoint and posted real payloads.",
            (
                "This smoke test verifies the POST path without depending on an "
                "external collector image."
            ),
        ],
    }


def _capture_handler(state: _CaptureState) -> type[BaseHTTPRequestHandler]:
    class CaptureHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/v1/traces":
                self.send_response(404)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            state.requests.append(
                {
                    "path": self.path,
                    "content_type": self.headers.get("Content-Type", ""),
                    "body": json.loads(body.decode("utf-8")),
                }
            )
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            return

    return CaptureHandler


def _smoke_failed_checks(
    *,
    spans: list[dict[str, Any]],
    export_summary: dict[str, Any],
    received_request_count: int,
    received_span_count: int,
    content_types: list[str],
) -> list[str]:
    failed: list[str] = []
    if export_summary["posted_payload_count"] != export_summary["payload_count"]:
        failed.append("posted_payload_count_mismatch")
    if received_request_count != export_summary["payload_count"]:
        failed.append("received_request_count_mismatch")
    if received_span_count != len(spans):
        failed.append("received_span_count_mismatch")
    if export_summary["status_codes"] != [200] * export_summary["payload_count"]:
        failed.append("unexpected_status_codes")
    if content_types != ["application/json"]:
        failed.append("unexpected_content_type")
    return failed


def _payload_span_count(payload: dict[str, Any]) -> int:
    return sum(
        len(scope_spans.get("spans", []))
        for resource_spans in payload.get("resourceSpans", [])
        for scope_spans in resource_spans.get("scopeSpans", [])
    )
