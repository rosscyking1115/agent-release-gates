from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.public_rag_model_reranker import (
    _select_packet_rows,
    write_public_rag_model_reranker_adapter_status,
)


def test_public_rag_model_reranker_writes_not_configured_status(
    tmp_path: Path,
) -> None:
    status = write_public_rag_model_reranker_adapter_status(tmp_path)

    assert status["status"] == "not_configured"
    assert status["candidate_case_count"] == 0
    assert (tmp_path / "reports/public_rag_model_reranker_adapter_status.json").exists()
    assert (tmp_path / "reports/public_rag_model_reranker_packet.jsonl").exists()
    stored = json.loads(
        (tmp_path / "reports/public_rag_model_reranker_adapter_status.json").read_text(
            encoding="utf-8"
        )
    )
    assert stored["provider_input_boundary"].startswith("Provider input includes public")


def test_select_packet_rows_prioritizes_rerankable_with_controls() -> None:
    rows = [
        {"case_id": "r1", "selection_reason": "rerankable", "dataset": "a"},
        {"case_id": "r2", "selection_reason": "rerankable", "dataset": "b"},
        {"case_id": "c1", "selection_reason": "top1_control", "dataset": "a"},
        {"case_id": "c2", "selection_reason": "top1_control", "dataset": "b"},
        {"case_id": "c3", "selection_reason": "top1_control", "dataset": "a"},
    ]

    selected = _select_packet_rows(rows, packet_limit=4)

    assert [row["case_id"] for row in selected] == ["r1", "r2", "c1", "c2"]
