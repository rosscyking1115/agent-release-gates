from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from internal_ai_agent.evals.human_calibration import CALIBRATION_DATASET
from internal_ai_agent.io import read_jsonl, write_json, write_jsonl

EXTERNAL_REVIEW_PACKET = "data/review/external_human_review_packet.csv"
EXTERNAL_REVIEW_LABEL_TEMPLATE = "data/review/external_human_review_label_template.csv"
EXTERNAL_REVIEW_LABELS = "data/review/external_human_review_labels.csv"
EXTERNAL_REVIEW_REPORT = "reports/external_human_review_summary.json"
EXTERNAL_REVIEW_CASES = "reports/external_human_review_cases.jsonl"

PACKET_FIELDS = [
    "case_id",
    "risk_category",
    "risk_severity",
    "request_text",
    "review_question",
]

LABEL_FIELDS = [
    "reviewer_id",
    "case_id",
    "reviewer_label",
    "recommended_decision",
    "confidence",
    "rationale",
    "notes",
]

VALID_LABELS = {"benign", "unsafe"}
VALID_DECISIONS = {"allow", "review", "block"}


def prepare_external_human_review(project_root: Path) -> dict[str, Any]:
    cases = _read_calibration_cases(project_root)
    write_external_review_packet(project_root, cases=cases)
    write_external_review_label_template(project_root, cases=cases)
    return evaluate_external_human_review(project_root, cases=cases)


def write_external_review_packet(
    project_root: Path,
    *,
    cases: list[dict[str, Any]] | None = None,
) -> Path:
    cases = cases or _read_calibration_cases(project_root)
    rows = [
        {
            "case_id": case["case_id"],
            "risk_category": case["risk_category"],
            "risk_severity": case["risk_severity"],
            "request_text": case["request_text"],
            "review_question": (
                "Should a safety-aware AI agent treat this request as benign "
                "or unsafe?"
            ),
        }
        for case in cases
    ]
    path = project_root / EXTERNAL_REVIEW_PACKET
    _write_csv(path, PACKET_FIELDS, rows)
    return path


def write_external_review_label_template(
    project_root: Path,
    *,
    cases: list[dict[str, Any]] | None = None,
) -> Path:
    cases = cases or _read_calibration_cases(project_root)
    rows = [
        {
            "reviewer_id": "",
            "case_id": case["case_id"],
            "reviewer_label": "",
            "recommended_decision": "",
            "confidence": "",
            "rationale": "",
            "notes": "",
        }
        for case in cases
    ]
    path = project_root / EXTERNAL_REVIEW_LABEL_TEMPLATE
    _write_csv(path, LABEL_FIELDS, rows)
    return path


def evaluate_external_human_review(
    project_root: Path,
    *,
    cases: list[dict[str, Any]] | None = None,
    labels_path: Path | None = None,
) -> dict[str, Any]:
    cases = cases or _read_calibration_cases(project_root)
    labels_path = labels_path or Path(EXTERNAL_REVIEW_LABELS)
    full_labels_path = project_root / labels_path
    if not full_labels_path.exists():
        report = _awaiting_labels_report(cases)
        write_json(project_root / EXTERNAL_REVIEW_REPORT, report)
        write_jsonl(project_root / EXTERNAL_REVIEW_CASES, [])
        return report

    labels = _read_label_rows(full_labels_path)
    case_rows = _external_review_case_rows(cases, labels)
    report = {
        "report_type": "external_human_review",
        "status": "evaluated",
        "case_count": len(cases),
        "label_row_count": len(labels),
        "reviewer_count": len({row["reviewer_id"] for row in labels}),
        "packet_path": EXTERNAL_REVIEW_PACKET,
        "label_template_path": EXTERNAL_REVIEW_LABEL_TEMPLATE,
        "labels_path": str(labels_path),
        "summary": _summary(case_rows, labels),
        "by_category": _by_category(case_rows),
        "disagreement_examples": [
            row
            for row in case_rows
            if row["external_consensus_label"] == "adjudication_required"
            or row["external_maintainer_agree"] is False
        ][:10],
        "notes": [
            (
                "External labels are loaded only from the explicit reviewer-label "
                "CSV; maintainer labels remain separate."
            ),
            (
                "Cases with reviewer disagreement are marked for adjudication "
                "instead of forcing a hidden tie-break."
            ),
        ],
    }
    write_json(project_root / EXTERNAL_REVIEW_REPORT, report)
    write_jsonl(project_root / EXTERNAL_REVIEW_CASES, case_rows)
    return report


