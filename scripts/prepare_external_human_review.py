from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.external_review import prepare_external_human_review


def main() -> None:
    report = prepare_external_human_review(Path.cwd())
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
