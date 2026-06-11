from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.memory_context_intervention import (
    write_memory_context_intervention,
)


def main() -> None:
    report = write_memory_context_intervention(Path.cwd())
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
