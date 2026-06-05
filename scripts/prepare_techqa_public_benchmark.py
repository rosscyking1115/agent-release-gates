from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.techqa_public import write_techqa_sample


def main() -> None:
    output_path = write_techqa_sample(Path.cwd())
    print(f"TechQA public benchmark sample written to {output_path}")


if __name__ == "__main__":
    main()
