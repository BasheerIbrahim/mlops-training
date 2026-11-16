---
type: Domain Concept
title: Experiment tracking
description: Recording each run of ML or data code, with its inputs, settings, results and output files, so that people can compare and reproduce runs.
tags: [mlops, experiment-tracking, reproducibility, mlflow]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.1", "NIST-AI-RMF:MAP 2.3", "ISO-42001:A.6.2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:30:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: mlflow-tracking
    resource: https://mlflow.org/docs/latest/ml/tracking/
    title: ML Experiment Tracking
    author: team:mlflow
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: iso-42001
    resource: https://www.iso.org/standard/42001
    title: "ISO/IEC 42001:2023 Information technology — Artificial intelligence — Management system"
    author: org:iso
  - id: advisera-42001
    resource: https://advisera.com/articles/iso-42001-mandatory-documents/
    title: List of ISO 42001 mandatory documents (Annex A control list)
    author: org:advisera
  - id: lab02
    resource: https://github.com/majlisofai/mlops-training/blob/02-mlflow/exercises/mlflow/README.md
    title: "Exercise: track data versions and data checks in MLflow"
    author: org:majlisofai
---

# Definition

Experiment tracking is the practice of recording each run of ML or data code. A run is one execution of the code, for example one `python train.py`.[^mlflow-tracking] For each run, you record the parameters, the code version, the metrics, the start and end times and the output files.[^mlflow-tracking] An experiment groups the runs for one task.[^mlflow-tracking]

A tracking tool stores the records and shows them in a UI. In the lab, the tool is MLflow, with an [MLflow tracking server](/knowledge/mlops/mlflow-tracking-server.md). Each record is an [MLflow run](/knowledge/mlops/mlflow-run.md).

# Why it matters

Memory and file names do not tell you which data, code and settings gave a result. A tracking record does. Recorded run metadata helps with data and artifact lineage, reproducibility and comparisons. It also helps you debug errors and anomalies.[^google-mlops]

NIST AI RMF asks that test sets, metrics and the tools used during test, evaluation, verification and validation (TEVV) are documented (MEASURE 2.1). It also asks that data collection and selection are documented (MAP 2.3).[^nist-ai-rmf] ISO/IEC 42001 Annex A has a control for the documentation of AI system design and development (A.6.2.3).[^iso-42001][^advisera-42001] Experiment tracking produces this evidence as a side effect of the work.

Think of the race engineer's logbook. Each run gets one new page: which timing sheet, which setup, which checks and which result. You never tear out a page.

# Examples

- The lab experiment is `f1-data-checks`. Each run of `log_data_checks.py` on `f1/data/races.csv` adds one run.[^lab02]
- Run 1 is on the original data: md5 `199d7bda…`, 2,400 rows, 23 columns, `validation.status = passed`, `dnf_rate = 0.10875`.[^lab02]
- Run 2 is after the timing feed sends `quali_gap_ms` in seconds: md5 `7fec7961…`, `validation.status = failed`, `failed_checks = 1`.
- Run 3 is after the DVC rollback: md5 `199d7bda…` again, `validation.status = passed`.[^lab02]
- In the MLflow UI, you select runs 1 and 2 and click **Compare**. The table shows that `data_md5`, `validation.status` and `failed_checks` changed together.[^lab02]
- In lab 03, the same practice records model runs: [hyperparameters](/knowledge/mlops/hyperparameter.md) and [classification metrics](/knowledge/mlops/classification-metrics.md).

# Common mistakes

- Tracking only the final, good run. The failed run 2 is the evidence that the checks work.
- Tracking metrics but not the data version. Then two runs with different results look the same. Record the [data lineage](/knowledge/mlops/data-lineage.md) in every run.
- Giving runs no names or tags. Then you cannot find or filter them later. The lab names each run `races-<first 8 characters of the md5>`.
- Keeping the tracking store on one laptop. The team cannot see or compare the runs. Use a shared tracking server.

[^mlflow-tracking]: MLflow documentation, "ML Experiment Tracking", sections on runs, experiments and the FAQ on tags.
[^google-mlops]: Google Cloud Architecture Center, "MLOps: Continuous delivery and automation pipelines in machine learning", section "ML metadata management".
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 2.3) and Table 3 (MEASURE 2.1).
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.6.2.3.
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.6.2.3 (AI system design and development).
[^lab02]: Lab 02 exercise README, steps 3 to 6.
