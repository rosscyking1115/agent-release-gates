from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.multi_model_comparison import (
    write_multi_model_comparison_plan,
)


def main() -> None:
    plan = write_multi_model_comparison_plan(Path.cwd())
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
