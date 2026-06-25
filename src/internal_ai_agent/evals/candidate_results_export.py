from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.incident_replay import (
    CANDIDATE_RESULTS_SCHEMA_VERSION,
    INCIDENT_ID_PATTERN,
    INCIDENT_ID_PATTERN_TEXT,
)
from internal_ai_agent.io import write_jsonl

_DECISION_ALIASES = {
    "allow": "allow",
    "allowed": "allow",
    "approve": "allow",
    "approved": "allow",
    "pass": "allow",
    "passed": "allow",
    "success": "allow",
    "block": "block",
    "blocked": "block",
    "deny": "block",
    "denied": "block",
    "refuse": "block",
    "refused": "block",
    "refusal": "block",
    "reject": "block",
    "rejected": "block",
    "review": "review",
    "escalate": "review",
    "escalated": "review",
    "hold": "review",
    "human_review": "review",
    "needs_review": "review",
}
_DECISIONS = {"allow", "block", "review"}
_BOOL_TRUE_STRINGS = {"true", "yes", "1"}
_BOOL_FALSE_STRINGS = {"false", "no", "0"}
_INCIDENT_ID_FIELDS = ("incident_id", "case_id", "caseId", "id")
_ANSWER_FIELDS = ("answer", "final_answer", "finalAnswer", "output", "response", "content")
_DECISION_FIELDS = ("decision", "action", "status", "safety_decision", "safetyDecision")
_TRACE_ID_FIELDS = ("trace_id", "traceId", "run_id", "runId")
_MODEL_VERSION_FIELDS = ("model_version", "modelVersion", "model", "runner_version")
_POLICY_VERSION_FIELDS = ("policy_version", "policyVersion", "policy", "prompt_version")
_TOOL_COLLECTION_FIELDS = ("tool_outcomes", "tool_calls", "toolCalls", "tools", "actions")
_LANGCHAIN_ROOT_DECISION_FIELDS = (
    "decision",
    "action",
    "safety_decision",
    "safetyDecision",
)


def export_candidate_results_from_agent_log(
    *,
    input_path: Path,
    output_path: Path,
    candidate_id: str,
    default_model_version: str = "external_candidate_result",
    default_policy_version: str = "unknown",
    source_format: str = "generic_agent_log",
) -> dict[str, Any]:
    rows = _read_jsonl_any(input_path)
    candidate_results = candidate_results_from_agent_logs(
        rows,
        candidate_id=candidate_id,
        default_model_version=default_model_version,
        default_policy_version=default_policy_version,
        source_format=source_format,
    )
    write_jsonl(output_path, candidate_results)
    return {
        "status": "completed",
        "schema_version": CANDIDATE_RESULTS_SCHEMA_VERSION,
        "source_format": source_format,
        "input_path": input_path.as_posix(),
        "output_path": output_path.as_posix(),
        "candidate_id": candidate_id,
        "result_count": len(candidate_results),
        "incident_ids": [str(row["incident_id"]) for row in candidate_results],
    }


def candidate_results_from_agent_logs(
    rows: list[Any],
    *,
    candidate_id: str,
    default_model_version: str = "external_candidate_result",
    default_policy_version: str = "unknown",
    source_format: str = "generic_agent_log",
) -> list[dict[str, Any]]:
    _validate_safe_identifier(
        candidate_id,
        field="candidate_id",
        row_index=0,
        source="candidate exporter arguments",
    )
    if not rows:
        raise ValueError("Agent log input must contain at least one JSONL row.")
    return [
        candidate_result_from_agent_log(
            row,
            candidate_id=candidate_id,
            default_model_version=default_model_version,
            default_policy_version=default_policy_version,
            source_format=source_format,
            row_index=index,
        )
        for index, row in enumerate(rows, start=1)
    ]


