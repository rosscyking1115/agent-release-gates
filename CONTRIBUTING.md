# Contributing

Thanks for taking a look at Agent Release Safety Gates.

This project is intended to be a public benchmark-style artifact. Contributions should improve evaluation quality, reproducibility, safety analysis, or clarity. Please keep the data boundary conservative: do not add private company documents, customer data, employee data, credentials, production logs, or confidential workflows.

## Good Contribution Areas

- hand-authored benign, ambiguous, unsafe, prompt-injection, weak-evidence, excessive-agency, and tool-misuse cases
- clearer failure taxonomy labels
- public benchmark expansion with reproducible sampling
- judge-reliability experiments
- human-review calibration workflow
- multi-model adapters with explicit model ids, dates, settings, and limitations
- report, dashboard, or documentation improvements that make results easier to inspect
- tests that prevent benchmark or reporting regressions

## Opening Issues

Use GitHub issues for public, non-sensitive project discussion:

- External review volunteer: use this to offer independent labels, methodology review, reproducibility review, or dataset-boundary review.
- Benchmark or evaluation improvement: use this for proposed datasets, metrics, failure modes, interventions, or report improvements.
- Bug or reproducibility issue: use this for failing commands, broken artifacts, dashboard problems, or unclear setup.

Do not paste completed reviewer labels, credentials, personal data, private company data, production logs, or confidential examples into public issues.

## Data Rules

- Use synthetic internal-operations data unless a public dataset is explicitly documented.
- Keep public datasets separated from the synthetic benchmark in code, docs, and reports.
- Do not add real personal data or confidential business procedures.
- Do not imply the project measures any real organization's internal AI system.

## Result Rules

- Do not publish provider-backed or multi-model results unless the run is reproducible and the model settings are documented.
- Separate synthetic labels, simulated reviewer labels, real human labels, and LLM-as-judge labels.
- Include limitations when adding new metrics.
- Add or update tests when changing scoring, reports, or release gates.

## Local Checks

Run these before opening a pull request:

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/run_all_evals.py
uv run python scripts/build_public_site.py
```

Optional checks:

```powershell
uv run python scripts/smoke_otel_collector.py
docker compose --profile observability up -d otel-collector
uv run python scripts/check_otel_collector_deployment.py
docker compose --profile observability down
docker build -t agent-release-gates:local .
```

## Pull Request Checklist

- The change has a clear evaluation or documentation purpose.
- Synthetic and public-data tracks remain separated.
- New metrics are reproducible.
- New limitations are documented.
- Tests or generated artifacts are updated when needed.
