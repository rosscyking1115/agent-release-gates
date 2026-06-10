# Action Gate Intervention

Status: evaluated

| Variant | Unsafe action attempt rate | Side-effect block rate | Useful completion rate | Review burden per 100 tasks |
| --- | ---: | ---: | ---: | ---: |
| Baseline tool router | 100.00% | 0.00% | 50.00% | 0.00% |
| Confirmation gate | 0.00% | 100.00% | 50.00% | 50.00 |
| Risk classifier gate | 50.00% | 50.00% | 50.00% | 0.00% |
| Layered action gate | 0.00% | 100.00% | 50.00% | 25.00 |

## Findings

- Layered action gating reduced unsafe action execution from 100.00% to 0.00%.
- The strongest variant adds review burden for high-risk actions, but preserves low-risk read-only completion.

## Limitations

- The study uses mock actions only; no real side effects are possible.
- Risk classification is deterministic and policy-based.
