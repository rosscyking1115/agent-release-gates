# Instruction Hierarchy Intervention

Status: evaluated

| Variant | Prompt-injection attack success rate | Conflict detection rate | Benign task success rate | Review burden per 100 cases |
| --- | ---: | ---: | ---: | ---: |
| Baseline agent | 75.00% | 25.00% | 100.00% | 0.00% |
| Hierarchy-prompt agent | 37.50% | 62.50% | 100.00% | 41.67 |
| Hierarchy-validator agent | 0.00% | 100.00% | 75.00% | 75.00 |
| Layered hierarchy agent | 0.00% | 100.00% | 100.00% | 66.67 |

## Findings

- Layered hierarchy controls reduced prompt-injection attack success from 75.00% to 0.00%.
- The layered variant preserved benign task success while adding an audit event for lower-priority instruction conflicts.

## Limitations

- This is a deterministic controlled study, not a live model red-team run.
- Cases are synthetic and intentionally small so CI can reproduce the result.
