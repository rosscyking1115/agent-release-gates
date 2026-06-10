from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.rag_grounding_intervention import (
    write_rag_grounding_intervention,
)


def main() -> None:
    report = write_rag_grounding_intervention(Path.cwd())
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
