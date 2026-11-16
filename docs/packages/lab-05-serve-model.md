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

The deck continues the cook-off. In lab 04 the champion ribbon went to a checked recipe. In lab 05 a restaurant opens. The counter serves the champion dish, the menu says what you can order, and the lunch rush tests the promise "food in 5 minutes".

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Open the counter | The API loads `@champion` once, at start-up, and every answer names the model version. `/v1/` is the contract version, not the model version. | A restaurant counter serves the champion dish. Each plate has a ticket that says which recipe version made it. | [Model serving API](/knowledge/mlops/model-serving-api.md), [model registry](/knowledge/mlops/model-registry.md), [model alias promotion](/knowledge/mlops/model-alias-promotion.md) |
| 2 | The menu and the mystery shopper | The input contract refuses bad input with 422 and one line per problem; the model never sees it. Contract tests check the URLs, fields, types and errors, not accuracy. | The menu lists what you can order. A customer asks for "grid 21" and an "oval" dish, and the waiter says no and why. A mystery shopper checks that the counter follows the menu, without tasting the food. | [Input contract](/knowledge/mlops/input-contract.md), [contract test](/knowledge/mlops/contract-test.md), [DataFrame schema](/knowledge/mlops/dataframe-schema.md), [data leakage](/knowledge/mlops/data-leakage.md) |
| 3 | Pack the food truck | The image holds the code and pinned packages, not the model. It runs the same in the codespace and on GitHub Actions. `--network host` lets it reach MLflow. | A packed food truck with the stove and pans. When it opens, it fetches the champion recipe from the recipe book. | [Container image](/knowledge/mlops/container-image.md) |
| 4 | The lunch rush and the 5-minute promise | A load test with 10 users for 30 seconds measures p95 latency, failures and requests. The SLO turns them into pass or fail: p95 ≤ 500 ms, failures ≤ 1 %, ≥ 150 requests. | Ten hungry customers arrive at once. A big clock on the wall shows whether the kitchen keeps its promise: food within 5 minutes. | [Load test](/knowledge/mlops/load-test.md), [service-level objective](/knowledge/mlops/service-level-objective.md) |
| 5 | The slow chef | The huge forest passes all seven gates (accuracy 0.840) but breaks the SLO (p95 2300 ms, 97 requests on CI). Roll back the alias, reload, and the SLO is met again. Serving checks belong in the release. | A new chef cooks dishes as tasty as the old chef's, but very slowly, and the queue grows out of the door. You give the job back to the old chef without closing the restaurant, and the queue goes away. | [Model hot reload](/knowledge/mlops/model-hot-reload.md), [model rollback](/knowledge/mlops/model-rollback.md), [quality gate](/knowledge/mlops/quality-gate.md), [release criteria](/knowledge/mlops/release-criteria.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md), [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md), [random forest](/knowledge/mlops/random-forest.md) |

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
