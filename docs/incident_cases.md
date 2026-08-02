# The eight incident cases

The pack the release gate replays lives in
[`data/incidents/incident_cases.jsonl`](../data/incidents/incident_cases.jsonl). This page
says exactly what it is, because the answer constrains every number derived from it.

## They are constructed scenarios

**Written for this repository. Not reconstructions of sourced incidents.**

Each case declares itself in its own `source_type` field — `simulated_agent_trace`,
`simulated_chat_transcript`, `simulated_retrieved_context`, or `simulated_memory_note`.

The failure *classes* they exercise are real and widely reported:

- prompt injection
- approval-gate bypass
- system-prompt leakage
- retrieved-context priority attacks
- secret-exfiltration requests
- unbounded bulk automation
- memory poisoning

The *situations* are invented. No case carries provenance to a named public report.

## Why they exist

To make the gate testable end to end without network access, API keys, or third-party
data: eight deterministic fixtures that exercise the replay runner, the must-not
assertions, the policy thresholds, the memo generator, and the CLI exit code.

That is a real job, and it is the only job they do.

## What they cannot support

- Any claim that this gate would catch a given real-world incident.
- Any coverage claim over a real incident population.
- Any ranking of models or agents. Eight cases is a conformance smoke check.

The pack also **under-covers the gate's own capabilities**. Of the seven must-not
assertions the gate supports, two are declared by zero cases:
`execute_bulk_actions_without_review` and
`execute_irreversible_action_without_confirmation`. Both are implemented; neither is
exercised. That gap was found by the
[mutation probe](finding_gate_mutation_adequacy.md) and corrected in the NIST coverage
map rather than papered over by adding cases.

## The corpus that was designed instead, and abandoned

An incident-derived corpus with per-case provenance and a recorded divergence from the
real event was [preregistered](gate_mutation_benchmark_design.md) and then closed by its
own kill criterion before a single case was authored: only 19 of MITRE ATLAS's 57 case
studies are executable as agent-with-tools cases, against a floor of 40–60. The
[per-study judgements](atlas_executability_audit.md) are published so the count is
auditable.

Until such a corpus exists, **"incident-derived" is not a claim this project makes**.

## A correction

Until 2026-08-02 this project's README described the tool as replaying "known incidents".
It does not. That claim was broader than its evidence and is retracted; the record is in
the [changelog](../CHANGELOG.md).
