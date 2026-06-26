"""Inspect (UK AISI) packaging for the agent-release-gates safety suite.

The pure ``scoring`` module reuses the project's deterministic release-gate logic
and has no ``inspect_ai`` dependency, so it is tested in CI. The ``tasks`` /
``scorers`` / ``_registry`` modules import ``inspect_ai`` and are loaded only when
the optional peer dependency is installed (``pip install inspect_ai``), exposing
``inspect eval agent-release-gates/incident_replay --model <provider/model>``.
"""
