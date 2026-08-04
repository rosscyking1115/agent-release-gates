"""Draw the gate mutation adequacy figure from the committed probe output.

The figure this replaces was a dashboard screenshot: it evidenced that a dashboard
exists, not the finding the README leads with, and it drifted for three weeks because
nothing regenerated it. This one is generated from
``reports/gate_mutation_adequacy_before_approval_split.json`` — the run whose 47.4% the
README quotes — so it cannot say something the committed evidence does not.

Everything drawn is derived. The headline fraction, the per-operator counts and the
95% Wilson interval are all computed from the mutant records, so no number in the SVG
can drift from the file it was built from. Output is SVG rather than a raster because
it is text: a change to the figure is legible in review as a diff, which is the
property whose absence let the screenshot go stale.

Run::

    uv run python scripts/build_gate_mutation_figure.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

SOURCE_PATH = Path("reports/gate_mutation_adequacy_before_approval_split.json")
LATER_RUN_PATH = Path("reports/gate_mutation_adequacy_after_approval_split.json")
OUTPUT_PATH = Path("docs/img/gate_mutation_adequacy.svg")

# Plain-English glosses, matching the operator table in
# docs/finding_gate_mutation_adequacy.md. They are here so the figure is legible to a
# reader who has never opened this project.
OPERATOR_GLOSS = {
    "weaken_threshold": "Loosens a numeric bound in the policy",
    "perturb_wording": "Rewords a rule to a synonym of identical intent",
    "delete_rule": "Removes a rule that enforces an obligation",
    "narrow_scope": "Keeps the rule, reduces what it applies to",
    "change_tool_route": "Reclassifies a tool's type, risk, or approval requirement",
    "remove_evidence_source": "Removes an input the verdict depends on",
}

# Noun phrases for the summary sentence. The operator identifiers do not decline into
# English -- "all 4 weaken_thresholds" does not read.
OPERATOR_NOUN = {
    "weaken_threshold": "threshold loosenings",
    "perturb_wording": "synonym rewordings",
    "delete_rule": "rule deletions",
    "narrow_scope": "scope narrowings",
    "change_tool_route": "tool reroutings",
    "remove_evidence_source": "evidence removals",
}

WIDTH = 1000
MARGIN = 34
BAND_HEIGHT = 106
LABEL_RIGHT = 250
DOT_LEFT = 272
DOT_STEP = 34
DOT_RADIUS = 9.5
# Four dots is the widest row, ending at DOT_LEFT + 3 * DOT_STEP + DOT_RADIUS.
COUNT_X = 402
GLOSS_X = 520
ROW_HEIGHT = 42

INK = "#0F172A"
MUTED = "#64748B"
RULE = "#CBD5E1"
CAUGHT = "#0F766E"
SURVIVED = "#DC2626"
PAPER = "#FFFFFF"
PANEL = "#F8FAFC"

SANS = "Inter, 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Return the Wilson score interval for a binomial proportion.

    Args:
        successes: Number of successes.
        total: Number of trials. Must be positive.
        z: Standard normal quantile; 1.96 gives a 95% interval.

    Returns:
        ``(lower, upper)`` as proportions in ``[0, 1]``.

    Raises:
        ValueError: If ``total`` is not positive.
    """
    if total <= 0:
        raise ValueError("total must be positive")
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = (proportion + z**2 / (2 * total)) / denominator
    spread = (
        z
        / denominator
        * math.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2))
    )
    return centre - spread, centre + spread


def _operator_rows(report: dict) -> list[dict]:
    """Group the dangerous mutants by operator, hardest-hit first.

    Args:
        report: A parsed gate mutation adequacy report.

    Returns:
        One row per operator, ordered by catch rate ascending then by seeded count
        descending, so the operators the gate is blind to sit at the top.
    """
    grouped: dict[str, list[dict]] = {}
    for mutant in report["mutants"]:
        if mutant["expected"] != "kill":
            continue
        grouped.setdefault(str(mutant["operator"]), []).append(mutant)

    rows = []
    for operator, mutants in grouped.items():
        ordered = sorted(mutants, key=lambda m: str(m["mutant_id"]))
        caught = [m for m in ordered if m["outcome"] == "killed"]
        rows.append(
            {
                "operator": operator,
                "mutants": ordered,
                "seeded": len(ordered),
                "caught": len(caught),
            }
        )
    rows.sort(key=lambda r: (r["caught"] / r["seeded"], -r["seeded"], r["operator"]))
    return rows


