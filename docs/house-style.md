# House style

The documentation standard for these repositories. This repo is the reference
implementation; the others are checked against it.

The reason it exists: without a written standard every repository guesses, and guesses
diverge. Public repositories by one author are read together, so inconsistency between
them is more visible to an outside reader than any individual choice would be.

## 1. README section order

**A README is a decision aid, not documentation.** Its job is to let a reader decide
within about thirty seconds whether to spend more time, and if yes, to get them working.

Answer the reader's questions in this order. Never present a later item before the
earlier ones are satisfied.

| # | The reader asks | What answers it |
| --- | --- | --- |
| 1 | What is this? | One sentence, no jargon, legible to a technical person outside the field |
| 2 | Who is it for? | One or two sentences naming the audience and the problem |
| 3 | Does it work — show me | One image, or one command with its output. Above the fold |
| 4 | What state is it in? | Active / concluded / experimental / archived, and what is *not* claimed |
| 5 | How do I start? | One install line, one usage line, both copy-pasteable |
| 6 | Anything deeper | **A link.** Not inline prose |

Items 1–5 fit in roughly one screen. **If a reader must scroll to learn what the project
is, the order is inverted.**

### By project type

The order is fixed; what fills each slot is not.

- **Research repository** — the output is a finding. **Do not lead with the finding.** A
  finding stated in the project's own vocabulary is illegible to someone who does not yet
  know what the project studies, and leading with it makes the reader feel stupid.
  Lead with the *question*: a question is legible to anyone, an answer only to someone
  already holding the question. Then: answer in one line, figure, status, what it's for,
  how it was reached, why it is trustworthy, reproduce, contents.
- **Library or tool** — installation and one real working example are the point. Never
  document the API in the README; link it.
- **Application or service** — a screenshot belongs immediately after the title, before
  any prose.
- **Data project** — provenance, licence *of the data*, coverage and reproduction.

### Length

Roughly **1,200 words**. Past that, identify what should become a linked document rather
than trimming sentences. Nothing worth having needs deleting; it needs relocating.

Sections that almost never belong in a README: full API or CLI reference, long
changelogs, extended results tables, architecture deep-dives, roadmaps beyond three
bullets, and defensive disclaimers about what the project is *not*.

**On disclaimers:** opening by denying something nobody asked about makes a suspicious
reader out of an incurious one. If one is genuinely required, put it where it is needed —
the bottom, or the page it applies to.

### Numbers

**A number in a README carries its meaning or it does not appear.** A bare `100.00%`
means nothing to a newcomer and reads as a red flag to a specialist. Either say what
produces it, in the same breath, or move it to a linked results document.

## 2. Docstrings

**Google style.** Recorded in `pyproject.toml` so the linter and any doc generator agree:

```toml
[tool.ruff.lint.pydocstyle]
convention = "google"
```

Chosen because it is compact and readable for short functions, which is what these
codebases mostly contain. NumPy style suits parameter-heavy scientific code; that is not
the shape of this work. The choice matters less than applying it everywhere.

### What to document, in priority order

Full coverage is not the goal. Document in this order and stop when the return falls off:

1. The public surface — anything a user imports, calls, or runs.
2. Anything with a non-obvious contract — units, ranges, what happens on empty input,
   whether arguments are mutated.
3. Anything whose name could mislead. A `make_tool_decision` that also *executes* the
   tool needs a docstring saying so.
4. Module docstrings for every module a reader might open first.
5. Private helpers — only where the logic is not self-evident.

**A docstring written to satisfy a linter is worse than none.** It costs maintenance and
teaches readers that docstrings here are noise. Accordingly `D1` (missing-docstring) is
**not** enabled in these repositories; `D2` and `D4` are, so every docstring that does
exist is well formed.

### Comments versus docstrings

They answer different questions for different readers. A **comment** explains *why*, to
someone changing the code. A **docstring** explains *what and how to use it*, to someone
calling it. A comment that restates the code is worse than no comment. Never leave
commented-out code.

The highest-value comments record a decision invisible in the code: why a threshold has
that value, why the obvious approach was rejected, what breaks if a line is removed.

## 3. Badges

Same set, same order, every repository:

**PyPI version · Python versions · Licence · CI status**

Then a DOI badge if one exists. Nothing else. Coverage badges without context,
dependency counts and download counts on a small project all invite a comparison that
does not flatter, and a low number displayed prominently is worse than no badge.

Badges go **after** the opening sentences, not before them. The first thing a reader sees
should be words that tell them what the project is.

## 4. The status statement

Every repository states its state explicitly, in a blockquote, **immediately after the
figure or screenshot** — before "what this is for", and never buried at the bottom.

Purpose and status are the two rarest things in READMEs, which makes stating them cheap
differentiation.

```markdown
> **Status: concluded, not maintained.** A reference implementation and a research
> result, not a product. There is no roadmap and no support commitment.
> Released under the [MIT Licence](https://github.com/owner/repo/blob/main/LICENSE).
```

Say what is *not* claimed as well as what is.

## 5. Licence

A **file**, not a mention. `LICENSE` at the repository root, no extension, containing the
full licence text. A README that says "MIT" without the file is rejected by JOSS review
and is the single cheapest thing to get right.

The licence badge links to that file by **absolute URL**, for the reason in §7 — a
relative link resolves on GitHub and silently breaks on the package index.

## 6. Corrections

**Correct in place; never quietly rewrite.** If a published claim was wrong, say so in
the README and record it in `CHANGELOG.md` as a correction rather than a tidy-up.

A visible retraction reads as trustworthy. A silent edit reads as nothing at all, until
somebody finds the diff — and then it reads as concealment.

This applies to published artifacts too. A release deleted from a package index leaves a
version gap; a gap with an explanation is better than a gap without one.

## 7. Links, on PyPI

A README that ships as a package's long description is rendered on the package index,
where **no relative link resolves** — not to a document, not to a directory, and not to
`LICENSE`. The index serves the rendered description, not a browsable copy of the source
tree, so a relative path has nothing to resolve against.

Use absolute URLs for **every** link in a README that doubles as a package description,
including the licence badge. GitHub resolves absolute links perfectly well, so there is no
cost to making them all absolute and no reliable way to make a relative one work in both
places.

## Applying this elsewhere

When bringing another repository to this standard, audit before editing:

1. **Cover test.** Hide everything below the first screen. Can a non-specialist say what
   this is and who it is for? If not, nothing else matters until that is fixed.
2. **Jargon sweep.** List every term in the first three paragraphs a newcomer would have
   to look up.
3. **Order.** Map each section to the ladder above. Note anything appearing early.
4. **Type mix.** A README that contains a tutorial, an API reference and a results
   discussion is three documents wearing one hat, and reads as a mess because it is one.
5. **Length.** Count words. Over ~1,200, decide what becomes a link.
6. **Claim check.** Does every number still trace to something in the repository?
7. **Command check.** Run every command shown, from a clean checkout. A command that
   only works from a clone must not appear under `pip install`.
