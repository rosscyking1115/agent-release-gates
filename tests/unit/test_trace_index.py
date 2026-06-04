from internal_ai_agent.observability.trace_index import build_trace_index


def test_build_trace_index_summarizes_traces_components_and_errors() -> None:
    spans = [
        {
            "trace_id": "trace-1",
            "span_id": "root",
            "parent_span_id": None,
            "name": "retriever.failure_analysis",
            "start_time_unix_nano": 1_000,
            "end_time_unix_nano": 5_000,
            "status": {"code": "OK"},
            "attributes": {
                "lab.trace_id": "retriever_failures_vector",
                "lab.component": "retrieval",
            },
        },
        {
            "trace_id": "trace-1",
            "span_id": "child",
            "parent_span_id": "root",
            "name": "retriever.case_failure",
            "start_time_unix_nano": 2_000,
            "end_time_unix_nano": 3_000,
            "status": {"code": "ERROR"},
            "attributes": {
                "lab.trace_id": "retriever_failures_vector",
                "lab.component": "retrieval",
                "eval.case_id": "CASE-1",
                "retriever.failure_reasons": "missing_or_wrong_citation",
            },
        },
        {
            "trace_id": "trace-2",
            "span_id": "api-root",
            "parent_span_id": None,
            "name": "api.contract_analysis",
            "start_time_unix_nano": 10_000,
            "end_time_unix_nano": 20_000,
            "status": {"code": "OK"},
            "attributes": {"lab.trace_id": "api_contracts", "lab.component": "api"},
        },
    ]

    index = build_trace_index(spans)

    assert index["index_type"] == "local_observability_trace_index"
    assert index["span_count"] == 3
    assert index["trace_count"] == 2
    assert index["error_span_count"] == 1
    assert index["components"][0] == {
        "component": "retrieval",
        "span_count": 2,
        "root_span_count": 1,
        "error_span_count": 1,
    }
    assert index["traces"][0]["trace_label"] == "retriever_failures_vector"
    assert index["traces"][0]["first_error_case_id"] == "CASE-1"
    assert index["error_spans"][0]["failure_reasons"] == "missing_or_wrong_citation"
    assert next(
        query for query in index["queries"] if query["query"] == "retriever_failures"
    )["span_count"] == 1