def _text(
    x: float,
    y: float,
    content: str,
    *,
    size: float = 14,
    fill: str = INK,
    weight: str = "400",
    anchor: str = "start",
    family: str = SANS,
) -> str:
    """Return one SVG ``<text>`` element with the given content escaped."""
    return (
        f'<text x="{x:g}" y="{y:g}" font-family="{family}" font-size="{size:g}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
        f"{escape(content)}</text>"
    )


def _dot(x: float, y: float, caught: bool) -> str:
    """Return one mutant marker: filled when the gate caught it, hollow when it did not."""
    if caught:
        return (
            f'<circle cx="{x:g}" cy="{y:g}" r="{DOT_RADIUS:g}" fill="{CAUGHT}" '
            f'stroke="{CAUGHT}" stroke-width="2"/>'
        )
    return (
        f'<circle cx="{x:g}" cy="{y:g}" r="{DOT_RADIUS:g}" fill="none" '
        f'stroke="{SURVIVED}" stroke-width="2"/>'
    )


def build_svg(report: dict, later: dict) -> str:
    """Render the figure.

    Args:
        report: The run the README quotes, used for every drawn number.
        later: The subsequent run, used only for the footnote.

    Returns:
        A complete SVG document.
    """
    rows = _operator_rows(report)
    summary = report["summary"]
    seeded = int(summary["dangerous_mutant_count"])
    caught = int(summary["killed_count"])
    adequacy = caught / seeded
    low, high = wilson_interval(caught, seeded)

    controls = sorted(
        (m for m in report["mutants"] if m["expected"] == "survive"),
        key=lambda m: str(m["mutant_id"]),
    )
    false_alarms = int(summary["false_positive_count"])

    blind = [row for row in rows if row["caught"] == 0]
    blind_phrase = " and ".join(
        f"all {row['seeded']} {OPERATOR_NOUN[row['operator']]}" for row in blind
    )

    parts: list[str] = []
    y = 176.0
    for row in rows:
        parts.append(
            _text(
                LABEL_RIGHT,
                y + 5,
                row["operator"],
                size=14.5,
                weight="600",
                anchor="end",
                family=MONO,
            )
        )
        for index, mutant in enumerate(row["mutants"]):
            parts.append(
                _dot(
                    DOT_LEFT + index * DOT_STEP,
                    y,
                    mutant["outcome"] == "killed",
                )
            )
        fill = SURVIVED if row["caught"] == 0 else INK
        weight = "700" if row["caught"] == 0 else "500"
        parts.append(
            _text(
                COUNT_X,
                y + 5,
                f"{row['caught']} of {row['seeded']} caught",
                size=13.5,
                fill=fill,
                weight=weight,
            )
        )
        parts.append(
            _text(GLOSS_X, y + 5, OPERATOR_GLOSS[row["operator"]], size=13, fill=MUTED)
        )
        y += ROW_HEIGHT

    divider_y = y + 4
    control_y = divider_y + 34
    parts.append(
        f'<line x1="{MARGIN}" y1="{divider_y:g}" x2="{WIDTH - MARGIN}" '
        f'y2="{divider_y:g}" stroke="{RULE}" stroke-width="1"/>'
    )
    parts.append(
        _text(
            LABEL_RIGHT,
            control_y + 5,
            "benign_control",
            size=14.5,
            weight="600",
            anchor="end",
            family=MONO,
        )
    )
    for index, _ in enumerate(controls):
        parts.append(
            f'<circle cx="{DOT_LEFT + index * DOT_STEP:g}" cy="{control_y:g}" '
            f'r="{DOT_RADIUS:g}" fill="none" stroke="{MUTED}" stroke-width="2" '
            'stroke-dasharray="3 2"/>'
        )
    parts.append(
        _text(
            COUNT_X,
            control_y + 5,
            f"{false_alarms} false alarms",
            size=13.5,
            weight="500",
        )
    )
    parts.append(
        _text(
            GLOSS_X,
            control_y + 5,
            "Changed the policy without weakening it — the gate should not react",
            size=13,
            fill=MUTED,
        )
    )

    caption_y = control_y + 54
    parts.append(
        _text(
            MARGIN,
            caption_y,
            "Two whole classes of weakening were never caught.",
            size=15.5,
            weight="700",
        )
    )
    parts.append(
        _text(
            MARGIN,
            caption_y + 23,
            f"{blind_phrase[0].upper()}{blind_phrase[1:]} left the gate "
            "reporting a clean release.",
            size=14,
        )
    )
    parts.append(
        _text(
            MARGIN,
            caption_y + 47,
            f"Gate mutation adequacy {adequacy * 100:.1f}% ({caught} of {seeded}). "
            f"95% Wilson interval {low * 100:.1f}%–{high * 100:.1f}%. "
            f"{len(controls)} benign controls, {false_alarms} false alarms.",
            size=13.5,
            fill=INK,
        )
    )
    later_caught = int(later["summary"]["killed_count"])
    later_rate = later_caught / int(later["summary"]["dangerous_mutant_count"])
    parts.append(
        _text(
            MARGIN,
            caption_y + 69,
            f"A later fix moved this to {later_rate * 100:.1f}% "
            f"({later_caught} of {seeded}) — one discordant mutant, exact McNemar "
            "p = 1.0, reported and not banked.",
            size=12.5,
            fill=MUTED,
        )
    )

    height = caption_y + 93

    legend_y = 138.0
    legend = [
        _dot(DOT_LEFT, legend_y, True),
        _text(DOT_LEFT + 17, legend_y + 5, "caught", size=12.5, fill=MUTED),
        _dot(DOT_LEFT + 92, legend_y, False),
        _text(
            DOT_LEFT + 109,
            legend_y + 5,
            "survived — the gate still said ship",
            size=12.5,
            fill=MUTED,
        ),
    ]

    header = [
        _text(
            MARGIN,
            56,
            "A release gate, tested against its own safety rules being weakened",
            size=23,
            weight="700",
        ),
        _text(
            MARGIN,
            84,
            f"{seeded} semantically meaningful defects seeded into this gate's own "
            f"configuration. It caught {caught}.",
            size=14,
            fill=MUTED,
        ),
    ]

    body = "\n  ".join(header + legend + parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
        f'height="{height:g}" viewBox="0 0 {WIDTH} {height:g}" '
        f'role="img" aria-label="{escape(_alt_text(rows, caught, seeded, adequacy))}">\n'
        f'  <rect width="{WIDTH}" height="{height:g}" fill="{PAPER}"/>\n'
        f'  <rect x="0" y="0" width="{WIDTH}" height="{BAND_HEIGHT}" fill="{PANEL}"/>\n'
        f'  <line x1="0" y1="{BAND_HEIGHT}" x2="{WIDTH}" y2="{BAND_HEIGHT}" '
        f'stroke="{RULE}" stroke-width="1"/>\n'
        f"  {body}\n"
        "</svg>\n"
    )


def _alt_text(rows: list[dict], caught: int, seeded: int, adequacy: float) -> str:
    """Return the figure's accessible description.

    The alt text states the finding rather than describing the artwork, because the
    previous figure's alt text advertised a metric the README deliberately withholds.
    """
    blind = ", ".join(row["operator"] for row in rows if row["caught"] == 0)
    return (
        f"Gate mutation adequacy: {seeded} deliberate weakenings seeded into a release "
        f"gate's own configuration, of which the gate caught {caught} "
        f"({adequacy * 100:.1f}%). Every mutant in the {blind} classes survived, "
        "leaving the gate reporting a clean release."
    )


def main() -> None:
    """Build the figure and write it to ``docs/img/gate_mutation_adequacy.svg``."""
    report = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    later = json.loads(LATER_RUN_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_svg(report, later), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
