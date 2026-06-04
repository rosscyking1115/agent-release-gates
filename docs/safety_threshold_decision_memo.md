# Safety Threshold Decision Memo Template

Status: planned template for the Safety Prevalence & Classifier Evaluation module.

## 1. Scope And Intended Use

Describe the classifier or rule layer being evaluated, the synthetic request surfaces covered, and the actions available to the system: auto-allow, review, block, or escalate.

## 2. Taxonomy And Policy Boundaries

List each unsafe category, severity band, allowed/disallowed boundary, benign near-neighbor, and whether the category has a deterministic high-severity rule.

## 3. Dataset Design

Separate:

- enriched challenge cases used to test robustness
- sampled prevalence cases used to estimate synthetic operational base rates
- benign near-miss cases used to measure overblocking

State all sampling weights and limitations.

## 4. Evaluation Method

Summarize classifier scores, deterministic rules, thresholds, validation/test split, human-review simulation, and adjudication logic.

## 5. Results

Report:

- precision, recall, specificity, false positive rate, and false negative rate
- high-severity false negatives
- benign near-miss false positives
- prevalence estimates with confidence intervals
- review queue volume and capacity risk
- category-level performance

## 6. Threshold Options

Compare strict, balanced, and permissive policies.

| Option | Target | Expected benefit | Main cost |
| --- | --- | --- | --- |
| Strict | Minimize unsafe pass-through | Lower high-severity false negatives | Higher review and overblock rate |
| Balanced | Keep high-severity risk low with manageable review | Practical default | Some benign overblocking |
| Permissive | Reduce overblocking | Lower reviewer burden | Higher unsafe pass-through risk |

## 7. Mitigation Impact

Show before/after impact for rules, thresholds, and review routing. Include false-negative reduction, false-positive increase, review-load change, latency/cost impact, and residual risk.

## 8. Residual Risks And Monitoring

Document remaining unsafe categories, ambiguous policy areas, brittle rules, likely paraphrase gaps, and dashboard indicators to monitor over time.

## 9. Recommendation

Choose one:

- proceed
- proceed with guardrails
- hold

State the recommended threshold policy and human-review policy.

## 10. Owners And Review Cadence

Name the synthetic owner role, review cadence, rollback trigger, and artifact regeneration command.
