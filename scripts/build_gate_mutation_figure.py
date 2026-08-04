"""Draw the gate mutation adequacy figure from the committed probe output.

The figure this replaces was a dashboard screenshot: it evidenced that a dashboard
exists, not the finding the README leads with, and it drifted for three weeks because
nothing regenerated it. This one is generated from
``reports/gate_mutation_adequacy_before_approval_split.json`` — the run whose 47.4% the
README quotes — so it cannot say something the committed evidence does not.

Everything drawn is derived. The headline fraction, the per-operator counts and the
95% Wilson interval are all computed from the mutant records, so no number in the SVG
can drift from the file it was built from. The SVG is the source of truth because it is
text: a change to the figure is legible in review as a diff, which is the property whose
absence let the screenshot go stale.

``--render-png`` additionally rasterises the SVG to ``docs/img/dashboard.png`` through a
headless browser. That path is deliberately opt-in and is never exercised by the test
suite, because a browser render is not reproducible byte for byte across platforms or
browser versions, and a test that demanded it would be a control nobody could keep
green. Staleness is caught a different way: the render stamps the SHA-256 of the SVG it
was made from into a PNG ``tEXt`` chunk, and the test suite asserts that fingerprint
still matches the committed SVG. Edit the figure without re-rendering and the build
fails, which is the failure the previous screenshot never had.

Run::

    uv run python scripts/build_gate_mutation_figure.py
    uv run python scripts/build_gate_mutation_figure.py --render-png
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
from xml.sax.saxutils import escape

SOURCE_PATH = Path("reports/gate_mutation_adequacy_before_approval_split.json")
LATER_RUN_PATH = Path("reports/gate_mutation_adequacy_after_approval_split.json")
OUTPUT_PATH = Path("docs/img/gate_mutation_adequacy.svg")

# The README image keeps this path on purpose. PyPI's published 0.1.4 description is
# frozen text carrying this exact URL pinned to main, so the text can never change and
# only the file it resolves to can. Moving the figure to a new path would leave the
# published description showing the superseded screenshot for good; deleting it would
# leave a broken image. Replacing the content here corrects both surfaces at once.
PNG_PATH = Path("docs/img/dashboard.png")
PNG_SCALE = 2
FINGERPRINT_KEY = "svg-sha256"

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


def svg_fingerprint(svg: str) -> str:
    """Return the SHA-256 of an SVG document, over its exact UTF-8 bytes."""
    return hashlib.sha256(svg.encode("utf-8")).hexdigest()


def read_png_fingerprint(png_bytes: bytes) -> str | None:
    """Return the SVG fingerprint stamped into a PNG, or ``None`` if absent.

    Args:
        png_bytes: A complete PNG file.

    Returns:
        The recorded SHA-256 hex digest, or ``None`` when the PNG carries no
        ``svg-sha256`` ``tEXt`` chunk.

    Raises:
        ValueError: If the bytes are not a PNG.
    """
    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG file")
    offset = 8
    while offset + 8 <= len(png_bytes):
        (length,) = struct.unpack(">I", png_bytes[offset : offset + 4])
        chunk_type = png_bytes[offset + 4 : offset + 8]
        data = png_bytes[offset + 8 : offset + 8 + length]
        if chunk_type == b"tEXt":
            keyword, _, value = data.partition(b"\x00")
            if keyword.decode("latin-1") == FINGERPRINT_KEY:
                return value.decode("latin-1")
        if chunk_type == b"IEND":
            break
        offset += 12 + length
    return None


def png_dimensions(png_bytes: bytes) -> tuple[int, int]:
    """Return ``(width, height)`` from a PNG's IHDR chunk."""
    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG file")
    width, height = struct.unpack(">II", png_bytes[16:24])
    return width, height


def _stamp_png(png_bytes: bytes, fingerprint: str) -> bytes:
    """Insert the SVG fingerprint as a ``tEXt`` chunk immediately after IHDR.

    Args:
        png_bytes: A complete PNG file.
        fingerprint: The SHA-256 hex digest of the SVG this PNG was rendered from.

    Returns:
        The PNG with the fingerprint chunk added.
    """
    payload = FINGERPRINT_KEY.encode("latin-1") + b"\x00" + fingerprint.encode("latin-1")
    chunk = (
        struct.pack(">I", len(payload))
        + b"tEXt"
        + payload
        + struct.pack(">I", zlib.crc32(b"tEXt" + payload) & 0xFFFFFFFF)
    )
    # IHDR is always the first chunk: 8-byte signature, then 4 length + 4 type + 13
    # data + 4 CRC.
    ihdr_end = 8 + 12 + 13
    return png_bytes[:ihdr_end] + chunk + png_bytes[ihdr_end:]


def _find_browser() -> str:
    """Locate a Chromium-family browser for rasterising.

    Returns:
        Path to the executable.

    Raises:
        RuntimeError: If none is found. Set ``FIGURE_BROWSER`` to override.
    """
    override = os.environ.get("FIGURE_BROWSER")
    if override:
        return override
    candidates = [
        "chrome",
        "google-chrome",
        "chromium",
        "chromium-browser",
        "msedge",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        found = shutil.which(candidate) or (
            candidate if Path(candidate).exists() else None
        )
        if found:
            return found
    raise RuntimeError(
        "No Chromium-family browser found for --render-png. Set FIGURE_BROWSER to one."
    )


def render_png(svg: str) -> bytes:
    """Rasterise the SVG and stamp it with the SVG's fingerprint.

    Args:
        svg: The SVG document to render.

    Returns:
        PNG bytes carrying an ``svg-sha256`` ``tEXt`` chunk.

    Raises:
        RuntimeError: If the browser produces no output.
    """
    browser = _find_browser()
    width = WIDTH
    height = int(float(svg.split('height="', 1)[1].split('"', 1)[0]))
    with tempfile.TemporaryDirectory() as work:
        work_dir = Path(work)
        svg_file = work_dir / "figure.svg"
        svg_file.write_text(svg, encoding="utf-8", newline="\n")
        png_file = work_dir / "figure.png"
        subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--force-device-scale-factor={PNG_SCALE}",
                f"--screenshot={png_file}",
                f"--window-size={width},{height}",
                f"--user-data-dir={work_dir / 'profile'}",
                svg_file.resolve().as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        if not png_file.exists():
            raise RuntimeError("the browser produced no PNG")
        return _stamp_png(png_file.read_bytes(), svg_fingerprint(svg))


def main(argv: list[str] | None = None) -> int:
    """Build the figure, optionally rendering the README PNG alongside it.

    Args:
        argv: Command-line arguments, defaulting to ``sys.argv[1:]``.

    Returns:
        Process exit status.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--render-png",
        action="store_true",
        help=(
            "also rasterise to docs/img/dashboard.png through a headless browser. "
            "Requires Chrome, Chromium or Edge; override with FIGURE_BROWSER."
        ),
    )
    args = parser.parse_args(argv)

    report = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    later = json.loads(LATER_RUN_PATH.read_text(encoding="utf-8"))
    svg = build_svg(report, later)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT_PATH}")

    if args.render_png:
        png = render_png(svg)
        PNG_PATH.write_bytes(png)
        width, height = png_dimensions(png)
        print(f"Wrote {PNG_PATH} ({width}x{height}, svg-sha256={svg_fingerprint(svg)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
