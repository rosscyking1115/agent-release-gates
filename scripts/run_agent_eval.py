from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.agent import evaluate_agent


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    report = evaluate_agent(project_root)
    print("Agent evaluation complete")
    for metric, value in report["metrics"].items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
