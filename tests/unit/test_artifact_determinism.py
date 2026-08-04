"""Enforce the claim that regenerating an unchanged artifact produces no diff.

``io.write_json`` states in its docstring that regenerating an unchanged artifact
produces no diff and a real change stays legible in review. That claim was false on
Windows for as long as the writers used Python's default newline translation: an
artifact regenerated there came back CRLF against the LF committed from Linux, so a
six-line content change arrived in review as a two-thousand-line diff, and the real
change was invisible inside it.

A docstring is not a control. These tests make the claim executable, so it cannot
quietly stop being true on one platform again.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from internal_ai_agent.io import write_json, write_jsonl

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE_ROOTS = ("src", "scripts")

PAYLOAD = {
    "beta": ["one", "two"],
    "alpha": {"nested": True, "count": 3},
}
ROWS = [{"b": 2, "a": 1}, {"b": 4, "a": 3}]


def test_write_json_regeneration_produces_an_identical_file(tmp_path) -> None:
    path = tmp_path / "artifact.json"

    write_json(path, PAYLOAD)
    first = path.read_bytes()
    write_json(path, PAYLOAD)
    second = path.read_bytes()

    assert first == second


def test_write_jsonl_regeneration_produces_an_identical_file(tmp_path) -> None:
    path = tmp_path / "artifact.jsonl"

    write_jsonl(path, ROWS)
    first = path.read_bytes()
    write_jsonl(path, ROWS)
    second = path.read_bytes()

    assert first == second


@pytest.mark.parametrize(
    ("writer", "name", "payload"),
    [
        (write_json, "artifact.json", PAYLOAD),
        (write_jsonl, "artifact.jsonl", ROWS),
    ],
)
def test_writers_emit_lf_on_every_platform(writer, name, payload, tmp_path) -> None:
    # The platform-dependent half of the defect. On Windows the default newline
    # translation turns every "\n" into "\r\n", so this fails there and passes on
    # Linux -- which is exactly how it survived CI.
    path = tmp_path / name

    writer(path, payload)

    written = path.read_bytes()
    assert b"\r\n" not in written
    assert written.endswith(b"\n")


def test_write_csv_regeneration_produces_an_identical_file(tmp_path) -> None:
    # The review packets are written with the csv module, which emits CRLF per
    # RFC 4180. That is correct and is deliberately not normalised to LF; what matters
    # is that regenerating produces the same bytes, which is asserted here rather than
    # a line-ending shape.
    from internal_ai_agent.evals.external_review import _write_csv

    path = tmp_path / "packet.csv"
    fields = ["case_id", "note"]
    rows = [{"case_id": "A-1", "note": "first"}, {"case_id": "A-2", "note": "second"}]

    _write_csv(path, fields, rows)
    first = path.read_bytes()
    _write_csv(path, fields, rows)
    second = path.read_bytes()

    assert first == second


def _unpinned_write_sites() -> list[str]:
    """Return every text-write call site that does not pin ``newline``.

    Returns:
        ``path:lineno`` for each offending call, sorted by path.
    """
    offenders: list[str] = []
    for root in SOURCE_ROOTS:
        for path in sorted((REPO_ROOT / root).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute):
                    continue
                if "newline" in {keyword.arg for keyword in node.keywords}:
                    continue
                relative = path.relative_to(REPO_ROOT).as_posix()
                if node.func.attr == "write_text":
                    offenders.append(f"{relative}:{node.lineno}")
                elif node.func.attr == "open" and node.args:
                    mode = getattr(node.args[0], "value", None)
                    if isinstance(mode, str) and "w" in mode and "b" not in mode:
                        offenders.append(f"{relative}:{node.lineno}")
    return offenders


def test_every_text_writer_pins_newline() -> None:
    # Pinning the two writers in io.py is not enough on its own: the report, the
    # intervention studies, the incident memos, the synthetic corpus and the public
    # site all write text through their own call sites. One unpinned writer is enough
    # to churn a whole artifact, so the rule is checked across the tree rather than
    # per file.
    offenders = _unpinned_write_sites()

    assert offenders == [], (
        "These text-write call sites do not pin newline=\"\\n\", so the artifacts they "
        "produce will churn line-by-line when regenerated on Windows: "
        + ", ".join(offenders)
    )
