"""Map release-gate evidence to NIST AI 600-1 (Generative AI Profile) subcategories.

This produces a coverage map that tags each artifact the gate already generates with
the AI RMF subcategory and GenAI risk category it provides *evidence* for. It is an
evidence-alignment aid for reviewers, NOT a compliance certification: it claims the
suite generates the documented TEVV-style evidence those subcategories ask for.

Granularity is intentionally the AI RMF subcategory (e.g. ``MEASURE 2.4`` / action-ID
prefix ``MS-2.4-*``), not a specific action sequence number -- exact ``MS-/MG-NNN`` IDs
should be confirmed against NIST AI 600-1 section 3 before any external publication.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from internal_ai_agent.io import write_json

NIST_PROFILE_ID = "NIST AI 600-1"
NIST_COVERAGE_MAP_PATH = Path("reports/nist_ai_600_1_coverage_map.json")

_DISCLAIMER = (
    "Evidence-alignment aid only. This maps artifacts the release gate produces to "
    "the AI RMF subcategories and GenAI risk categories they help evidence; it does "
    "not certify compliance. Subcategory granularity is used deliberately -- confirm "
    "exact NIST AI 600-1 section 3 action IDs against the primary document. "
    "'evidence_present' is a file-existence check and proves nothing about content; "
    "'exercised' records whether the shipped evaluation actually produces the named "
    "measurement, and entries where it is false are excluded from "
    "'covered_subcategories'. Only the incident-replay entries were audited "
    "case-by-case, on 2026-08-02."
)

# Each entry: an evidence artifact the gate emits -> the AI RMF function/subcategories
# and GenAI Profile risk categories it provides evidence for, with the action-ID prefix.
_NIST_EVIDENCE_MAP: list[dict[str, Any]] = [
    {
        "evidence_id": "red_team_and_injection_replay",
        "evidence": (
            "Red-team and prompt-injection replay with weighted safe-rate and "
            "residual-risk metrics"
        ),
        "source_artifact": "reports/security_eval_summary.json",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.4", "MEASURE 2.7"],
        "action_id_prefixes": ["MS-2.4-*", "MS-2.7-*"],
        "genai_risk_categories": ["Information Security", "Information Integrity"],
        "rationale": (
            "Pre-deployment TEVV evidence of jailbreak / prompt-injection resistance "
            "and system security and resilience."
        ),
    },
    {
        "evidence_id": "safety_classifier",
        "evidence": "Safety classifier recall and unsafe-miss / benign-block accounting",
        "source_artifact": "reports/safety_classifier_eval_summary.json",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.6"],
        "action_id_prefixes": ["MS-2.6-*"],
        "genai_risk_categories": [
            "Dangerous, Violent, or Hateful Content",
            "Information Integrity",
        ],
        "rationale": "Measures the system's ability to flag and refuse unsafe requests.",
    },
    {
        "evidence_id": "incident_release_gates",
        "evidence": "Incident-replay release gate pass/warn/fail with must-not violations",
        "source_artifact": "reports/incident_release_gates.json",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.4", "MANAGE 4.1"],
        "action_id_prefixes": ["MS-2.4-*", "MG-4.1-*"],
        "genai_risk_categories": ["Information Security", "Human-AI Configuration"],
        "rationale": (
            "Gates a release on replay of a constructed incident-scenario pack and "
            "tracks/responds to reintroduced unsafe behavior."
        ),
    },
    {
        "evidence_id": "action_safety_axes",
        "evidence": (
            "Confirmation-before-irreversible-action and unsafe-bulk-automation "
            "must-not assertions (implemented, not exercised)"
        ),
        "source_artifact": "reports/incident_replay_runs.jsonl",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.7"],
        "action_id_prefixes": ["MS-2.7-*"],
        "genai_risk_categories": ["Human-AI Configuration", "Information Security"],
        "exercised": False,
        "rationale": (
            "NOT EVIDENCE. The 'execute_irreversible_action_without_confirmation' and "
            "'execute_bulk_actions_without_review' assertions are implemented and "
            "supported by the gate, but no case in the shipped incident pack declares "
            "either one, so the named artifact contains no instance of them being "
            "measured. Corrected 2026-08-02 after a mutation probe found that removing "
            "the irreversible-action set changed nothing. Listed here so the capability "
            "and the gap are both visible; it must not be counted as coverage."
        ),
    },
    {
        "evidence_id": "dataset_profile_and_eval_metrics",
        "evidence": "Documented synthetic/public test sets, metrics, and evaluation tools",
        "source_artifact": "reports/dataset_profile.json",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.1", "MEASURE 2.2"],
        "action_id_prefixes": ["MS-2.1-*", "MS-2.2-*"],
        "genai_risk_categories": ["Information Integrity"],
        "rationale": (
            "Documents the test sets, metrics, and tooling, and the limits of "
            "deployment-representative testing."
        ),
    },
    {
        "evidence_id": "refusal_and_abstention",
        "evidence": "Agent refusal / weak-evidence abstention coverage",
        "source_artifact": "reports/agent_eval_summary.json",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.6"],
        "action_id_prefixes": ["MS-2.6-*"],
        "genai_risk_categories": ["Human-AI Configuration", "Confabulation"],
        "rationale": "Measures appropriate refusal and abstention under weak evidence.",
    },
    {
        "evidence_id": "grounding_and_citation",
        "evidence": "Retrieval grounding hit-rate and citation-coverage metrics",
        "source_artifact": "reports/retriever_comparison.json",
        "nist_function": "MEASURE",
        "nist_subcategories": ["MEASURE 2.6"],
        "action_id_prefixes": ["MS-2.6-*"],
        "genai_risk_categories": ["Confabulation", "Information Integrity"],
        "rationale": "Evidence against confabulation: answers are grounded and cited.",
    },
    {
        "evidence_id": "audit_trail_and_observability",
        "evidence": "Audit events, OpenTelemetry-style spans, and trace index",
        "source_artifact": "reports/observability_trace_index.json",
        "nist_function": "MANAGE",
        "nist_subcategories": ["MANAGE 4.1"],
        "action_id_prefixes": ["MG-4.1-*"],
        "genai_risk_categories": ["Human-AI Configuration"],
        "rationale": "Provides the monitoring, audit, and accountability trail for review.",
    },
]


def build_nist_coverage_map(project_root: Path | None = None) -> dict[str, Any]:
    """Build the coverage map, marking which source artifacts are present if given.

    ``exercised`` is the load-bearing field, not ``evidence_present``. A file can exist
    and contain no instance of the measurement it is cited for: that is exactly how an
    entry claiming coverage of two must-not axes survived here while no case in the
    shipped pack asserted either of them. Entries with ``exercised`` false are excluded
    from ``covered_subcategories``.
    """
    mappings: list[dict[str, Any]] = []
    for entry in _NIST_EVIDENCE_MAP:
        mapped = dict(entry)
        mapped["exercised"] = bool(entry.get("exercised", True))
        if project_root is not None:
            mapped["evidence_present"] = (project_root / entry["source_artifact"]).exists()
        mappings.append(mapped)

    covered = sorted(
        {sub for entry in mappings if entry["exercised"] for sub in entry["nist_subcategories"]}
    )
    unexercised = sorted(
        {
            sub
            for entry in mappings
            if not entry["exercised"]
            for sub in entry["nist_subcategories"]
        }
        - set(covered)
    )
    return {
        "report_type": "nist_ai_600_1_coverage_map",
        "profile": NIST_PROFILE_ID,
        "alignment_type": "evidence_alignment_not_certification",
        "disclaimer": _DISCLAIMER,
        "covered_subcategories": covered,
        "claimed_but_unexercised_subcategories": unexercised,
        "unexercised_evidence_ids": [
            entry["evidence_id"] for entry in mappings if not entry["exercised"]
        ],
        "mappings": mappings,
    }


def write_nist_coverage_map(project_root: Path) -> dict[str, Any]:
    coverage = build_nist_coverage_map(project_root)
    write_json(project_root / NIST_COVERAGE_MAP_PATH, coverage)
    return coverage
