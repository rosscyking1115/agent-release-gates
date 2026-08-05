"""The release path must gate, not merely build and upload.

Before `.github/workflows/publish.yml` existed, this project had no automated release
path at all: `docs/publishing.md` instructed a human to run `uv publish --token`, which
runs no tests, checks no tag, and needs a credential that should not exist. Under that
arrangement `tests/unit/test_sdist_contents.py` was a CI gate and not a release gate --
the test written to stop a packaging leak did not run on the path that publishes. That
leak is not hypothetical: `.claude/settings.local.json` reached PyPI in 0.1.1 and 0.1.2.

Three guards are pinned here, all answering "what may publish?":

1. **The suite runs before the upload**, enforced by `needs:` rather than by step
   ordering or by a status check reported elsewhere. PyPI has no un-publish, so a check
   that runs after the upload can only describe what already escaped.
2. **The tagged commit is reachable from `main`.** A tag can be created on any commit on
   any branch, and there is no tag ruleset.
3. **The CHANGELOG heading matches the release.** A PyPI description is frozen at
   upload; 0.1.4's is permanently wrong for exactly that reason.

Also pinned: the test job must not hold `id-token: write`. GitHub scopes permissions per
job, and only the publishing job needs to mint an OIDC token.

This reads the workflow rather than running it. A release gate cannot be proven by
releasing -- the behaviour is proven by breaking a test on a branch and watching the job
that `publish` depends on go red.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLISH_YML = PROJECT_ROOT / ".github" / "workflows" / "publish.yml"


def _workflow() -> dict[str, Any]:
    data = yaml.safe_load(PUBLISH_YML.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _jobs() -> dict[str, Any]:
    jobs = _workflow()["jobs"]
    assert isinstance(jobs, dict)
    # Non-vacuity: an empty or renamed job map would make every check below pass by
    # having nothing to look at.
    assert len(jobs) >= 2, f"expected a test job and a publish job, found {sorted(jobs)}"
    return jobs


def _run_steps(job: str) -> str:
    return " ".join(
        str(step.get("run", "")) for step in _jobs()[job]["steps"] if isinstance(step, dict)
    )


def test_the_workflow_still_triggers_only_on_a_published_release() -> None:
    """If the trigger changes, the guards below may no longer be on the path.

    A tag push in particular must not publish: a pushed tag stays reversible only for
    as long as nothing watches for it.
    """
    # PyYAML parses the bare key `on` as the boolean True.
    triggers = _workflow()[True]
    assert set(triggers) == {"release"}, f"unexpected publish triggers: {sorted(triggers)}"
    assert triggers["release"]["types"] == ["published"]


def test_publish_depends_on_the_test_job() -> None:
    """The gate. Ordering must be structural -- `needs:`, not step order."""
    jobs = _jobs()
    needs = jobs["publish"].get("needs")
    needs = [needs] if isinstance(needs, str) else (needs or [])
    assert "test" in needs, (
        "the publish job does not declare `needs: test`, so the upload does not depend "
        "on the suite passing. PyPI has no un-publish."
    )
    assert "test" in jobs, "`needs: test` names a job that does not exist"


def test_the_gating_job_actually_runs_the_suite() -> None:
    """`needs:` on a job that checks nothing is a gate satisfied by absence.

    The commands asserted here are the three `ci.yml` enforces. `ruff format --check` is
    deliberately not among them: this repository does not enforce it and 66 files do not
    satisfy it, so requiring it would be a release gate that fails on a clean tree.
    Asserting a bar the project does not hold would make this test a fiction rather than
    a control.
    """
    run_steps = _run_steps("test")
    for command in ("ruff check", "mypy", "pytest"):
        assert command in run_steps, f"the test job never runs {command!r}"


def test_the_gating_job_verifies_the_changelog_heading() -> None:
    """The heading is frozen on PyPI at upload, so it is checked before the upload."""
    run_steps = _run_steps("test")
    assert "check_release_heading.py" in run_steps, (
        "the gate job does not verify the CHANGELOG heading. A PyPI description is "
        "frozen at upload and a released version cannot be re-uploaded."
    )
    assert "--published-at" in run_steps, (
        "the heading check is invoked without the release's own timestamp, so it would "
        "fall back to nothing and could not compare a date at all."
    )


def test_the_tagged_commit_must_be_reachable_from_main() -> None:
    """Closes the second hole: tested-but-unreviewed code reaching PyPI."""
    run_steps = _run_steps("publish")
    assert "merge-base --is-ancestor" in run_steps, (
        "the publish job does not verify the tagged commit is an ancestor of main. A "
        "tag can be created on any commit on any branch."
    )
    assert "origin/main" in run_steps, "the ancestor check names no branch to compare against"


def _step_index(steps: list[Any], needle: str) -> int:
    """Return the position of the first step whose name *or* action mentions ``needle``.

    Both fields are searched on purpose: the upload step carries a `name:` as well as a
    `uses:`, so looking at only one of them silently finds nothing -- and a lookup that
    finds nothing is not a passing check, it is no check.
    """
    for index, step in enumerate(steps):
        haystack = f"{step.get('name', '')} {step.get('uses', '')}"
        if needle in haystack:
            return index
    raise AssertionError(f"no step in the publish job mentions {needle!r}")


def test_both_verifications_precede_the_upload() -> None:
    """A check that runs after the upload describes what already escaped."""
    steps = _jobs()["publish"]["steps"]
    upload = _step_index(steps, "pypi-publish")
    for label in ("Verify the tag matches the package version", "Verify the tagged commit is on"):
        index = _step_index(steps, label)
        assert index < upload, f"{label!r} runs at step {index}, after the upload at step {upload}"


def test_the_build_happens_after_both_verifications() -> None:
    """A rejected release should cost nothing and must not half-happen."""
    steps = _jobs()["publish"]["steps"]
    build = _step_index(steps, "Build sdist")
    for label in ("Verify the tag matches the package version", "Verify the tagged commit is on"):
        assert _step_index(steps, label) < build


def test_the_version_check_survives() -> None:
    """Weak, but not wrong, and it catches a mistake the others do not."""
    assert 'test "$PKG" = "$TAG"' in _run_steps("publish")


def test_only_the_publish_job_may_mint_a_publishing_token() -> None:
    """Least privilege, per job.

    `id-token: write` is what Trusted Publishing needs. A test job holding it is a wider
    blast radius for no benefit, and it stays invisible until someone looks -- which is
    what this test is for.
    """
    workflow = _workflow()
    assert "permissions" not in workflow, (
        "workflow-level permissions apply to every job. Scope them per job so the test "
        "job cannot inherit a publishing credential."
    )
    for name, job in _jobs().items():
        permissions = job.get("permissions")
        assert permissions is not None, f"job {name!r} declares no permissions block"
        if name == "publish":
            assert permissions.get("id-token") == "write", "publish cannot use Trusted Publishing"
        else:
            assert "id-token" not in permissions, (
                f"job {name!r} holds id-token and does not publish"
            )


def test_no_credential_is_referenced_anywhere_in_the_workflow() -> None:
    """Trusted Publishing means no token exists. Nothing here may reach for one."""
    raw = PUBLISH_YML.read_text(encoding="utf-8")
    assert "secrets." not in raw, (
        "the publish workflow references a repository secret. This project publishes "
        "over OIDC and no PyPI token exists for it; none should be created."
    )
    assert "password:" not in raw
    assert "TWINE_" not in raw


def test_third_party_actions_are_pinned_to_a_commit_sha() -> None:
    """A moving tag is a supply-chain hole: `@v6` can be repointed by its owner."""
    unpinned: list[str] = []
    for job_name, job in _jobs().items():
        for step in job["steps"]:
            uses = step.get("uses")
            if not uses:
                continue
            ref = uses.split("@", 1)[1] if "@" in uses else ""
            if len(ref) != 40 or not all(character in "0123456789abcdef" for character in ref):
                unpinned.append(f"{job_name}: {uses}")
    assert unpinned == [], f"actions not pinned to a full commit SHA: {unpinned}"
