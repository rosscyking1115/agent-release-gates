from __future__ import annotations

from pathlib import Path

from internal_ai_agent.reporting.public_report import write_public_report


def main() -> None:
    output_path = write_public_report(Path.cwd())
    print(f"Wrote {output_path}")
    print(f"Wrote {output_path.with_suffix('.html')}")


if __name__ == "__main__":
    main()
