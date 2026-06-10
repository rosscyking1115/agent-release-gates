# RAG Grounding Intervention Study

## Abstract

This study evaluates deterministic grounding and abstention controls over public TechQA and WixQA RAG cases. It measures whether evidence thresholds reduce unsupported answer attempts and what usefulness or review burden they introduce.

## Results

| Variant | Cases | Unsupported answer rate | Useful answer rate | False abstention/review | Impossible intercept | Review burden / 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline public retriever | 240 | 20.67% | 75.96% | 3.37% | 34.38% | 0.00 |
| Citation-required answering | 240 | 20.67% | 75.96% | 3.37% | 34.38% | 0.00 |
| Moderate evidence gate | 240 | 16.35% | 72.60% | 11.06% | 46.88% | 0.00 |
| Strict grounding gate | 240 | 9.62% | 63.46% | 26.92% | 56.25% | 0.00 |
| Strict gate with review | 240 | 9.62% | 63.46% | 26.92% | 56.25% | 30.83 |

## Findings

- A moderate evidence gate reduces unsupported public-RAG answer attempts by 4.32% absolute while keeping useful-answer rate at 72.60%.
- A stricter grounding gate reduces unsupported answer attempts by 11.05% absolute but increases false abstention/review to 26.92%.
- Routing strict low-evidence cases to review makes the operational cost explicit: 30.83 reviews per 100 public-RAG cases.

## Recommendations

- Use the moderate evidence gate as the default public-RAG release guard until a stronger reranker or model judge is validated.
- Keep the strict gate as a high-risk mode where unsupported answers are more costly than manual review or abstention.
- Evaluate the same thresholds against a provider-backed reranker before claiming model-level improvements.

## Limitations

- The intervention is deterministic and uses public benchmark labels only for scoring, not for making decisions.
- The study measures answer/citation decisions, not natural-language answer quality.
- Thresholds are intentionally simple so the result is reproducible in CI and public deployment.
