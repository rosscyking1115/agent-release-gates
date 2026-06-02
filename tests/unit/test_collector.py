from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.observability.collector import (
    collector_export_preview,
    export_spans_to_collector,
    otlp_trace_payload,
    otlp_trace_payloads,
    write_collector_export_preview,
)
from internal_ai_agent.observability.collector_smoke import run_local_collector_smoke


def _span(
    *,
    trace_id: str = "a" * 32,
    span_id: str = "b" * 16,
    parent_span_id: str | None = None,
    name: str = "evaluation.run",
    status: str = "OK",
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "name": name,
        "kind": "INTERNAL",
        "start_time_unix_nano": 1_735_689_600_000_000_000,
        "end_time_unix_nano": 1_735_689_600_005_000_000,
        "status": {"code": status},
        "attributes": {
            "lab.component": "evaluation",
            "eval.case_count": 296,
            "eval.schema_valid": True,
            "eval.score": 1.0,
        },
    }


def test_otlp_trace_payload_maps_local_spans_to_otlp_json() -> None:
    payload = otlp_trace_payload([_span()], service_name="lab", service_version="test")

    resource_span = payload["resourceSpans"][0]
    resource_attributes = resource_span["resource"]["attributes"]
    otlp_span = resource_span["scopeSpans"][0]["spans"][0]
    attributes = {row["key"]: row["value"] for row in otlp_span["attributes"]}

    assert resource_attributes[0] == {
        "key": "service.name",
        "value": {"stringValue": "lab"},
    }
    assert otlp_span["traceId"] == "a" * 32
    assert otlp_span["spanId"] == "b" * 16
    assert "parentSpanId" not in otlp_span
    assert otlp_span["kind"] == 1
    assert otlp_span["status"] == {"code": 1}
    assert attributes["eval.case_count"] == {"intValue": "296"}
    assert attributes["eval.schema_valid"] == {"boolValue": True}
    assert attributes["eval.score"] == {"doubleValue": 1.0}


def test_otlp_trace_payload_includes_parent_and_error_status() -> None:
    payload = otlp_trace_payload(
        [
            _span(
                parent_span_id="c" * 16,
                name="retriever.case_failure",
                status="ERROR",
            )
        ]
    )

    otlp_span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]

    assert otlp_span["parentSpanId"] == "c" * 16
    assert otlp_span["status"] == {"code": 2}


def test_otlp_trace_payloads_batches_spans() -> None:
    spans = [
        _span(trace_id=f"{index:032x}", span_id=f"{index:016x}")
        for index in range(5)
    ]

    payloads = otlp_trace_payloads(spans, batch_size=2)

    assert len(payloads) == 3
    assert len(payloads[0]["resourceSpans"][0]["scopeSpans"][0]["spans"]) == 2
    assert len(payloads[2]["resourceSpans"][0]["scopeSpans"][0]["spans"]) == 1


def test_collector_export_preview_summarizes_without_posting() -> None:
    preview = collector_export_preview(
        [
            _span(trace_id="a" * 32, span_id="b" * 16),
            _span(trace_id="a" * 32, span_id="c" * 16, parent_span_id="b" * 16),
            _span(trace_id="d" * 32, span_id="e" * 16),
        ],
        batch_size=2,
    )

    assert preview["export_mode"] == "dry_run_preview"
    assert preview["span_count"] == 3
    assert preview["trace_count"] == 2
    assert preview["root_span_count"] == 2
    assert preview["payload_count"] == 2
    assert preview["first_payload_span_count"] == 2


def test_export_spans_to_collector_dry_run_skips_http_post() -> None:
    calls = []

    def fake_post(
        endpoint: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> tuple[int, str]:
        calls.append((endpoint, body, headers, timeout_seconds))
        return 200, ""

    summary = export_spans_to_collector([_span()], dry_run=True, http_post=fake_post)

    assert summary["export_mode"] == "dry_run"
    assert summary["posted_payload_count"] == 0
    assert calls == []


def test_export_spans_to_collector_posts_batches_with_content_type() -> None:
    calls = []

    def fake_post(
        endpoint: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> tuple[int, str]:
        calls.append((endpoint, body, headers, timeout_seconds))
        return 200, "accepted"

    summary = export_spans_to_collector(
        [_span(span_id="b" * 16), _span(span_id="c" * 16)],
        endpoint="http://collector:4318/v1/traces",
        batch_size=1,
        timeout_seconds=3.0,
        dry_run=False,
        http_post=fake_post,
    )

    assert summary["export_mode"] == "posted"
    assert summary["posted_payload_count"] == 2
    assert summary["status_codes"] == [200, 200]
    assert len(calls) == 2
    assert calls[0][0] == "http://collector:4318/v1/traces"
    assert calls[0][2]["Content-Type"] == "application/json"
    assert calls[0][3] == 3.0


def test_write_collector_export_preview_reads_observability_spans(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    spans_path = reports_dir / "observability_otel_spans.jsonl"
    spans_path.write_text(
        "\n".join(
            [
                '{"attributes": {}, "end_time_unix_nano": 2, "kind": "INTERNAL", '
                '"name": "root", "parent_span_id": null, "span_id": "bbbbbbbbbbbbbbbb", '
                '"start_time_unix_nano": 1, "status": {"code": "OK"}, '
                '"trace_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}',
                '{"attributes": {}, "end_time_unix_nano": 3, "kind": "INTERNAL", '
                '"name": "child", "parent_span_id": "bbbbbbbbbbbbbbbb", '
                '"span_id": "cccccccccccccccc", "start_time_unix_nano": 2, '
                '"status": {"code": "OK"}, '
                '"trace_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    preview = write_collector_export_preview(tmp_path, batch_size=1)
    output_path = reports_dir / "collector_export_preview.json"

    assert preview["span_count"] == 2
    assert preview["payload_count"] == 2
    assert output_path.exists()


def test_run_local_collector_smoke_posts_to_capture_endpoint() -> None:
    summary = run_local_collector_smoke(
        [
            _span(trace_id="a" * 32, span_id="b" * 16),
            _span(trace_id="a" * 32, span_id="c" * 16, parent_span_id="b" * 16),
            _span(trace_id="d" * 32, span_id="e" * 16),
        ],
        batch_size=2,
    )

    assert summary["export_mode"] == "local_collector_smoke"
    assert summary["span_count"] == 3
    assert summary["payload_count"] == 2
    assert summary["posted_payload_count"] == 2
    assert summary["received_request_count"] == 2
    assert summary["received_span_count"] == 3
    assert summary["status_codes"] == [200, 200]
    assert summary["content_types"] == ["application/json"]
    assert summary["passed"] is True
    assert summary["failed_checks"] == []
