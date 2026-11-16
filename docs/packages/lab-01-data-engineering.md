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

The deck tells one story: **a synthetic Grand Prix championship**, the same world as the lab data. Our strategy team (the trainees) builds the predictor (the model), which says before each race, for every car, "points or no points?". The timing sheets (`races.csv`, one row per car per race) are the data, and the final classification, known only after the race and the stewards, is the label. The story and the lab are the same thing, so every number on a slide is a measured lab number from the table below; there is no separate "In the lab" box. One slide per deck carries the caption "The championship, teams and drivers are synthetic: every team, driver and race is made up."

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Study the timing sheets first | Profile the data first. The facts you write down (ranges, rates) become your quality checks later. | Our strategy team reads every timing sheet before the predictor says a word: 120 races, 2,400 entries, 28 drivers, 10.9 % of cars do not finish. The ranges (`rain_prob` 0 to 0.55, `quali_gap_ms` 0 to 2,839) are written down, so that next season a change stands out | [Data profiling](/knowledge/mlops/data-profiling.md) |
| 2 | Don't read the finishing order | A column known only after the event is leakage. It gives perfect test scores and useless predictions. Ask "known before the lights go out?" for every input. | Knowing the finishing order before the race: `finish_position` ≤ 10 is right for every row (1.0) and useless before the start; the honest grid rule gets 0.804. The rain forecast (`rain_prob`) is fine; whether it really rained (`actual_rain`) is the result | [Data leakage](/knowledge/mlops/data-leakage.md) |
| 3 | Provisional, then final | Labels arrive late (provisional, then final). Keep both as versions. Git keeps the small pointer; DVC keeps the data; the md5 is the version. | The chequered flag gives the provisional result; the stewards' 7 penalties, 2 to 26 hours later, give the final classification (23 positions, 6 labels change). Two versions of the same timing sheet: Git keeps the ticket (`.dvc`), DVC keeps the sheet in the team's archive | [Data versioning](/knowledge/mlops/data-versioning.md), [DVC pointer file](/knowledge/mlops/dvc-pointer-file.md), [Delayed labels](/knowledge/mlops/delayed-labels.md) |
| 4 | Scrutineering for data | Write the rules for good data as one suite. Run it on every batch. A fail stops the pipeline (exit code 1). | Scrutineering: every batch is inspected with the same checklist before it may race (grid 1 to 20, rain 0 to 1, one row per car per race). `races.csv` is cleared to race (13 of 13, exit code 0); `season_2026.csv` is stopped (12 of 13, exit code 1) | [Data validation](/knowledge/mlops/data-validation.md), [Expectation suite](/knowledge/mlops/expectation-suite.md) |
| 5 | Legal is not the same as normal | Every 2026 value is valid, but the data is not like the training data. Only the distribution check catches the DNF shift. | Every 2026 car passes scrutineering, yet 27.5 % retire instead of 10.9 %: new regulations, fragile power units. Each car is legal; the field is not normal | [Validity vs distribution checks](/knowledge/mlops/validity-vs-distribution-checks.md) |

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
