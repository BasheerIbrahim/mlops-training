---
type: Domain Concept
title: Random forest
description: An ensemble of decision trees, each grown on a random sample of rows and features, whose combined vote is steadier than one tree.
tags: [model, classification, ensemble, decision-tree, scikit-learn]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 2.1", "NIST-AI-RMF:MEASURE 2.5"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:30:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: breiman-2001
    resource: https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf
    title: Random Forests (Machine Learning 45(1), 5-32, 2001; doi:10.1023/A:1010933404324)
    author: Leo Breiman
  - id: sklearn-rf-guide
    resource: https://scikit-learn.org/stable/modules/ensemble.html#random-forests
    title: "Ensembles — Random forests"
    author: team:scikit-learn
  - id: sklearn-rf-api
    resource: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    title: sklearn.ensemble.RandomForestClassifier (scikit-learn 1.9.1)
    author: team:scikit-learn
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
---

# Definition

A random forest is a combination of tree predictors. Each tree depends on a random vector that is sampled independently and with the same distribution for all trees.[^breiman-2001] In scikit-learn, each tree is built from a bootstrap sample (rows drawn with replacement) of the training set. At each split, the tree looks at a random subset of the features.[^sklearn-rf-guide]

One decision tree has high variance and tends to overfit. The two sources of randomness make the errors of the trees less related. When you average the trees, some errors cancel out.[^sklearn-rf-guide] Breiman's forests let the trees vote for the most popular class. scikit-learn averages the predicted probabilities of the trees instead.[^sklearn-rf-guide]

# Why it matters

A random forest finds non-linear patterns and interactions between inputs without manual feature work. For example, a good grid position may count for less on a street circuit in the rain. It works well on tables of mixed numeric data.

Its defaults can overfit. The default `max_depth=None` and `min_samples_leaf=1` grow fully developed, unpruned trees.[^sklearn-rf-api] Each tree can then learn the training rows by heart. NIST asks teams to show that the model to deploy is valid and reliable, and to document the limits of its generalisation.[^nist-ai-rmf] A score on held-out data is the evidence.

Kid version: one cook can have strange habits. A forest asks 300 cooks, each with a different shopping basket, and takes the average of their opinions.

# Examples

In lab 03 the forest uses the same seven inputs as the logistic regression. The 2025 scores:

| Run | Trees | Max depth | Min rows per leaf | Accuracy | F1 | ROC AUC |
|---|---:|---:|---:|---:|---:|---:|
| `forest-n100-dNone-l1` | 100 | none | 1 | 0.819 | 0.823 | 0.902 |
| `forest-n200-d5-l1` | 200 | 5 | 1 | 0.833 | 0.839 | 0.908 |
| `forest-n300-d8-l5` | 300 | 8 | 5 | 0.842 | 0.847 | 0.907 |

- The default forest (0.819) is worse than the logistic regression (0.835). Its trees learn the training data too closely. Limits on depth and leaf size fix this.
- `forest-n300-d8-l5` is the best honest model. It is registered as `f1-points-finish` version 1.
- MLflow 3.18 saves scikit-learn models in the skops format. A forest contains `sklearn.tree._tree.Tree` objects, so `train.py` passes `skops_trusted_types` to `mlflow.sklearn.log_model`. See [Model registry](/knowledge/mlops/model-registry.md).

# Common mistakes

- Trusting the defaults. Fully grown trees can overfit, as the default run shows.
- Comparing forests only on accuracy. The best forest has a higher accuracy than the `n200/d5` forest but a lower ROC AUC (0.907 against 0.908). Look at more than one metric. See [Classification metrics](/knowledge/mlops/classification-metrics.md).
- No `random_state`. The bootstrap and the feature sampling are random.[^sklearn-rf-api] Without a fixed seed, the same command gives a different score. The lab fixes `random_state=42`.
- Expecting more trees to fix everything. More trees help up to a point and then stop helping, while training gets slower.[^sklearn-rf-guide]
- A perfect score from a forest. In the leakage run the forest sees `finish_position` and scores 1.000. See [Data leakage](/knowledge/mlops/data-leakage.md).

[^breiman-2001]: Breiman, "Random Forests", 2001, abstract and section 1.1.
[^sklearn-rf-guide]: scikit-learn user guide, section 1.11.2.1 "Random Forests" and 1.11.2.3 "Parameters".
[^sklearn-rf-api]: scikit-learn API reference, `RandomForestClassifier` (parameters and the note on tree size).
[^nist-ai-rmf]: NIST AI 100-1, MAP 2.1 (methods defined) and MEASURE 2.5 (valid and reliable; limits of generalisability documented).
