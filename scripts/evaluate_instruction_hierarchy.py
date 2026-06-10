from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.intervention_study import (
    write_instruction_hierarchy_intervention,
)


def main() -> None:
    report = write_instruction_hierarchy_intervention(Path.cwd())
    print(
        "Instruction hierarchy intervention complete: "
        f"{report['case_count']} cases, {len(report['variants'])} variants"
    )


if __name__ == "__main__":
    main()
