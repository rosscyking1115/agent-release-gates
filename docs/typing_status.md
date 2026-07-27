# Static typing status

Last updated 2026-07-27.

**There is a blocking, `strict`-mode type-check gate in CI over 12 modules — the ones
where a type error would corrupt a published number. The rest of the repo is unchecked
and is not claimed to be checked.**

That distinction is the whole point of this page. A badge is a claim, a passing local run
is evidence, a blocking CI gate is proof. This is the third one, over a deliberately
narrow scope.

## What is gated

`[tool.mypy]` in `pyproject.toml` sets `strict = true` and pins an explicit `files` list.
CI runs bare `uv run mypy` as a **blocking** step (`.github/workflows/ci.yml`), so the
scope lives in one place and cannot drift between config and command.

| Module | Why it is in the gate |
| --- | --- |
| `evals/runner.py` | Computes the synthetic retrieval metrics (`citation_coverage`, `issue_category_accuracy`, `next_action_accuracy`, `retrieval_hit_rate_at_3`). |
| `evals/public_rag_findings.py` | Computes the **headline** external figures: 79.92% weighted hit@3, 69.61% top-1, 40.47% failure rate. |
| `evals/techqa_public.py` | TechQA track metrics, including the 85 impossible-question abstention failures. |
| `evals/wixqa_public.py` | WixQA track metrics. |
| `evals/gates.py` | Turns metrics into the `ship` / `warn` / `block` decision and the CLI exit code. |
| `evals/safety_classifier.py` | Computes safety recall, false-positive rate, and weighted prevalence. |
| `evals/incident_replay.py` | Computes incident closure rate and drives the incident release gates. |
| `inspect_suite/scoring.py` | Turns a model completion into a pass/fail verdict. |
| `inspect_suite/scorers.py` | Emits the Inspect `Score` (CORRECT/INCORRECT) for each sample. |
| `providers/agent_runner.py` | Parses model responses into the decision object every scorer consumes. |
| `rag/baseline.py` | The retrievers themselves — a type error here changes what gets scored. |
| `reporting/public_report.py` | Renders every published metric into the committed report artifacts. |

The selection rule is narrow and stated in the config: **if a type error in this module
could change a number that this project publishes, it is gated.** Modules that only
affect presentation (`dashboard/`), data generation (`data/synthetic.py`), or the HTTP
surface (`api/`) are out of scope for now.

### The gate is not vacuous

Verified by injecting a deliberate type error into a gated module
(`evals/runner.py`) and confirming `mypy` exits non-zero:

```
src\internal_ai_agent\evals\runner.py:521: error: Incompatible types in assignment
    (expression has type "str", variable has type "int")  [assignment]
Found 1 error in 1 file (checked 12 source files)
mypy exit code: 1
```

After reverting, `mypy` exits 0. A permissive config that passed regardless would be
worse than no gate, because it would advertise a guarantee it does not provide.

### The list ratchets up only

Stated in the config comment and repeated here: **never remove a module from `files` to
make CI pass.** Fix the type error instead. A gate whose scope can shrink under pressure
is not a gate.

## What it cost to get here

Twelve strict errors had to be fixed to bring these modules in. All were fixed properly —
**no `# type: ignore` was added**:

| Fix | Modules | Nature |
| --- | --- | --- |
| Validate `json.loads` returns an object instead of returning `Any` | `public_rag_findings.py`, `public_report.py` | Genuine improvement — a malformed report file now raises instead of silently returning a non-dict. |
| `sqrt(...)` instead of `... ** 0.5` in cosine similarity | `techqa_public.py`, `wixqa_public.py`, `baseline.py` | `float.__pow__` is typed `Any` in typeshed (the complex-result case). `math.sqrt` is typed `-> float`, and is faster. |
| `IncidentInputPaths` TypedDict | `incident_replay.py` | Replaced `dict[str, Path | None]`, which lost per-key precision and forced four read sites to look optional when they cannot be. |
| Annotate `score: float` | `baseline.py` | The lexical retriever's score is rebound from `int` to `float` by `_current_evidence_score`. Behavior unchanged: that function is non-negative, so the `== 0` guard still excludes exactly the unscored sections. |
| Annotate `flattened: list[dict[str, Any]]` | `wixqa_public.py` | Missing annotation. |
| Annotate `-> Scorer` | `scorers.py` | Missing return type on the scorer factory. |
| Read `bytes` into a local before decoding | `agent_runner.py` | `HTTPResponse.read()` widened to `Any`. |

None of these was a latent runtime bug. As the previous audit found and this work
confirms, the strict error count measures **annotation debt, not known brokenness** — the
value of the gate is that it stops new debt landing in the code that produces the numbers.

## What is still unchecked

All figures below were re-measured against the final state of this change set, after the
12 gated modules were fixed.

| Scope | Mode | Errors | Files |
| --- | --- | ---: | ---: |
| The 12 gated modules | `--strict` | **0** | 0 |
| `src/internal_ai_agent` (73 files) | `--strict` | 74 | 14 |
| `src` + `app` + `scripts` + `tests` (149 files) | `--strict` | 403 | 38 |

Remaining package errors, largest first — this is the ratchet order:

| Module | Errors | Note |
| --- | ---: | --- |
| `dashboard/data.py` | 41 | More than half the remaining total. Also holds most of the 41 `# type: ignore` comments in the repo, which nothing currently verifies. |
| `data/synthetic.py` | 9 | Generates the (circular) synthetic corpus. |
| `api/main.py` | 7 | FastAPI surface. |
| `extraction/service.py` | 5 | Pydantic `Literal` narrowing; runtime-validated, so low risk. |
| `observability/trace_index.py`, `evals/public_rag_reranking.py` | 2 each | |
| 8 further modules | 1 each | Mostly `no-any-return` at JSON boundaries. |

### Next steps, cheapest first

1. **`extraction/service.py` and `observability/trace_index.py`** (7 errors combined) —
   small, self-contained, and `extraction` feeds reported extraction accuracy, so it
   arguably belongs in the gate already.
2. **`data/synthetic.py`** (9) — brings corpus generation under the gate.
3. **`api/main.py`** (7) — brings the HTTP surface under the gate.
4. **`dashboard/data.py`** (41) — the big one. Worth pairing with an audit of the 41
   `# type: ignore` comments, since `strict` enables `warn_unused_ignores` and will
   flag any that are now stale.
5. **`scripts/` and `tests/`** — lowest value; a type error there cannot corrupt a
   published number, which is exactly the criterion this gate is built on.

Until those land, the accurate claim is the one at the top: strict typing is enforced on
the metric and gating core, and nowhere else.
