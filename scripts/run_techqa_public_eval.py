from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.techqa_public import evaluate_techqa_public


def main() -> None:
    report = evaluate_techqa_public(Path.cwd())
    print("TechQA public RAG benchmark complete")
    print(f"status: {report['status']}")
    print(f"case_count: {report['case_count']}")
    for metric, value in report.get("metrics", {}).items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
