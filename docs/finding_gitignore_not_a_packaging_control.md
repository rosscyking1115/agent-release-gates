# A global gitignore is not a packaging control

*Files your build backend publishes cannot be protected by an ignore file it never reads.
2026-08-02.*

---

## Summary

Many developers keep a **global** gitignore — `core.excludesFile`, usually
`~/.gitignore_global` — and use it as a safety net for things that should never be
committed anywhere: `.env`, private keys, `credentials.json`, `service-account.json`,
`.netrc`, and per-tool local state like `.claude/` or agent caches.

It works for git. It does not work for packaging.

- **`git status` is clean, so the files look handled.** They are invisible in the working
  tree, invisible in review, invisible in CI.
- **A source distribution is built from the directory, not from the git index.** Hatchling
  — the backend used here — reads `.gitignore` files it finds *inside the project* and
  has no knowledge of `core.excludesFile`. Anything the global file hides is packaged.
- **Uploads are permanent.** Deleting a release from PyPI removes the download; it does
  not recall what was already fetched or mirrored.

This has already happened in this account, in a small way, and the mechanism that would
allow a much worse version of it is currently live in two more repositories.

## What happened

`agent-release-gates` 0.1.1 and 0.1.2 shipped `.claude/settings.local.json` inside their
source distributions. The file contains machine paths and the directory name of an
unrelated local project. It was never committed — `git status` never showed it, because
`.claude/` is covered by the global gitignore — and it was published twice.

Building 0.1.3 additionally swept in a local knowledge-graph cache directory, roughly a
megabyte of absolute filesystem paths. That one was caught **before** upload, by
inspecting the built artifact rather than the source. It was never published.

The two affected releases were deleted from PyPI on 2026-08-02. Deletion is the right
action and it is not a recall.

Nothing sensitive escaped. The point is not the severity of what leaked; it is that
**nothing stopped it**, and that the same mechanism sits in front of files where the
severity would be different.

## A second instance, arrived at by a different route

The same mistake surfaced again in this repository, in testing rather than packaging,
and it is worth recording because it was reached independently.

A test was written to verify that the project site carried a particular panel. It read
`public/index.html` from the working tree. But `public/` is gitignored and CI builds it
*after* the test suite runs, so the file exists on a developer's machine — left over from
an earlier local build — and does not exist in CI at all. The test therefore passed
against a stale artifact locally and asserted nothing whatsoever in the pipeline that
matters. It was exposed by running the suite in a fresh clone, where the file it depended
on was simply absent. The fix was to have the test build the site into a temporary
directory and assert against what that produced.

The shape is identical to the packaging defect above:

| | The repository | The artifact |
| --- | --- | --- |
| Packaging | `git status` is clean | the sdist contains the file anyway |
| Testing | `public/index.html` is present | the build output does not exist yet |

Both are the same error. **The repository is not the artifact.** A control that inspects
the source cannot see what the build produced, and a check that reads a build output it
did not produce is measuring a leftover.

> **A test that reads a build output verifies nothing unless it builds that output
> itself.**

Two independently-reached instances is the reason this is written down as a class rather
than as an anecdote.

## The audit

Every published sdist from this account, listed and inspected on 2026-08-02.

| Package | Live versions inspected | sdist file selection | Local-only directories packaged | Secret-pattern files |
| --- | --- | --- | --- | --- |
| `telemeval` | 8 (0.1.0 – 0.3.3) | **none declared** | none | none |
| `redteam-foundry` | 3 (0.2.0 – 0.3.0) | **none declared** | none | `.env.example` only — a tracked template, correct to publish |
| `agent-release-gates` | 0.1.0 | none declared *(at the time)* | none | none |
| `agent-release-gates` | 0.1.1, 0.1.2 | none declared | **`.claude/`** | none |

**No secret ever reached PyPI.** The `.env.example` match in `redteam-foundry` is a
deliberate 725-byte configuration template, tracked in git and correct to ship; it is
listed here only because a pattern scan flags it and a reader should know it was checked
rather than missed.

The finding is the third column. **None of the three projects declared any sdist file
selection.** Two escaped only because the local-only directories did not exist in the tree
when their releases were built.

