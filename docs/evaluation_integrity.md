# Evaluation integrity: what the synthetic benchmark does and does not measure

This page reports a defect in this project's own headline evaluation, found by auditing
the generator on 2026-07-27. The synthetic operations benchmark is **circular**: the
query is constructed from the same variables as its gold answer. Its high scores measure
string overlap the generator created, not retrieval quality.

The honest measurement is the external one, below. Read that first.

## The measurement that counts

The same retriever, run against external public corpora it did not generate
(`reports/public_rag_findings.json`, NVIDIA TechQA-RAG-Eval + Wix WixQA, 640 cases,
510 documents):

| Metric | Result |
| --- | --- |
| Weighted retrieval hit rate@3 | **79.92%** |
| Weighted top-1 citation accuracy | **69.61%** |
| Weighted failure rate | **40.47%** |
| Failures to abstain on impossible questions (TechQA) | **85** |
| False abstentions on answerable questions (TechQA) | 17 |

Against the in-corpus synthetic figure of 99.31% hit@3, that is a **~20-point drop the
moment the retriever leaves the corpus its own generator wrote**, and a 40% case-level
failure rate. The 85 impossible questions it answered instead of abstaining are the
single largest failure mode, and they are the failure mode the synthetic benchmark is
least able to see.

Treat 79.92% / 69.61% as this project's retrieval result. Treat the synthetic numbers as
a fixture-level regression check.

## Finding 1: the query is a projection of its own gold answer

Both sides of the synthetic benchmark are templated from the same three variables —
`category`, `title` (which is just `category` re-cased), and `system`.

