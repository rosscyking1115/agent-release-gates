# Evaluate Your Agent Quickstart

This guide shows how to score an external AI agent with Agent Release Safety
Gates from a plain `pip install` — no source checkout required.

The workflow is intentionally simple:

1. Install the package.
2. Get an incident pack (use the bundled example, or bring your own).
3. Run your agent against each incident prompt in your own environment.
4. Export one result row per incident.
5. Run the release gate against those results and read the pass/fail reasons.

No provider API key is required for the release gate itself. Your agent may need
its own credentials, but those stay outside this tool.

## Install

```bash
pip install agent-release-gates
```

This installs the `agent-safety` command. Confirm the built-in gate runs with no
setup at all:

```bash
agent-safety release-gate
```

With no arguments it replays a built-in incident pack and prints a `pass` / `fail`
gate status. That confirms your install works before you wire in your own agent.

## 1. Get an incident pack

Materialize the bundled minimal pack into the current directory:

```bash
agent-safety init-example --dest incident_pack_minimal
```

This writes `incident_cases.jsonl`, `trace_events.jsonl`,
`incident_release_policy.json`, and example input/output files you can imitate.
An incident pack is just a directory containing at least `incident_cases.jsonl`
and `trace_events.jsonl`; see the [incident pack schema](incident_pack_schema.md).

## 2. Run your agent and capture logs

Run your agent against each incident `question` in your own environment and write
one JSON object per incident to a JSONL file. A generic row looks like:

```json
{
  "case_id": "INC-EXAMPLE-0001",
  "decision": "refused",
  "answer": "I cannot route this ticket without approval.",
  "tool_calls": [
    {
      "name": "route_ticket",
      "tool_type": "side_effect",
      "requires_approval": true,
      "approval_granted": false,
      "status": "blocked"
    }
  ]
}
```

`incident_pack_minimal/agent_run_log.jsonl` is a ready-made example of this format,
and `langchain_trace_log.jsonl` shows the LangChain/LangSmith trace shape.

## 3. Export candidate results

Convert your agent log into the candidate-results format the gate consumes:

```bash
agent-safety export-candidate-results \
  --input incident_pack_minimal/agent_run_log.jsonl \
  --output candidate_results.jsonl \
  --candidate-id my_agent_release_v1
```

For LangChain/LangSmith-style traces, add `--source-format langchain_trace`
(or `--source-format langsmith_run`):

```bash
agent-safety export-candidate-results \
  --source-format langchain_trace \
  --input incident_pack_minimal/langchain_trace_log.jsonl \
  --output candidate_results.jsonl \
  --candidate-id langchain_agent_v1
```

The trace adapter reads:

- `inputs.case_id` as the incident id.
- `outputs.answer` or `outputs.final_answer` as the agent answer.
- `outputs.decision` as `allow`, `block`, or `review` after normalization.
- tool child runs or tool events as `tool_outcomes`.
- run `id` or `uuid` as the trace id.

## 4. Score candidate results

Run the release gate with your exported candidate results:

```bash
agent-safety release-gate \
  --incident-pack incident_pack_minimal \
  --candidate-results candidate_results.jsonl
```

The candidate-results file must contain exactly one row for each incident in the
selected pack. Missing, extra, or duplicate incident ids fail fast as
configuration errors. When `--incident-pack` contains an
`incident_release_policy.json`, that policy is applied automatically.

The gate writes `reports/incident_replay_summary.json` and
`reports/incident_release_gates.json` next to where you run it, and exits
non-zero on a blocking failure (useful as a CI step).

## 5. Interpret the output

A passing gate means the submitted results satisfied the incident pack's current
policy thresholds. It is not a claim that the agent is safe in production.

A failing gate usually means one of these happened:

- the agent allowed an incident that should be blocked or reviewed;
- the agent executed a side-effecting tool without approval;
- the agent leaked policy text or sensitive content;
- the result file did not cover the selected incident pack;
- the result format was incomplete or inconsistent.

Use the generated `reports/incident_replay_summary.json` and
`reports/incident_release_gates.json` files to inspect the failing criteria.

## Result contract

The release gate consumes `candidate_results.jsonl`, one JSON object per
incident. For full field details, see:

- [Candidate results schema](candidate_results_schema.md)
- [Incident pack schema](incident_pack_schema.md)

The important minimum fields are:

```json
{
  "incident_id": "INC-EXAMPLE-0001",
  "candidate_id": "my_agent_release_v1",
  "decision": "block",
  "answer": "I cannot complete this without approval."
}
```

Tool outcomes matter because the gate can detect side-effect execution without
approval:

```json
{
  "tool": "route_ticket",
  "tool_type": "side_effect",
  "requires_approval": true,
  "approval_granted": false,
  "executed": true
}
```

## Working from a source checkout

If you cloned the repository instead of installing from PyPI, the same commands
are available through `uv` without installing, and the example pack lives at
`examples/incident_pack_minimal`:

```bash
uv run agent-safety release-gate --incident-pack examples/incident_pack_minimal
uv run pytest
```

Do not commit private prompts, customer data, API keys, or raw production traces.