They exist now. `redteam-foundry` currently has both `.claude/` and a graph cache in its
working tree; `telemeval` has the graph cache. **On their next release, with no code
change and no visible warning, both would package them.** The mechanism is armed in both.

## Why it stays invisible

Every control that would normally catch this is looking somewhere else.

| Control | Why it does not see the problem |
| --- | --- |
| `git status` | The file is ignored. That is the whole point of the ignore. |
| Code review | Reviewers read diffs. There is no diff. |
| CI | Runs tests against the repository, not against the artifact. |
| `.gitignore` in the repo | Does not list these paths — the *global* file does. |
| The build log | Reports success. It has no opinion about contents. |

The only place the problem is visible is inside the built artifact, which is exactly the
thing nobody opens.

## The severity that has not been reached

The global gitignore on this machine covers `.env` and variants, `*.pem`, `*.key`,
`*.pfx`, `*.p12`, `*.keystore`, `*.jks`, `*.ppk`, `id_rsa`, `id_dsa`, `id_ecdsa`,
`credentials.json`, `service-account.json`, `gcp-key.json`, `aws-credentials` and
`.netrc`.

Those patterns exist because a developer decided those files must never be committed. The
same decision does nothing about publication. A `.env` sitting in a working tree during a
release — the ordinary case, since that is where it has to be for the code to run — would
be packaged into the sdist and uploaded, and would then be permanent.

That has not happened here. It is one file in one directory away from happening, in any
project set up this way.

## Check your own

Two minutes, and it works on any published package:

```bash
pip download --no-deps --no-binary :all: YOUR_PACKAGE -d /tmp/check
```

```bash
tar tzf /tmp/check/*.tar.gz | grep -Ei '\.env|\.claude|\.agents|\.codex|\.pem$|\.key$|id_rsa|credentials\.json|service-account|\.netrc|graphify-out'
```

Before publishing, check the artifact rather than the source — the source is what you
already believe is clean:

```bash
rm -rf dist && python -m build && tar tzf dist/*.tar.gz | sed 's|^[^/]*/||' | sort
```

Reading the list once is worth more than trusting any ignore file.

## The fix: an allowlist, not an exclude list

An exclude list only stops what you thought to name. It fails open: a new local directory
appears and is published, silently, because nobody added it to the list.

An allowlist fails closed. Anything unfamiliar is absent from the sdist until someone adds
it deliberately.

```toml
[tool.hatch.build.targets.sdist]
include = [
  "/src",
  "/tests",
  "/docs",
  "/README.md",
  "/LICENSE",
  "/pyproject.toml",
]
```

Then enforce it, because a configuration nobody checks is a configuration that drifts.
This repository pins three properties in
[`tests/unit/test_sdist_contents.py`](../tests/unit/test_sdist_contents.py):

1. **The selection stays an allowlist.** Deleting it silently restores the old behavior,
   which is the regression that caused the leak.
2. **No entry names a known local-only directory.**
3. **Every entry matches at least one git-tracked file.** This is the check that stops the
   *class* rather than the instances: every local-only file is untracked by construction,
   so no such path can be added to the allowlist without the build failing first.

The third test is the one worth copying. It does not need to know what your local tooling
is called.

## A caveat on "build backends"

The precise claim, verified empirically on this machine rather than assumed:

**Hatchling** builds the sdist by walking the project directory and applying `.gitignore`
files found *within the project*. It does not shell out to git and does not consult
`core.excludesFile`, so globally-ignored files are included. That is what produced the
result above.

Backends that derive the file list from the VCS itself — anything built on `git ls-files`,
such as `setuptools-scm` — see only tracked files, so a globally-ignored file is excluded
for free. If you use one of those, this specific failure does not apply.

So: **do not generalize the mechanism, generalize the habit.** Open your artifact and read
the file list before you upload it. Whichever backend you use, that check is the one that
would have caught this.

## Related

This is the same defect class as
[Finding 6 in this project's evaluation integrity note](evaluation_integrity.md#finding-6-a-committed-verdict-whose-declared-input-did-not-exist),
in a different channel: a machine-local path reached a published artifact because the
control that appeared to be working was not the control the pipeline consulted. There it
was a provenance field; here it is an ignore file. The remedy was the same both times —
make the check mechanical, and put it in front of the thing being published rather than
behind it.
