# Publishing to PyPI

The package builds a lean core (`pip install agent-release-gates` pulls only
`pydantic` and gives you the `agent-safety` CLI, the Inspect suite, the real-agent
runner, and the scoring logic). The API and dashboard are opt-in extras.

## Build

```powershell
uv build
```

Produces `dist/agent_release_gates-<version>-py3-none-any.whl` and `.tar.gz`. Verify
the wheel installs lean and the console + Inspect entry points register:

```powershell
uv venv /tmp/check --python 3.12
uv pip install --python /tmp/check/Scripts/python.exe dist/agent_release_gates-*.whl
/tmp/check/Scripts/agent-safety.exe release-gate   # runs on the built-in incident pack
```

## Publish

Use a [PyPI API token](https://pypi.org/help/#apitoken) (project-scoped once the name
is registered):

```powershell
# Dry-run on TestPyPI first.
uv publish --publish-url https://test.pypi.org/legacy/ --token <test-token>

# Real release.
uv publish --token <pypi-token>
```

`twine upload dist/*` works equally well if you prefer it.

## Before the first release — confirm

- **License.** Currently MIT (`LICENSE` + `license = "MIT"` in `pyproject.toml`).
  Change both if you want a different license (e.g. Apache-2.0).
- **Name availability.** `agent-release-gates` must be free on PyPI; register it with
  the first upload.
- **Version.** Bump `version` in `pyproject.toml` for each release.
- `inspect_ai` is an optional **peer** dependency (not a declared dependency), so
  Inspect users run `pip install agent-release-gates inspect_ai`.

## Install matrix (post-publish)

```bash
pip install agent-release-gates                # CLI + Inspect suite + scoring
pip install "agent-release-gates[api]"         # + FastAPI evidence service
pip install "agent-release-gates[dashboard]"   # + Streamlit dashboard deps
pip install agent-release-gates inspect_ai     # to run under Inspect
```
