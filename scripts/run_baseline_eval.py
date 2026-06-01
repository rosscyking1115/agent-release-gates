from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.runner import evaluate_comparison


def main() -> None:
    report = evaluate_comparison(Path.cwd())
    print("Evaluation comparison complete")
    for metric, values in report["metrics"].items():
        print(
            f"{metric}: baseline={values['baseline']:.4f} "
            f"improved={values['improved']:.4f} delta={values['delta']:.4f}"
        )


if __name__ == "__main__":
    main()
