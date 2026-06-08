from __future__ import annotations

import argparse
import json
from pathlib import Path

from internal_ai_agent.evals.model_judge import (
    dry_run_status,
    evaluate_hosted_model_judge,
)
from internal_ai_agent.io import write_json
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
        "--model",
        default=None,
        help="Hosted judge model id.",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help="Responses API endpoint.",
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
    requested_model = args.model or DEFAULT_OPENAI_JUDGE_MODEL

    if not args.run:
        status = dry_run_status(project_root, provider="openai", model=requested_model)
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        return

    env_config = openai_judge_config_from_env()
    if env_config is None:
        status = {
            **dry_run_status(project_root, provider="openai", model=requested_model),
            "status": "blocked",
            "reason": "OPENAI_API_KEY is not set.",
        }
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1)

    config = OpenAIJudgeConfig(
        api_key=env_config.api_key,
        model=args.model or env_config.model,
        endpoint=args.endpoint or env_config.endpoint,
        timeout_seconds=args.timeout_seconds or env_config.timeout_seconds,
        max_output_tokens=args.max_output_tokens or env_config.max_output_tokens,
    )
    client = OpenAIJudgeClient(config)
    try:
        report = evaluate_hosted_model_judge(
            project_root,
            judge_case=client.judge_case,
            provider="openai",
            model=config.model,
        )
    except OpenAIJudgeProviderError as exc:
        status = _provider_error_status(config, exc)
        write_json(Path(args.status_output), status)
        print(json.dumps(status, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    status = {
        "status": "completed",
        "provider": "openai",
        "model": config.model,
        "summary_path": "reports/model_judge_eval_summary.json",
        "cases_path": "reports/model_judge_eval_cases.jsonl",
        "case_count": report["case_count"],
        "metrics": report["summary"],
        "publication_review": report["publication_review"],
    }
    write_json(Path(args.status_output), status)
    print(json.dumps(status, indent=2, sort_keys=True))


def _provider_error_status(
    config: OpenAIJudgeConfig,
    exc: OpenAIJudgeProviderError,
) -> dict[str, object]:
    status = {
        "status": "provider_error",
        "provider": "openai",
        "model": config.model,
        "http_status_code": exc.status_code,
        "reason": exc.reason,
        "retry_after": exc.retry_after,
        "safe_error_summary": _safe_error_summary(exc),
        "next_steps": _provider_error_next_steps(exc),
    }
    if exc.response_body:
        status["provider_error_body_preview"] = exc.response_body[:500]
    return status


def _safe_error_summary(exc: OpenAIJudgeProviderError) -> str:
    if exc.status_code == 429:
        return (
            "OpenAI returned HTTP 429. The key is being accepted, but the project or "
            "organization is currently blocked by rate, quota, billing, or usage limits."
        )
    return f"OpenAI returned HTTP {exc.status_code} {exc.reason}."


def _provider_error_next_steps(exc: OpenAIJudgeProviderError) -> list[str]:
    if exc.status_code == 429:
        return [
            "Check the project and organization usage limits in the OpenAI dashboard.",
            "Confirm billing or credits are active for the project that owns this API key.",
            "If this is a burst/rate limit, wait for the reset window before rerunning.",
            (
                "If retry-after is present, wait at least that long before rerunning "
                "scripts/run_model_judge_eval.py --run."
            ),
        ]
    return [
        "Review the provider error body preview.",
        "Confirm the API key, project, endpoint, and model are valid.",
    ]


if __name__ == "__main__":
    main()
