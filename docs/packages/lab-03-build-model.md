---
type: Learning Package
title: Lab 03 deck — build a model and track experiments
description: A five-slide classroom deck for engineers on baselines, models, tuning, leakage, subgroups and the MLflow Model Registry, built on the F1 lab.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:20:00+03:00 }
uses:
  - /knowledge/mlops/temporal-holdout-split
  - /knowledge/mlops/baseline-model
  - /knowledge/mlops/logistic-regression
  - /knowledge/mlops/random-forest
  - /knowledge/mlops/hyperparameter
  - /knowledge/mlops/classification-metrics
  - /knowledge/mlops/subgroup-evaluation
  - /knowledge/mlops/model-registry
  - /knowledge/mlops/data-versioning
  - /knowledge/mlops/data-leakage
  - /knowledge/mlops/experiment-tracking
  - /knowledge/mlops/mlflow-run
---

# Lab

| | |
|---|---|
| Branch | `03-build-model` |
| Exercise | `exercises/build-model/README.md` (reference solution in `exercises/build-model/solution/train.py`) |
| Duration | About 60 minutes for the lab, plus 15 minutes for this deck and the discussion |
| Milestone | Six runs in the MLflow experiment `f1-points-finish` (one tagged `leakage=true`), and the best honest model in the Model Registry as `f1-points-finish` version 1 |

The task: predict `points_finish` (1 = the car finishes in the top 10) before the race, from seven inputs that are known before the race.

# Deck outline

The deck tells one story: **predicting the price of a home**. The appraiser is the model, a listing is one row of data, and the sale price is the label. Story numbers (prices, sizes, shares) are made-up examples. Each slide also has an "In the lab (F1 race data)" box with the measured lab numbers below, so trainees know what to expect.

The models are appraisers, and the lab is the appraiser test.

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Study the past, test on this year | Train on the past (2021-2024) and test on a season the model never saw (2025). | The appraisers study homes sold up to last year and are tested on homes sold this year, which stay sealed. The data version is the snapshot label on every run. | [Temporal holdout split](/knowledge/mlops/temporal-holdout-split.md), [Data versioning](/knowledge/mlops/data-versioning.md) |
| 2 | Beat the price-per-m² rule | A model is worth it only if it beats a simple rule on the same test; judge it on more than one score. | Try 1, the simple rule "average price per m² in the district" (in the lab: "start in the top 10, score points", 80 %). Try 2, a careful formula where each feature adds or takes away (logistic regression, 84 %). The score card has three lines. In the story the score is "how often the appraiser is close enough"; the lab measures a yes/no question. | [Baseline model](/knowledge/mlops/baseline-model.md), [Logistic regression](/knowledge/mlops/logistic-regression.md), [Classification metrics](/knowledge/mlops/classification-metrics.md) |
| 3 | Turn the settings, write it down | Hyperparameters change the score, so record every try. | Try 3, a forest of many small judges, each pricing the home from a different pile of listings; the settings are how many judges, how many questions each may ask, how many rows in each last group: 82 %, 83 %, 84 %. MLflow is the appraiser's file with one page per try. | [Random forest](/knowledge/mlops/random-forest.md), [Hyperparameter](/knowledge/mlops/hyperparameter.md), [Experiment tracking](/knowledge/mlops/experiment-tracking.md), [MLflow run](/knowledge/mlops/mlflow-run.md) |
| 4 | Too good to be true, and not good for everyone | A perfect score means the model peeked at the answer; a good average can hide a group it fails. | Try 4, the appraiser reads the final sale price: 100 % = cheating. Is the appraiser as good for villas in Desert Edge as for apartments in Marina? In the lab, rookies get only 52-65 % while the average is 84 %. | [Data leakage](/knowledge/mlops/data-leakage.md), [Subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [Classification metrics](/knowledge/mlops/classification-metrics.md) |
| 5 | The approved appraisers list | Register only the best honest model, with a name and a version number. | The Model Registry is the approved appraisers list: the best honest appraiser goes on as `f1-points-finish` version 1. The cheater never goes on the list. | [MLflow Model Registry](/knowledge/mlops/model-registry.md), [Experiment tracking](/knowledge/mlops/experiment-tracking.md) |

# Numbers to quote

All scores are on the 2025 holdout. Training data: 2021-2024, 1,920 rows. Test data: 2025, 480 rows (24 races × 20 cars). Half of the 2025 entries score points.

| Run | Accuracy | F1 | ROC AUC | Note |
|---|---:|---:|---:|---|
| `grid-rule` | 0.804 | 0.804 | 0.893 | Baseline, no learning, no logged model |
| `logreg-c1.0` | 0.835 | 0.837 | 0.906 | Reference model in `f1/data/README.md` |
| `forest-n100-dNone-l1` | 0.819 | 0.823 | 0.902 | Default forest; trees overfit |
| `forest-n200-d5-l1` | 0.833 | 0.839 | 0.908 | Best ROC AUC |
| `forest-n300-d8-l5` | 0.842 | 0.847 | 0.907 | Best honest model; registered as `f1-points-finish` v1 |
| `forest-n100-dNone-l1-leak` | 1.000 | 1.000 | 1.000 | Sees `finish_position`; tag `leakage=true` |

| Run | Rookies (48 entries) | Non-rookies (432) | Midfield teams (192) |
|---|---:|---:|---:|
| `grid-rule` | 0.521 | 0.836 | 0.667 |
| `logreg-c1.0` | 0.646 | 0.856 | 0.714 |
| `forest-n300-d8-l5` | 0.646 | 0.863 | 0.714 |

- Best forest against logistic regression: +0.007, about 3 more right answers out of 480.
- Best honest model against the grid rule: +0.038, about 18 more right answers out of 480.
- Data version tag on every run: `data.version = 199d7bda0a7b641e0e68ccee5236a3a7` (md5 of `races.csv`, the same as in lesson 02).
- MLflow filter that hides the cheat: `tags.leakage = "false"` (five runs remain).
- The registered model, loaded with `models:/f1-points-finish/1`, prints `accuracy: 0.842`.
- MLflow 3.18 saves scikit-learn models with skops; forests need `skops_trusted_types=["sklearn.tree._tree.Tree"]`.

# Discussion questions

1. The leakage run scored 1.000. Which parameter in the run shows the cause? Which check from lab 01 or lab 02 would stop `finish_position` from getting into the inputs?
2. The best models are right for about 65 % of rookie entries, against about 86 % for other drivers. Is overall accuracy enough to choose a model? What would you tell the team that uses it?
3. The best forest beats the logistic regression by 0.007 on 480 entries. Is that a real difference? Which model would you put in production, and why?
4. You chose the model by its 2025 score. Is 2025 still an honest test of that model? What would you do instead?
