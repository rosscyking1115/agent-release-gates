"""Every version surface must agree, because they used to be kept in step by hand.

Before this test there were three declarations of the package version and nothing
comparing them:

* ``pyproject.toml`` — the real one, which the build reads.
* ``src/internal_ai_agent/__init__.py`` — a hardcoded literal, synchronised by hand.
* ``src/internal_ai_agent/api/main.py`` — a second hardcoded literal, which had **already
  drifted**: it served ``0.1.0`` in the OpenAPI document from 0.1.1 through 0.1.4.

The drift is the point. A duplicated version does not announce itself; it sits there
agreeing until one release forgets, and then a wheel says one number while the code
inside says another. The duplicates are gone -- both now derive from the installed
distribution metadata -- and this test is what stops one being reintroduced.

Note for a local run: after bumping ``pyproject.toml`` you must reinstall
(``uv sync``) before the suite passes, because the installed metadata still carries the
old number until you do. That is the test working, not a false alarm.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from internal_ai_agent import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"


def _declared_version() -> str:
    return str(tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"])


def test_the_package_version_matches_pyproject() -> None:
    assert __version__ == _declared_version(), (
        f"internal_ai_agent.__version__ is {__version__!r} but pyproject.toml declares "
        f"{_declared_version()!r}. If you have just bumped the version, reinstall with "
        "`uv sync` -- the installed distribution metadata still carries the old number."
    )


def test_the_api_reports_the_package_version() -> None:
    # Imported inside the test so the module-level assertions above still run when the
    # optional [api] extra is not installed.
    from internal_ai_agent.api.main import app

    assert app.version == __version__, (
        f"the FastAPI app reports version {app.version!r} while the package is "
        f"{__version__!r}. This is the exact drift that shipped 0.1.0 in the OpenAPI "
        "document for three releases."
    )


def test_the_openapi_document_carries_it_too() -> None:
    # The served artifact, not just the constructor argument: a reader of /openapi.json
    # is who the number is for.
    from internal_ai_agent.api.main import app

    assert app.openapi()["info"]["version"] == _declared_version()


def test_no_module_restates_the_version_as_a_literal() -> None:
    """A second copy is a copy that will eventually disagree.

    Scoped to the package source. The literal is expected to appear in `pyproject.toml`
    (where it is declared), in `CHANGELOG.md` (where it is history), and in prose that
    discusses a specific past release -- none of which can drift into a wrong runtime
    value.
    """
    version = _declared_version()
    offenders: list[str] = []
    for path in sorted((PROJECT_ROOT / "src").rglob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if f'"{version}"' in line or f"'{version}'" in line:
                offenders.append(f"{path.relative_to(PROJECT_ROOT).as_posix()}:{number}")
    assert offenders == [], (
        "these modules restate the package version as a literal instead of deriving it "
        f"from distribution metadata: {offenders}"
    )