def candidate_result_from_agent_log(
    row: Any,
    *,
    candidate_id: str,
    default_model_version: str = "external_candidate_result",
    default_policy_version: str = "unknown",
    source_format: str = "generic_agent_log",
    row_index: int = 1,
) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError(f"Agent log row must be an object: row {row_index}")
    if source_format in {"langchain_trace", "langsmith_run"}:
        row = _agent_log_row_from_langchain_trace(row, row_index=row_index)

    incident_id = _validate_safe_identifier(
        _first_non_empty_string(row, _INCIDENT_ID_FIELDS),
        field="incident_id",
        row_index=row_index,
        source="agent log",
    )
    normalized_candidate_id = _validate_safe_identifier(
        candidate_id,
        field="candidate_id",
        row_index=row_index,
        source="candidate exporter arguments",
    )
    decision = _normalize_decision(
        _first_non_empty_string(row, _DECISION_FIELDS),
        row_index=row_index,
    )
    answer = _required_string(
        _first_non_empty_string(row, _ANSWER_FIELDS),
        field="answer",
        row_index=row_index,
    )
    citations = _normalize_citations(row.get("citations", row.get("source_ids", [])))
    tool_outcomes = _normalize_tool_outcomes(
        _first_present(row, _TOOL_COLLECTION_FIELDS, default=[]),
        row_index=row_index,
    )
    audit_events = row.get("audit_events", [])
    if audit_events is not None and not isinstance(audit_events, list):
        raise ValueError(f"Agent log field 'audit_events' must be a list: row {row_index}")
    answer_abstained = _normalize_optional_bool(
        _first_present(
            row,
            ("answer_abstained", "abstained", "refused", "is_refusal"),
            default=decision == "block",
        ),
        field="answer_abstained",
        row_index=row_index,
    )
    model_version = _optional_string(
        _first_non_empty_string(row, _MODEL_VERSION_FIELDS),
        default=default_model_version,
        field="model_version",
        row_index=row_index,
    )
    policy_version = _optional_string(
        _first_non_empty_string(row, _POLICY_VERSION_FIELDS),
        default=default_policy_version,
        field="policy_version",
        row_index=row_index,
    )
    trace_id = _optional_string(
        _first_non_empty_string(row, _TRACE_ID_FIELDS),
        default=_stable_trace_id(candidate_id=normalized_candidate_id, incident_id=incident_id),
        field="trace_id",
        row_index=row_index,
    )
    metadata = _normalize_metadata(row.get("metadata", {}), source_format=source_format)
    return {
        "incident_id": incident_id,
        "candidate_id": normalized_candidate_id,
        "decision": decision,
        "answer": answer,
        "answer_abstained": answer_abstained,
        "citations": citations,
        "citation_count": len(citations),
        "tool_outcomes": tool_outcomes,
        "audit_event_count": len(audit_events or []),
        "model_version": model_version,
        "policy_version": policy_version,
        "trace_id": trace_id,
        "metadata": metadata,
    }


def _normalize_decision(value: str | None, *, row_index: int) -> str:
    decision = _required_string(value, field="decision", row_index=row_index).strip().lower()
    normalized = _DECISION_ALIASES.get(decision, decision)
    if normalized not in _DECISIONS:
        raise ValueError(
            f"Agent log field 'decision' must map to one of {sorted(_DECISIONS)}: row {row_index}"
        )
    return normalized


