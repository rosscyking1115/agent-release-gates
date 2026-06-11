# Goal Conflict Intervention Study

## Abstract

This controlled study evaluates whether an agent can arbitrate between user goals and safety, evidence, privacy, and tool-risk constraints while still completing benign tasks.

## Results

| Variant | Cases | Unsafe goal complied | Conflict detected | Safe alternative offered | High-risk action blocked | Benign goal completed | Review burden / 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline goal-following agent | 12 | 100.00% | 0.00% | 0.00% | 0.00% | 100.00% | 0.00 |
| Policy-aware planner | 12 | 62.50% | 37.50% | 0.00% | 0.00% | 100.00% | 0.00 |
| Evidence-priority planner | 12 | 75.00% | 25.00% | 12.50% | 0.00% | 100.00% | 0.00 |
| Tool-risk-aware planner | 12 | 75.00% | 25.00% | 12.50% | 100.00% | 100.00% | 0.00 |
| Layered goal arbitration with review | 12 | 0.00% | 100.00% | 37.50% | 100.00% | 100.00% | 58.33 |

## Findings

- Layered goal arbitration reduced unsafe-goal compliance by 100.00% absolute compared with the baseline goal-following agent.
- The recommended variant detects 100.00% of goal conflicts and offers a safe alternative in 37.50%.
- The mitigation preserves benign-goal completion at 100.00% while adding 58.33 reviews per 100 cases.

## Recommendations

- Separate user-intent satisfaction from goal acceptance: agents should help with safe alternatives when the requested goal conflicts with policy, evidence, privacy, or tool-risk boundaries.
- Use layered arbitration for high-risk goals so safety policy, evidence quality, and tool approval checks can override raw goal following.
- Track benign completion rate alongside unsafe-goal compliance so goal-conflict controls do not turn into broad refusal behavior.

## Limitations

- This is a deterministic controlled study over synthetic goal conflicts.
- Real production validation would need live task traces, human labels, and repeated hosted-model runs.
- The review layer is simulated and should be calibrated with external reviewers.
