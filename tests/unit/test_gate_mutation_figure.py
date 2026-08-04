"""Pin the README figure to the committed evidence it is drawn from.

The figure this replaces was a screenshot. Nothing regenerated it, nothing compared it
to anything, and it drifted for three weeks while the claims around it were corrected.
These tests close that specific gap: the figure must be reproducible from a committed
file, and every number it displays must be derivable from that file rather than typed
into the generator.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BEFORE_PATH = REPO_ROOT / "reports/gate_mutation_adequacy_before_approval_split.json"
AFTER_PATH = REPO_ROOT / "reports/gate_mutation_adequacy_after_approval_split.json"
PROBE_OUTPUT_PATH = REPO_ROOT / "reports/gate_mutation_adequacy.json"
FIGURE_PATH = REPO_ROOT / "docs/img/gate_mutation_adequacy.svg"
GENERATOR_PATH = REPO_ROOT / "scripts/build_gate_mutation_figure.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_gate_mutation_figure import build_svg, wilson_interval  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_before_run_has_a_committed_source_file() -> None:
    # The README quotes 47.4% as its headline. Before this file existed that number's
    # only evidence was a git object, reachable via `git show 34bee32:...` -- a
    # published claim whose source could not be opened from a checkout.
    assert BEFORE_PATH.exists()

    summary = _load(BEFORE_PATH)["summary"]

    assert summary["gate_mutation_adequacy"] == 0.4737
    assert summary["killed_count"] == 9
    assert summary["dangerous_mutant_count"] == 19
    assert summary["benign_control_count"] == 4
    assert summary["false_positive_count"] == 0


def test_the_after_run_snapshot_matches_the_live_probe_output() -> None:
    # Two files holding the same run can disagree. This is the check that stops the
    # named snapshot drifting away from whatever the probe last wrote.
    assert AFTER_PATH.read_bytes() == PROBE_OUTPUT_PATH.read_bytes(), (
        f"{AFTER_PATH.name} no longer matches {PROBE_OUTPUT_PATH.name}. If the probe "
        "was re-run deliberately, copy the new output over the snapshot and rebuild "
        "the figure with scripts/build_gate_mutation_figure.py; if it was not, the "
        "probe output has changed unintentionally."
    )


def test_the_two_runs_are_the_pair_the_finding_reports() -> None:
    before = _load(BEFORE_PATH)["summary"]
    after = _load(AFTER_PATH)["summary"]

    assert before["gate_mutation_adequacy"] == 0.4737
    assert after["gate_mutation_adequacy"] == 0.5263
    # One discordant mutant is what makes the McNemar p = 1.0 claim true.
    assert after["killed_count"] - before["killed_count"] == 1
    assert before["dangerous_mutant_count"] == after["dangerous_mutant_count"]
    assert before["false_positive_count"] == after["false_positive_count"] == 0


def test_wilson_interval_reproduces_the_published_bounds() -> None:
    # The generator computes the interval rather than repeating the literal in the
    # README, so this checks the computation lands on the published numbers.
    low, high = wilson_interval(9, 19)

    assert f"{low * 100:.1f}" == "27.3"
    assert f"{high * 100:.1f}" == "68.3"


def test_wilson_interval_rejects_an_empty_denominator() -> None:
    with pytest.raises(ValueError):
        wilson_interval(0, 0)


def test_the_figure_regenerates_byte_identically() -> None:
    # The invariant the screenshot never had: running the generator against the
    # committed JSON must reproduce the committed figure exactly.
    rebuilt = build_svg(_load(BEFORE_PATH), _load(AFTER_PATH))

    assert rebuilt == FIGURE_PATH.read_text(encoding="utf-8")


def test_the_generator_is_deterministic_across_runs() -> None:
    first = build_svg(_load(BEFORE_PATH), _load(AFTER_PATH))
    second = build_svg(_load(BEFORE_PATH), _load(AFTER_PATH))

    assert first == second


def test_the_committed_figure_uses_lf_endings() -> None:
    assert b"\r\n" not in FIGURE_PATH.read_bytes()


def test_running_the_generator_leaves_the_figure_unchanged() -> None:
    # End to end, through the actual entry point, because the unit-level rebuild above
    # would still pass if main() wrote somewhere else or transformed the text on write.
    before = FIGURE_PATH.read_bytes()

    result = subprocess.run(
        [sys.executable, str(GENERATOR_PATH)],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert FIGURE_PATH.read_bytes() == before


def test_every_number_in_the_figure_traces_to_the_committed_run() -> None:
    report = _load(BEFORE_PATH)
    summary = report["summary"]
    svg = FIGURE_PATH.read_text(encoding="utf-8")

    caught = int(summary["killed_count"])
    seeded = int(summary["dangerous_mutant_count"])
    low, high = wilson_interval(caught, seeded)

    assert f"{caught / seeded * 100:.1f}%" in svg
    assert f"({caught} of {seeded})" in svg
    assert f"{low * 100:.1f}%–{high * 100:.1f}%" in svg
    assert f"{summary['false_positive_count']} false alarms" in svg


def test_the_figure_names_the_operators_the_gate_never_caught() -> None:
    # The figure's claim is not the headline percentage, it is that two whole classes
    # of weakening were caught zero times. If a re-run ever changes which operators
    # those are, the caption must change with it.
    report = _load(BEFORE_PATH)
    blind = sorted(
        {
            str(mutant["operator"])
            for mutant in report["mutants"]
            if mutant["expected"] == "kill"
        }
        - {
            str(mutant["operator"])
            for mutant in report["mutants"]
            if mutant["expected"] == "kill" and mutant["outcome"] == "killed"
        }
    )
    svg = FIGURE_PATH.read_text(encoding="utf-8")

    assert blind == ["perturb_wording", "weaken_threshold"]
    for operator in blind:
        assert operator in svg
    assert "never caught" in svg


def test_the_alt_text_states_the_finding_rather_than_the_artwork() -> None:
    # The previous figure's alt text advertised "safety recall" -- a number the README
    # deliberately does not headline. This one has to carry the finding instead.
    svg = FIGURE_PATH.read_text(encoding="utf-8")

    assert 'role="img"' in svg
    assert "aria-label=" in svg
    assert "clean release" in svg
    assert "safety recall" not in svg.lower()
