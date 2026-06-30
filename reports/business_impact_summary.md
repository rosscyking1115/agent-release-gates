# Business Impact Summary

## What this reframes

This summary re-expresses the agent-safety intervention study as an operational trade-off for reviewers and release owners. It adds no new measurement; it pairs each safeguard's safety gain with its review cost.

**3 layered safeguards address unsafe outcomes on their risk surfaces averaging ~0.42 extra reviews per unsafe outcome addressed.**

## Safety gain vs. review cost

| Safeguard | In-scope cases | Unsafe outcomes addressed / 100 | Extra reviews / 100 | Reviews per outcome |
| --- | ---: | ---: | ---: | ---: |
| Instruction hierarchy and prompt-injection controls | 12 | 75 | 66.7 | 0.89 |
| Action-risk policy and confirmation gate | 12 | 100 | 25 | 0.25 |
| Safety classifier and secondary review | 40 | 100 | 12.5 | 0.12 |

## Plain-language impact

- Per 100 prompt-injection attempt cases, Layered hierarchy agent prevents 75 unsafe outcomes at a cost of 66.7 extra human reviews (~0.89 extra reviews per unsafe outcome).
- Per 100 unsafe-action attempt cases, Layered action gate prevents 100 unsafe outcomes at a cost of 25 extra human reviews (~0.25 extra reviews per unsafe outcome).
- Per 100 unsafe request cases, Classifier plus release gate catches 100 unsafe outcomes at a cost of 12.5 extra human reviews (~0.12 extra reviews per unsafe outcome).

## Responsible boundary

> Rates are per 100 requests that reach each safeguard's risk surface in the controlled synthetic benchmark, not per unit of production traffic. These are engineering-evidence trade-offs, not production safety guarantees.
