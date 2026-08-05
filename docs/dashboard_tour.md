# A tour of the dashboard

Nine views, what each one shows, and what to conclude from it. The dashboard is the
interactive complement to the [project page](https://rosscyking1115.github.io/agent-release-gates/);
[run it locally or deploy it](dashboard.md), or open the
[hosted instance](https://agent-release-gates.streamlit.app/).

**Read this first.** The dashboard reports two different kinds of number and they are
not interchangeable.

- **External** figures come from public corpora this project did not generate — NVIDIA
  TechQA-RAG-Eval and Wix WixQA, 640 cases. They are the retrieval result.
- **In-corpus** figures come from this project's own synthetic operations benchmark,
  which is circular by construction: the generator templates each query from the same
  variables as its gold answer. They are a regression fixture and are labelled
  `(in-corpus)` wherever they appear. See
  [evaluation integrity](evaluation_integrity.md).

Every capture below was taken from the running app at a fixed 1280px-wide desktop
viewport in the dark theme, so the set reads as one sitting rather than nine.

---

## Overview — what the release decision is, and what it is worth

![Overview](img/dashboard/overview-release-decision.png)

The external retrieval result leads: 640 public cases, 79.92% hit@3, 69.61% top-1
citation, 40.47% case-level failure rate. Below it the synthetic case count and the gate
status, then the panel that matters most on this screen — **what a pass is worth**.

**What to conclude.** The gate says `pass`, and the panel beside it says that half the
deliberate weaknesses planted in this gate's own configuration left it saying exactly
that. A pass here means the seeded checks did not fire; it is not evidence that the
safety layer works. That is the finding this repository exists to publish, and it is
placed where a reader meets the verdict rather than three documents away.

Note what is *not* here. Safety recall has no tile: it appears further down, in the
evidence list, with the caveat that it was measured with case-specific signals still in
place. A metric with nowhere to put its qualification does not belong in a grid beside
external results.

---

## Dataset Profile — what the benchmark is made of

![Dataset Profile](img/dashboard/dataset-profile-benchmark-composition.png)

358 golden cases, 102 of them hand-written, 46 noise types, 70 cases where the correct
answer is to abstain. Tabs break the corpus down by noise type, task, issue category and
red-team risk, and name the known gaps.

**What to conclude.** High scores on a synthetic benchmark mean nothing without its
composition, and a benchmark whose gaps are not stated is a benchmark you cannot size.
The 70 expected abstentions are the interesting number: they are the cases where
answering at all is the failure.

---

## Retrieval Evaluation — the external result, and the fixture beside it

![Retrieval Evaluation](img/dashboard/retrieval-external-vs-in-corpus.png)

The in-corpus retriever experiment, explicitly labelled as not retrieval evidence, then
the two public tracks: TechQA at 80.73% retrieval@3 over 480 cases, WixQA at 77.50% over
160, and the cross-track weighted figure of 79.92%. Then reranking headroom, failure
analysis and the release-gate table.

**What to conclude.** The same retriever scores 99.31% in-corpus and 79.92% on corpora
it did not generate. That ~20-point gap is what the benchmark's circularity is worth in
points, and it is the reason the external number is the one reported.

---

## Safety & Extraction — the classifier as an operating decision

![Safety & Extraction](img/dashboard/safety-classifier-operating-point.png)

Challenge-set recall, false-positive rate, prevalence, threshold sweep, retuning
comparison, human-review simulation, reviewer disagreement slices, secondary-review band
and the threshold decision memo.

**What to conclude.** Read the warning above the tiles before the tiles. The 90.91%
recall was measured with benign-intent signals that match single evaluation cases
verbatim still in place — the classifier partly recognises its own test set, and the
number should be expected to fall when they are removed. This view is included as an
example of reporting a metric alongside what it cost and what it cannot support, not as
a headline.

---

## Intervention Study — what each safeguard buys and what it costs

![Intervention Study](img/dashboard/intervention-safety-usefulness-tradeoff.png)

Frozen baseline against layered safeguards across prompt injection, action gating, RAG
grounding, memory pollution and goal conflict — each reporting the unsafe behaviour it
prevents *and* the review burden it adds per 100 requests.

**What to conclude.** A safeguard reported without its cost is a safeguard nobody can
decide about. Blocking everything scores perfectly on safety and is useless; these
panels are built so that trade-off is visible rather than implied.

---

## Incident Replay — eight scenarios, replayed against the current agent

![Incident Replay](img/dashboard/incident-replay-verdicts.png)

Eight constructed incidents replayed against the shipped controlled agent: the original
verdict, the replay verdict, whether the expected behaviour matched, must-not violations,
trace coverage, and per-incident memos, traces and release gates.

**What to conclude.** Every incident closes and there are no must-not violations —
which is exactly the reassuring picture the panel beneath the gate tile qualifies. Note
`INC-2026-0003`: its replay decision is `review`, not `block`. It read `block` until the
committed evidence was made reproducible, and the movement is
[recorded rather than quietly corrected](evaluation_integrity.md#finding-6-a-committed-verdict-whose-declared-input-did-not-exist).

---

## Agent Observability — whether the run can be inspected at all

![Agent Observability](img/dashboard/observability-traces-and-spans.png)

180 in-corpus agent cases, side-effect block rate, OpenTelemetry-style span export, a
local trace index of 21 traces, component summaries and error-span examples.

**What to conclude.** A safety claim you cannot trace is a safety claim you cannot
audit. The spans are deterministic and exported in a standard shape, which is what makes
the approval decisions in the other views checkable rather than merely asserted.

---

## Evaluation Report — the whole generated report, inline

![Evaluation Report](img/dashboard/evaluation-report-full-text.png)

The full deterministic evaluation report rendered in the page, identical to the
[HTML](https://rosscyking1115.github.io/agent-release-gates/evaluation_report.html) and
[PDF](https://rosscyking1115.github.io/agent-release-gates/evaluation_report.pdf)
exports.

**This capture is truncated** — the view runs to 36,356px and is cut at 9,000px, roughly
the first quarter. Nothing is lost by that: the document it renders is published in full
at both links above. It is shown here only so the tour is complete.

**What to conclude.** The report is generated, not written, so it cannot drift from the
artifacts. Its retrieval section carries the circularity warning and its safety section
carries the recall caveat, in the same words as everywhere else.

---

## Case Review — the individual failures

![Case Review](img/dashboard/case-review-per-case-failures.png)

Per-case rows for the baseline and improved retrievers: which cases failed, on what, and
with which citation.

**What to conclude.** Aggregates hide the shape of a failure. This is where a reader
checks whether the 5 remaining improved-retriever failures are a long tail or one
systematic gap — and the answer determines whether the headline number means anything.

---

## How these captures are kept honest

Every number above was checked against the committed artifact that produces it, read
from the file rather than from the page: 34 metrics across seven views traced to
`reports/*.json`, with no mismatches. All nine views render with no exception, no
placeholder state and no empty data frame, and all 15 charts were confirmed to contain
drawn marks rather than bare axes.

The captures are documentation, not part of the package: `docs/img` is excluded from the
sdist, so nothing a `pip install` produces depends on them.
