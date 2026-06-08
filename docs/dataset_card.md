# Dataset Card

## Dataset Summary

This project uses two clearly separated data sources:

- Synthetic internal-operations data generated locally for controlled evaluation.
- A compact public TechQA-RAG-Eval sample for external retrieval validation.

The synthetic data is designed for safety and reproducibility. It does not contain real company documents, customer data, employee data, credentials, production logs, or confidential workflows.

## Synthetic Internal-Operations Data

| Asset | Current count | Purpose |
| --- | ---: | --- |
| Runbook sections | 24 | Grounded retrieval and citation |
| Synthetic operations tickets | 180 | Structured extraction and routing |
| Golden evaluation cases | 358 | Retrieval, citation, abstention, and answer checks |
| Red-team cases | 60 | Safety, prompt-injection, and policy-resistance checks |
| Safety classifier challenge cases | 40 | Classifier/rule threshold evaluation |
| Safety secondary-floor validation cases | 39 | Ambiguous medium-severity review-floor validation |
| Safety prevalence sampled cases | 80 | Weighted synthetic prevalence and review-load estimation |

## Public TechQA Track

The public validation track uses a 160-case compact sample from NVIDIA TechQA-RAG-Eval. It is used only for external technical-support retrieval and abstention validation. It is not treated as internal-operations data.

Current profile:

- 128 answerable cases
- 32 impossible cases
- 119 unique public documents
- Apache-2.0 upstream dataset license

## Label Sources

Synthetic labels are generated and maintained inside the repo:

- expected source ids
- expected issue categories
- expected next actions
- expected abstention behavior
- risk categories and severity bands
- simulated reviewer outcomes

The project includes a 24-case maintainer-labeled calibration sample for checking classifier/rubric behavior against adjudicated labels. It does not yet publish independent external human labels, so external review should still be reported separately when added.

## Collection Process

Synthetic data is generated with local deterministic scripts. Public TechQA data is prepared only when the upstream `train.json` is downloaded into `data/public/techqa_train.json`, then sampled through the preparation script.

## Safety And Privacy

The dataset boundary is intentionally conservative:

- no real personal data
- no real company documents
- no real operational procedures
- no real financial actions
- no production traffic
- mock tools only

## Limitations

- Synthetic cases can overstate performance if the generator and evaluator share assumptions.
- Some ticket and runbook text is still templated despite manual-case expansion.
- Simulated reviewer labels are useful for workflow testing but are not a substitute for independent human review.
- The maintainer-labeled calibration sample is useful for reproducibility and rubric debugging, but it is not an external annotation study.
- The local rubric judge is deterministic and transparent; the hosted judge track currently has one reviewed OpenAI calibration run, not a multi-model comparison.
- Public TechQA coverage is compact and should be expanded before drawing broader external conclusions.

## Recommended Dataset Work

- Add more hand-authored benign, ambiguous, unsafe, prompt-injection, weak-evidence, excessive-agency, and tool-misuse cases.
- Add independent reviewer labels for the calibration sample.
- Track inter-rater agreement and reviewer-disagreement reasons.
- Extend the hosted LLM judge comparison beyond the first reviewed OpenAI run and publish judge disagreement slices.
- Expand public TechQA coverage beyond the compact sample.
- Keep synthetic and public-data metrics separated in every public report.
