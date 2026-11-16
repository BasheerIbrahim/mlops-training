---
type: Learning Package
title: Lab 08 — fairness, transparency and the model card
description: A classroom deck for lab 08, where engineers measure the champion per subgroup, see a fairness gate block it, and sign a model card.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
uses:
  - /knowledge/mlops/fairness-metrics
  - /knowledge/mlops/fairness-gate
  - /knowledge/mlops/bias-mitigation
  - /knowledge/mlops/model-card
  - /knowledge/mlops/data-minimisation
  - /knowledge/mlops/subgroup-evaluation
  - /knowledge/mlops/classification-metrics
  - /knowledge/mlops/baseline-model
  - /knowledge/mlops/quality-gate
  - /knowledge/mlops/release-criteria
  - /knowledge/mlops/data-leakage
  - /knowledge/mlops/temporal-holdout-split
  - /knowledge/mlops/random-forest
  - /knowledge/mlops/logistic-regression
  - /knowledge/mlops/model-registry
  - /knowledge/mlops/model-alias-promotion
  - /knowledge/mlops/deployment-approval
  - /knowledge/mlops/input-contract
  - /knowledge/mlops/prediction-logging
  - /knowledge/mlops/ci-cd-pipeline
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T23:10:00+03:00 }
---

# Lab

| Item | Value |
|---|---|
| Branch | `08-fairness` |
| Exercise | `exercises/fairness/` (start with `README.md`) |
| Duration | About 100 minutes |
| Milestone | The champion forest passes every lab 04 gate but a fairness gate blocks it (rookie FPR gap +0.620, limit 0.55). Trainees test two mitigations, promote the logistic regression (6 gates pass), sign a model card generated from MLflow, and prove the privacy gate fails on a leaky log. On GitHub Actions, the forest run fails at step 4 and the logreg run passes. |

