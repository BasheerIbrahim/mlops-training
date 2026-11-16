---
type: Domain Concept
title: Hyperparameter
description: A setting that you choose before training, such as tree depth or regularisation strength, which the model does not learn from data.
tags: [model-training, tuning, hyperparameter, experiment-tracking]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 2.3", "NIST-AI-RMF:MEASURE 2.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:40:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sklearn-grid-search
    resource: https://scikit-learn.org/stable/modules/grid_search.html
    title: "Tuning the hyper-parameters of an estimator"
    author: team:scikit-learn
  - id: sklearn-cv
    resource: https://scikit-learn.org/stable/modules/cross_validation.html
    title: "Cross-validation: evaluating estimator performance"
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

Hyperparameters are parameters that an estimator does not learn directly. In scikit-learn you pass them as arguments to the constructor of the estimator class.[^sklearn-grid-search] `estimator.get_params()` shows their names and current values.[^sklearn-grid-search]

Compare them with model parameters. A logistic regression learns its weights from the data; you choose `C` before training. A random forest learns its split rules from the data; you choose the number of trees (`n_estimators`), the maximum depth (`max_depth`) and the minimum rows per leaf (`min_samples_leaf`).[^sklearn-rf-api]

# Why it matters

The same model type with different hyperparameters can give very different results. To find good values you train many versions and compare them. That is a search, so you must record each try. Otherwise you forget which setting gave which score. This is the main reason for [experiment tracking](/knowledge/mlops/experiment-tracking.md).

The search itself can cheat. When you tune settings until the test score is best, knowledge of the test set leaks into the model, and the test score no longer reports generalisation.[^sklearn-cv] scikit-learn recommends a development set for the search and a separate evaluation set for the final score.[^sklearn-grid-search] NIST asks teams to document experimental design and the details of test sets, metrics and tools.[^nist-ai-rmf]

Kid version: hyperparameters are the car setup, such as the wing angle and the tyre pressure. The car learns nothing about its setup. The team sets it in practice before the race, and writes down each setup so that it can use the best one again.

# Examples

- Lab 03 tunes three forest hyperparameters on the command line: `--n-estimators`, `--max-depth` and `--min-samples-leaf`. Each run logs them as MLflow parameters, and the run name holds them too, for example `forest-n300-d8-l5`.
- The three settings give accuracy 0.819 (100 trees, no depth limit, 1 row per leaf), 0.833 (200 trees, depth 5) and 0.842 (300 trees, depth 8, 5 rows per leaf).
- The logistic regression has the hyperparameter `C` (`--c`, default 1.0). The run name `logreg-c1.0` records it.
- The lab also logs `random_state = 42`. It is not a quality knob, but without it you cannot repeat the run.
- In the MLflow UI, **Compare** on the five honest runs shows the hyperparameters and the metrics side by side.

# Common mistakes

- Tuning on the test set. In lab 03 the best forest is picked by its 2025 score, so 2025 is no longer an honest test for it. Tune on the training years, for example with time-series cross-validation, and test once at the end. See [Temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).
- Changing two things at once without a record. If you change the depth and the data in the same run and do not log both, you cannot tell which change helped.
- Over-reading small gains. The best forest beats the logistic regression by 0.007, about 3 entries out of 480. Such a gain can disappear with another season or another seed.
- Logging only the hyperparameters that you changed. Log all of them, including the defaults, so the run can be repeated.

[^sklearn-grid-search]: scikit-learn user guide, "Tuning the hyper-parameters of an estimator".
[^sklearn-cv]: scikit-learn user guide, section 3.1 "Cross-validation: evaluating estimator performance" (introduction).
[^sklearn-rf-api]: scikit-learn API reference, `RandomForestClassifier` (parameters `n_estimators`, `max_depth`, `min_samples_leaf`).
[^nist-ai-rmf]: NIST AI 100-1, MAP 2.3 (experimental design documented) and MEASURE 2.1 (test sets, metrics and tool details documented).