def _normalize_citations(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Agent log field 'citations' must be a list when present.")
    normalized: list[str] = []
    for item in value:
        if isinstance(item, str):
            citation = item
        elif isinstance(item, dict):
            citation = str(
                item.get("id")
                or item.get("doc_id")
                or item.get("document_id")
                or item.get("source_id")
                or item.get("url")
                or ""
            )
        else:
            raise ValueError("Agent log field 'citations' must contain strings or objects.")
        if citation.strip():
            normalized.append(citation)
    return normalized


def _normalize_tool_outcomes(value: Any, *, row_index: int) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Agent log field 'tool_outcomes' must be a list: row {row_index}")

    normalized: list[dict[str, Any]] = []
    for tool_index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise ValueError(
                f"Agent log field 'tool_outcomes' must contain objects: row {row_index}"
            )
        requires_approval = _normalize_optional_bool(
            _first_present(item, ("requires_approval", "needs_approval"), default=False),
            field=f"tool_outcomes[{tool_index}].requires_approval",
            row_index=row_index,
        )
        approval_granted = _normalize_optional_bool(
            _first_present(item, ("approval_granted", "approved"), default=False),
            field=f"tool_outcomes[{tool_index}].approval_granted",
            row_index=row_index,
        )
        executed = _normalize_executed(item, row_index=row_index, tool_index=tool_index)
        normalized_tool = dict(item)
        normalized_tool.update(
            {
                "tool": _optional_string(
                    _first_non_empty_string(item, ("tool", "tool_name", "name")),
                    default="",
                    field=f"tool_outcomes[{tool_index}].tool",
                    row_index=row_index,
                    allow_empty=True,
                ),
                "tool_type": _optional_string(
                    _first_non_empty_string(item, ("tool_type", "type")),
                    default="side_effect" if requires_approval else "",
                    field=f"tool_outcomes[{tool_index}].tool_type",
                    row_index=row_index,
                    allow_empty=True,
                ),
                "requires_approval": requires_approval,
                "approval_granted": approval_granted,
                "executed": executed,
                "blocked_reason": _optional_string(
                    _first_non_empty_string(item, ("blocked_reason", "reason", "error")),
                    default="",
                    field=f"tool_outcomes[{tool_index}].blocked_reason",
                    row_index=row_index,
                    allow_empty=True,
                ),
            }
        )
        normalized.append(normalized_tool)
    return normalized


def _normalize_executed(row: dict[str, Any], *, row_index: int, tool_index: int) -> bool:
    value = _first_present(row, ("executed", "called", "ran"), default=None)
    if value is not None:
        return _normalize_optional_bool(
            value,
            field=f"tool_outcomes[{tool_index}].executed",
            row_index=row_index,
        )
    status = row.get("status")
    if isinstance(status, str):
        return status.strip().lower() in {
            "called",
            "complete",
            "completed",
            "executed",
            "executed_without_approval",
            "ran",
            "success",
            "succeeded",
        }
    return False


def _normalize_optional_bool(value: Any, *, field: str, row_index: int) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        parsed = value.strip().lower()
        if parsed in _BOOL_TRUE_STRINGS:
            return True
        if parsed in _BOOL_FALSE_STRINGS:
            return False
    raise ValueError(f"Agent log field {field!r} must be a boolean: row {row_index}")


def _normalize_metadata(value: Any, *, source_format: str) -> dict[str, Any]:
    if value is None:
        metadata: dict[str, Any] = {}
    elif isinstance(value, dict):
        metadata = dict(value)
    else:
        raise ValueError("Agent log field 'metadata' must be an object when present.")
    metadata.setdefault("source_format", source_format)
    metadata.setdefault("exporter", "agent_log_to_candidate_results")
    return metadata


def _agent_log_row_from_langchain_trace(
    row: dict[str, Any],
    *,
    row_index: int,
) -> dict[str, Any]:
    inputs = _optional_object(row.get("inputs", {}), field="inputs", row_index=row_index)
    outputs = _optional_object_or_string(
        row.get("outputs", {}),
        field="outputs",
        row_index=row_index,
    )
    metadata = _langchain_metadata(row, row_index=row_index)
    output_fields = _flatten_output_fields(outputs)
    transformed: dict[str, Any] = {
        "incident_id": _first_non_empty_string(inputs, _INCIDENT_ID_FIELDS)
        or _first_non_empty_string(metadata, _INCIDENT_ID_FIELDS)
        or _first_non_empty_string(row, ("incident_id", "case_id", "caseId")),
        "decision": _first_non_empty_string(output_fields, _DECISION_FIELDS)
        or _first_non_empty_string(metadata, _LANGCHAIN_ROOT_DECISION_FIELDS)
        or _first_non_empty_string(row, _LANGCHAIN_ROOT_DECISION_FIELDS),
        "answer": _first_non_empty_string(output_fields, _ANSWER_FIELDS)
        or _first_non_empty_string(row, _ANSWER_FIELDS),
        "citations": row.get(
            "citations",
            output_fields.get("citations", output_fields.get("source_ids", [])),
        ),
        "tool_outcomes": _langchain_tool_outcomes(row, row_index=row_index),
        "audit_events": row.get("audit_events", row.get("events", [])),
        "model_version": _first_non_empty_string(row, _MODEL_VERSION_FIELDS)
        or _first_non_empty_string(metadata, _MODEL_VERSION_FIELDS),
        "policy_version": _first_non_empty_string(row, _POLICY_VERSION_FIELDS)
        or _first_non_empty_string(metadata, _POLICY_VERSION_FIELDS),
        "trace_id": _first_non_empty_string(row, _TRACE_ID_FIELDS)
        or str(row.get("id") or row.get("uuid") or ""),
        "metadata": {
            "langchain_run_id": str(row.get("id") or row.get("uuid") or ""),
            "langchain_name": str(row.get("name") or ""),
            "langchain_run_type": str(row.get("run_type") or row.get("runType") or ""),
            "langchain_tags": row.get("tags", []),
        },
    }
    if "answer_abstained" in output_fields:
        transformed["answer_abstained"] = output_fields["answer_abstained"]
    elif "refused" in output_fields:
        transformed["refused"] = output_fields["refused"]
    return transformed


def _langchain_metadata(row: dict[str, Any], *, row_index: int) -> dict[str, Any]:
    metadata = _optional_object(row.get("metadata", {}), field="metadata", row_index=row_index)
    extra = _optional_object(row.get("extra", {}), field="extra", row_index=row_index)
    extra_metadata = _optional_object(
        extra.get("metadata", {}),
        field="extra.metadata",
        row_index=row_index,
    )
    merged = dict(extra_metadata)
    merged.update(metadata)
    return merged


def _flatten_output_fields(outputs: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(outputs, str):
        return {"answer": outputs}
    fields = dict(outputs)
    nested = outputs.get("output")
    if isinstance(nested, dict):
        fields.update(nested)
    return fields


def _langchain_tool_outcomes(row: dict[str, Any], *, row_index: int) -> list[dict[str, Any]]:
    explicit = _first_non_empty_list(row, _TOOL_COLLECTION_FIELDS, row_index=row_index)
    outcomes: list[dict[str, Any]] = []
    if explicit is not None:
        outcomes.extend(explicit)

    outputs = _optional_object_or_string(
        row.get("outputs", {}),
        field="outputs",
        row_index=row_index,
    )
    if isinstance(outputs, dict):
        output_tools = _first_non_empty_list(
            outputs,
            _TOOL_COLLECTION_FIELDS,
            row_index=row_index,
        )
        if output_tools is not None:
            outcomes.extend(output_tools)

    child_runs = row.get("child_runs", row.get("childRuns", []))
    if child_runs:
        if not isinstance(child_runs, list):
            raise ValueError(f"LangChain field 'child_runs' must be a list: row {row_index}")
        outcomes.extend(_langchain_child_tool_outcomes(child_runs, row_index=row_index))

    events = row.get("events", [])
    if not events:
        return _dedupe_tool_outcomes(outcomes)
    if not isinstance(events, list):
        raise ValueError(f"LangChain field 'events' must be a list: row {row_index}")
    outcomes.extend(
        _langchain_event_to_tool_outcome(event, row_index=row_index)
        for event in events
        if isinstance(event, dict) and _is_langchain_tool_event(event)
    )
    return _dedupe_tool_outcomes(outcomes)


def _langchain_child_tool_outcomes(
    child_runs: list[Any],
    *,
    row_index: int,
) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    for child_run in child_runs:
        if not isinstance(child_run, dict):
            continue
        run_type = str(child_run.get("run_type") or child_run.get("runType") or "").lower()
        if run_type == "tool":
            outcomes.append(_langchain_child_run_to_tool_outcome(child_run, row_index=row_index))
        nested_child_runs = child_run.get("child_runs", child_run.get("childRuns", []))
        if nested_child_runs:
            if not isinstance(nested_child_runs, list):
                raise ValueError(
                    f"LangChain field 'child_runs' must be a list: row {row_index}"
                )
            outcomes.extend(
                _langchain_child_tool_outcomes(nested_child_runs, row_index=row_index)
            )
    return outcomes


def _langchain_child_run_to_tool_outcome(
    child_run: dict[str, Any],
    *,
    row_index: int,
) -> dict[str, Any]:
    metadata = _langchain_metadata(child_run, row_index=row_index)
    outputs = _optional_object_or_string(
        child_run.get("outputs", {}),
        field="child_runs.outputs",
        row_index=row_index,
    )
    return {
        "id": str(child_run.get("id") or child_run.get("uuid") or ""),
        "tool": str(child_run.get("name") or ""),
        "tool_type": str(metadata.get("tool_type") or ""),
        "requires_approval": metadata.get("requires_approval", False),
        "approval_granted": metadata.get("approval_granted", False),
        "executed": _langchain_run_executed(child_run, outputs),
        "blocked_reason": str(child_run.get("error") or metadata.get("blocked_reason") or ""),
        "status": str(child_run.get("status") or ""),
        "inputs": child_run.get("inputs", {}),
        "outputs": outputs,
    }


def _langchain_event_to_tool_outcome(
    event: dict[str, Any],
    *,
    row_index: int,
) -> dict[str, Any]:
    metadata = _optional_object(
        event.get("metadata", {}),
        field="events.metadata",
        row_index=row_index,
    )
    data = _optional_object(event.get("data", {}), field="events.data", row_index=row_index)
    event_name = str(event.get("event") or event.get("type") or event.get("status") or "")
    return {
        "tool": str(event.get("name") or data.get("name") or ""),
        "tool_type": str(metadata.get("tool_type") or ""),
        "requires_approval": metadata.get("requires_approval", False),
        "approval_granted": metadata.get("approval_granted", False),
        "executed": event_name.lower()
        in {"on_tool_start", "on_tool_end", "tool_start", "tool_end"},
        "blocked_reason": str(
            event.get("error") or data.get("error") or metadata.get("blocked_reason") or ""
        ),
        "event": event_name,
        "data": data,
    }


def _langchain_run_executed(row: dict[str, Any], outputs: dict[str, Any] | str) -> bool:
    status = str(row.get("status") or "").strip().lower()
    if status in {"error", "failed", "blocked"}:
        return False
    if status in {"success", "succeeded", "complete", "completed"}:
        return True
    return bool(outputs)


def _is_langchain_tool_event(event: dict[str, Any]) -> bool:
    event_name = str(event.get("event") or event.get("type") or "").lower()
    return "tool" in event_name


def _first_non_empty_list(
    row: dict[str, Any],
    fields: tuple[str, ...],
    *,
    row_index: int,
) -> list[Any] | None:
    for field in fields:
        value = row.get(field)
        if value is None:
            continue
        if not isinstance(value, list):
            raise ValueError(f"LangChain field {field!r} must be a list: row {row_index}")
        if value:
            return value
    return None


def _dedupe_tool_outcomes(outcomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    stable_id_positions: dict[str, int] = {}
    for outcome in outcomes:
        stable_id = str(outcome.get("id") or outcome.get("call_id") or "")
        if stable_id:
            if stable_id in stable_id_positions:
                existing_index = stable_id_positions[stable_id]
                deduped[existing_index] = _merge_tool_outcome(deduped[existing_index], outcome)
                continue
            stable_id_positions[stable_id] = len(deduped)
        deduped.append(outcome)
    return deduped


def _merge_tool_outcome(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in new.items():
        if key in {"requires_approval", "executed"}:
            merged[key] = _merge_bool_or(merged.get(key), value)
            continue
        if key == "approval_granted":
            if "approval_granted" in merged:
                merged[key] = _merge_approval_granted(merged[key], value)
            else:
                merged[key] = value
            continue
        if key == "tool_type" and (value == "side_effect" or _is_missing(merged.get(key))):
            merged[key] = value
            continue
        if _is_missing(merged.get(key)) and not _is_missing(value):
            merged[key] = value
    return merged


def _merge_bool_or(existing: Any, new: Any) -> Any:
    existing_bool = _parse_bool_like(existing)
    new_bool = _parse_bool_like(new)
    if existing_bool is True or new_bool is True:
        return True
    if existing_bool is False and new_bool is False:
        return False
    if existing_bool is None and not _is_missing(existing):
        return existing
    if new_bool is None and not _is_missing(new):
        return new
    return False


def _merge_approval_granted(existing: Any, new: Any) -> Any:
    existing_bool = _parse_bool_like(existing)
    new_bool = _parse_bool_like(new)
    if existing_bool is False or new_bool is False:
        return False
    if existing_bool is True and new_bool is True:
        return True
    if existing_bool is None and not _is_missing(existing):
        return existing
    if new_bool is None and not _is_missing(new):
        return new
    return False


def _parse_bool_like(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        parsed = value.strip().lower()
        if parsed in _BOOL_TRUE_STRINGS:
            return True
        if parsed in _BOOL_FALSE_STRINGS:
            return False
    if _is_missing(value):
        return False
    return None


def _is_missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _optional_object(value: Any, *, field: str, row_index: int) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"LangChain field {field!r} must be an object: row {row_index}")
    return value


def _optional_object_or_string(
    value: Any,
    *,
    field: str,
    row_index: int,
) -> dict[str, Any] | str:
    if value is None:
        return {}
    if not isinstance(value, (dict, str)):
        raise ValueError(f"LangChain field {field!r} must be an object or string: row {row_index}")
    return value


def _validate_safe_identifier(
    value: Any,
    *,
    field: str,
    row_index: int,
    source: str,
) -> str:
    parsed = _required_string(value, field=field, row_index=row_index)
    if INCIDENT_ID_PATTERN.fullmatch(parsed) is None:
        raise ValueError(
            f"{source} field {field!r} must match {INCIDENT_ID_PATTERN_TEXT!r}: row {row_index}"
        )
    return parsed


def _required_string(value: Any, *, field: str, row_index: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Agent log field {field!r} must be a non-empty string: row {row_index}")
    return value


def _optional_string(
    value: Any,
    *,
    default: str,
    field: str,
    row_index: int,
    allow_empty: bool = False,
) -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError(f"Agent log field {field!r} must be a string: row {row_index}")
    if not allow_empty and not value.strip():
        return default
    return value


def _first_non_empty_string(row: dict[str, Any], fields: tuple[str, ...]) -> str | None:
    for field in fields:
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value
        if value is not None and not isinstance(value, str):
            return value
    return None


def _first_present(row: dict[str, Any], fields: tuple[str, ...], *, default: Any) -> Any:
    for field in fields:
        if field in row:
            return row[field]
    return default


def _stable_trace_id(*, candidate_id: str, incident_id: str) -> str:
    digest = hashlib.sha256(f"{candidate_id}|{incident_id}".encode()).hexdigest()[:12]
    return f"candidate_{incident_id}_{digest}"


def _read_jsonl_any(path: Path) -> list[Any]:
    import json

    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]
