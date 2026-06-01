from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.security import evaluate_security


def main() -> None:
    report = evaluate_security(Path.cwd())
    print("Security evaluation complete")
    for metric, value in report["metrics"].items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