The runbook section, which is the gold answer
([`synthetic.py:224`](../src/internal_ai_agent/data/synthetic.py#L224)):

```
When {team_name} receives a {title.lower()} ticket for {system},
the analyst should classify the issue as {category}, ...
Recommended next action: {action}
```

The ticket, which becomes the query
([`synthetic.py:267`](../src/internal_ai_agent/data/synthetic.py#L267)):

```
{title} observed in {system}. The synthetic event severity is {severity}. ...
```

The gold citation is the section built from those same variables. Retrieving it requires
matching `{title}` and `{system}` against a document that contains `{title}` and
`{system}` verbatim. Any lexical retriever scores near-perfectly by construction. The
task contains no retrieval problem to solve.

## Finding 2: three reported metrics are one measurement

`citation_coverage`, `issue_category_accuracy`, and `next_action_accuracy` all move
0.1875 → 0.9826 in `reports/eval_comparison.json`, identical to four decimal places.
That is not three metrics agreeing. It is one metric printed three times.

All three answers derive from a single variable — the top-ranked section
([`baseline.py:283`](../src/internal_ai_agent/rag/baseline.py#L283)):

```python
chosen = retrieved[0]
issue_category = chosen.title.lower().replace(" ", "_")
next_action = _extract_next_action(chosen.content)
citations = [chosen.section_id]
```

Because the generator makes `section_id` ↔ `title` ↔ `category` ↔ `action` a bijection
over the 24 sections, and each case has exactly one expected citation, all three scored
matches reduce to the same boolean: *is `chosen` the gold section?* They are
mathematically incapable of disagreeing. Reporting them as separate metrics overstates
the evidence threefold.

## Finding 3: the baseline is not a baseline

The comparison's "before" number is not a measurement of retrieval quality.

`retrieve_baseline` scores sections only by broad team hints
([`baseline.py:162`](../src/internal_ai_agent/rag/baseline.py#L162)), so all six sections
belonging to the matched team receive an identical score, and the tie is broken by
`section_id` ascending. The `-01` section of each team therefore always wins. Measured
over the 288 answerable golden cases, the baseline can return only **4 of the 24 runbook
sections**; 20 are unreachable:

```
RB-CLIENT_ONBOARDING-01   RB-DATA_QUALITY-01   RB-PAYMENTS_OPS-01   RB-TRADE_SUPPORT-01
```

Its reported 0.1875 is exactly the share of answerable cases whose gold citation happens
to be a `-01` section: **54 / 288 = 0.1875**, matching the published figure exactly. The
number is a property of the eval set's section numbering, not of any retrieval behavior.

Its own docstring concedes the design
([`baseline.py:144`](../src/internal_ai_agent/rag/baseline.py#L144)):

> This baseline intentionally uses broad system/team hints rather than procedure-level
> matching.

A "+79.51 point improvement" measured against an alphabetical tie-break is not evidence
of an improvement.

## Finding 4: the improved retriever is fitted to the eval strings

The retrieval gain comes substantially from hand-written dictionaries keyed to phrasing
that appears in the evaluation set, not from a general method:

- `SEMANTIC_ALIASES` ([`baseline.py:65`](../src/internal_ai_agent/rag/baseline.py#L65)) —
  24 per-category alias lists, written by hand, one per gold category.
- `CURRENT_EVIDENCE_MARKERS` ([`baseline.py:1031`](../src/internal_ai_agent/rag/baseline.py#L1031))
  and `_evidence_summary_text`, which keys on the literal substring `"this summary:"` —
  a phrase authored into the manual eval cases.
- `_stale_context_penalty` stale markers (`"older comment"`, `"side thread"`,
  `"guessed"`) — likewise verbatim eval phrasings.

There is **no held-out split anywhere in the synthetic arm**. Every golden case is
visible while the aliases and penalties are tuned, and every golden case is scored. A
retriever tuned on the strings it is later scored against has no generalization claim,
which is why the external result in the table above is ~20 points lower.

## Finding 5: the safety classifier whitelists a case by name

`BENIGN_INTENT_SIGNALS`
([`safety_classifier.py:141`](../src/internal_ai_agent/evals/safety_classifier.py#L141))
contains the literal string:

```
"inspect 25 synthetic records once"
```

That fragment appears in exactly **one** distinct request text across the safety eval
files. Two further entries — `"bounded scan plan"` and `"then stop"` — are fragments of
that same sentence. Measured across the 79 distinct request texts in
`data/eval/safety_*.jsonl`:

| Benign signal | Distinct texts matched |
| --- | --- |
| `inspect 25 synthetic records once` | 1 |
| `should be treated as untrusted` | 1 |
| `without asking to disable` | 1 |
| `by asking follow-up questions` | 1 |
| `instead of guessing` | 1 |
| `without asking to route` | **0** (dead signal) |

Six of the thirteen benign signals are effectively case-specific, and one matches nothing
at all. A classifier that recognizes a test case by name is measuring memorization.

> **Standing of the published 90.91% recall figure.** It was measured **with all thirteen
> signals in place, including the case-specific ones**, and it has not been re-measured
> since they were identified. To be exact about what has and has not happened: the signals
> have been *documented*, not *removed* — all four named above are still live in
> `safety_classifier.py` today. The figure is therefore not stale relative to the shipped
> classifier; it is an accurate measurement of a classifier that partly recognizes its own
> test set. **It should be expected to fall when the signals are removed**, and it should
> not be read as a generalization estimate until then. Re-measurement is step 5 of the
> remediation order below; a caveat does not make the number safe to quote on its own.

The same pattern holds for the category signals.
`CATEGORY_SIGNALS = {**LEGACY_CATEGORY_SIGNALS, ...}`
([`safety_classifier.py:83`](../src/internal_ai_agent/evals/safety_classifier.py#L83))
extends exactly the three categories the legacy version missed, with precisely the
phrases it missed them on — and `PER_CATEGORY_THRESHOLDS` additionally lowers the
decision threshold for those same three categories (0.65 → 0.55, 0.70 → 0.55,
0.70 → 0.55). The reported gain over the legacy classifier is the gain from adding the
answers.

## Finding 6: a committed verdict whose declared input did not exist

Found 2026-07-27 while auditing committed evidence artifacts.

`reports/incident_replay_summary.json` recorded this as the provenance of the published
incident-replay result:

```json
"candidate_results": "C:/Users/leaff/AppData/Local/Temp/lg.jsonl"
```

A machine-local temporary file. It is untracked, it is not reproducible on any other
machine, and it no longer exists on the machine that produced it. Anything derived from
it could not be checked by anyone, including its author.

The artifact was also **internally inconsistent with the rest of the repository**:

| | Committed incident artifact | Everything else |
| --- | --- | --- |
| Incidents replayed | **1** (`INC-EXAMPLE-0001`) | 8 (README, evaluation report, project page) |
| Candidate | `langgraph_example` | `controlled_agent_approval_gate_v0` |
| Policy | `minimal_example_incident_policy` | `incident_release_policy_v0` |
| Incident pack | `examples/incident_pack_minimal/` | `data/incidents/` |

So the committed evidence was a one-case run of a LangGraph *example* against the
*minimal example pack*, while the published claim next to it said eight incidents against
the built-in pack. The eight per-incident memos were committed from a different run again,
which is why `incident_memo_INC-2026-0003.md` described a verdict that appeared in no
committed run file.

### What changed when it was made reproducible

Regenerated against the built-in controlled agent and the tracked incident pack:

| Field | Before | After |
| --- | --- | --- |
| `candidate_results` | `C:/Users/leaff/AppData/Local/Temp/lg.jsonl` | `built_in_controlled_agent` |
| `incident_cases` | `examples/incident_pack_minimal/incident_cases.jsonl` | `data/incidents/incident_cases.jsonl` |
| `candidate_id` | `langgraph_example` | `controlled_agent_approval_gate_v0` |
| `policy_id` | `minimal_example_incident_policy` | `incident_release_policy_v0` |
| `case_count` | 1 | 8 |
| **`INC-2026-0003` replay decision** | **`block`** | **`review`** |

Closure rate, expected-behavior match rate, must-not violation count (0), and the overall
gate status (`pass`) are unchanged. The one substantive movement is INC-2026-0003.

### Why the original `block` was not evidence

It is tempting to read the change as the cost of fixing the path. It is not — **it is the
finding.**

A verdict whose declared input is an untracked temporary file was never reproducible, so
the published `block` was never evidence of anything. It was the residue of one local run
against the wrong candidate and the wrong pack, preserved in a committed file that looked
authoritative. The correct verdict for that incident, from the candidate this project
actually ships and the pack it actually documents, is `review`.

A verdict that moves the moment you make it reproducible is precisely the failure this
project exists to catch. Recording it quietly, or treating the movement as a regrettable
side effect of a cleanup, would be the same defect one level up: an unreproducible claim
protected because restating it is inconvenient.

Both the artifact and the report now agree at 8 incidents under
`incident_release_policy_v0`, and no path under `reports/` references a temporary
directory.

`reports/incident_memo_INC-EXAMPLE-0001.md` was left orphaned by the regeneration — the
new summary references only the eight `INC-2026-*` memos — and has been removed. It was
the last artifact of the same superseded run.

## What this means for the published numbers

| Figure | Status |
| --- | --- |
| Synthetic hit@3 99.31% / citation 98.26% / 100% | In-corpus fixture check. Not a retrieval result. |
| Baseline 18.75% and the +79.51pt delta | Artifact of an alphabetical tie-break. Not a comparison. |
| Three separate synthetic accuracy metrics | One measurement. Report one. |
| Safety classifier gain over legacy | Partly memorization of eval strings. |
| **External 79.92% hit@3 / 69.61% top-1** | **The retrieval result.** |

The synthetic suite is still useful for what it actually is: a deterministic,
fully-specified fixture set that catches regressions in the gating pipeline and lets the
release gate be tested without network access or API keys. It is kept for that purpose.
It is not evidence of retrieval quality, and the numbers above are no longer presented as
if it were.

## What would fix it, and what has not been done

None of this is attempted yet; it is recorded so the gap is explicit rather than implied.

### Do these in this order

**The order matters, and it is not the order the findings are numbered in.** The root
defect is Finding 1 — the query is templated from its own gold answer. That is the
corpus-level form of a test that cannot fail. Every other item is downstream of it, and
two of them are actively misleading if done first:

1. **Decouple the query from the answer.** *(Finding 1 — do this first.)* Generate the
   ticket from an independent surface form, such as a symptom description written without
   reference to the runbook's `{title}`/`{system}`. Until this lands, the corpus itself
   guarantees near-perfect retrieval.

2. **Then add a held-out split.** Aliases and penalties tuned on a train split, scored on
   a test split never read during tuning.

   > Do **not** start here because it sounds like the easy one. A held-out split laid over
   > a corpus whose queries are projections of their own answers **inherits the defect**:
   > the test split is templated the same way, so a retriever that matches the template
   > scores just as well on unseen cases. You would get a clean-looking generalization
   > number that certifies nothing, which is worse than today's state, because today the
   > circularity is at least declared. The split only starts measuring generalization once
   > step 1 has removed the shared template.

3. **A real baseline.** BM25, or TF-IDF with no category dictionary, so the comparison
   measures a method rather than the alphabetical tie-break described in Finding 3.

4. **Report one metric, not three.** Collapse citation/category/next-action into a single
   `top1_section_correct`, or make them genuinely independent. Safe to do at any point —
   it is a reporting change, not a measurement change.

5. **Remove the case-specific safety signals and re-measure.** Independent of steps 1–4,
   and see the note under Finding 5 on the standing of the current recall figure.

The external TechQA/WixQA arm already avoids problems 1–3 by construction, which is why it
is the headline: its queries were written by other people, against documents this project
did not generate.
