---
type: Domain Concept
title: Subgroup evaluation
description: Measure model quality separately for each group of cases, because a good overall score can hide poor results for a small group.
tags: [model-evaluation, subgroups, disaggregated-evaluation, fairness]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.11", "NIST-AI-RMF:MEASURE 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:00:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
  - id: google-mlcc-fairness
    resource: https://developers.google.com/machine-learning/crash-course/fairness/evaluating-for-bias
    title: "Fairness: Evaluating for bias"
    author: team:google
  - id: model-cards
    resource: https://arxiv.org/abs/1810.03993
    title: Model Cards for Model Reporting
    author: Margaret Mitchell, Simone Wu, Andrew Zaldivar, Parker Barnes, Lucy Vasserman, Ben Hutchinson, Elena Spitzer, Inioluwa Deborah Raji, Timnit Gebru
---

# Definition

Subgroup evaluation (also called disaggregated evaluation) computes the same metric for each group of cases, not only for all cases together. A group is a slice of the test data, for example rookie drivers or midfield teams.

NIST says that accuracy measurements may include disaggregation of results for different data segments.[^nist-ai-rmf] Model cards report a model's evaluation across different conditions and groups, including intersectional groups.[^model-cards]

# Why it matters

Good performance for most examples can mask poor performance for a minority subset. Aggregate metrics such as accuracy may not show the problem.[^google-mlcc-fairness] The people who use the model need to know where it is weak, so they can add a human check or not use it there.

NIST asks teams to evaluate fairness and bias and to document the results, and to measure performance for conditions similar to deployment.[^nist-ai-rmf]

Kid version: the grid rule calls 80 % of all cars right. That sounds good. But for rookies, the drivers in their first season, it is right only 52 % of the time. The average hides them, so you must check each group.

# Examples

In lab 03, `train.py` logs the accuracy for each `team_tier` and for rookies and non-rookies, for example `accuracy_rookie_true` and `accuracy_team_tier_midfield`. The 2025 holdout has 48 rookie entries, 432 non-rookie entries and 192 midfield entries.

| Run | All entries | Rookies | Non-rookies | Midfield teams |
|---|---:|---:|---:|---:|
| `grid-rule` | 0.804 | 0.521 | 0.836 | 0.667 |
| `logreg-c1.0` | 0.835 | 0.646 | 0.856 | 0.714 |
| `forest-n300-d8-l5` | 0.842 | 0.646 | 0.863 | 0.714 |

- Every model is much worse for rookies. The grid rule is right for 0.521 of rookie entries, close to a coin toss. The models reach 0.646, against about 0.86 for the other drivers.
- Midfield teams are hard too (0.714), because their cars finish around tenth place, on the edge of the points. In 2025 their mean finish position is 10.2, and 57 % of their entries score points.
- The two best models have the same rookie and midfield accuracy. Overall accuracy (0.842 against 0.835) does not separate them for the groups that matter.
- In the MLflow UI you add the columns `accuracy_rookie_true` and `accuracy_team_tier_midfield` to compare the runs by group.
- `rookie` and `team_tier` are reporting groups, not model inputs. The data README says they exist to teach subgroup measurement and are not protected characteristics.

# Common mistakes

- Overall score only. A model is chosen at 0.842 and nobody knows that it is right for only 65 % of rookie entries.
- Ignoring group size. 48 rookie entries is a small sample: one entry changes the rookie accuracy by about 0.02. Report the count with the metric.
- Adding the group as an input without thought. Adding `rookie` as a model input can raise rookie accuracy. First decide if the input is allowed and fair to use.
- Checking groups once. Groups shift over time (new rookies, a new regulation). Repeat the check on each new model and in monitoring.

[^nist-ai-rmf]: NIST AI 100-1, section 3.1 "Valid and Reliable", MEASURE 2.11 (fairness and bias evaluated and documented) and MEASURE 2.3.
[^google-mlcc-fairness]: Google Machine Learning Crash Course, "Fairness: Evaluating for bias".
[^model-cards]: Mitchell et al., "Model Cards for Model Reporting", FAT* 2019 (arXiv:1810.03993), abstract.
