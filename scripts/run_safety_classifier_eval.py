from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.safety_classifier import evaluate_safety_classifier


def main() -> None:
    report = evaluate_safety_classifier(Path.cwd())
    print("Safety classifier evaluation complete")
    print(f"challenge_case_count: {report['challenge_case_count']}")
    print(f"prevalence_case_count: {report['prevalence_case_count']}")
    print(f"false_negative_rate: {report['metrics']['false_negative_rate']:.4f}")
    print(f"false_positive_rate: {report['metrics']['false_positive_rate']:.4f}")
    print(
        "unsafe_prevalence: "
        f"{report['weighted_prevalence']['unsafe_prevalence']:.4f}"
    )


if __name__ == "__main__":
    main()
