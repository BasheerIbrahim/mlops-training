---
type: Learning Package
title: "Lab 02: MLflow, log the data version and the data checks"
description: Classroom deck for lab 02, where trainees log the DVC data version and pandera checks of races.csv to MLflow, then break and restore the data.
tags: [mlops, mlflow, dvc, pandera, lab-02]
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T17:05:00+03:00 }
uses:
  - /knowledge/mlops/experiment-tracking
  - /knowledge/mlops/mlflow-tracking-server
  - /knowledge/mlops/mlflow-run
  - /knowledge/mlops/data-lineage
  - /knowledge/mlops/dataframe-schema
  - /knowledge/mlops/fail-fast-pipeline
  - /knowledge/mlops/data-versioning
  - /knowledge/mlops/dvc-pointer-file
  - /knowledge/mlops/data-validation
  - /knowledge/mlops/validity-vs-distribution-checks
---

# Lab

| Item | Value |
|---|---|
| Branch | `02-mlflow` (open the codespace from the badge in the top-level README) |
| Exercise | `exercises/mlflow/README.md`, code in `exercises/mlflow/log_data_checks.py` (TODO 1 to TODO 5) |
| Duration | About 45 minutes |
| Tools | MLflow 3.18.0, DVC 3.67.1, pandera 0.36.0, Python 3.12 |
| Milestone | Three runs in the MLflow experiment `f1-data-checks`: passed on md5 `199d7bda…`, failed on md5 `7fec7961…` (exit code 1), passed again on `199d7bda…` after the DVC rollback |

# Deck outline

The deck tells one story: **a synthetic Grand Prix championship**, the same world as the lab data. Our strategy team (the trainees) builds the predictor (the model), which says before each race, for every car, "points or no points?". The timing sheets (`races.csv`, one row per car per race) are the data, and the final classification, known only after the race and the stewards, is the label. The story and the lab are the same thing, so every number on a slide is a measured lab number from the table below; there is no separate "In the lab" box. One slide per deck carries the caption "The championship, teams and drivers are synthetic: every team, driver and race is made up."

MLflow is **the race engineer's logbook**: which timing sheet, which checks, which result, every time. Each run is one page in the logbook.

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Which timing sheet, and did it pass? | Before you train, record which exact data you used and whether it passed its checks. A tracking server keeps that record for the whole team. | The team's data room: shelves for the logbook pages (`sqlite:///mlflow.db`), archive boxes for the files (`./mlartifacts`), and a door that lets in only the passes on the list (`--allowed-hosts`), or it says 403. | [Experiment tracking](/knowledge/mlops/experiment-tracking.md), [MLflow tracking server](/knowledge/mlops/mlflow-tracking-server.md) |
| 2 | One logbook page per run | A run holds tags, parameters, metrics, the dataset input and artifact files. Each kind of record has its own job. | One page in the race engineer's logbook: labels on top (tags), the session settings (params), the results (metrics), which timing sheet (input), printouts clipped on, such as the check report (artifacts). | [MLflow run](/knowledge/mlops/mlflow-run.md) |
| 3 | The timing sheet's fingerprint | DVC gives the file an md5. The run stores it as `data.version`, with the Git commit and the `.dvc` file, so you can find and restore the exact data. | The logbook names the exact timing-sheet version (md5 `199d7bda…`): the same fingerprint is on the logbook page and on the sheet in the team's archive. | [Data lineage](/knowledge/mlops/data-lineage.md), [Data versioning](/knowledge/mlops/data-versioning.md), [DVC pointer file](/knowledge/mlops/dvc-pointer-file.md) |
| 4 | The technical regulations | A pandera schema states the types, ranges, allowed values and table rules of `races.csv`. `lazy=True` lists every failure. | The technical regulations for a timing sheet: `quali_gap_ms` is a whole number, grid 1 to 20, the team tier comes from the list, each car once per race. The scrutineers write down every problem, not only the first. | [DataFrame schema](/knowledge/mlops/dataframe-schema.md), [Data validation](/knowledge/mlops/data-validation.md), [Validity vs distribution checks](/knowledge/mlops/validity-vs-distribution-checks.md) |
| 5 | Red flag: break it, catch it, roll it back | Seconds instead of milliseconds give a new md5, 1 failed check and exit code 1, so the pipeline stops. DVC restores the old file, and the next run passes on the old md5. | A new timing feed sends the qualifying gap in seconds (1,080 ms becomes 1.08): a red flag stops the session (exit code 1) before the bad batch is used. Three logbook pages side by side: passed, failed, passed again with the same fingerprint as page 1. | [Fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md), [Data lineage](/knowledge/mlops/data-lineage.md), [MLflow run](/knowledge/mlops/mlflow-run.md) |

# Numbers to quote

| Item | Value | Where it comes from |
|---|---|---|
| Original data version (DVC md5) | `199d7bda0a7b641e0e68ccee5236a3a7` | Step 2 check |
| Rows and columns of `races.csv` | 2,400 rows, 23 columns | Step 4, run parameters |
| `points_finish_rate` | 0.5 | Step 4, run metrics |
| `dnf_rate` | 0.10875 (261 of 2,400 entries) | Step 4, run metrics |
| Run on the original data | `races-199d7bda`: 0 failed checks, 0 failure cases, exit code 0 | Steps 3 and 4 |
| Broken data version (DVC md5) | `7fec79616f5fd84d7113406b0094d400` | Step 5, `quali_gap_ms / 1000` |
| Run on the broken data | `races-7fec7961`: 1 failed check, 1 failure case, exit code 1 | Step 5 |
| The failed check | `dtype('int64')` on `quali_gap_ms`; failure case `float64` | `validation/failure_cases.csv` |
| `quali_gap_ms` median, before and after | 1,080 ms, then 1.08 | Measured on `races.csv` |
| Run after rollback | `data.version = 199d7bda…` again, validation passed | Step 6 |
| Schema size | 17 column rules, 2 table rules (unique `race_id` + `driver_code`; `target_matches_finish_position`) | `SCHEMA` in `log_data_checks.py` |
| Server | MLflow 3.18.0 on port 5000; `sqlite:///mlflow.db`; `./mlartifacts` | Step 1 |

# Discussion questions

1. Which check caught the timing feed change? Would the range check `quali_gap_ms >= 0` catch it alone? What check would catch it if the feed sent whole seconds as integers?
2. The script exits with `1` on failed checks. Where in a pipeline would you use that exit code, and what must run before the exit?
3. MLflow logs its own dataset digest, and DVC logs an md5. Why log both? Which one can you use to get the file back?
4. Why does the failed run 2 matter as much as the passing run 1?
5. The UI returned 403 until you added `--allowed-hosts`. Why is `--allowed-hosts "*"` a bad fix for a shared server?
