from __future__ import annotations

# Thin shim: the implementation lives in the installable package so it can be
# wired to the `agent-safety` console entry point. This script remains for
# `python scripts/agent_safety.py` usage and is re-exported for direct loading.
from internal_ai_agent.cli import (
    main,
    run_release_gate,
)

__all__ = ["main", "run_release_gate"]


if __name__ == "__main__":
    main()
