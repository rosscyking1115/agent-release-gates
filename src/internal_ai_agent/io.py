"""Reading and writing the JSON and JSONL artifacts under ``reports/`` and ``data/``.

Every writer creates parent directories, writes UTF-8, and pins ``newline="\\n"``.

The pin is load-bearing. These writers previously used Python's default newline
translation, so an artifact regenerated on Windows came back with CRLF line endings
against the LF committed from Linux, and a six-line change arrived in review as a
two-thousand-line diff. ``write_json`` claimed in its own docstring that regenerating
an unchanged artifact produced no diff; on Windows that was false, and this module's
docstring separately recorded the defect while the function's kept asserting the
opposite. ``tests/unit/test_artifact_determinism.py`` now enforces the claim rather
than restating it.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file into a list of objects.

    Args:
        path: File to read. Must exist; this does not tolerate a missing file.

    Returns:
        One object per non-blank line, in file order.

    Raises:
        json.JSONDecodeError: If any non-blank line is not valid JSON.
    """
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write one JSON object, creating parent directories as needed.

    Keys are sorted, the output is indented, and newlines are pinned to ``\\n`` on every
    platform, so regenerating an unchanged artifact produces no diff and a real change
    is legible in review.

    Args:
        path: Destination. Overwritten if it exists.
        payload: Object to serialise.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    """Write objects as JSONL, one per line, creating parent directories as needed.

    Keys are sorted and newlines are pinned for the same reasons as ``write_json``.

    Args:
        path: Destination. Overwritten if it exists.
        rows: Objects to serialise. Consumed once, so a generator is fine.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for row in rows:
            file.write(json.dumps(row, sort_keys=True) + "\n")
