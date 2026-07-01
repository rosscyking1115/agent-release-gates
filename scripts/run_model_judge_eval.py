from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import URLError

from internal_ai_agent.evals.model_judge import (
    dry_run_status,
    evaluate_hosted_model_judge,
)
from internal_ai_agent.io import write_json
from internal_ai_agent.providers.anthropic_judge import (
    DEFAULT_ANTHROPIC_JUDGE_MODEL,
    AnthropicJudgeClient,
    AnthropicJudgeConfig,
    AnthropicJudgeProviderError,
    anthropic_judge_config_from_env,
)
from internal_ai_agent.providers.local_judge import (
    DEFAULT_LOCAL_JUDGE_MODEL,
    LocalJudgeClient,
    LocalJudgeConfig,
    LocalJudgeProviderError,
    local_judge_config_from_env,
)
from internal_ai_agent.providers.local_judge import (
    PROVIDER_NAME as LOCAL_PROVIDER_NAME,
)
from internal_ai_agent.providers.openai_judge import (
    DEFAULT_OPENAI_JUDGE_MODEL,
    OpenAIJudgeClient,
    OpenAIJudgeConfig,
    OpenAIJudgeProviderError,
    openai_judge_config_from_env,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Optionally compare calibration labels with a hosted model judge."
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Make provider API calls. Omit for a cost-free dry run.",
    )
    parser.add_argument(
        "--provider",
        choices=("openai", "anthropic", "local"),
        default="openai",
        help=(
            "Judge provider. 'local' uses a self-hosted OpenAI-compatible endpoint "
            "(Ollama/vLLM/LM Studio) and needs no API key."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Hosted judge model id.",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help="Provider API endpoint.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="HTTP timeout for each provider request.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=None,
        help="Maximum output tokens per judge response.",
    )
    parser.add_argument(
        "--status-output",
        default="reports/model_judge_eval_status.json",
        help="Path to write run status.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path.cwd()
    provider_name = LOCAL_PROVIDER_NAME if args.provider == "local" else args.provider
    requested_model = args.model or _default_model(args.provider)

    if not args.run:
        status = dry_run_status(
            project_root,
            provider=provider_name,
            model=requested_model,
        )
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        return

    env_config = _config_from_env(args.provider)
    if env_config is None:
        status = {
            **dry_run_status(
                project_root,
                provider=provider_name,
                model=requested_model,
            ),
            "status": "blocked",
            "reason": f"{_credential_env_var(args.provider)} is not set.",
        }
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1)

    config, judge_case = _build_judge_client(args, env_config)
    try:
        report = evaluate_hosted_model_judge(
            project_root,
            judge_case=judge_case,
            provider=provider_name,
            model=config.model,
        )
    except (
        OpenAIJudgeProviderError,
        AnthropicJudgeProviderError,
        LocalJudgeProviderError,
    ) as exc:
        status = _provider_error_status(provider_name, config.model, exc)
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    except URLError as exc:
        status = _local_unreachable_status(provider_name, config, exc)
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    except ValueError as exc:
        status = _judge_parse_error_status(provider_name, config.model, exc)
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    status = {
        "status": "completed",
        "provider": provider_name,
        "model": config.model,
        "summary_path": "reports/model_judge_eval_summary.json",
        "cases_path": "reports/model_judge_eval_cases.jsonl",
        "case_count": report["case_count"],
        "metrics": report["summary"],
        "publication_review": report["publication_review"],
    }
    write_json(Path(args.status_output), status)
    print(json.dumps(status, indent=2, sort_keys=True))


def _default_model(provider: str) -> str:
    if provider == "anthropic":
        return DEFAULT_ANTHROPIC_JUDGE_MODEL
    if provider == "local":
        return DEFAULT_LOCAL_JUDGE_MODEL
    return DEFAULT_OPENAI_JUDGE_MODEL


def _credential_env_var(provider: str) -> str:
    if provider == "anthropic":
        return "ANTHROPIC_API_KEY"
    if provider == "local":
        return "none required (local runtime)"
    return "OPENAI_API_KEY"


def _config_from_env(provider: str) -> object | None:
    if provider == "local":
        return local_judge_config_from_env()
    if provider == "anthropic":
        return anthropic_judge_config_from_env()
    return openai_judge_config_from_env()


def _build_judge_client(
    args: argparse.Namespace,
    env_config: object,
) -> tuple[object, object]:
    if args.provider == "local":
        config = LocalJudgeConfig(
            model=args.model or env_config.model,
            endpoint=args.endpoint or env_config.endpoint,
            api_key=env_config.api_key,
            timeout_seconds=args.timeout_seconds or env_config.timeout_seconds,
            max_output_tokens=args.max_output_tokens or env_config.max_output_tokens,
        )
        return config, LocalJudgeClient(config).judge_case
    if args.provider == "anthropic":
        config = AnthropicJudgeConfig(
            api_key=env_config.api_key,
            model=args.model or env_config.model,
            endpoint=args.endpoint or env_config.endpoint,
            anthropic_version=env_config.anthropic_version,
            timeout_seconds=args.timeout_seconds or env_config.timeout_seconds,
            max_output_tokens=args.max_output_tokens or env_config.max_output_tokens,
        )
        return config, AnthropicJudgeClient(config).judge_case
    config = OpenAIJudgeConfig(
        api_key=env_config.api_key,
        model=args.model or env_config.model,
        endpoint=args.endpoint or env_config.endpoint,
        timeout_seconds=args.timeout_seconds or env_config.timeout_seconds,
        max_output_tokens=args.max_output_tokens or env_config.max_output_tokens,
    )
    return config, OpenAIJudgeClient(config).judge_case


def _provider_error_status(
    provider: str,
    model: str,
    exc: OpenAIJudgeProviderError | AnthropicJudgeProviderError | LocalJudgeProviderError,
) -> dict[str, object]:
    status = {
        "status": "provider_error",
        "provider": provider,
        "model": model,
        "http_status_code": exc.status_code,
        "reason": exc.reason,
        "retry_after": exc.retry_after,
        "safe_error_summary": _safe_error_summary(provider, exc),
        "next_steps": _provider_error_next_steps(provider, exc),
    }
    if exc.response_body:
        status["provider_error_body_preview"] = exc.response_body[:500]
    return status


def _safe_error_summary(
    provider: str,
    exc: OpenAIJudgeProviderError | AnthropicJudgeProviderError | LocalJudgeProviderError,
) -> str:
    if exc.status_code == 429:
        return (
            f"{provider} returned HTTP 429. The key is being accepted, but the project or "
            "organization is currently blocked by rate, quota, billing, or usage limits."
        )
    return f"{provider} returned HTTP {exc.status_code} {exc.reason}."


def _provider_error_next_steps(
    provider: str,
    exc: OpenAIJudgeProviderError | AnthropicJudgeProviderError | LocalJudgeProviderError,
) -> list[str]:
    if exc.status_code == 429:
        return [
            f"Check the project and organization usage limits in the {provider} dashboard.",
            "Confirm billing or credits are active for the project that owns this API key.",
            "If this is a burst/rate limit, wait for the reset window before rerunning.",
            (
                "If retry-after is present, wait at least that long before rerunning "
                f"scripts/run_model_judge_eval.py --provider {provider} --run."
            ),
        ]
    return [
        "Review the provider error body preview.",
        "Confirm the API key, project, endpoint, and model are valid.",
    ]


def _local_unreachable_status(
    provider: str,
    config: LocalJudgeConfig,
    exc: URLError,
) -> dict[str, object]:
    return {
        "status": "local_runtime_unreachable",
        "provider": provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "safe_error_summary": (
            f"Could not reach the local judge endpoint {config.endpoint}: {exc.reason}."
        ),
        "next_steps": [
            "Start a local OpenAI-compatible server, e.g. run `ollama serve` and "
            "`ollama pull llama3.1:8b`.",
            "Confirm LOCAL_JUDGE_ENDPOINT matches the server (Ollama default is "
            "http://localhost:11434/v1/chat/completions).",
            "Then rerun scripts/run_model_judge_eval.py --provider local --run.",
        ],
    }


def _judge_parse_error_status(
    provider: str,
    model: str,
    exc: ValueError,
) -> dict[str, object]:
    return {
        "status": "judge_parse_error",
        "provider": provider,
        "model": model,
        "safe_error_summary": str(exc)[:500],
        "next_steps": [
            "The provider returned text that did not match the expected judge JSON schema.",
            "This is a provider-output formatting issue, not an API key or billing issue.",
            "Review the safe error summary, then rerun after updating parser or prompt handling.",
        ],
    }


if __name__ == "__main__":
    main()
