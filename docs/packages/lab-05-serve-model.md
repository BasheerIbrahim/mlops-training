---
type: Learning Package
title: Lab 05 — serve the model and roll back a faulty release
description: A classroom deck for lab 05, where engineers serve the champion behind a tested API, load-test it and roll back a slow release.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
uses:
  - /knowledge/mlops/model-serving-api
  - /knowledge/mlops/input-contract
  - /knowledge/mlops/contract-test
  - /knowledge/mlops/container-image
  - /knowledge/mlops/load-test
  - /knowledge/mlops/service-level-objective
  - /knowledge/mlops/model-hot-reload
  - /knowledge/mlops/model-rollback
  - /knowledge/mlops/model-alias-promotion
  - /knowledge/mlops/model-registry
  - /knowledge/mlops/quality-gate
  - /knowledge/mlops/release-criteria
  - /knowledge/mlops/ci-cd-pipeline
  - /knowledge/mlops/fail-fast-pipeline
  - /knowledge/mlops/dataframe-schema
  - /knowledge/mlops/data-leakage
  - /knowledge/mlops/random-forest
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:45:00+03:00 }
---

# Lab

| Item | Value |
|---|---|
| Branch | `05-serve-model` |
| Exercise | `exercises/serve-model/` (start with `README.md`) |
| Duration | About 90 minutes |
| Milestone | A versioned API and a proved rollback: the huge forest passes all seven gates but breaks the SLO; after the rollback and a reload, the SLO is met again. On GitHub Actions, the good candidate passes the serving check and the huge forest fails at step 5. |

The deck continues the house-price story. In lab 04 the "official appraiser" badge went to a checked appraiser. In lab 05 the price app opens: people type in a home and get a price back, the app's form says what you may send, and launch day tests the promise "a price in under half a second". The story uses made-up homes; every slide also shows the measured F1 lab numbers in an "In the lab (F1 race data)" box.

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Open the price app | The API loads `@champion` once, at start-up, and every answer names the model version. `/v1/` is the contract version, not the model version. | The price app opens: type a home in, get a price back. Every price names the appraiser version that made it (example: a made-up 400 m² villa in Palm Gardens, SAR 2.4 million, version 1). /v1/ is the version of the form, not of the appraiser. | [Model serving API](/knowledge/mlops/model-serving-api.md), [model registry](/knowledge/mlops/model-registry.md), [model alias promotion](/knowledge/mlops/model-alias-promotion.md) |
| 2 | The app's form and the mystery shopper | The input contract refuses bad input with 422 and one line per problem; the model never sees it. Contract tests check the URLs, fields, types and errors, not accuracy. | The app's form lists what you may send: bedrooms 0 to 10, size in m², type from the list. A request with 14 bedrooms, a "castle", no size and the final sale price gets "422, please fix", one line per problem, and the appraiser never sees it. A mystery shopper checks that the app keeps its form, without checking the prices. | [Input contract](/knowledge/mlops/input-contract.md), [contract test](/knowledge/mlops/contract-test.md), [DataFrame schema](/knowledge/mlops/dataframe-schema.md), [data leakage](/knowledge/mlops/data-leakage.md) |
| 3 | Pack the price app in a box | The image holds the code and pinned packages, not the model. It runs the same in the codespace and on GitHub Actions. `--network host` lets it reach MLflow. | The price app is packed in a box that runs the same everywhere: the code, the pinned packages and the start command go in. The appraiser does not: when the box opens, it asks the approved appraisers list for the one with the badge. | [Container image](/knowledge/mlops/container-image.md) |
| 4 | Launch day and the half-second promise | A load test with 10 users for 30 seconds measures p95 latency, failures and requests. The SLO turns them into pass or fail: p95 ≤ 500 ms, failures ≤ 1 %, ≥ 150 requests. | Launch day: everyone checks their home at once. The app's promise, checked with a clock and not a feeling: a price in under half a second for 95 of 100 people, almost no failed answers, and enough answers to keep up. | [Load test](/knowledge/mlops/load-test.md), [service-level objective](/knowledge/mlops/service-level-objective.md) |
| 5 | The slow appraiser | The huge forest passes all seven gates (accuracy 0.840) but breaks the SLO (p95 2300 ms, 97 requests on CI). Roll back the alias, reload, and the SLO is met again. Serving checks belong in the release. | A new appraiser gives prices just as good and passes every rule on the bank's list, but it is far too slow: people wait, then leave the app. You move the badge back to the old appraiser and reload, without closing the app, and the promise is kept again. | [Model hot reload](/knowledge/mlops/model-hot-reload.md), [model rollback](/knowledge/mlops/model-rollback.md), [quality gate](/knowledge/mlops/quality-gate.md), [release criteria](/knowledge/mlops/release-criteria.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md), [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md), [random forest](/knowledge/mlops/random-forest.md) |

