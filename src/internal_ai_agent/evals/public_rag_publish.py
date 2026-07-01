"""Shared helper for the published public-RAG provider-embedding result.

Kept dependency-light (no eval imports) so both the public track modules and the
provider-embedding eval can use it without a circular import.
"""

from __future__ import annotations

import json
from pathlib import Path

PUBLISHED_PATH = "reports/public_rag_provider_embedding_published_result.json"


def published_tracks(project_root: Path) -> set[str]:
    """Return the set of public tracks with a committed, reviewed provider result."""
    path = project_root / PUBLISHED_PATH
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    if data.get("status") != "published":
        return set()
    return {
        track
        for track, block in data.get("tracks", {}).items()
        if isinstance(block, dict) and block.get("status") == "evaluated"
    }
