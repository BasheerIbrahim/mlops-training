---
type: Domain Concept
title: Classification metrics
description: Accuracy, F1 and ROC AUC score a yes/no model in different ways; read them together on the same test set.
tags: [model-evaluation, metrics, accuracy, f1, roc-auc]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 1.1", "NIST-AI-RMF:MEASURE 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:50:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sklearn-metrics
    resource: https://scikit-learn.org/stable/modules/model_evaluation.html
    title: "Metrics and scoring: quantifying the quality of predictions"
    author: team:scikit-learn
  - id: google-mlcc-accuracy
    resource: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
    title: "Classification: Accuracy, recall, precision, and related metrics"
    author: team:google
  - id: google-mlcc-roc
    resource: https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc
    title: "Classification: ROC and AUC"
    author: team:google
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
---

# Definition

A classification metric gives one number for how well a model separates the classes. Lab 03 uses three metrics for the yes/no target `points_finish`:

- **Accuracy** is the fraction of predictions that are correct.[^sklearn-metrics] It counts right "yes" and right "no" answers together.[^google-mlcc-accuracy]
- **F1** is the harmonic mean of precision and recall.[^google-mlcc-accuracy] Precision is `tp / (tp + fp)`: of the predicted "yes", how many are right. Recall is `tp / (tp + fn)`: of the real "yes", how many the model finds.[^sklearn-metrics]
- **ROC AUC** is the area under the ROC curve. It needs a score or a probability for the positive class, not a hard 0/1 label.[^sklearn-metrics] It is the probability that the model ranks a random positive example above a random negative one. 1.0 is perfect; 0.5 is chance.[^google-mlcc-roc] The ROC curve covers all thresholds.[^google-mlcc-roc]

# Why it matters

Each metric can hide a weakness that another shows. Accuracy misleads on imbalanced data: a model that always says "no" scores 99 % when only 1 % of cases are "yes".[^google-mlcc-accuracy] F1 is better than accuracy for imbalanced classes.[^google-mlcc-accuracy] Accuracy and F1 depend on one cut-off (0.5); ROC AUC tells you how well the model orders the entries at every cut-off.

NIST asks teams to select metrics for the risks they found, to measure performance for conditions similar to deployment, and to document the measures.[^nist-ai-rmf] NIST also says that accuracy measures should consider false positive and false negative rates.[^nist-ai-rmf]

Kid version: accuracy asks "how many dishes did the judges like?" F1 asks "when the cook said 'this one is great', was it, and did the cook find all the great ones?" ROC AUC asks "can the cook put the dishes in order from best to worst?"

# Examples

All numbers are on the 2025 holdout (480 entries).

| Run | Accuracy | F1 | ROC AUC |
|---|---:|---:|---:|
| `grid-rule` (baseline) | 0.804 | 0.804 | 0.893 |
| `logreg-c1.0` | 0.835 | 0.837 | 0.906 |
| `forest-n100-dNone-l1` | 0.819 | 0.823 | 0.902 |
| `forest-n200-d5-l1` | 0.833 | 0.839 | 0.908 |
| `forest-n300-d8-l5` | 0.842 | 0.847 | 0.907 |
| `forest-n100-dNone-l1-leak` | 1.000 | 1.000 | 1.000 |

- Exactly half of the 2025 entries score points, so the classes are balanced. That is why accuracy and F1 are close in every run.
- The grid rule has a ROC AUC (0.893) because `train.py` gives it a score that falls with the grid position. ROC AUC needs a score, not only a 0/1 answer.
- The ranking changes with the metric: `forest-n300-d8-l5` has the best accuracy and F1, but `forest-n200-d5-l1` has the best ROC AUC.
- `train.py` computes the metrics with `accuracy_score`, `f1_score` and `roc_auc_score` from `sklearn.metrics`, and logs them to MLflow with `mlflow.log_metrics`.
- A 1.000 on all three metrics is a warning sign, not a success. See [Data leakage](/knowledge/mlops/data-leakage.md).

# Common mistakes

- One metric only. Accuracy alone hides problems with imbalanced classes and with ranking.
- Labels passed to `roc_auc_score`. It needs probabilities or scores, for example `predict_proba(X)[:, 1]`.[^sklearn-metrics]
- Metrics measured on the training data. Measure on held-out data. See [Temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).
- Small differences read as real. 0.842 against 0.835 is about 3 entries out of 480.
- Overall metrics only. The same model is right for 0.646 of rookie entries and 0.863 of the others. See [Subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md).

[^sklearn-metrics]: scikit-learn user guide, "Metrics and scoring", sections "Accuracy score", "Precision, recall and F-measures" and "Receiver operating characteristic (ROC)".
[^google-mlcc-accuracy]: Google Machine Learning Crash Course, "Classification: Accuracy, recall, precision, and related metrics".
[^google-mlcc-roc]: Google Machine Learning Crash Course, "Classification: ROC and AUC".
[^nist-ai-rmf]: NIST AI 100-1, section 3.1 "Valid and Reliable", MEASURE 1.1 (approaches and metrics selected) and MEASURE 2.3 (performance measured for deployment-like conditions and documented).
