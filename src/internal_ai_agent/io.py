"""Reading and writing the JSON and JSONL artifacts under ``reports/`` and ``data/``.

Every writer creates parent directories and writes UTF-8. Note that these use Python's
default newline translation, so generated artifacts carry the platform's line endings:
regenerating reports on Windows produces a diff against artifacts committed from Linux
even when no content changed. See docs/finding_gitignore_not_a_packaging_control.md for
the related class of build-time surprise.
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

    Keys are sorted and the output is indented, so regenerating an unchanged artifact
    produces no diff and a real change is legible in review.

    Args:
        path: Destination. Overwritten if it exists.
        payload: Object to serialise.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    """Write objects as JSONL, one per line, creating parent directories as needed.

    Keys are sorted for the same reason as ``write_json``.

    Args:
        path: Destination. Overwritten if it exists.
        rows: Objects to serialise. Consumed once, so a generator is fine.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, sort_keys=True) + "\n")
