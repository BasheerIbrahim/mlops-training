---
type: Learning Package
title: Lab 06 — monitor drift, skew and delayed labels
description: A classroom deck for lab 06, where engineers log every prediction, build a monitor with five checks and name injected production faults.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
uses:
  - /knowledge/mlops/prediction-logging
  - /knowledge/mlops/data-drift
  - /knowledge/mlops/training-serving-skew
  - /knowledge/mlops/performance-monitoring
  - /knowledge/mlops/monitoring-alert
  - /knowledge/mlops/delayed-labels
  - /knowledge/mlops/concept-drift
  - /knowledge/mlops/validity-vs-distribution-checks
  - /knowledge/mlops/input-contract
  - /knowledge/mlops/model-serving-api
  - /knowledge/mlops/service-level-objective
  - /knowledge/mlops/baseline-model
  - /knowledge/mlops/classification-metrics
  - /knowledge/mlops/ci-cd-pipeline
  - /knowledge/mlops/incident-triage
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T20:00:00+03:00 }
---

# Lab

| Item | Value |
|---|---|
| Branch | `06-monitoring` |
| Exercise | `exercises/monitoring/` (start with `README.md`) |
| Duration | About 2 hours |
| Milestone | The API logs every request. A monitor with five checks (three written by the trainee) is quiet on the reference window and alerts on the storm (input drift), the new timing feed (service health and skew) and 2026 with final labels (delayed labels). The trainee names a Drift Detective fault from the monitor output alone. On GitHub Actions the reference run passes and the wet-race run fails. |

The deck continues the Grand Prix story, which is the lab data itself: a synthetic championship of 10 fictional teams. In lab 05 the pit-wall radio opened and kept its half-second promise. In lab 06 our strategy team records telemetry for every call, spots a storm race, catches a new timing feed that sends seconds instead of milliseconds, waits for the stewards' final classification, and sets a yellow flag that waves for a real change, not for one car going off the track. Every number on a slide is a measured lab number.

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Telemetry for every call | You cannot monitor what you did not record. The API logs one line per entry: time, request id, status, model version, inputs, prediction. Rejected requests too: the new timing feed had 80 of 80 entries rejected, and the log said why. | Car telemetry on the pit wall: every question on the radio, every answer, which predictor gave it, and every message sent back with "say again", and why. | [Prediction logging](/knowledge/mlops/prediction-logging.md), [model serving API](/knowledge/mlops/model-serving-api.md) |
| 2 | The storm race | Data drift: the inputs move, the data is correct, the world changed. The storm moves `rain_prob` from 0.185 to 0.92, 10.41 sd. Evidently is a second opinion, but small windows fool it. | A storm race: the rain forecast jumps for every car. The forecast is real; the strategy team should still know, because the predictor never saw a race this wet. | [Data drift](/knowledge/mlops/data-drift.md), [validity vs distribution checks](/knowledge/mlops/validity-vs-distribution-checks.md) |
| 3 | Seconds, not milliseconds | Training-serving skew: the API gets a different value than the training pipeline computes. The new timing feed sends the qualifying gap in seconds: loud when the contract rejects it, silent when whole seconds pass. Compare value by value: 76 of 80 differ. | A new timing feed writes the qualifying gap as 0.825 seconds instead of 825 milliseconds. Every car looks a thousand times closer to pole. Only comparing each value with the timing sheet shows it. | [Training-serving skew](/knowledge/mlops/training-serving-skew.md), [input contract](/knowledge/mlops/input-contract.md) |
| 4 | Wait for the stewards | In 2026 the inputs barely move, yet accuracy falls from 0.842 to 0.706. Only the delayed final labels show it, and the verdict waits for 90 % label coverage. | The provisional result comes first; the stewards' final classification arrives hours later. The strategy team waits until most results are final before judging the predictor. | [Performance monitoring](/knowledge/mlops/performance-monitoring.md), [delayed labels](/knowledge/mlops/delayed-labels.md), [concept drift](/knowledge/mlops/concept-drift.md), [baseline model](/knowledge/mlops/baseline-model.md), [classification metrics](/knowledge/mlops/classification-metrics.md) |
| 5 | A yellow flag, not for one spin | Each threshold sits between measured normal windows and measured problems (2.0 sd: normal 1.03, storm 10.41). An alert gives a reason and exit code 1, so GitHub Actions fails the job. Then play Drift Detective. | A marshal waves the yellow flag for a real change on track, not every time one car runs wide. You test the flag rule on normal races and on the storm before you trust it. | [Monitoring alert](/knowledge/mlops/monitoring-alert.md), [service-level objective](/knowledge/mlops/service-level-objective.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md), [incident triage](/knowledge/mlops/incident-triage.md) |

