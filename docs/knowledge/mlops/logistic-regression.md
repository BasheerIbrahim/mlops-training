---
type: Domain Concept
title: Logistic regression
description: A linear classification model that turns a weighted sum of the inputs into a probability between 0 and 1.
tags: [model, classification, linear-model, scikit-learn]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 2.1", "NIST-AI-RMF:MEASURE 2.9"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:20:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sklearn-logreg-guide
    resource: https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression
    title: "Linear models — Logistic regression"
    author: team:scikit-learn
  - id: sklearn-logreg-api
    resource: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    title: sklearn.linear_model.LogisticRegression (scikit-learn 1.9.1)
    author: team:scikit-learn
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
---

# Definition

Logistic regression is a linear model for classification, despite its name. It models the probability of an outcome with the logistic function.[^sklearn-logreg-guide] For a 0/1 target, the fitted model gives the probability of class 1 as `1 / (1 + exp(-(X·w + w0)))`. Here `w` holds one weight per input and `w0` is the intercept.[^sklearn-logreg-guide] The model predicts class 1 when this probability is more than 0.5.

In scikit-learn, `LogisticRegression` applies regularisation by default. The parameter `C` is the inverse of the regularisation strength: smaller values give stronger regularisation. The default is `C=1.0`.[^sklearn-logreg-api] `predict_proba` returns the probability of each class.[^sklearn-logreg-api]

# Why it matters

Logistic regression is often the first real model after a baseline. It is fast, stable and easy to explain: each input has one weight, and the sign of the weight tells you the direction of its effect. NIST asks teams to define the method that the AI system uses (for example, a classifier) and to explain, validate and document the model.[^nist-ai-rmf] A simple model makes these tasks easier.

When a complex model beats logistic regression by only a small margin, the simple model is often the better choice in production.

Kid version: logistic regression is a race engineer with a scale. Each input (grid position, form, rain) adds or takes away some weight. The total weight tips the scale to "points" or "no points".

# Examples

- In lab 03, `python exercises/build-model/train.py --model logreg` trains the run `logreg-c1.0`. The pipeline scales the six numeric inputs with `StandardScaler`, turns `circuit_type` into three 0/1 columns (one-hot encoding), and fits `LogisticRegression(C=1.0, max_iter=1000)`.
- On the 2025 holdout it scores accuracy 0.835, F1 0.837 and ROC AUC 0.906. This beats the grid rule (0.804) and is the reference model in `f1/data/README.md`.
- The best random forest scores 0.842, only 0.007 more. On 480 entries that is about 3 more right answers. Logistic regression is a strong contender for production.
- Stretch task: run `--c 0.1` and `--c 0.01` to see the effect of stronger regularisation.

# Common mistakes

- Treating it as a regression model. It predicts a class and a probability, not a number such as a finish position.
- Unscaled inputs. Regularisation acts on the weights, so inputs on very different scales (milliseconds against a 0-1 rain probability) are penalised unequally. Scale the numeric inputs first, as the lab pipeline does.
- Text categories passed as numbers. `circuit_type` has no order, so it needs one-hot encoding, not the codes 1, 2, 3.
- Reading the weights as causes. A large weight shows a link in the data, not a cause.
- Trusting the probabilities without a check. The 0.5 cut-off is a choice; ROC AUC measures the ranking across all cut-offs. See [Classification metrics](/knowledge/mlops/classification-metrics.md).

[^sklearn-logreg-guide]: scikit-learn user guide, section 1.1.11 "Logistic regression" and 1.1.11.1 "Binary case".
[^sklearn-logreg-api]: scikit-learn API reference, `LogisticRegression` (parameters `C`, `max_iter`; method `predict_proba`).
[^nist-ai-rmf]: NIST AI 100-1, MAP 2.1 (tasks and methods defined, for example classifiers) and MEASURE 2.9 (model explained, validated and documented).
