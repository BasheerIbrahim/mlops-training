---
type: Domain Concept
title: Temporal holdout split
description: Train a model on older data and test it on a later period that it never saw, so the test matches real use.
tags: [model-evaluation, train-test-split, time-series, holdout]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.1", "NIST-AI-RMF:MAP 2.3", "NIST-AI-RMF:MEASURE 2.5"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:00:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sklearn-cv
    resource: https://scikit-learn.org/stable/modules/cross_validation.html
    title: "Cross-validation: evaluating estimator performance"
    author: team:scikit-learn
  - id: fpp3-accuracy
    resource: https://otexts.com/fpp3/accuracy.html
    title: "Forecasting: Principles and Practice (3rd ed.), section 5.8: Evaluating point forecast accuracy"
    author: Rob J Hyndman and George Athanasopoulos
  - id: fpp3-tscv
    resource: https://otexts.com/fpp3/tscv.html
    title: "Forecasting: Principles and Practice (3rd ed.), section 5.10: Time series cross-validation"
    author: Rob J Hyndman and George Athanasopoulos
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
---

# Definition

A temporal holdout split divides the data by time. The model learns from the older rows (the training set). Then you measure it on rows from a later period (the test set, or holdout). The model never sees the test rows during training.

To test a model on the data that it learned from is a methodological mistake. A model that only repeats the labels it saw gets a perfect score and predicts nothing useful. This is called overfitting, so you hold out a test set.[^sklearn-cv] When the rows have an order in time, rows that are near in time are correlated. A random split puts near neighbours on both sides and gives a score that is too good. You must test on "future" rows.[^sklearn-cv] The training set must contain only observations from before the test observations.[^fpp3-tscv]

# Why it matters

A model for the next race runs on races that have not happened yet. A temporal split copies that situation, so the test score is a fair guess of the score in real use. NIST asks for test sets that are clearly defined, realistic and representative of the conditions of expected use, and for documented test sets and metrics.[^nist-ai-rmf]

A model that fits the training data well does not always predict well. Only data that the model did not see gives a reliable score for new data.[^fpp3-accuracy]

Kid version: you practise in the kitchen with old recipes (2021-2024). The judges keep the 2025 taste test sealed until the end. If you taste the test dishes while you practise, the contest is not fair.

# Examples

- In lab 03, `train.py` trains on the seasons 2021-2024 (1,920 rows) and tests on the 2025 season (480 rows). The test set is 20 % of the data. Hyndman and Athanasopoulos say a test set of about 20 % of the sample is typical.[^fpp3-accuracy]
- Every run in the MLflow experiment `f1-points-finish` logs the parameters `train_seasons = 2021-2024` and `test_season = 2025`. Anyone can see which data the score comes from.
- The grid rule scores 0.804 accuracy on 2025, the logistic regression 0.835, and the best forest 0.842. All three numbers come from the same 480 holdout rows, so you can compare them.

# Common mistakes

- Random split of time-ordered rows. Races from 2025 land in the training data, and the model learns from the "future".
- Re-use of the holdout to choose a model. Each time you tune a setting to the test score, knowledge of the test set leaks into the model, and the score no longer measures generalisation.[^sklearn-cv] In lab 03 you pick the best forest by its 2025 score, so 2025 is no longer a clean test for it. Tune on the training years (for example, train on 2021-2023 and validate on 2024, or use time-series cross-validation[^fpp3-tscv]). Then test the final model once on 2025.
- Inputs that are known only after the event. A time split does not stop this. See [Data leakage](/knowledge/mlops/data-leakage.md).
- A test period that is too short or not typical. One season holds 24 races; a rule change in a new season can make the old test score wrong.

[^sklearn-cv]: scikit-learn, "Cross-validation: evaluating estimator performance" (section intro and "Cross validation of time series data").
[^fpp3-accuracy]: Hyndman and Athanasopoulos, Forecasting: Principles and Practice, 3rd ed., section 5.8, "Training and test sets".
[^fpp3-tscv]: Hyndman and Athanasopoulos, Forecasting: Principles and Practice, 3rd ed., section 5.10.
[^nist-ai-rmf]: NIST AI 100-1, section 3.1 "Valid and Reliable", and MEASURE 2.1 (test sets, metrics and tools documented), MAP 2.3 (experimental design and data selection), MEASURE 2.5 (limits of generalisability documented).
