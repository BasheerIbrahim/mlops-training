---
type: Learning Package
title: Lab 03 deck — build a model and track experiments
description: A six-slide classroom deck for engineers on baselines, models, tuning, leakage, subgroups and the MLflow Model Registry, built on the F1 lab.
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
  - /knowledge/mlops/quality-gate
  - /knowledge/mlops/release-criteria
  - /knowledge/mlops/model-alias-promotion
  - /knowledge/mlops/deployment-approval
  - /knowledge/mlops/model-rollback
  - /knowledge/mlops/ci-cd-pipeline
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

The deck tells one story: **a synthetic Grand Prix championship**, the same world as the lab data. Our strategy team (the trainees) builds the predictor (the model), which says before each race, for every car, "points or no points?". The timing sheets (`races.csv`, one row per car per race) are the data, and the final classification, known only after the race and the stewards, is the label. The story and the lab are the same thing, so every number on a slide is a measured lab number from the table below; there is no separate "In the lab" box. One slide per deck carries the caption "The championship, teams and drivers are synthetic: every team, driver and race is made up."

The models are the candidate predictors, practice is the 2021-2024 seasons, and the race is the sealed 2025 season.

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Practise on old seasons, race on a new one | Train on the past (2021-2024) and test on a season the model never saw (2025). | The predictor practises on the 2021-2024 seasons (1,920 rows); the 2025 season (480 rows, 24 races × 20 cars) is a race it has never seen and stays sealed. The timing-sheet version (`data.version`) is on every run. | [Temporal holdout split](/knowledge/mlops/temporal-holdout-split.md), [Data versioning](/knowledge/mlops/data-versioning.md) |
| 2 | Beat "grid position decides" | A model is worth it only if it beats a simple rule on the same test; judge it on more than one score. | Try 1, "grid position decides": start in the top ten, score points (0.804). Try 2, a race engineer with a scale, where each input adds or takes away weight (logistic regression, 0.835). The score card has three lines: accuracy, F1 score, ROC AUC. | [Baseline model](/knowledge/mlops/baseline-model.md), [Logistic regression](/knowledge/mlops/logistic-regression.md), [Classification metrics](/knowledge/mlops/classification-metrics.md) |
| 3 | Tune the setup, log every run | Hyperparameters change the score, so record every try. | Try 3, a forest of many race engineers, each studying a different pile of timing sheets. The hyperparameters are the car setup you tune in practice (trees, depth, rows per leaf): 0.819, 0.833, 0.842. MLflow is the race engineer's logbook with one page per try. | [Random forest](/knowledge/mlops/random-forest.md), [Hyperparameter](/knowledge/mlops/hyperparameter.md), [Experiment tracking](/knowledge/mlops/experiment-tracking.md), [MLflow run](/knowledge/mlops/mlflow-run.md) |
| 4 | Too good to be true, and not good for everyone | A perfect score means the model peeked at the answer; a good average can hide a group it fails. | Try 4 knows the finishing order (`finish_position`): 1.000, disqualified. Is the best honest predictor as good for rookies as for experienced drivers? Rookies get 0.646 (grid rule 0.521) while the average is 0.842; only 48 rookie entries, and these are practice subgroups, not protected characteristics. | [Data leakage](/knowledge/mlops/data-leakage.md), [Subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [Classification metrics](/knowledge/mlops/classification-metrics.md) |
| 5 | The homologation register | Register only the best honest model, with a name and a version number. | The Model Registry is the team's homologation register of approved predictors: the best honest one goes in as `f1-points-finish` version 1 (a close call, +0.007 over logistic regression). The disqualified predictor never goes in. | [MLflow Model Registry](/knowledge/mlops/model-registry.md), [Experiment tracking](/knowledge/mlops/experiment-tracking.md) |
| 6 | From timing sheet to the grid | Lab 03 builds, logs and registers a candidate; lab 04 lets it race only after every quality gate passes and a person approves, and it can always be rolled back. | An infographic of nine numbered stations that snakes from the timing sheets to the grid. Lab 03 (stations 1-6): the timing sheets (`races.csv`, 2,400 rows, md5 `199d7bda…`), the split by season (1,920 practice rows, 480 sealed 2025 rows), three predictors (grid rule, logistic regression, forest with its setup), the 2025 evaluation (accuracy, F1, ROC AUC, rookies), the race engineer's logbook (MLflow: params, metrics, model, tags `data.version` and `leakage`), and the homologation register (`f1-points-finish`, alias `@candidate`). Lab 04 (stations 7-9): scrutineering, the six gates from `criteria.yaml` side by side for the best honest forest (passes all: 0.842, +0.038, 0.907, 0.646), the leaky run (1.000, stopped by the after-race columns check) and the grid rule (fails accuracy 0.804, margin 0, rookies 0.521); the team principal signs (GitHub Actions `environment: production`; the course repo has no reviewer, so "no review recorded"); `@champion` is the race car the pit-wall radio serves, with a dashed rollback arrow to the previous champion (`promote.py --rollback`). | [Quality gate](/knowledge/mlops/quality-gate.md), [Release criteria](/knowledge/mlops/release-criteria.md), [MLflow Model Registry](/knowledge/mlops/model-registry.md), [Model alias promotion](/knowledge/mlops/model-alias-promotion.md), [Deployment approval](/knowledge/mlops/deployment-approval.md), [Model rollback](/knowledge/mlops/model-rollback.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md) |

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
