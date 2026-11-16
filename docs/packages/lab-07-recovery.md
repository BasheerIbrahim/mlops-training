---
type: Learning Package
title: Lab 07 — recover the service and train a controlled challenger
description: A classroom deck for lab 07, where engineers triage a broken release, roll back with proof, and test a challenger against the champion.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
uses:
  - /knowledge/mlops/incident-triage
  - /knowledge/mlops/incident-runbook
  - /knowledge/mlops/concept-drift
  - /knowledge/mlops/challenger-model
  - /knowledge/mlops/retraining-strategy
  - /knowledge/mlops/model-rollback
  - /knowledge/mlops/model-alias-promotion
  - /knowledge/mlops/model-registry
  - /knowledge/mlops/model-hot-reload
  - /knowledge/mlops/quality-gate
  - /knowledge/mlops/deployment-approval
  - /knowledge/mlops/release-criteria
  - /knowledge/mlops/input-contract
  - /knowledge/mlops/contract-test
  - /knowledge/mlops/load-test
  - /knowledge/mlops/service-level-objective
  - /knowledge/mlops/data-leakage
  - /knowledge/mlops/delayed-labels
  - /knowledge/mlops/data-drift
  - /knowledge/mlops/performance-monitoring
  - /knowledge/mlops/monitoring-alert
  - /knowledge/mlops/temporal-holdout-split
  - /knowledge/mlops/subgroup-evaluation
  - /knowledge/mlops/classification-metrics
  - /knowledge/mlops/baseline-model
  - /knowledge/mlops/ci-cd-pipeline
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T23:20:00+03:00 }
---

# Lab

| Item | Value |
|---|---|
| Branch | `07-recovery` |
| Exercise | `exercises/recovery/` (start with `README.md`; keep `RUNBOOK.md` open next to it) |
| Duration | About 150 minutes |
| Milestone | A recovery proved with measurements and an incident report; a challenger compared with the champion on 2026 rounds 5 to 8 and promoted through the gates with a named approver; on GitHub Actions, one run where the challenger wins and one where it is blocked. |

The deck continues the Grand Prix story, which is the lab data itself: a synthetic championship of 10 fictional teams. In lab 05 the pit-wall radio opened, and in lab 06 our strategy team watched the telemetry and the final classification. In lab 07 someone makes a setup change in parc fermé on the weekend, without scrutineering, and the car will not start. The team reads the telemetry, goes back to last weekend's setup, and then tests a new setup in practice against the race setup on the same laps. Every number on a slide is a measured lab number.

