# RAG Grounding Intervention Study

## Abstract

This study evaluates deterministic grounding and abstention controls over public TechQA and WixQA RAG cases. It measures whether evidence thresholds reduce unsupported answer attempts and what usefulness or review burden they introduce.

## Results

| Variant | Cases | Unsupported answer rate | Useful answer rate | False abstention/review | Impossible intercept | Review burden / 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline public retriever | 640 | 28.86% | 68.01% | 3.12% | 11.46% | 0.00 |
| Citation-required answering | 640 | 28.86% | 68.01% | 3.12% | 11.46% | 0.00 |
| Moderate evidence gate | 640 | 23.53% | 65.99% | 10.48% | 28.12% | 0.00 |
| Strict grounding gate | 640 | 19.12% | 60.66% | 20.22% | 38.54% | 0.00 |
| Strict gate with review | 640 | 19.12% | 60.66% | 20.22% | 38.54% | 22.97 |

## Findings

- A moderate evidence gate reduces unsupported public-RAG answer attempts by 5.33% absolute while keeping useful-answer rate at 65.99%.
- A stricter grounding gate reduces unsupported answer attempts by 9.74% absolute but increases false abstention/review to 20.22%.
- Routing strict low-evidence cases to review makes the operational cost explicit: 22.97 reviews per 100 public-RAG cases.

## Recommendations

- Use the moderate evidence gate as the default public-RAG release guard until a stronger reranker or model judge is validated.
- Keep the strict gate as a high-risk mode where unsupported answers are more costly than manual review or abstention.
- Evaluate the same thresholds against a provider-backed reranker before claiming model-level improvements.

## Limitations

- The intervention is deterministic and uses public benchmark labels only for scoring, not for making decisions.
- The study measures answer/citation decisions, not natural-language answer quality.
- Thresholds are intentionally simple so the result is reproducible in CI and public deployment.