# Numbers to quote

| What | Number | Source |
|---|---:|---|
| Endpoints | `GET /health`, `POST /v1/predict` (1 to 1000 entries), `POST /admin/reload` | `app.py` |
| Contract inputs | 7 (grid 1 to 20, circuit type `street`, `permanent` or `high_speed`, extra fields forbidden) | lab 05 README |
| Two-car smoke test | predictions `[1,0]`, probabilities 0.96 and 0.01 | lab 05 README |
| Bad entry (grid 21, `"oval"`, no `rain_prob`, `finish_position`) | status 422, 4 lines | lab 05 README |
| Contract tests | 8 (5 done, 3 written by trainees); `5 passed, 3 skipped` before, `8 passed` after | lab 05 README |
| Image `f1-api:1` | about 810 MB | lab 05 README |
| SLO under 10 users for 30 s | p95 ≤ 500 ms, failure rate ≤ 1 %, ≥ 150 requests | `slo.yaml` |
| Good model (300 trees, depth 8) in a 2-CPU container | p95 71 to 190 ms, 245 to 263 requests, 0 % failures | lab 05 README |
| Huge forest (3000 trees, depth 12): accuracy, ROC AUC, margin, rookie accuracy | 0.840, 0.906, 0.035, 0.667: all 7 gates pass | lab 05 README |
| Huge forest in a 2-CPU container | p95 1800 ms (4300 ms in another run), 129 requests: SLO BROKEN | lab 05 README |
| Version 1 vs version 2: model file, container memory, start-up | 11 MB vs 121 MB, 188 MiB vs 385 MiB, 2.5 s vs 5.5 s | lab 05 README |
| Huge forest on a 10-CPU laptop, no container | p95 670 ms (version 1: 53 ms) | lab 05 README |
| After rollback and reload | p95 71 ms, 247 requests: SLO MET | lab 05 README |
| Passing push run [43890454930](https://github.com/majlisofai/mlops-training/actions/runs/43890454930) | 7 gates passed, contract tests `5 passed, 3 skipped`, p95 140 ms, 247 requests, 0 % failures: SLO MET | GitHub Actions log |
| Failing dispatch run [43890470443](https://github.com/majlisofai/mlops-training/actions/runs/43890470443), `huge_forest.yaml` | steps 1 to 4 passed (7 gates, accuracy 0.840); step 5 failed: p95 2300 ms, 97 requests, 0 % failures: `SLO BROKEN: requests, p95 latency` | GitHub Actions log |

Note for the trainer: in CI each run has its own registry, so the candidate is always version 1 and there is nothing to roll back to. The CI run shows the block; the codespace shows the rollback. The upstream runs show `5 passed, 3 skipped` contract tests because the upstream branch keeps the TODOs. A trainee fork with the TODOs written shows `8 passed`.

# Discussion questions

1. The huge forest passed every quality gate and was better for rookies. Where would you check latency: as a gate in `release.yml` before promotion, or on the running service after deployment? What does each catch that the other misses?
2. After the promotion, the API kept serving version 1 until you called `/admin/reload`. Is that a bug or a safety feature? Compare reload on command, reload every minute and restart the container.
3. Anyone who can reach the API can call `/admin/reload`. Who should be allowed to, and what could go wrong if anyone can?
4. Who should choose the numbers in `slo.yaml`: the data scientists, the team that runs the API, or the people who use the predictions? What would you ask them?
