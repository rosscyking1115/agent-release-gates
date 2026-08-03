from __future__ import annotations

import importlib.util
import json
import re
import shutil
from html import unescape
from pathlib import Path


def _load_public_site_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts/build_public_site.py"
    spec = importlib.util.spec_from_file_location("build_public_site", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_artifact_index_keeps_technical_links_off_homepage() -> None:
    public_site = _load_public_site_module()
    html = public_site._artifact_index_html(public_site._public_artifact_links())

    assert "<h1>Technical Artifact Index</h1>" in html
    assert 'href="index.html"' in html
    assert 'href="evaluation_gates.json"' in html
    assert 'href="incident_replay_summary.json"' in html
    assert 'href="incident_release_gates.json"' in html
    assert 'href="incident_response_plan.json"' in html
    assert 'href="incident_pack_v1.schema.json"' in html
    assert 'href="candidate_results_v1.schema.json"' in html
    assert 'href="safety_classifier_eval_summary.json"' in html
    assert "progress checker" not in html.lower()
    assert "internal notes" not in html.lower()


def test_public_docs_link_evaluate_your_agent_quickstart() -> None:
    project_root = Path(__file__).resolve().parents[2]
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    artifacts = (project_root / "docs/technical_artifacts.md").read_text(encoding="utf-8")
    site_builder = (project_root / "scripts/build_public_site.py").read_text(
        encoding="utf-8"
    )

    assert "docs/evaluate_your_agent_quickstart.md" in readme
    assert "evaluate_your_agent_quickstart.md" in artifacts
    assert "Evaluate your agent" in site_builder
    assert "docs/evaluate_your_agent_quickstart.md" in site_builder


def test_candidate_results_schema_describes_jsonl_row() -> None:
    schema_path = (
        Path(__file__).resolve().parents[2] / "schemas/candidate_results_v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["title"] == "Agent Safety Candidate Result Row v1"
    assert set(schema["required"]) == {
        "incident_id",
        "candidate_id",
        "decision",
        "answer",
    }
    assert schema["properties"]["candidate_id"]["pattern"] == (
        "^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"
    )
    assert "candidate_results" not in schema["properties"]


def test_artifact_index_only_links_current_incident_memos(tmp_path) -> None:
    public_site = _load_public_site_module()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    current_memo = reports_dir / "incident_memo_INC-CURRENT.md"
    stale_memo = reports_dir / "incident_memo_INC-STALE.md"
    current_memo.write_text("# current", encoding="utf-8")
    stale_memo.write_text("# stale", encoding="utf-8")
    (reports_dir / "incident_replay_summary.json").write_text(
        json.dumps({"memo_paths": ["reports/incident_memo_INC-CURRENT.md"]}),
        encoding="utf-8",
    )

    artifact_links = public_site._public_artifact_links(tmp_path)
    linked_artifacts = {href for _, _, href in artifact_links}

    assert "incident_memo_INC-CURRENT.md" in linked_artifacts
    assert "incident_memo_INC-STALE.md" not in linked_artifacts


# --- The finding panel on the project site ------------------------------------------
#
# The site is a third public surface. PyPI and GitHub drifted from one another within
# hours, and two claims were retracted across six surfaces before that, so the panel is
# sourced from the document that owns the finding rather than copied. These tests pin the
# properties that keep it that way, and they check the *rendered* HTML rather than the
# generator, because a check that reads the source cannot see what the artifact contains.

_PANEL_START = "<!-- site-panel:start -->"
_PANEL_END = "<!-- site-panel:end -->"


def _finding_doc_text() -> str:
    project_root = Path(__file__).resolve().parents[2]
    return (project_root / "docs/finding_gate_mutation_adequacy.md").read_text(
        encoding="utf-8"
    )


def _plain(html: str) -> str:
    """Rendered HTML reduced to its visible text, for comparison against source markdown.

    Tags and entity escapes are presentation, not content. Comparing them literally would
    make the test fail on `&#x27;` versus `'` while passing on genuinely divergent prose,
    which is the wrong way round.
    """
    text = re.sub(r"<[^>]+>", " ", html)
    return " ".join(unescape(text).split())


def _plain_source(markdown: str) -> str:
    return " ".join(markdown.replace("**", "").split())


def _rendered_panel() -> str:
    public_site = _load_public_site_module()
    project_root = Path(__file__).resolve().parents[2]
    source = public_site.read_finding_panel_source(project_root)
    return public_site._finding_panel_html(source, "https://example.invalid/repo")


def test_finding_document_carries_the_panel_markers() -> None:
    text = _finding_doc_text()
    assert _PANEL_START in text and _PANEL_END in text, (
        "docs/finding_gate_mutation_adequacy.md must delimit the site panel. Without the "
        "markers the site has no source and the build fails loudly rather than shipping "
        "an empty panel."
    )


def test_panel_is_sourced_from_the_finding_document_not_copied() -> None:
    """Every sentence rendered on the site must come from the canonical document.

    This is the property that makes drift impossible rather than merely unlikely.
    """
    public_site = _load_public_site_module()
    project_root = Path(__file__).resolve().parents[2]
    source = public_site.read_finding_panel_source(project_root)
    rendered = _rendered_panel()

    assert source, "the panel source block is empty"
    panel_text = _plain(rendered.split("<h3>The finding</h3>", 1)[1])
    expected = _plain_source(source)

    assert expected in panel_text, (
        "the rendered panel does not contain its source text verbatim. The site must "
        "quote the finding document, not paraphrase it, or the two can drift. "
        f"expected {expected[:120]!r} but rendered {panel_text[:120]!r}"
    )
    # And nothing beyond the source plus the link: extra prose on the site would be a
    # second copy in the making.
    remainder = panel_text.replace(expected, "").replace("Read the full finding →", "")
    assert len(remainder.strip()) < 5, (
        f"the panel carries prose absent from its source: {remainder.strip()!r}"
    )


def test_panel_carries_no_precise_figure() -> None:
    """Exact numbers live in exactly one place.

    A percentage copied onto a third surface goes stale the moment the measurement is
    repeated; a rounded qualitative claim survives it. The panel is a signpost.
    """
    rendered = _rendered_panel()
    body = rendered.split("<h3>The finding</h3>", 1)[1]
    assert not re.search(r"\d+(\.\d+)?\s*%", body), (
        "the finding panel contains a precise figure. Numbers belong in the artifact "
        "that owns them, not on the project site."
    )
    assert not re.search(r"\b\d+\s+of\s+\d+\b", body), (
        "the finding panel contains an exact count. Use a rounded qualitative claim."
    )


def test_panel_link_resolves_from_the_deployed_path() -> None:
    """The link must be absolute.

    The site is served from a different origin than the repository, and the canonical
    document is not copied into `public/`, so a relative path 404s once deployed -- the
    same trap as the relative README links that broke on PyPI.
    """
    rendered = _rendered_panel()
    hrefs = re.findall(r'href="([^"]+)"', rendered)
    assert hrefs, "the finding panel must link to the full write-up"
    for href in hrefs:
        assert href.startswith("https://"), (
            f"the finding panel link {href!r} is not absolute and will not resolve "
            "from the deployed site."
        )
        assert "docs/finding_gate_mutation_adequacy.md" in href


def test_built_index_html_contains_the_panel(tmp_path) -> None:
    """Build the site and check the produced HTML, not the generator.

    The site is built by CI *after* the tests run and `public/` is gitignored, so a
    fresh clone has no built page. Asserting against a pre-existing `public/index.html`
    would therefore pass on a stale artifact locally and verify nothing at all in CI.
    This builds into a temporary root so the check runs everywhere and exercises the real
    build path end to end.
    """
    public_site = _load_public_site_module()
    project_root = Path(__file__).resolve().parents[2]

    for name in ("reports", "schemas", "docs"):
        shutil.copytree(project_root / name, tmp_path / name)
    public_site.build_public_site(tmp_path)
    html = (tmp_path / "public/index.html").read_text(encoding="utf-8")

    assert "<h3>The finding</h3>" in html, "the built site has no finding panel"
    panel = html.split("<h3>The finding</h3>", 1)[1].split("</div>", 1)[0]

    source = public_site.read_finding_panel_source(project_root)
    assert _plain_source(source) in _plain(panel), (
        "the built site's panel does not match its source in the finding document."
    )
    assert "https://github.com/rosscyking1115/agent-release-gates/blob/main/" in panel
    assert not re.search(r"\d+(\.\d+)?\s*%", panel)
