from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.extraction import evaluate_extraction


def main() -> None:
    report = evaluate_extraction(Path.cwd())
    print("Extraction evaluation complete")
    for metric, value in report["metrics"].items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
