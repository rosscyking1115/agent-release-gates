# Publishing to PyPI

The package builds a lean core (`pip install agent-release-gates` pulls only
`pydantic` and gives you the `agent-safety` CLI, the Inspect suite, the real-agent
runner, and the scoring logic). The API and dashboard are opt-in extras.

## There is no token, and none should be created

Publication is [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) over
OIDC. `.github/workflows/publish.yml` mints a short-lived credential at run time, and
**no PyPI API token exists for this project anywhere.**

Earlier versions of this document ended with `uv publish --token <pypi-token>`. That
described a mechanism this project does not use and would send whoever followed it
looking for a secret that must not exist. It also bypassed every guard below, because
the checks live in the workflow: a local upload runs none of them.

**Do not run `twine` or `uv publish`. Do not create a PyPI API token.**

### One-time setup, on the PyPI website

1. Go to <https://pypi.org/manage/project/agent-release-gates/settings/publishing/>.
2. Add a **new trusted publisher** → GitHub, with:
   - **Owner:** `rosscyking1115`
   - **Repository:** `agent-release-gates`
   - **Workflow name:** `publish.yml`
   - **Environment:** *(leave blank)*
3. Save. From then on, publishing a GitHub release runs the workflow and uploads.

If the upload step fails saying no trusted publisher is configured, this step has not
been done. Nothing is published when that happens; it is safe. Do not fall back to a
token.

## What the workflow refuses to publish

Three things must hold, and all three are checked *before* the build, so a rejected
release costs nothing and cannot half-happen. PyPI has no un-publish, so every check
runs ahead of the upload rather than after it.

| Guard | Refuses |
| --- | --- |
| `publish` declares `needs: test` | a release whose lint, typecheck or test suite fails |
| `git merge-base --is-ancestor` against `main` | a tag on a commit not reachable from `main` |
| `scripts/check_release_heading.py` | a CHANGELOG heading whose version or date disagrees with the release |
| `test "$PKG" = "$TAG"` | a tag name that disagrees with the package version |

The last is the weakest: it establishes that two things agree about a number, not that
the code works. It is kept because it catches a mistake the others do not.

**The `needs:` edge is the one that matters here.** `tests/unit/test_sdist_contents.py`
exists because `.claude/settings.local.json` reached PyPI in 0.1.1 and 0.1.2 — the sdist
build ignores a global gitignore and nothing caught it. Before this workflow existed
there was no automated release path at all, so that test was a CI gate and not a release
gate: it did not run on the path that publishes.

`tests/unit/test_release_gate.py` pins the structure — the trigger, the `needs:` edge,
the per-job permissions, the ordering of the guards against the build, the SHA pinning,
and the absence of any credential reference. A release gate cannot be proven by
releasing.

The workflow **rebuilds from the tag**; it does not upload anything built locally.
Anything verified by hand before a release is verified against the same source tree, not
against the same bytes.

## 1. Pre-flight

- [ ] `main` is green in CI.
- [ ] Working tree clean; you are on `main` and up to date.
- [ ] `uv run ruff check .`, `uv run mypy`, `uv run pytest` all pass by exit status.

> `ruff format --check` is **not** a gate in this project — neither in `ci.yml` nor in
> the release workflow — and 66 files do not currently satisfy it. Adding it to either
> would be a check that fails on a clean tree. Reformatting is a separate change.

## 2. Version and changelog

- [ ] Bump `version` in `pyproject.toml`. **That is the only place it is declared.**
      `src/internal_ai_agent/__init__.py` reads the installed distribution metadata and
      the API takes its OpenAPI version from that, so there is no second copy to keep in
      step. **Do not add one.** There were two until 0.1.5, synchronised by hand and
      checked by nothing, and one had already drifted: the API served `0.1.0` from 0.1.1
      through 0.1.4. `tests/unit/test_version.py` now asserts every surface agrees and
      fails if a literal is reintroduced anywhere under `src/`.
- [ ] After bumping, **reinstall** (`uv sync`) before running the suite locally: the
      installed metadata still carries the old number until you do, and
      `tests/unit/test_version.py` will fail on the mismatch. That is the test working.
- [ ] Move the `CHANGELOG.md` `[Unreleased]` notes under a new `[X.Y.Z]` heading with
      the date, and update the compare links at the bottom.
- [ ] Follow SemVer: patch = fixes, minor = additive features, major = breaking.

> **The heading is checked for you — you are not the guard.** `publish.yml` runs
> `scripts/check_release_heading.py` before anything is built, asserting that the
> top-most versioned heading's **version** matches `pyproject.toml` and its **date**
> matches the release's own `published_at` timestamp in UTC. If the notes were prepared
> on one day and released on another, the release fails and prints both values rather
> than publishing a wrong date and leaving you to notice.
>
> The version half is additionally asserted in `tests/unit/test_release_heading.py`, so
> a bump that forgets the heading goes red on the pull request rather than at the
> release, when the tag is already pushed.

## 3. Build — locally, to inspect only

The workflow rebuilds from the tag and uploads what *it* built, so nothing built here is
ever published. Build locally to look at the artifact:

```bash
uv build
```

`tests/unit/test_sdist_contents.py` already builds the sdist in process and asserts its
selection is an allowlist of git-tracked paths, so the packaging check is part of the
suite rather than a manual step.

## 4. Tag, then release — and know which one is the point of no return

**Pushing the tag publishes nothing.** No workflow watches tag pushes: `ci.yml` triggers
on `pull_request` and on `push` to `main`; `publish.yml` triggers on
`release: types: [published]`. A pushed tag is therefore still reversible
(`git push --delete origin vX.Y.Z`).

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

- [ ] **Publishing the GitHub release is the irreversible step.** It fires
      `publish.yml`, which runs the gate, then builds from the tag and uploads.
      **PyPI has no un-publish**: a version can be yanked, which hides it from
      resolvers, but the files and the version number are permanent and cannot be
      reused. Everything before this point can be undone; nothing after it can.
- [ ] Create the GitHub release from the tag and paste the `CHANGELOG.md` section.

## 5. Smoke the published package, from outside the repository

CI green on the source says nothing about the wheel. Install from PyPI in a throwaway
environment in a temporary directory **outside this checkout** — a source tree on the
path is how a broken package passes its own check.

```bash
pip install agent-release-gates
agent-safety release-gate
```

## Install matrix

```bash
pip install agent-release-gates                # CLI + Inspect suite + scoring
pip install "agent-release-gates[api]"         # + FastAPI evidence service
pip install "agent-release-gates[dashboard]"   # + Streamlit dashboard deps
pip install agent-release-gates inspect_ai     # to run under Inspect
```

## Notes

- `dist/` is build output — do not commit it.
- `inspect_ai` is an optional **peer** dependency, not a declared one, so Inspect users
  run `pip install agent-release-gates inspect_ai`.
- The README **is** the PyPI description, and PyPI freezes it at upload. A released
  version cannot be re-uploaded or edited, so the README must be final *before* the tag.
  0.1.4's description permanently describes a figure that has since been replaced; see
  the `CHANGELOG.md` entry recording it.
