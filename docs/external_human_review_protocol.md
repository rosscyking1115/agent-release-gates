# External Human Review Protocol

This protocol lets independent reviewers label the same calibration cases used by
the local rubric judge and hosted model-judge workflow.

## Purpose

The goal is to measure whether independent reviewers agree with the maintainer
labels, deterministic rules, classifier decisions, and hosted judge decisions.
Reviewer labels must be reported separately from maintainer labels.

## Files

| File | Purpose |
| --- | --- |
| `data/review/external_human_review_packet.csv` | Case packet shared with reviewers. |
| `data/review/external_human_review_label_template.csv` | Blank label sheet for reviewer responses. |
| `data/review/external_human_review_reviewer_guide.md` | Reviewer-facing instructions for blind labelling. |
| `data/review/external_human_review_labels.csv` | Optional completed labels, kept separate from maintainer labels. |
| `reports/external_human_review_manifest.json` | Machine-readable readiness checklist and artifact map. |
| `reports/external_human_review_summary.json` | Generated review status and agreement metrics. |
| `reports/external_human_review_cases.jsonl` | Generated case-level external-review comparison. |

## Reviewer Instructions

For each case, assign:

| Field | Allowed values |
| --- | --- |
| `reviewer_id` | Stable pseudonymous reviewer id, such as `reviewer_a`. |
| `case_id` | Case id from the packet. |
| `reviewer_label` | `benign` or `unsafe`. |
| `recommended_decision` | `allow`, `review`, or `block`. |
| `confidence` | Optional number between 0 and 1. |
| `rationale` | Short reason for the label. |
| `notes` | Optional uncertainty or edge-case comments. |

Do not use the maintainer label, classifier label, hosted model-judge label, or
public report metrics while reviewing. Reviewers should label the request text
itself.

Each case should be reviewed by at least two independent reviewers. If reviewer
labels tie, the evaluator marks the case as `adjudication_required` instead of
forcing a hidden tie-break.

## Commands

```powershell
uv run python scripts/prepare_external_human_review.py
```

After adding completed labels to
`data/review/external_human_review_labels.csv`, rerun the command. The report
will include label coverage, pairwise agreement, Cohen kappa, maintainer
agreement, and adjudication-required counts.

## Publication Rule

Publish external human-review metrics only when the completed labels file is
present, all calibration cases have two independent labels, and reviewers are
independent of the maintainer labels. Otherwise, the public report should say
the packet is prepared and labels are awaiting review.
