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
_INCIDENT_ID_FIELDS = ("incident_id", "case_id", "caseId", "id")
_ANSWER_FIELDS = ("answer", "final_answer", "finalAnswer", "output", "response", "content")
_DECISION_FIELDS = ("decision", "action", "status", "safety_decision", "safetyDecision")
_TRACE_ID_FIELDS = ("trace_id", "traceId", "run_id", "runId")
_MODEL_VERSION_FIELDS = ("model_version", "modelVersion", "model", "runner_version")
_POLICY_VERSION_FIELDS = ("policy_version", "policyVersion", "policy", "prompt_version")
_TOOL_COLLECTION_FIELDS = ("tool_outcomes", "tool_calls", "toolCalls", "tools", "actions")


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
        if parsed in {"true", "yes", "1"}:
            return True
        if parsed in {"false", "no", "0"}:
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
