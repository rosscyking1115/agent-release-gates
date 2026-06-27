from __future__ import annotations

from pathlib import Path

from internal_ai_agent.evals.multilingual_safety import (
    evaluate_multilingual_safety,
    write_multilingual_safety,
)


def test_multilingual_safety_measures_per_language_coverage() -> None:
    report = evaluate_multilingual_safety()

    assert report["report_type"] == "multilingual_safety_eval"
    by_language = report["by_language"]

    # English trips an English phrase on every case.
    assert by_language["en"]["block_rate"] == 1.0
    # Curated multilingual phrases give partial non-English coverage...
    for lang in ("zh", "ja", "ko"):
        assert 0.0 < by_language[lang]["block_rate"] < 1.0
    # ...and the remaining gap is reported honestly, not hidden.
    assert report["non_english_coverage_gap"] > 0.0


def test_write_multilingual_safety(tmp_path: Path) -> None:
    report = write_multilingual_safety(tmp_path)

    assert (tmp_path / "reports/multilingual_safety_eval.json").exists()
    assert report["by_language"]["ko"]["case_count"] >= 1