Trainer note: do not show slide 1 before trainees have written their diagnosis in step 4. Slide 1 holds the answer.

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | The parc fermé hotfix | Version 2 trained on all eight 2026 races with provisional labels and the after-race input `laps_completed`, and moved `@champion` with no gates or approval. `/admin/reload` refused it (500); the nightly restart could not load it, and the API crash-looped. Its `accuracy_2026 0.931` was measured on its own training races. | On the weekend someone changes the car's setup in parc fermé, with no scrutineering and no team principal's signature. The new setup needs the laps completed, which nobody knows before the race. Its great lap time was set on the laps it learned from. On race morning the car will not start. | [Quality gate](/knowledge/mlops/quality-gate.md), [deployment approval](/knowledge/mlops/deployment-approval.md), [model alias promotion](/knowledge/mlops/model-alias-promotion.md), [data leakage](/knowledge/mlops/data-leakage.md), [input contract](/knowledge/mlops/input-contract.md), [model hot reload](/knowledge/mlops/model-hot-reload.md) |
| 2 | Read the telemetry first | Answer five questions in order before you change anything: health, version, logs, inputs, delayed labels. Compare with the healthy "normal". Only the version changed: a bad release. An AI assistant is a second opinion; a person decides. | The race engineer reads the telemetry before anyone touches the car: is it running, which setup is on it, what do the logs say, are the inputs normal, how good are the calls against the final classification? | [Incident triage](/knowledge/mlops/incident-triage.md), [model registry](/knowledge/mlops/model-registry.md), [delayed labels](/knowledge/mlops/delayed-labels.md), [monitoring alert](/knowledge/mlops/monitoring-alert.md) |
| 3 | Back to last weekend's setup | The decision table says "bad release: roll back, do not retrain in a hurry". `promote.py --rollback` brought the service back in 27 seconds. The incident ends when the checks pass: `8 passed`, `SLO MET`, 2026 accuracy 0.706 again. Then write a blameless report with actions. | The team's runbook says: put last weekend's setup back, then do a radio check, a race-start test and compare the calls with the final classification. After the bad weekend, one page: what went wrong and what we change. Nobody is told off. | [Model rollback](/knowledge/mlops/model-rollback.md), [incident runbook](/knowledge/mlops/incident-runbook.md), [contract test](/knowledge/mlops/contract-test.md), [load test](/knowledge/mlops/load-test.md), [service-level objective](/knowledge/mlops/service-level-objective.md) |
| 4 | New regulations | The service is back, but the champion gets only 0.706 of 2026 right (0.842 in 2025) on valid inputs. 27.5 % of cars do not finish (10.9 % before), and Cobalt Racing, a backmarker team, leads. That is concept drift. Choose: roll back, recalibrate, retrain, or wait for labels. | New regulations bring fragile power units, and a backmarker team leads the championship. The same grid position and the same timing sheets now mean something different. You can go back to an old setup, trim the setup a little, build a new setup from this season's races, or wait for more races. | [Concept drift](/knowledge/mlops/concept-drift.md), [data drift](/knowledge/mlops/data-drift.md), [performance monitoring](/knowledge/mlops/performance-monitoring.md), [retraining strategy](/knowledge/mlops/retraining-strategy.md) |
| 5 | Won by a whisker | Same model, newer data: 2023-2025 + 2026 rounds 1-4. Both models are tested on rounds 5-8 (80 entries). 0.688 against 0.738: +0.050, exactly the margin; the 90 % interval [-0.025, +0.125] includes zero. All history (+0.025), heavy weights and peeking are blocked. CI compares; the gates and a person promote. | A new setup runs in practice against the race setup on the same laps, which neither has seen. It must win clearly, not by one lap. A setup that peeked at the results is thrown out. The team principal still decides. | [Challenger model](/knowledge/mlops/challenger-model.md), [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md), [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [classification metrics](/knowledge/mlops/classification-metrics.md), [baseline model](/knowledge/mlops/baseline-model.md), [release criteria](/knowledge/mlops/release-criteria.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md) |

# Numbers to quote

| What | Number | Source |
|---|---:|---|
| Normal before the incident: inputs | `160 of 160 entries valid`; `team_dnf_rate` mean 0.109 to 0.207 (shift +0.98) | lab 07 README, step 2 |
| Did not finish | 10.9 % in 2021-2025, 27.5 % in 2026 | `triage.py inputs`, data README |
| Champion accuracy | 0.842 on the 2025 holdout; 0.706 on 160 2026 entries with final labels (0.60 to 0.80 per race) | lab 07 README, step 2 |
| Provisional labels that changed | 6 of 160; final labels arrive 2 to 26 hours after a race | lab 07 README, step 7 |
| Hotfix version 2 | 8 inputs (extra, after-race `laps_completed`), `gates: not run`, `promoted by hotfix-script`, run metric `accuracy_2026 0.931` on its own training races | lab 07 README, step 4 |
| Incident signals | `/admin/reload` 500; after the restart `Application startup failed`, container `restarting`, `last exit code 3` | lab 07 README, step 4 |
| Time to health after the rollback | 27 seconds | lab 07 README, step 6 |
| Proof of recovery | `8 passed`; `SLO MET` (247 requests, p95 81 ms); 2026 accuracy 0.706 | lab 07 README, step 6 |
| Challenger training data | 1,520 entries: 2023-2025 + 2026 rounds 1-4 (80 entries, final labels) | lab 07 README, step 7 |
| Test window | 2026 rounds 5-8, 80 entries; one more right call = +0.0125 | `comparison.yaml`, lab 07 README |
| Rules | accuracy gain ≥ +0.05; ROC AUC drop ≤ 0.02; subgroup drop ≤ 0.10; margin over grid rule ≥ 0.02 | `comparison.yaml` |
| Champion vs challenger: accuracy | 0.688 vs 0.738 (+0.050) | `compare.py` |
| Champion vs challenger: ROC AUC | 0.763 vs 0.756 (-0.008) | `compare.py` |
| Margin over the grid rule (0.675) | 0.012 vs 0.062 | `compare.py` |
| Top teams (24 entries) | 0.583 vs 0.750 (+0.167); midfield and backmarkers unchanged | `compare.py` |
| Per race (2026-05 to 2026-08) | champion 0.60, 0.65, 0.75, 0.75; challenger 0.70, 0.75, 0.85, 0.65 | `compare.py` |
| 90 % bootstrap interval of the gain | [-0.025, +0.125] | `compare.py` |
| Predicted points share (actual 0.50) | champion 0.61, challenger 0.59 | `compare.py` |
| After promotion of version 3 | `8 passed`, `SLO MET` (266 requests, p95 71 ms) | lab 07 README, step 9 |
| Blocked proposals (vs version 3) | all history 0.713 (-0.025, 2 gates fail); 2026 weighted 5x 0.750, ROC AUC 0.712; all eight 2026 rounds 0.800, `time_split` fails | lab 07 README, step 9 |
| History windows on rounds 2-4, one race at a time | 2021-2025: 0.683; 2023-2025: 0.667 | lab 07 README, step 8 |
| Passing push run [43899818497](https://github.com/majlisofai/mlops-training/actions/runs/43899818497) | 0.688 vs 0.738, gain +0.050, interval [-0.025, +0.125], `PROMOTE the challenger (version 2). It passed all 9 gates.` | GitHub Actions log |
| Blocked dispatch run [43900063755](https://github.com/majlisofai/mlops-training/actions/runs/43900063755), `all_history.yaml` | 0.688 vs 0.713, gain +0.025, interval [+0.000, +0.050]; step 3 fails: `KEEP the champion (version 1). The challenger (version 2) failed 1 of 9 gates.` | GitHub Actions log |

Note for the trainer: on GitHub Actions each run has its own MLflow store and no incident, so the challenger is version 2 and is compared with version 1. That is why all history fails one gate on CI and two gates in the codespace. On a Mac, ROC AUC can differ in the last digit (the champion reads 0.762).

# Discussion questions

1. The hotfix author saw a real problem. Which control would have stopped version 2: the lesson 04 gates, the API contract, an approval, or registry permissions? Which one did stop it, and why only at the nightly restart?
2. You rolled back to a model that you knew gets 0.706 right in 2026. Was that right, or should you have fixed forward? When is fixing forward the better choice?
3. The challenger met the rules with exactly the minimum gain, and the interval of its gain includes zero. Would you approve it? What would make you roll it back, and when will you know? The lab tried four proposals on the same four races: what does that do to "the challenger won"?
4. An AI assistant read your evidence and suggested commands. Who is accountable for a command that it suggested and you ran? What evidence should never be pasted into an assistant?
