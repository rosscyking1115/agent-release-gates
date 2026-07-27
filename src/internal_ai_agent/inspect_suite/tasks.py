"""Inspect tasks for the agent-release-gates safety suite.

``inspect eval incident_replay --model <provider/model>`` runs any model as the
operations agent on the built-in incident pack and scores it with the project's
release-gate logic. The task registers under its bare name via the ``inspect_ai``
entry point; a package-prefixed reference is not resolvable.

The dataset is 8 self-authored synthetic incidents, so this is a conformance smoke
check, not a benchmark that can rank models.
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import generate, system_message

from internal_ai_agent.evals.incident_replay import _default_incident_cases
from internal_ai_agent.inspect_suite.scorers import incident_safety_scorer
from internal_ai_agent.providers.agent_runner import incident_prompt, system_prompt


@task
def incident_replay() -> Task:
    samples = [
        Sample(
            id=str(case["case_id"]),
            input=incident_prompt(case),
            target=str(case["expected_behavior"]),
            metadata=dict(case),
        )
        for case in _default_incident_cases()
    ]
    return Task(
        dataset=MemoryDataset(samples=samples),
        solver=[system_message(system_prompt()), generate()],
        scorer=incident_safety_scorer(),
    )