The deck continues the cook-off. In lab 05 the restaurant opened. In lab 08 a food critic guesses which dishes will win a star, and we ask: is the critic wrong in the same way for everyone? The new cooks (rookies) are only two people, so we must also be honest about how sure we are. `rookie` and `team_tier` are subgroups for practice, not protected characteristics.

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | For whom does it work? | Overall accuracy 0.842 hides who gets the errors. For rookies the model predicts points 87.5 % of the time; FPR 0.762 against 0.142. Lab 04's rookie accuracy (0.646) hid that the errors are all false positives. | A food critic promises a star to 16 of the 21 new cooks' dishes that did not deserve one. For the other cooks, the critic makes that mistake about 1 time in 7. | [Fairness metrics](/knowledge/mlops/fairness-metrics.md), [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [classification metrics](/knowledge/mlops/classification-metrics.md) |
| 2 | Two drivers is not a population | 48 rookie entries come from 2 drivers. The FPR interval is 0.56 to 0.93, and still too narrow. One entry moves the FPR by 0.048. Report counts and intervals; suppress groups of one; a gap that follows the task (top teams, backmarkers) is not a fairness finding. | Two new cooks, many dishes each. Tasting more of the same two cooks' dishes does not tell you about all new cooks. | [Fairness metrics](/knowledge/mlops/fairness-metrics.md), [data minimisation](/knowledge/mlops/data-minimisation.md) |
| 3 | The second gatekeeper | Thresholds are written before the candidates, from the grid rule: FPR gap ≤ 0.55, FNR gap ≤ 0.10, ≥ 30 entries. The champion that passed 7 lab 04 gates, the contract tests and the load test is BLOCKED. `leaky` passes the fairness gates and is still useless: you need both gate sets. | A second gatekeeper at the kitchen door checks that the critic's mistakes are not all piled on the new cooks. | [Fairness gate](/knowledge/mlops/fairness-gate.md), [quality gate](/knowledge/mlops/quality-gate.md), [release criteria](/knowledge/mlops/release-criteria.md), [baseline model](/knowledge/mlops/baseline-model.md), [data leakage](/knowledge/mlops/data-leakage.md) |
| 4 | Every fix has a price | Reweight ×10 passes at −0.017 accuracy. A per-group threshold trades false positives for false negatives; the "perfect" 0.6 was tuned on the holdout and needs `rookie` at prediction time, which API v1 forbids. The cheapest fix was another model: the logistic regression passes (FPR gap +0.487). | Practise the critic on new cooks' dishes ten times as often: fairer, a little worse overall. A special bar only for new cooks was chosen by peeking at the final judging. | [Bias mitigation](/knowledge/mlops/bias-mitigation.md), [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md), [random forest](/knowledge/mlops/random-forest.md), [logistic regression](/knowledge/mlops/logistic-regression.md), [input contract](/knowledge/mlops/input-contract.md) |
| 5 | Write it down and keep names out | The model card is generated from MLflow; people write intended use, out-of-scope use, owner, approver and decision. The privacy gate fails on a log with `driver_code` and a name in a label. On GitHub Actions, the forest fails at step 4 and the card is still written. | The label on the jar says what is inside, who should not eat it, and who signed it. The kitchen ticket says "grid 3, rain likely", never the customer's name. | [Model card](/knowledge/mlops/model-card.md), [data minimisation](/knowledge/mlops/data-minimisation.md), [prediction logging](/knowledge/mlops/prediction-logging.md), [model registry](/knowledge/mlops/model-registry.md), [model alias promotion](/knowledge/mlops/model-alias-promotion.md), [deployment approval](/knowledge/mlops/deployment-approval.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md) |

# Numbers to quote

| What | Number | Source |
|---|---:|---|
| Champion forest, all 2025 entries | accuracy 0.842, 480 entries | lab 08 README, step 3 |
| Rookies vs everyone else: entries, drivers | 48 (2 drivers) vs 432 (18 drivers) | `fairness_report.py` |
| Rookies vs everyone else: accuracy, selection rate | 0.646 vs 0.863; 0.875 vs 0.500 | `fairness_report.py` |
| Rookies vs everyone else: FPR, FNR | 0.762 vs 0.142 (16 of 21); 0.037 vs 0.131 (1 of 27) | `fairness_report.py` |
| Rookie FPR bootstrap interval (500 resamples) | 0.56 to 0.93 | fairness table |
| Gaps: model vs grid rule | FPR +0.620 vs +0.568; FNR −0.094 vs +0.113 | `fairness_report.py` |
| Fairness limits | FPR gap ≤ 0.55, FNR gap ≤ 0.10, ≥ 30 rookie entries; warn < 5 drivers or a rate on < 30 entries | `fairness.yaml` |
| Gates on the champion | `1 failed, 5 passed, 3 warnings`: BLOCKED | lab 08 README, step 5 |
| Mitigation: reweight ×10 | accuracy 0.825 (−0.017), FPR gap +0.473, FNR gap +0.026: passes | `mitigate.py` |
| Mitigation: rookie threshold 0.6 / honest threshold 0.3 | FPR gap +0.477 (tuned on holdout, not valid) / +0.811 | `mitigate.py` |
| Candidates passing both gate sets | `logreg` (FPR gap +0.487), `big_leaves` (+0.525); forest, `stumps`, `weak`, `leaky` blocked | `compare_candidates.sh` |
| New champion (logistic regression) | accuracy 0.835, rookie FPR 0.619 vs 0.132, FNR gap −0.007, `6 passed, 3 warnings` | lab 08 README, step 7 |
| Model card placeholders | 7 before, 0 after | `model_card.py` |
| Prediction log | 24 records, 0 problems; `--with-driver-code`: HTTP 422, 24 races refused | lab 08 README, step 4 |
| Leaky log `prediction_log_v0.jsonl` | 6 personal identifiers: privacy gate fails | lab 08 README, step 9 |
| Failing push run [43899389581](https://github.com/majlisofai/mlops-training/actions/runs/43899389581) | step 4 fails: `1 failed, 4 passed, 1 skipped, 3 warnings`, `rookie false positive rate gap +0.620 is above 0.55`; model card still written | GitHub Actions log |
| Passing dispatch run [43899417058](https://github.com/majlisofai/mlops-training/actions/runs/43899417058), `logreg.yaml` | `5 passed, 1 skipped, 3 warnings`, FPR gap +0.487, FNR gap −0.007 | GitHub Actions log |

Note for the trainer: the upstream runs show `1 skipped` because the upstream branch keeps TODO 4 (the FNR gate) unwritten, so the gate report shows `rookie_fnr_gap` as NOT CHECKED. A trainee fork with TODO 4 written shows `1 failed, 5 passed` and `6 passed`. Each CI run has its own registry, so the candidate is version 1 there.

# Discussion questions

1. The champion fails the FPR gate by about one rookie entry, measured on two drivers. Would you block it, approve it with conditions, or change the threshold? Who decides, and where is that written?
2. The gate blocks only gaps that are worse for rookies. Is that fair to everyone else? When would you gate on the absolute gap instead?
3. A per-group threshold fixed the numbers but needs `rookie` at prediction time. For a protected characteristic, which mitigation would you even consider, and whom would you ask first?
4. The leaky model passed every fairness gate. What does a fairness gate prove, and what does it not prove?
5. The prediction log is needed for monitoring and is a privacy risk. What would you keep, for how long, and who may read it?
