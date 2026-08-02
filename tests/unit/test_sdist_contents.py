"""The sdist allowlist must stay an allowlist, and may only name tracked paths.

Until 0.1.3 this project had no sdist file selection at all, so hatchling packaged the
working tree minus the *repository's* `.gitignore`. Ignores that live in a contributor's
global gitignore are invisible both to `git status` and to the build backend, so
local-only files were packaged and uploaded: `.claude/settings.local.json` reached PyPI
in 0.1.1 and 0.1.2 carrying machine paths and an unrelated local project name, and the
0.1.3 build additionally picked up a 1 MB local knowledge-graph cache full of absolute
paths before it was caught pre-upload.

PyPI releases cannot be unpublished, so the control has to fail closed. Two properties
are pinned here:

1. **The selection stays an allowlist.** Deleting it silently restores the old behavior,
   which is the exact regression that caused the leak.
2. **Every entry names something git tracks.** An untracked path -- which is what every
   local-only file is -- cannot be added to the allowlist without this failing first.

This does not build the sdist; it constrains what the sdist may be told to include.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Directory names that are local-only for at least one contributor and must never be
# named in the allowlist, whatever a future edit thinks.
LOCAL_ONLY_MARKERS = (
    ".claude",
    ".agents",
    "graphify-out",
    ".venv",
    "logs",
    "dist",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
)


def _sdist_include() -> list[str]:
    config = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    sdist = config["tool"]["hatch"]["build"]["targets"]["sdist"]
    include = sdist["include"]
    assert isinstance(include, list)
    return [str(entry) for entry in include]


def _tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def test_sdist_selection_is_an_allowlist() -> None:
    include = _sdist_include()
    assert include, (
        "The sdist include allowlist is empty. Without it hatchling packages the whole "
        "working tree minus the repository .gitignore, which is how local-only files "
        "reached PyPI in 0.1.1 and 0.1.2."
    )


def test_allowlist_names_no_local_only_directory() -> None:
    for entry in _sdist_include():
        parts = entry.strip("/").split("/")
        for marker in LOCAL_ONLY_MARKERS:
            assert marker not in parts, (
                f"sdist allowlist entry {entry!r} names {marker!r}, which is local-only "
                "for at least one contributor and must not be published."
            )


def test_every_allowlist_entry_is_tracked_by_git() -> None:
    """An untracked path cannot enter the sdist allowlist.

    Every local-only file is untracked by construction, so this is the check that stops
    the original defect rather than merely naming the directories it happened to involve.
    """
    tracked = _tracked_paths()
    for entry in _sdist_include():
        rel = entry.strip("/")
        matched = rel in tracked or any(path.startswith(f"{rel}/") for path in tracked)
        assert matched, (
            f"sdist allowlist entry {entry!r} matches no git-tracked file. Either it is "
            "stale, or it names something untracked -- which must never be packaged."
        )
