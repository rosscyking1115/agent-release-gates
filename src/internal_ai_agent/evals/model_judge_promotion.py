from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from internal_ai_agent.io import read_jsonl, write_json


def promote_model_judge_result(
    project_root: Path,
    *,
    summary_path: Path,
    cases_path: Path,
    output_path: Path,
    reviewer: str,
    decision: str,
    note: str,
) -> dict[str, Any]:
    summary = json.loads((project_root / summary_path).read_text(encoding="utf-8"))
    cases = read_jsonl(project_root / cases_path)
    report = _reviewed_summary(
        summary,
        cases,
        reviewer=reviewer,
        decision=decision,
        note=note,
    )
    write_json(project_root / output_path, report)
    return report


def _reviewed_summary(
    summary: dict[str, Any],
    cases: list[dict[str, Any]],
    *,
    reviewer: str,
    decision: str,
    note: str,
) -> dict[str, Any]:
    disagreement_rows = [
        _public_disagreement(row)
        for row in cases
        if not row["model_judge_label_match"]
        or not row["classifier_model_judge_agree"]
    ]
    review = summary["publication_review"]
    return {
        "report_type": "reviewed_hosted_model_judge_result",
        "provider": summary["provider"],
        "model": summary["model"],
        "reviewed_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "reviewer": reviewer,
        "manual_publication_decision": decision,
        "review_note": note,
        "case_count": summary["case_count"],
        "metrics": summary["summary"],
        "publication_review": summary["publication_review"],
        "by_category": summary["by_category"],
        "public_disagreement_examples": disagreement_rows,
        "limitations": _limitations(review),
    }


def _limitations(review: dict[str, Any]) -> list[str]:
    limitations = [
            (
                "Provider-backed judge results are stochastic and may vary by "
                "model version and run time."
            ),
            (
                "This result uses maintainer-labeled calibration cases, not "
                "independent external human labels."
            ),
    ]
    unsafe_miss_count = int(review.get("unsafe_miss_count", 0))
    benign_auto_block_count = int(review.get("benign_auto_block_count", 0))
    if unsafe_miss_count:
        limitations.append(
            f"The hosted judge missed {unsafe_miss_count} unsafe case(s) in this run."
        )
    if benign_auto_block_count:
        limitations.append(
            "The hosted judge over-blocked "
            f"{benign_auto_block_count} benign case(s) in this run."
        )
    if not unsafe_miss_count and not benign_auto_block_count:
        limitations.append(
            "No unsafe misses or benign auto-blocks were observed in this calibration run."
        )
    return limitations


def _public_disagreement(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row["case_id"],
        "risk_category": row["risk_category"],
        "risk_severity": row["risk_severity"],
        "human_label": row["human_adjudicated_label"],
        "classifier_label": row["classifier_label"],
        "model_judge_label": row["model_judge_label"],
        "model_judge_decision": row["model_judge_decision"],
        "model_judge_error_type": row["model_judge_error_type"],
    }
