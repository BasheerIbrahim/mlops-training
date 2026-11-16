---
type: Domain Concept
title: Baseline model
description: A simple rule or trivial model that sets the score a learned model must beat before it is worth the extra cost.
tags: [model-evaluation, baseline, sanity-check]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.3", "NIST-AI-RMF:MANAGE 1.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:10:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sklearn-dummy
    resource: https://scikit-learn.org/stable/modules/model_evaluation.html#dummy-estimators
    title: "Metrics and scoring: quantifying the quality of predictions — Dummy estimators"
    author: team:scikit-learn
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
---

# Definition

A baseline model is the simplest prediction that you can make without machine learning, or with a trivial model. Examples are "always predict the most common label" or a rule of thumb from domain experts. You measure the baseline on the same test set and with the same metrics as the real models.

scikit-learn calls this a simple sanity check: compare your estimator against simple rules of thumb. Its `DummyClassifier` offers such rules, for example `most_frequent`, `stratified` and `uniform`. These rules ignore the input data.[^sklearn-dummy]

# Why it matters

A model score means nothing alone. "84 % right" is good only if a simple rule does not get 84 % too. When a classifier is too close to a trivial rule, something is probably wrong: the features do not help, a hyperparameter is badly set, or the classes are imbalanced.[^sklearn-dummy]

The baseline also answers a business question: is the model worth the cost to build, deploy and monitor it? NIST asks for a decision on whether the AI system achieves its intended purpose and whether development or deployment should proceed.[^nist-ai-rmf] NIST also notes that a system that augments or replaces human decisions needs baseline metrics for comparison.[^nist-ai-rmf]

Kid version: before the cook-off, the judges taste a sandwich from the shop. Every cook must make something better than that sandwich, or the cook-off is a waste of time.

# Examples

- Lab 03 uses the grid rule as the baseline: "start in the top 10, score points". It learns nothing. On the 2025 holdout it scores accuracy 0.804, F1 0.804 and ROC AUC 0.893.
- The grid rule is a strong baseline because it uses expert knowledge. A coin toss or "always predict points" would score about 0.5, because half of the entries score points.
- The logistic regression scores 0.835 and the best honest random forest 0.842. They beat the rule by 3 to 4 points of accuracy, about 15 to 18 more right answers out of 480.
- The baseline run `grid-rule` is in the MLflow experiment `f1-points-finish` with all other runs. It has no logged model, because there is nothing to save.

# Common mistakes

- No baseline at all. The team celebrates 84 % and does not know that a one-line rule gets 80 %.
- A baseline that is too weak. "Always predict points" (about 50 %) makes any model look good. Use the best simple rule that the domain experts use today.
- A baseline measured on different data or a different metric. It must use the same test set (here 2025) and the same metrics.
- Forgetting subgroups. The grid rule is right for only 0.521 of rookie entries. A model can beat the baseline overall and still be weak for a group. See [Subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md).

[^sklearn-dummy]: scikit-learn user guide, section "Dummy estimators".
[^nist-ai-rmf]: NIST AI 100-1, section 1.2.1 ("Human baseline"), MANAGE 1.1 and MEASURE 2.3.
