---
type: Learning Package
title: Lab 01 — data engineering
description: A classroom deck for lab 01, where engineers explore the F1 data, find leakage, version results with DVC and check quality with Great Expectations.
tags: [mlops, data-engineering, lab-01]
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T12:00:00+03:00 }
uses:
  - /knowledge/mlops/data-profiling
  - /knowledge/mlops/data-leakage
  - /knowledge/mlops/data-versioning
  - /knowledge/mlops/dvc-pointer-file
  - /knowledge/mlops/delayed-labels
  - /knowledge/mlops/data-validation
  - /knowledge/mlops/expectation-suite
  - /knowledge/mlops/validity-vs-distribution-checks
---

# Lab

| Item | Value |
|---|---|
| Branch | `01-data-engineering` (open it in GitHub Codespaces from the README badge) |
| Exercise | `exercises/data-engineering/README.md`, with `explore.ipynb`, `apply_stewards.py` and `quality_checks.py` (reference solution in `solution/`) |
| Data | `f1/data/races.csv`, `season_2026_provisional.csv`, `season_2026_final.csv`, `stewards_2026.csv` (all synthetic, seed 2026) |
| Duration | About 75 minutes: three parts of about 25 minutes (explore, version, check quality), then the group discussion |
| Milestone | `dvc diff HEAD~1` shows `f1/data/season_2026.csv` as modified, with 23 positions and 6 labels changed. The quality suite passes on `races.csv` (13 of 13, exit code 0) and fails on `season_2026.csv` (12 of 13, exit code 1) |
| Tools | Jupyter, DuckDB, ydata-profiling, Data Wrangler, DVC, Great Expectations. The course tech pack pairs DVC with pandera; this lab uses Great Expectations, and lab 02 uses pandera |
| Next | Lab 02 (`02-mlflow`) logs the data version and the quality checks to an MLflow tracking server |

# Deck outline

The deck tells one story: **predicting the price of a home**. The appraiser is the model, a listing is one row of data, and the sale price is the label. Story numbers (prices, sizes, shares) are made-up examples. Each slide also has an "In the lab (F1 race data)" box with the measured lab numbers below, so trainees know what to expect.

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Look before you price | Profile the data first. The facts you write down (ranges, rates) become your quality checks later. | Walk through the listings before you price anything: how big the homes are, how many villas, which districts. Write the facts down, so that next month a change stands out | [Data profiling](/knowledge/mlops/data-profiling.md) |
| 2 | Don't peek at the sale price | A column known only after the event is leakage. It gives perfect test scores and useless predictions. Ask "known before the sale (the race)?" for every input. | Using the final sale price, or the agent's closing offer, to predict the price: the appraiser looks perfect and is useless before the sale. The asking price is fine, because it is known before the sale | [Data leakage](/knowledge/mlops/data-leakage.md) |
| 3 | Snapshots of the listings book | Labels arrive late (provisional, then final). Keep both as versions. Git keeps the small pointer; DVC keeps the data; the md5 is the version. | The asking price comes first, the real sale price weeks later: two snapshots of the listings book. Git keeps the small receipt; DVC keeps the full book | [Data versioning](/knowledge/mlops/data-versioning.md), [DVC pointer file](/knowledge/mlops/dvc-pointer-file.md), [Delayed labels](/knowledge/mlops/delayed-labels.md) |
| 4 | The listing inspector at the door | Write the rules for good data as one suite. Run it on every batch. A fail stops the pipeline (exit code 1). | The listing inspector at the door: a 9-bedroom studio, a floor of −3 or a 10,000 m² apartment gets stopped before anyone prices it | [Data validation](/knowledge/mlops/data-validation.md), [Expectation suite](/knowledge/mlops/expectation-suite.md) |
| 5 | Allowed is not the same as normal | Every 2026 value is valid, but the data is not like the training data. Only the distribution check catches the DNF shift. | Every listing is allowed, but if half of this month's listings are penthouses, something changed | [Validity vs distribution checks](/knowledge/mlops/validity-vs-distribution-checks.md) |

# Numbers to quote

All numbers are measured in lab 01 on the synthetic F1 data.

| What | Value |
|---|---|
| Training data (`races.csv`) | 120 races, 2,400 entries, 28 drivers, points share 0.5 |
| DNF rate, `races.csv` (2021-2025) | 0.10875 (10.9 %) |
| DNF rate, 2026 provisional (first 8 races) | 0.275 (27.5 %), high for every team tier |
| Grid-only rule ("start top ten, score points"), 2025 | Right for 0.804 of entries |
| Leakage rules (`finish_position` ≤ 10, `points` > 0) | Right for every row (1.0) |
| Leakage columns | `finish_position`, `points`, `status`, `laps_completed`, `fastest_lap`, `actual_rain` |
| `rain_prob` range in training | 0 to 0.55 |
| `quali_gap_ms` range in training | 0 to 2,839 |
| Stewards' penalties (`stewards_2026.csv`) | 7 penalties, published 2 to 26 hours after the race |
| md5, version 1 (provisional) | `1dee862a3599e087b764cfb9ebd79ee8` |
| md5, version 2 (final) | `87ffbc792aeb259333a41f7f573a38e3` |
| Changes between versions | 23 finish positions, 6 labels (`points_finish`) |
| Quality suite on `races.csv` | 13 of 13 checks pass, exit code 0 |
| Quality suite on `season_2026.csv` | 12 of 13 pass; the `dnf` mean check (range 0.05 to 0.20) fails with 0.275, exit code 1 |

# Discussion questions

1. You train a model on Monday morning, and the stewards publish a penalty on Monday afternoon. Which version of the labels did your model use? How does DVC help you answer this question three months later?
2. Six labels changed between the provisional and the final results. Which version should you use to evaluate a model, and why?
3. Which checks in the suite check that values are *valid*, and which check that the data is *like the training data*? Which kind fails more often in production?
4. The `dnf` check uses the range 0.05 to 0.20. How would you choose that range for a real system?
5. `rain_prob` is a legal input and `actual_rain` is leakage. Find one more pair of columns in your own work where one is known before the event and the other only after it.
