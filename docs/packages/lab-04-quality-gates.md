---
type: Learning Package
title: Lab 04 — quality gates and controlled promotion
description: A classroom deck for lab 04, where engineers turn release criteria into automated gates and promote a model only after approval.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
uses:
  - /knowledge/mlops/release-criteria
  - /knowledge/mlops/quality-gate
  - /knowledge/mlops/model-alias-promotion
  - /knowledge/mlops/model-rollback
  - /knowledge/mlops/ci-cd-pipeline
  - /knowledge/mlops/deployment-approval
  - /knowledge/mlops/model-registry
  - /knowledge/mlops/data-leakage
  - /knowledge/mlops/data-validation
  - /knowledge/mlops/baseline-model
  - /knowledge/mlops/subgroup-evaluation
  - /knowledge/mlops/classification-metrics
  - /knowledge/mlops/temporal-holdout-split
  - /knowledge/mlops/fail-fast-pipeline
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:45:00+03:00 }
---

# Lab

| Item | Value |
|---|---|
| Branch | `04-quality-gates` |
| Exercise | `exercises/quality-gates/` (start with `README.md`) |
| Duration | About 75 minutes |
| Milestone | Bad build blocked, approved promotion: the leaky candidate fails the gates and is never offered for approval; the honest candidate becomes `@champion` only after a reviewer approves it in GitHub Actions |

The deck continues the lab 03 cook-off. In lab 03 the [model registry](/knowledge/mlops/model-registry.md) was the official recipe book. In lab 04 a gatekeeper with a checklist stands at the kitchen door, and a grown-up stamps the dish before it becomes the champion.

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Write the rules first | Write the release rules, each with a number and a reason, before you look at the candidate. | The judges write the score sheet before they taste any dish. | [Release criteria](/knowledge/mlops/release-criteria.md), [baseline model](/knowledge/mlops/baseline-model.md), [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [data validation](/knowledge/mlops/data-validation.md) |
| 2 | The gatekeeper with a checklist | Each rule becomes a pytest gate that measures `@candidate` again on 2025. A gate that is not written checks nothing: the cheater got through until we wrote its gate. | A gatekeeper at the kitchen door ticks a checklist. First the "no peeking at the answers" box is blank, and the cheater walks in. Then the box is added, and the cheater is stopped. | [Quality gate](/knowledge/mlops/quality-gate.md), [data leakage](/knowledge/mlops/data-leakage.md), [classification metrics](/knowledge/mlops/classification-metrics.md), [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md) |
| 3 | Move the ribbon, keep the record | Promotion moves the alias `@champion` to the checked version. It never retrains or copies. Tags record who, when, the gates and the previous champion. | A "champion" ribbon bookmark moves to a new page in the official recipe book, and a note on the page says who moved it. | [Model alias promotion](/knowledge/mlops/model-alias-promotion.md), [model registry](/knowledge/mlops/model-registry.md) |
| 4 | The conveyor belt and the grown-up's stamp | GitHub Actions runs validate, train, gates in job `gates`. Job `promote` waits for a required reviewer in the environment `production`. A failed gate skips the promotion. | A kitchen conveyor belt with stations. If a station rejects the dish, the belt stops. At the end a grown-up looks at the dish and stamps it before it goes on the champion plate. | [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md), [deployment approval](/knowledge/mlops/deployment-approval.md), [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md) |
| 5 | Move the ribbon back | Gates stop new bad models, not old ones. A rollback moves `@champion` back to the previous version in a second, with a record. | The ribbon went to the cheater's recipe. You move it back to the last honest recipe and write down who did it. | [Model rollback](/knowledge/mlops/model-rollback.md) |

# Numbers to quote

| What | Number | Source |
|---|---:|---|
| 2025 holdout entries / rookie entries | 480 / 48 | lab 04 README |
| Thresholds: accuracy, margin over grid rule, ROC AUC, rookie accuracy | 0.82, 0.02, 0.88, 0.60 | `criteria.yaml` |
| Grid rule: accuracy, ROC AUC, rookie accuracy | 0.804, 0.893, 0.521 | lab 04 README |
| Best honest forest (300 trees, depth 8, leaf 5): accuracy, ROC AUC, margin, rookie accuracy, inputs | 0.842, 0.907, 0.038, 0.646, 7 | lab 04 README |
| Leaky forest (+ `finish_position`): accuracy | 1.000; promoted as version 2 before the gate is written; blocked by `no_forbidden_features` after | lab 04 README |
| Weak forest (5 unlimited trees) | accuracy 0.806, ROC AUC 0.876, margin 0.002; blocked by `accuracy`, `roc_auc`, `beats_grid_rule` | lab 04 README |
| Stumps (10 one-split trees) | accuracy 0.829, ROC AUC 0.886, rookie accuracy 0.583; blocked only by `rookie_accuracy` | lab 04 README |
| Lab 03 default forest | accuracy 0.819, just under 0.82 | lab 04 README |
| Gates written by trainees | 3 of 7 | lab 04 README |
| Green push run [43871972909](https://github.com/majlisofai/mlops-training/actions/runs/43871972909) | `gates` 4 passed, 3 skipped (upstream TODOs); `promote` made version 1 `@champion` | GitHub Actions log |
| Blocked dispatch run [43872014499](https://github.com/majlisofai/mlops-training/actions/runs/43872014499), `weak.yaml` | step 3 failed: accuracy 0.806 < 0.82, ROC AUC 0.876 < 0.88; `promote` skipped | GitHub Actions log |

Note for the trainer: the upstream `production` environment has no required reviewer, so run 43871972909 promoted without waiting (`no review recorded`). Show it as the "what goes wrong without the stamp" example. In a trainee fork with a required reviewer, the job waits for **Approve and deploy**.

# Discussion questions

1. `promote.py` let three skipped gates through, and the cheating model became champion. Should a skipped gate block a release? What would a team lose if it did?
2. Anyone who can change `candidate.yaml` can also lower `min_accuracy` in `criteria.yaml` in the same commit. How would you stop that? Think of reviews, branch protection and file owners.
3. The grid rule has ROC AUC 0.893, above the floor of 0.88. Should a model be allowed to rank the cars worse than the rule? What floor would you choose, and why?
4. You approved your own model. In a real team, who should approve a release, and what should they look at before they click **Approve and deploy**?
