"""The evaluation-integrity doc's internal links must resolve.

Two contracts are pinned here. The first covers `../src/**#L<n>` citations into source
files. The second covers intra-document `#heading` links, which are cheap to break by
renaming a heading and which nothing else checks.

## Source-line citations

`docs/evaluation_integrity.md` is the document that reports this project's own benchmark
as circular, and the README labels it "read first". Its authority rests entirely on the
`file:line` references resolving to the code they claim to show. Those are live GitHub
anchors, and nothing else in the build checks them.

They have already drifted once: they were computed before comment blocks were inserted
above them in the same change set, and nine of nine anchors ended up short by exactly the
number of inserted lines. This test makes that failure mode loud.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = PROJECT_ROOT / "docs/evaluation_integrity.md"

# (repo-relative path, 1-indexed line, substring the cited line must contain).
# Add a row whenever a new source citation is added to the doc.
EXPECTED_CITATIONS = {
    ("src/internal_ai_agent/data/synthetic.py", 224): "receives a {title.lower()} ticket",
    ("src/internal_ai_agent/data/synthetic.py", 267): "{title} observed in",
    ("src/internal_ai_agent/evals/safety_classifier.py", 83): "CATEGORY_SIGNALS = {",
    ("src/internal_ai_agent/evals/safety_classifier.py", 141): "BENIGN_INTENT_SIGNALS = [",
    ("src/internal_ai_agent/rag/baseline.py", 65): "SEMANTIC_ALIASES = {",
    ("src/internal_ai_agent/rag/baseline.py", 144): "intentionally uses broad system/team hints",
    ("src/internal_ai_agent/rag/baseline.py", 162): "for hint in hints if hint in normalized",
    ("src/internal_ai_agent/rag/baseline.py", 283): "chosen = retrieved[0]",
    ("src/internal_ai_agent/rag/baseline.py", 1031): "CURRENT_EVIDENCE_MARKERS = (",
}

_ANCHOR = re.compile(r"\(\.\./(src/[^)#]+)#L(\d+)\)")


def _anchors_in_doc() -> set[tuple[str, int]]:
    text = DOC_PATH.read_text(encoding="utf-8")
    return {(path, int(line)) for path, line in _ANCHOR.findall(text)}


def test_every_cited_line_contains_what_the_doc_claims() -> None:
    for (rel_path, line_number), expected in sorted(EXPECTED_CITATIONS.items()):
        lines = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8").splitlines()
        assert line_number <= len(lines), (
            f"{rel_path}#L{line_number} is past the end of the file ({len(lines)} lines)"
        )
        actual = lines[line_number - 1]
        assert expected in actual, (
            f"{rel_path}#L{line_number} should contain {expected!r} but contains "
            f"{actual.strip()!r}. The doc's citation has drifted from the code."
        )


def test_doc_anchors_and_expected_citations_agree() -> None:
    """Neither side may gain an entry without the other."""
    in_doc = _anchors_in_doc()
    in_table = set(EXPECTED_CITATIONS)

    assert in_doc - in_table == set(), (
        f"doc cites lines with no expectation pinned here: {sorted(in_doc - in_table)}"
    )
    assert in_table - in_doc == set(), (
        f"expectations pinned here are no longer cited by the doc: {sorted(in_table - in_doc)}"
    )


def _heading_slugs() -> set[str]:
    """GitHub's slug rule: lowercase, drop punctuation, spaces to hyphens."""
    slugs: set[str] = set()
    for line in DOC_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            continue
        title = line.lstrip("#").strip()
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slugs.add(re.sub(r"[\s]+", "-", slug).strip("-"))
    return slugs


def test_intra_document_links_resolve_to_a_heading() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    targets = re.findall(r"\]\(#([a-z0-9-]+)\)", text)
    assert targets, "expected the doc to cross-reference its own sections"

    slugs = _heading_slugs()
    unresolved = sorted({t for t in targets if t not in slugs})
    assert not unresolved, (
        f"intra-document links point at headings that do not exist: {unresolved}. "
        "A heading was probably renamed without updating the links to it."
    )


def test_inline_code_labels_match_their_anchors() -> None:
    """`baseline.py:283` in the link text must match the #L283 in the href."""
    text = DOC_PATH.read_text(encoding="utf-8")
    labelled = re.findall(r"\[`([^`]+\.py):(\d+)`\]\(\.\./(src/[^)#]+)#L(\d+)\)", text)
    assert labelled, "expected labelled source citations in the doc"
    for filename, label_line, href_path, href_line in labelled:
        assert label_line == href_line, (
            f"citation label says {filename}:{label_line} but the link points at "
            f"#L{href_line}"
        )
        assert href_path.endswith(filename), (
            f"citation label names {filename} but the link points at {href_path}"
        )
