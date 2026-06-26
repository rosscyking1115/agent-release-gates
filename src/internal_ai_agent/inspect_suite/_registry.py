"""Inspect entry-point registry.

Referenced by ``[project.entry-points.inspect_ai]`` so ``inspect eval`` can discover
the suite's tasks once ``inspect_ai`` is installed.
"""

from internal_ai_agent.inspect_suite.tasks import incident_replay

__all__ = ["incident_replay"]
