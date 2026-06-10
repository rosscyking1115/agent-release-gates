from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.intervention_study import write_action_gate_intervention


def main() -> None:
    report = write_action_gate_intervention(Path.cwd())
    print(
        "Action gate intervention complete: "
        f"{report['case_count']} cases, {len(report['variants'])} variants"
    )


if __name__ == "__main__":
    main()
