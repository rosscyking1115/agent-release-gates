"""Provenance fields must name tracked, reproducible inputs.

`docs/evaluation_integrity.md` Finding 6 records what happened when they did not: a
committed evidence artifact declared its input as a file under `AppData\\Local\\Temp`.
The file was gone, so the attestation could never be checked by anyone, and the string --
including an OS account name -- was published and cannot be recalled.

Stating that rule in prose is not enforcement. These tests are.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Absolute locations that are specific to one machine and therefore cannot be a
# provenance: a reader cannot re-run against them.
MACHINE_LOCAL_MARKERS = (
    "appdata/local/temp",
    "appdata\\local\\temp",
    "/private/var/folders/",
    "/var/folders/",
)

# A user-home path carrying a real account name. The redacted placeholder is allowed:
# Finding 6 quotes the offending string deliberately, with the account name removed.
_USER_PATH = re.compile(r"(?:[A-Za-z]:[\\/]+)?(?:Users|home)[\\/]+([^\\/\s\"'`|)\]]+)")
_ALLOWED_ACCOUNT_NAMES = {"<redacted>", "runner", "<user>", "user"}

_SKIP_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2"}

# Third-party corpora are quoted verbatim and must not be edited. The TechQA sample is
# real IBM support-forum text carrying six of its own authors' account names in Windows
# and POSIX home paths. They belong to those authors, not to this project, and rewriting
# them would corrupt the benchmark; they are also not provenance claims by this
# repository. The offending strings are deliberately not reproduced in this comment --
# the check below would flag them, and it is right to.
_EXCLUDED_PREFIXES = ("data/public/",)


def _tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [PROJECT_ROOT / name for name in out.split("\0") if name]


def _readable_tracked_files() -> list[Path]:
    return [
        path
        for path in _tracked_files()
        if path.suffix.lower() not in _SKIP_SUFFIXES
        and path.is_file()
        and not path.relative_to(PROJECT_ROOT).as_posix().startswith(_EXCLUDED_PREFIXES)
    ]


def test_no_committed_report_declares_a_machine_local_path() -> None:
    """No committed report artifact may point at a machine-local location.

    Scans raw text rather than parsed JSON, so `.jsonl` and `.md` artifacts are covered
    too. An earlier version globbed `reports/*.json` and silently skipped 23 `.jsonl`
    files -- including `incident_replay_runs.jsonl`, the direct sibling of the artifact
    Finding 6 is about -- while the prose claimed the whole directory was guarded.
    """
    offenders: list[str] = []
    scanned = 0
    for path in sorted((PROJECT_ROOT / "reports").rglob("*")):
        if not path.is_file() or path.suffix.lower() in _SKIP_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        lowered = text.lower()
        for marker in MACHINE_LOCAL_MARKERS:
            if marker in lowered:
                line = lowered.count("\n", 0, lowered.index(marker)) + 1
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}:{line}: {marker}")

    assert scanned > 0, "expected committed report artifacts to scan"
    assert not offenders, (
        "committed report artifacts declare machine-local paths, which cannot be "
        "provenance because no one else can re-run against them:\n  "
        + "\n  ".join(offenders)
    )


def test_public_corpus_exclusion_still_covers_only_the_upstream_samples() -> None:
    """The `data/public/` exclusion must not quietly widen.

    That directory is skipped because it holds third-party corpora containing their own
    authors' account names. If a file that is *not* an upstream sample lands there, the
    exclusion would start hiding this project's own paths.
    """
    tracked = sorted(
        p.relative_to(PROJECT_ROOT).as_posix()
        for p in _tracked_files()
        if p.relative_to(PROJECT_ROOT).as_posix().startswith("data/public/")
    )
    assert tracked == [
        "data/public/techqa_rag_eval_sample.jsonl",
        "data/public/wixqa_public_rag_sample.jsonl",
    ], (
        "tracked files under data/public/ changed; the account-name check skips this "
        f"directory, so confirm each of these is an upstream corpus: {tracked}"
    )


def test_no_tracked_file_exposes_an_account_name() -> None:
    """A user-home path in a tracked file must have its account name redacted.

    The repository is public. An account name that reaches a commit cannot be recalled
    by editing the working tree later.
    """
    offenders: list[str] = []
    for path in _readable_tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for match in _USER_PATH.finditer(text):
            account = match.group(1)
            if account.lower() in _ALLOWED_ACCOUNT_NAMES:
                continue
            line = text.count("\n", 0, match.start()) + 1
            offenders.append(f"{path.relative_to(PROJECT_ROOT)}:{line}: {match.group(0)}")

    assert not offenders, (
        "tracked files expose an OS account name in a user-home path; redact it as "
        "`<redacted>` before committing:\n  " + "\n  ".join(offenders)
    )
