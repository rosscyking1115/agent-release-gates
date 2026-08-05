"""The version half of the CHANGELOG heading check, asserted at pull-request time.

`publish.yml` verifies both halves of the top-most versioned heading -- version and date
-- before anything is built. The date half can only be checked against a release that
does not exist yet, so it stays in the workflow. The version half can be checked here,
which means a bump that forgets the heading goes red on the pull request rather than at
the release, when the tag is already pushed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT_ROOT / "scripts" / "check_release_heading.py"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from check_release_heading import (  # noqa: E402
    declared_version,
    problems,
    published_date,
    top_heading,
)


def _changelog() -> str:
    return (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


def test_the_top_versioned_heading_matches_the_declared_version() -> None:
    heading_version, _ = top_heading(_changelog())

    assert heading_version == declared_version(), (
        "CHANGELOG.md's top-most versioned heading does not match the version in "
        "pyproject.toml. Bump both, or the release notes describe a different version "
        "than the one published."
    )


def test_a_changelog_without_a_versioned_heading_is_an_error_not_a_pass() -> None:
    # The failure mode this guards is a gate satisfied by absence: no heading found,
    # nothing to compare, everything green.
    with pytest.raises(ValueError, match="no versioned heading"):
        top_heading("# Changelog\n\n## [Unreleased]\n\n- something\n")


def test_the_heading_pattern_accepts_both_separators_in_use() -> None:
    # This repository uses a plain hyphen; the sibling repository the checker came from
    # uses an em dash. A shared script that silently matched neither would find no
    # heading and fail closed, but one that matched only one would be worse: it would
    # fail on a correct file.
    assert top_heading("## [1.2.3] - 2026-01-02\n") == ("1.2.3", "2026-01-02")
    assert top_heading("## [1.2.3] — 2026-01-02\n") == ("1.2.3", "2026-01-02")


def test_published_date_is_normalised_to_utc() -> None:
    # A release published just before midnight in one zone must not stamp the next day.
    assert published_date("2026-08-05T00:15:23Z") == "2026-08-05"
    assert published_date("2026-08-05T00:15:23+00:00") == "2026-08-05"
    assert published_date("2026-08-04T23:30:00-02:00") == "2026-08-05"


def test_problems_names_both_fields_and_both_values() -> None:
    found = problems(
        heading_version="0.1.4", heading_date="2026-08-02", version="0.1.5", date="2026-08-05"
    )

    assert len(found) == 2
    assert any("VERSION mismatch" in line and "0.1.4" in line and "0.1.5" in line for line in found)
    assert any(
        "DATE mismatch" in line and "2026-08-02" in line and "2026-08-05" in line for line in found
    )


def test_problems_is_empty_when_the_heading_agrees() -> None:
    assert (
        problems(
            heading_version="0.1.5", heading_date="2026-08-05", version="0.1.5", date="2026-08-05"
        )
        == []
    )


def test_the_checker_exits_non_zero_on_a_mismatched_date() -> None:
    # End to end through the real entry point, by exit status. A date that cannot match
    # is used deliberately: whatever the CHANGELOG says today, it does not say 1999.
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--published-at", "1999-01-01T00:00:00Z"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert b"DATE mismatch" in result.stdout
