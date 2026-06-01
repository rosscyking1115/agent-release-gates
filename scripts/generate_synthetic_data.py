from __future__ import annotations

from pathlib import Path

from internal_ai_agent.data.synthetic import generate_all


def main() -> None:
    counts = generate_all(Path.cwd())
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
