# Safety Classifier Intervention Study

Status: evaluated

| Variant | Unsafe recall | High-severity false negatives | Benign false-positive rate | Review burden per 100 tasks |
| --- | ---: | ---: | ---: | ---: |
| No classifier | 0.00% | 18 | 0.00% | 0.00% |
| Single threshold classifier | 75.76% | 5 | 0.00% | 57.50 |
| Severity-aware threshold | 90.91% | 0 | 0.00% | 5.00 |
| Classifier plus secondary review | 100.00% | 0 | 0.00% | 12.50 |
| Classifier plus release gate | 100.00% | 0 | 0.00% | 12.50 |

## Findings

- Classifier plus secondary review improved unsafe capture from 0.00% to 100.00%.
- The mitigation adds review burden, making capacity planning part of the safety decision rather than an afterthought.

## Limitations

- This study formalizes the existing deterministic classifier results.
- Reviewer behavior is simulated until independent labels are collected.
