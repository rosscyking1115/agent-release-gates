# Agent Safety Intervention Study

## Abstract

This study upgrades the lab from a benchmark-only artifact into a mitigation-aware evaluation. In controlled synthetic operations-agent settings, layered safeguards are compared against frozen baseline behavior while reporting safety gains and operational costs.

## Motivation

Agent safety work should show whether a safeguard reduces a concrete failure mode, and whether it introduces review burden, over-blocking, or usefulness loss.

## Threat Model

The study covers lower-priority prompt injection in retrieved/tool content, unsafe side-effecting mock actions, and unsafe requests that may need classifier or human-review intervention.

## Related Work Anchors

- AgentDojo: https://arxiv.org/abs/2406.13352
- tau-bench: https://arxiv.org/abs/2406.12045
- AI Agents That Matter: https://arxiv.org/abs/2407.01502
- ToolSandbox: https://arxiv.org/abs/2408.04682
- OpenAI instruction hierarchy: https://openai.com/index/the-instruction-hierarchy/
- OpenAI Operator System Card: https://openai.com/index/operator-system-card/
- Anthropic agentic misalignment: https://www.anthropic.com/research/agentic-misalignment

## Results

| Experiment | Cases | Recommended variant | Baseline | Recommended | Delta | Review burden / 100 |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Instruction hierarchy and prompt-injection controls | 12 | Layered hierarchy agent | 75.00% | 0.00% | 75.00% | 66.67 |
| Action-risk policy and confirmation gate | 12 | Layered action gate | 100.00% | 0.00% | 100.00% | 25.0 |
| Safety classifier and secondary review | 40 | Classifier plus release gate | 0.00% | 100.00% | 100.00% | 12.5 |

## Main Finding

Layered safeguards reduced selected prompt-injection, unsafe-action, and unsafe-request failures in deterministic controlled studies while making review burden and over-blocking visible.

## Responsible Release Boundary

Results are controlled benchmark evidence. They are not production safety claims and should be strengthened with independent human labels.

## Future Work

- Collect independent labels for the prepared external review packet.
- Expand the intervention studies with repeated hosted model runs.
- Add grounding/abstention and memory-pollution intervention tracks.