# Numbers to quote

| What | Number | Source |
|---|---:|---|
| Windows | reference 80 entries (last 4 races of 2025), wet race 20, serving skew 80, season 2026 160 | lab 06 README |
| Checks and thresholds | rejected ≤ 1 %; mean shift ≤ 2.0 sd; spread x0.5 to x2.0; skew ≤ 5 % of values beyond 1 %; accuracy ≥ 0.792 (0.842 − 0.05); final label coverage ≥ 90 %; points share 0.5 ± 0.15 | `monitoring.yaml` |
| Reference window against itself | shift 0.00 sd, spread x1, Evidently flags none, 0.57 predicted in the points: `MONITOR OK`, exit 0 | lab 06 README |
| Storm (`wet_race`) | `rain_prob` mean 0.92 vs 0.185, shift 10.41 sd; other features ≤ 0.25 sd; Evidently flags `rain_prob` and `circuit_type` | lab 06 README |
| New timing feed (`serving_skew`) | 0 of 80 answered, 80 rejected (100 %); skew 76 of 80 `quali_gap_ms`, median x0.001 | lab 06 README |
| 2026 before labels | `MONITOR OK`; largest move `team_dnf_rate` 1.03 sd, spread x1.27; 0.61 predicted in the points | lab 06 README |
| 2026 with final labels | accuracy 0.706 vs baseline 0.842; 6 labels changed (3 right to wrong, 3 wrong to right) | lab 06 README |
| 2026 with provisional labels only | 0 of 160 final labels (0 %, need 90 %) | lab 06 README |
| Stricter threshold 1.0 sd | alerts on 2026 (`team_dnf_rate` 1.03 sd) and on four normal 2025 races (`rain_prob` 1.03 sd) | lab 06 README |
| `units_change` | drift spread x0.00106 (mean 0.95 vs 965.4); skew 76 of 80, median x0.000939 | answer key |
| `stuck_feature` | `driver_form` spread x0, shift 0.14 sd; skew 78 of 80, `served is always 10` | answer key |
| `category_renamed` | 20 of 80 rejected (25 %); skew `high-speed` vs `high_speed` (20 entries); input drift passes | answer key |
| `label_delay` | 60 of 160 final labels (38 %); accuracy 0.733 on three races | answer key |
| `normal_weekend` | no alert; `rain_prob` 1.03 sd; Evidently flags `team_dnf_rate`, `rain_prob` | answer key |
| Blind spots | `rain_prob` stuck at 0.15: drift passes (0.50 sd), skew 60 of 80; `quali_gap_ms` x0.62: drift passes (0.60 sd, x0.62), skew 76 of 80 | answer key |
| Clean run [43896441266](https://github.com/majlisofai/mlops-training/actions/runs/43896441266) | scenario `reference`, job 1 min 54 s, `MONITOR OK: no alerts` | GitHub Actions log |
| Alerting run [43896456941](https://github.com/majlisofai/mlops-training/actions/runs/43896456941) | scenario `wet_race`, `rain_prob` shift 10.41 sd, `MONITOR ALERT: input drift`, exit code 1 | GitHub Actions log |

Note for the trainer: keep `solution/ANSWER_KEY.md` closed until the detectives have named the fault. Pairs can play against each other: one trainee injects with `inject.py --random`, the partner runs the monitor. The daily schedule (05:23 UTC) runs only on the default branch of the fork.

# Discussion questions

1. In step 7 the contract turned skew into a loud failure. In `units_change` a feed that rounds to whole seconds passes silently. Should the API reject more, or should the monitor catch more? What does each cost?
2. 2026 showed no input drift above the threshold, yet the model got much worse. If your labels arrived only once a month, what would you watch in the meantime?
3. The reference window is four races. Would you rather use the whole 2021-2024 training data as the reference? What would you gain and lose?
4. Who should receive each alert: the team that runs the API, the data engineers who own the feeds, or the data scientists who own the model? Pick one for each of the five checks.
