# Memory Context Intervention Study

## Abstract

This controlled study evaluates whether an agent can resist stale, cross-user, injected, or conflicting memory while still using benign memory when it is scoped and useful.

## Results

| Variant | Cases | Polluted memory followed | Pollution detected | Current evidence prioritized | Cross-user leak | Benign memory useful | Review burden / 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline memory-enabled agent | 12 | 100.00% | 0.00% | 0.00% | 100.00% | 100.00% | 0.00 |
| Recency-filtered memory | 12 | 50.00% | 50.00% | 50.00% | 100.00% | 100.00% | 0.00 |
| Source-trust filtered memory | 12 | 75.00% | 25.00% | 25.00% | 100.00% | 100.00% | 0.00 |
| Scoped memory store | 12 | 0.00% | 100.00% | 100.00% | 0.00% | 100.00% | 0.00 |
| Scoped memory with review | 12 | 0.00% | 100.00% | 100.00% | 0.00% | 50.00% | 66.67 |

## Findings

- Scoped memory with review reduced polluted-memory following by 100.00% absolute compared with the baseline memory agent.
- The recommended variant prioritizes current evidence in 100.00% of polluted-memory cases.
- The mitigation preserves benign-memory usefulness at 50.00% while adding 66.67 reviews per 100 cases.

## Recommendations

- Treat memory as untrusted context unless it is scoped, recent, source-attributed, and consistent with current evidence.
- Route privacy-sensitive or injected memory conflicts to review instead of silently using remembered context.
- Keep benign-memory usefulness visible so safety controls do not turn memory off entirely.

## Limitations

- This is a deterministic controlled study, not a live long-term memory system.
- Cases are synthetic because real memory pollution would require sensitive or cross-user state.
- Reviewer behavior is simulated until external reviewers label memory-conflict cases.
