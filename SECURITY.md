# Security Policy

## Reporting a vulnerability

If you find a security issue, please report it **privately** rather than opening a
public issue:

- Email **rosscyking@gmail.com** with a description, reproduction steps, and impact.

You can expect an acknowledgement within a few days. Please allow reasonable time
for a fix before any public disclosure.

## Supported versions

This is a reference implementation, not a supported product. Fixes land on `main`
and in the latest [PyPI release](https://pypi.org/project/agent-release-gates/);
older versions are not maintained.

## Scope and context

- **No secrets or credentials are stored in this repository.** Hosted-provider
  comparisons (OpenAI/Anthropic/local judges and embeddings) read API keys from
  the environment at runtime only; keys are never committed. The deterministic
  core runs with no keys and no network.
- **Benchmark data is synthetic by design.** The controlled operations data
  (runbooks, tickets, incidents) is generated and contains no real company,
  customer, or personal data. TechQA and WixQA are public datasets used only for
  retrieval validation.
- This project evaluates the safety of *other* agents; it does not itself execute
  side-effecting tools against real systems. Tool use in the harness is mocked.

If a report concerns one of the optional provider integrations, note that the
relevant risk is typically on the caller's side (key handling, prompt content),
which the deterministic-core design deliberately keeps optional.
