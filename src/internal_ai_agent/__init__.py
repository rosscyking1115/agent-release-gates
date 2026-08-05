"""Agent Release Safety Gates."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

__all__ = ["__version__"]

# Read from the installed distribution rather than restating the number here.
#
# This used to be a hardcoded literal kept in step with `pyproject.toml` by hand, and a
# third copy sat in `api/main.py`. Nothing asserted they agreed, and one had already
# drifted: the API served `version="0.1.0"` in its OpenAPI document from 0.1.1 through
# 0.1.4, three releases behind the package it shipped in. A second copy of a version is
# a copy that will eventually disagree, and the only way to notice is for something to
# check -- so `tests/unit/test_version.py` now does.
try:
    __version__ = _distribution_version("agent-release-gates")
except PackageNotFoundError:  # pragma: no cover - only in an uninstalled source tree
    # Deliberately not a placeholder such as "0.0.0". A fallback value would let every
    # version check pass against a number nobody released, which is the shape of a
    # metric satisfied by absence.
    raise RuntimeError(
        "agent-release-gates is not installed, so its version cannot be read from "
        "distribution metadata. Install the project (`uv sync`) before importing it."
    ) from None