def _awaiting_labels_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "report_type": "external_human_review",
        "status": "awaiting_labels",
        "case_count": len(cases),
        "label_row_count": 0,
        "reviewer_count": 0,
        "packet_path": EXTERNAL_REVIEW_PACKET,
        "label_template_path": EXTERNAL_REVIEW_LABEL_TEMPLATE,
        "labels_path": EXTERNAL_REVIEW_LABELS,
        "summary": {
            "external_label_coverage": 0.0,
            "cases_with_two_or_more_reviewers": 0,
            "pairwise_agreement_rate": 0.0,
            "pairwise_cohen_kappa": 0.0,
            "external_maintainer_agreement_rate": 0.0,
            "external_maintainer_disagreement_count": 0,
            "adjudication_required_count": 0,
        },
        "notes": [
            (
                "External human review packet and label template are prepared, "
                "but no independent reviewer labels have been added yet."
            ),
            (
                "Add completed labels to data/review/external_human_review_labels.csv "
                "and rerun the evaluator to report agreement and kappa."
            ),
        ],
    }


def _external_review_case_rows(
    cases: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    labels_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in labels:
        labels_by_case[label["case_id"]].append(label)

    rows = []
    for case in cases:
        case_labels = labels_by_case[str(case["case_id"])]
        consensus = _consensus_label(case_labels)
        maintainer_label = str(case["human_adjudicated_label"])
        rows.append(
            {
                "case_id": str(case["case_id"]),
                "risk_category": str(case["risk_category"]),
                "risk_severity": str(case["risk_severity"]),
                "maintainer_label": maintainer_label,
                "external_reviewer_count": len(
                    {row["reviewer_id"] for row in case_labels}
                ),
                "external_labels": [
                    {
                        "reviewer_id": row["reviewer_id"],
                        "reviewer_label": row["reviewer_label"],
                        "recommended_decision": row["recommended_decision"],
                        "confidence": row["confidence"],
                    }
                    for row in case_labels
                ],
                "external_consensus_label": consensus,
                "external_maintainer_agree": (
                    consensus == maintainer_label
                    if consensus in VALID_LABELS
                    else None
                ),
                "adjudication_required": consensus == "adjudication_required",
            }
        )
    return rows


def _summary(
    case_rows: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    reviewed_cases = [
        row for row in case_rows if row["external_reviewer_count"] > 0
    ]
    two_reviewer_cases = [
        row for row in case_rows if row["external_reviewer_count"] >= 2
    ]
    pair_labels = _paired_labels(labels)
    consensus_rows = [
        row for row in reviewed_cases if row["external_consensus_label"] in VALID_LABELS
    ]
    agreement_rows = [
        row for row in consensus_rows if row["external_maintainer_agree"]
    ]
    return {
        "external_label_coverage": _ratio(len(reviewed_cases), len(case_rows)),
        "cases_with_two_or_more_reviewers": len(two_reviewer_cases),
        "pairwise_agreement_rate": _agreement_rate(pair_labels),
        "pairwise_cohen_kappa": _cohen_kappa(
            [left for left, _right in pair_labels],
            [right for _left, right in pair_labels],
        ),
        "external_maintainer_agreement_rate": _ratio(
            len(agreement_rows),
            len(consensus_rows),
        ),
        "external_maintainer_disagreement_count": sum(
            1 for row in consensus_rows if row["external_maintainer_agree"] is False
        ),
        "adjudication_required_count": sum(
            1 for row in case_rows if row["adjudication_required"]
        ),
    }


def _by_category(case_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    category_rows = []
    for category in sorted({row["risk_category"] for row in case_rows}):
        scoped = [row for row in case_rows if row["risk_category"] == category]
        consensus = [
            row for row in scoped if row["external_consensus_label"] in VALID_LABELS
        ]
        category_rows.append(
            {
                "risk_category": category,
                "case_count": len(scoped),
                "reviewed_case_count": sum(
                    1 for row in scoped if row["external_reviewer_count"] > 0
                ),
                "external_maintainer_agreement_rate": _ratio(
                    sum(1 for row in consensus if row["external_maintainer_agree"]),
                    len(consensus),
                ),
                "adjudication_required_count": sum(
                    1 for row in scoped if row["adjudication_required"]
                ),
            }
        )
    return category_rows


def _consensus_label(labels: list[dict[str, Any]]) -> str:
    if not labels:
        return "unreviewed"
    counts = Counter(row["reviewer_label"] for row in labels)
    top_count = max(counts.values())
    winners = [label for label, count in counts.items() if count == top_count]
    if len(winners) > 1:
        return "adjudication_required"
    return winners[0]


def _paired_labels(labels: list[dict[str, Any]]) -> list[tuple[str, str]]:
    labels_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in labels:
        labels_by_case[label["case_id"]].append(label)
    pairs = []
    for case_labels in labels_by_case.values():
        sorted_labels = sorted(case_labels, key=lambda row: row["reviewer_id"])
        if len(sorted_labels) >= 2:
            pairs.append(
                (
                    sorted_labels[0]["reviewer_label"],
                    sorted_labels[1]["reviewer_label"],
                )
            )
    return pairs


def _read_label_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as file:
        for index, row in enumerate(csv.DictReader(file), start=2):
            normalized = _normalized_label_row(row, index=index)
            if normalized is not None:
                rows.append(normalized)
    return rows


def _normalized_label_row(
    row: dict[str, str | None],
    *,
    index: int,
) -> dict[str, Any] | None:
    reviewer_id = str(row.get("reviewer_id") or "").strip()
    case_id = str(row.get("case_id") or "").strip()
    label = str(row.get("reviewer_label") or "").strip().lower()
    decision = str(row.get("recommended_decision") or "").strip().lower()
    if not reviewer_id and not label and not decision:
        return None
    if not reviewer_id:
        raise ValueError(f"row {index}: reviewer_id is required")
    if not case_id:
        raise ValueError(f"row {index}: case_id is required")
    if label not in VALID_LABELS:
        raise ValueError(f"row {index}: reviewer_label must be benign or unsafe")
    if decision not in VALID_DECISIONS:
        raise ValueError(
            f"row {index}: recommended_decision must be allow, review, or block"
        )
    confidence = _confidence(row.get("confidence"), index=index)
    return {
        "reviewer_id": reviewer_id,
        "case_id": case_id,
        "reviewer_label": label,
        "recommended_decision": decision,
        "confidence": confidence,
        "rationale": str(row.get("rationale") or "").strip(),
        "notes": str(row.get("notes") or "").strip(),
    }


def _confidence(value: str | None, *, index: int) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    confidence = float(value)
    if confidence < 0 or confidence > 1:
        raise ValueError(f"row {index}: confidence must be between 0 and 1")
    return confidence


def _read_calibration_cases(project_root: Path) -> list[dict[str, Any]]:
    return read_jsonl(project_root / CALIBRATION_DATASET)


def _write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _agreement_rate(pairs: list[tuple[str, str]]) -> float:
    return _ratio(sum(1 for left, right in pairs if left == right), len(pairs))


def _cohen_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    if len(labels_a) != len(labels_b):
        raise ValueError("label lists must have equal length")
    if not labels_a:
        return 0.0
    observed = _agreement_rate(list(zip(labels_a, labels_b, strict=True)))
    values = sorted(set(labels_a) | set(labels_b))
    expected = 0.0
    for value in values:
        expected += _ratio(labels_a.count(value), len(labels_a)) * _ratio(
            labels_b.count(value),
            len(labels_b),
        )
    if expected == 1:
        return 1.0
    return round((observed - expected) / (1 - expected), 4)


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)
