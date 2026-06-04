# Safety Prevalence And Classifier Evaluation Module Plan

## Purpose

Add a safety evaluation module that measures how a safety classifier or rule layer behaves under synthetic sampled traffic, not only curated red-team cases.

The module should answer:

- Which unsafe request categories are simulated?
- How well does the classifier catch them?
- Which benign requests are over-blocked?
- Which unsafe requests slip through?
- How does the threshold affect false positives, false negatives, and review burden?
- What mitigation changes improve safety without hiding trade-offs?

The module should keep three tracks separate:

- challenge evaluation for enriched harmful and adversarial cases
- sampled prevalence estimation for weighted synthetic traffic samples
- decision support for thresholds, review policy, and residual risk

## Research Basis

- NIST AI RMF frames AI risk management as practical, rights-preserving, operational risk work for systems that should be designed, evaluated, and monitored responsibly: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- OWASP GenAI guidance highlights prompt injection, sensitive information disclosure, excessive agency, insecure output handling, and related LLM application risks: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OpenAI moderation docs expose a useful classifier contract: per-category flags and category scores, with a warning that score-based custom policies may need recalibration over time: https://platform.openai.com/docs/guides/moderation
- scikit-learn documents precision, recall, threshold curves, and classification metrics that map directly to false-positive and false-negative trade-offs: https://scikit-learn.org/stable/modules/model_evaluation.html
- OpenAI safety evaluation reporting separates safety categories and uses automatic scoring for unsafe-output checks, which supports category-level reporting rather than one aggregate score: https://openai.com/safety/evaluations-hub/
- NIST/SEMATECH statistical guidance supports confidence intervals around measured proportions, which matters when unsafe events are rare: https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm

## Scope

This is a synthetic policy-evaluation module, not a real moderation service and not a production safety certification.

Included:

- synthetic harmful and unsafe request categories
- benign near-miss and ambiguous requests
- deterministic classifier/rule score contract
- threshold sweep and operating-point selection
- false positive / false negative analysis
- prevalence estimation from sampled synthetic cases
- human-review queue simulation
- mitigation impact dashboard
- threshold decision memo

Excluded:

- real user traffic
- real harmful instructions
- claims about production moderation quality
- confidential employer policies
- external API dependency in CI

## Proposed Unsafe Categories

Use policy-oriented labels that align with the current lab without publishing actionable harmful details:

| Category | Example Intent Shape | Severity |
| --- | --- | --- |
| `prompt_injection` | Override assistant instructions or retrieved-document priority | high |
| `sensitive_data_request` | Ask for private customer, employee, credential, or hidden-policy data | high |
| `system_prompt_leakage` | Ask the agent to reveal hidden instructions | medium |
| `approval_bypass` | Ask the agent to skip human approval for side effects | high |
| `tool_misuse` | Ask for unauthorized mock routing or escalation actions | high |
| `unsafe_financial_action` | Ask for real-world financial action outside the synthetic scope | high |
| `weak_evidence_pressure` | Push the agent to answer without enough evidence | medium |
| `retrieved_context_attack` | Unsafe instruction embedded in retrieved context | high |
| `unbounded_consumption` | Ask for excessive or runaway processing | medium |
| `benign_near_miss` | Legitimate request that resembles a blocked category | low |

## Proposed Artifacts

```text
data/eval/safety_prevalence_cases.jsonl
data/eval/safety_challenge_cases.jsonl
config/safety_taxonomy.yaml
reports/safety_classifier_eval_cases.jsonl
reports/safety_classifier_eval_summary.json
reports/safety_threshold_sweep.json
reports/safety_human_review_simulation.json
reports/safety_prevalence_report.md
docs/safety_threshold_decision_memo.md
```

## Case Schema

```text
case_id
sample_batch_id
request_text
true_label
risk_category
risk_severity
is_unsafe
near_miss
expected_action
review_required
synthetic_prevalence_bucket
```

## Classifier Output Schema

```text
case_id
classifier_version
threshold
category_scores
max_score
predicted_unsafe
predicted_category
decision
review_queue
review_reason
mitigation_applied
```

## Metrics

Core:

- total sampled cases
- estimated unsafe prevalence
- confidence interval for prevalence estimates
- true positives, true negatives, false positives, false negatives
- precision, recall, false positive rate, false negative rate
- specificity, negative predictive value, and PR-AUC / average precision
- calibration by score bucket
- high-severity false negative count
- benign near-miss false positive count
- category-level precision and recall

Review workflow:

- review queue count
- review queue share
- reviewer catch rate
- reviewer correction count
- reviewer disagreement and adjudication count
- unresolved risk count
- estimated reviewer capacity breach

Mitigation impact:

- pre-mitigation high-severity false negatives
- post-mitigation high-severity false negatives
- false positive increase after mitigation
- review-load increase after mitigation
- net risk reduction score

## Dashboard Shape

Add a new Streamlit view: `Safety Prevalence`.

Expected sections:

- prevalence overview
- classifier confusion matrix
- category performance table
- taxonomy heatmap by category and severity
- threshold tuning curve
- strict / balanced / permissive policy comparison
- false positive / false negative examples
- human review queue simulation
- mitigation impact comparison
- threshold decision memo download or preview

## Prevalence Design

Do not estimate prevalence from the intentionally enriched harmful challenge set. Instead, generate a separate sampled stream with visible sampling strata and weights.

Recommended strata:

- auto-allowed requests
- auto-blocked requests
- human-reviewed requests
- low, middle, and high score bands
- request route or surface
- category and severity where known

The report should show weighted prevalence estimates, sample counts, uncertainty intervals, and a clear note that the stream is synthetic rather than real production traffic.

## Human Review Policy

Use a three-band workflow:

- low score: auto-allow
- middle score or ambiguous category: human review
- high score or high-severity deterministic rule: auto-block or escalate

The simulation should model reviewer labels, double review on a subset, disagreement, adjudication, queue time, reviewer capacity, escalation reason, and final action.

## Threshold Tuning Policy

Avoid optimizing only one global F1 score.

Recommended approach:

- use per-category thresholds
- minimize high-severity false negatives even if review load increases
- cap false positives for benign productivity-sensitive requests
- route ambiguous cases to review instead of forcing a binary allow/block
- tune thresholds on validation data, freeze them, then report final test metrics
- present strict, balanced, and permissive threshold options in the dashboard

## Release Gate Additions

Potential blocking gates:

- high-severity false negatives must be zero after mitigation
- review simulation must catch all high-severity borderline cases
- category coverage must include prompt injection, sensitive data, approval bypass, tool misuse, and retrieved-context attacks

Potential warning gates:

- false positive rate above selected tolerance
- review queue exceeds simulated reviewer capacity
- prevalence sample size below target

## Implementation Sequence

1. Add safety taxonomy and separate challenge versus sampled-prevalence datasets.
2. Build deterministic classifier/rule scoring.
3. Generate confusion-matrix, PR/ROC, calibration, and threshold-sweep reports.
4. Add weighted prevalence estimation with confidence intervals.
5. Add human-review simulation.
6. Add mitigation-impact report.
7. Surface the module in FastAPI, Streamlit, public report, and release gates.
8. Add the threshold decision memo.
9. Regenerate reports, update README/docs, and verify CI.

## Fit With Current Project

This module strengthens the project because current safety evaluation is mostly a deterministic red-team pass/fail suite. The new module adds a practical operating question: how should an internal AI system set safety thresholds when unsafe requests are rare, benign near-misses exist, and human review capacity is limited?
