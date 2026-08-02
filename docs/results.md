# Measured results, and what produces them

Every headline number this project publishes, with what it does and does not support.
Read [evaluation integrity](evaluation_integrity.md) alongside it: that document reports
where this project's own benchmark is defective, and this one is written to stay
consistent with it.

## Retrieval

Reported on **external public corpora**, never on the synthetic benchmark this project
generates itself.

| Area | Result |
| --- | --- |
| **Retrieval (external, headline)** | **79.92% hit rate@3, 69.61% top-1 citation accuracy** over 640 public cases (NVIDIA TechQA + Wix WixQA, 510 documents) |
| **Largest external failure mode** | **40.47% case failure rate; 85 impossible questions answered instead of abstained** |
| Retrieval (in-corpus fixture) | 99.31–100% on 358 self-generated cases. **Not a retrieval result**: the generator templates the query from its own gold answer |

**The same retriever drops about 20 points the moment it leaves the corpus its own
generator wrote.** That gap is the point of the exercise, and the external number is the
one reported.

The synthetic benchmark is **circular by construction**: the generator builds the query
from the same `{category}`/`{system}` variables as the gold answer, three
separately-reported metrics are mathematically one measurement, and the 18.75% "baseline"
is an alphabetical tie-break rather than a retrieval result. It is kept as a deterministic
regression fixture and nothing more.

## Safety and judging

| Area | Result |
| --- | --- |
| Safety classifier | 90.91% recall, 0 high-severity false negatives — measured with case-specific signals still in place, not re-measured since they were identified, and expected to fall when they are removed |
| Multi-model judge comparison | Local `llama3.1:8b` 91.67% label accuracy vs 95.83% (`gpt-4.1-mini`) and 100% (`claude-sonnet-4-5`) on 24 calibration cases; the local judge missed 2 unsafe cases the frontier models caught |

The safety-classifier figure carries a live caveat rather than a footnote: several of its
benign-intent signals match a single evaluation case verbatim, which is memorization
rather than generalization. Detail in
[evaluation integrity, finding 5](evaluation_integrity.md#finding-5-the-safety-classifier-whitelists-a-case-by-name).

## Numbers that saturate

Nine metrics in `reports/agent_eval_summary.json` sit at exactly 1.0, and three more do in
the incident-replay summary. They are listed here with their cause, because a table of
100% figures is a warning sign rather than a result, and because the
[gate-mutation finding](finding_gate_mutation_adequacy.md) turns on understanding what
produces them.

| Metric | Why it is 1.0 |
| --- | --- |
| `side_effect_block_rate`, `approved_action_execution_rate` | The eval runs the same deterministic agent twice, once with approval withheld and once granted, and checks it blocked then executed. This confirms a boolean is wired up; nothing resists anything. |
| `approval_audit_rate`, `audit_event_coverage_rate`, `trace_coverage_rate`, `monitoring_snapshot_rate` | The controlled agent emits these unconditionally on every run. |
| `valid_tool_call_rate`, `approval_trigger_rate`, `route_tool_selection_accuracy` | Properties of the deterministic tool layer, not of a model under stress. |
| `expected_behavior_match_rate`, `incident_closure_rate`, `trace_event_coverage_rate` | The metrics the mutation probe showed could stay at 1.0 with the entire request-level safety policy deleted. |

Treat these as conformance checks that the harness is wired correctly. **They are not
evidence that a safety mechanism works**, and the gate-mutation result is the
demonstration of exactly that.

## What none of this supports

- Any claim of real-world production performance. These are controlled benchmarks.
- Any ranking of models or agents. The incident pack is eight cases.
- Any regulatory-compliance claim. The NIST AI 600-1 map in this repository is an
  evidence-alignment aid and says so on its face.
