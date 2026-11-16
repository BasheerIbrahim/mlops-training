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

The deck tells the Grand Prix story, which is the lab data itself: a synthetic championship of fictional teams. Our strategy team builds a predictor that says, before each race, whether each car will finish in the points. In lab 03 the [model registry](/knowledge/mlops/model-registry.md) was the team's register of approved predictors. In lab 04 the team writes its rules before the season, scrutineering checks every predictor before it may go to the grid, and the team principal signs before the race-car label moves. Every number on a slide is a measured lab number; one caption per deck says that the championship, teams and drivers are synthetic.

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Write the rules before the season | Write the release rules, each with a number and a reason, before you look at the candidate. | The team writes its rules like the technical regulations, before any predictor is tested: the timing sheets pass scrutineering, accuracy ≥ 0.82, beat the grid rule by 0.02, ROC AUC ≥ 0.88, rookies ≥ 0.60, no knowing the finish. Write them after, and you can bend them to fit your favourite. | [Release criteria](/knowledge/mlops/release-criteria.md), [baseline model](/knowledge/mlops/baseline-model.md), [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [data validation](/knowledge/mlops/data-validation.md) |
| 2 | Scrutineering before the grid | Each rule becomes a pytest gate that measures `@candidate` again on 2025. A gate that is not written checks nothing: the cheater got through until we wrote its gate. | Scrutineering ticks a checklist before a predictor may go to the grid. First the "no knowing the finishing order" box is blank, and the predictor that uses `finish_position` scores 1.000 and goes to the grid as champion. Then the box is added, and the same predictor is stopped. | [Quality gate](/knowledge/mlops/quality-gate.md), [data leakage](/knowledge/mlops/data-leakage.md), [classification metrics](/knowledge/mlops/classification-metrics.md), [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md) |
| 3 | Race car or spare? Move the label | Promotion moves the alias `@champion` to the checked version. It never retrains or copies. Tags record who, when, the gates and the previous champion. | Which car is the race car and which is the spare is just a label. The race-car label moves to the predictor that passed scrutineering; nobody rebuilds it, and the pit-wall radio needs no change. The logbook says who moved the label, when, who had it before and how every gate did. | [Model alias promotion](/knowledge/mlops/model-alias-promotion.md), [model registry](/knowledge/mlops/model-registry.md) |
| 4 | Pit-stop routine, then the principal signs | GitHub Actions runs validate, train, gates in job `gates`. Job `promote` waits for a required reviewer in the environment `production`. A failed gate skips the promotion. | The pit-stop routine: the same steps in the same order every time (check the timing sheets, train the candidate, run the gates). One failed step stops the stop. At the end the team principal signs before the label moves. Without a required signer, the label moves with no signature ("no review recorded"). | [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md), [deployment approval](/knowledge/mlops/deployment-approval.md), [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md) |
| 5 | Back to last weekend's setup | Gates stop new bad models, not old ones. A rollback moves `@champion` back to the previous version in a second, with a record. | The race-car label went to the predictor that knew the finishing order. You go back to last weekend's setup, the last honest predictor, and write down who did it. Then you write the missing check, or the cheater can come back. | [Model rollback](/knowledge/mlops/model-rollback.md) |

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
