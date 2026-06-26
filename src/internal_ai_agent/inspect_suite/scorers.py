"""Inspect scorer that grades a model run with the agent-release-gates safety gate."""

from __future__ import annotations

from typing import Any

from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, mean, scorer
from inspect_ai.solver import TaskState

from internal_ai_agent.inspect_suite.scoring import score_incident


@scorer(metrics=[accuracy(), mean()])
def incident_safety_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        case: dict[str, Any] = dict(state.metadata or {})
        result = score_incident(
            case,
            state.output.completion,
            model_version=str(state.model),
        )
        return Score(
            value=CORRECT if result["passed"] else INCORRECT,
            answer=str(result["decision"]),
            explanation=(
                f"decision={result['decision']}; "
                f"expected_behavior_match={result['expected_behavior_match']}; "
                f"must_not_violations={result['must_not_violations']}"
            ),
            metadata=result,
        )

    return score
