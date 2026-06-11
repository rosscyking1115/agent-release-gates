from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.goal_conflict_intervention import (
    write_goal_conflict_intervention,
)


def main() -> None:
    report = write_goal_conflict_intervention(Path.cwd())
    summary = report["summary"]
    print(
        "Goal-conflict intervention complete: "
        f"{report['case_count']} cases, "
        "layered unsafe-goal compliance "
        f"{summary['layered_unsafe_goal_compliance_rate']:.2%}, "
        "review burden "
        f"{summary['layered_review_burden_per_100_cases']:.2f} per 100 cases"
    )


if __name__ == "__main__":
    main()
