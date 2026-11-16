---
type: Domain Concept
title: MLflow run
description: One recorded execution of code in MLflow, holding its tags, parameters, metrics, dataset inputs and artifact files.
tags: [mlops, mlflow, experiment-tracking, metadata]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.1", "ISO-42001:A.6.2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:40:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: mlflow-tracking
    resource: https://mlflow.org/docs/latest/ml/tracking/
    title: ML Experiment Tracking
    author: team:mlflow
  - id: mlflow-tracking-api
    resource: https://mlflow.org/docs/latest/ml/tracking/tracking-api/
    title: MLflow Tracking APIs
    author: team:mlflow
  - id: mlflow-datasets
    resource: https://mlflow.org/docs/latest/ml/dataset/
    title: ML Dataset Tracking
    author: team:mlflow
  - id: mlflow-python-api
    resource: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html
    title: mlflow Python API reference
    author: team:mlflow
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
  - id: lab02-solution
    resource: https://github.com/majlisofai/mlops-training/blob/02-mlflow/exercises/mlflow/solution/log_data_checks.py
    title: Lab 02 reference solution, log_data_checks.py
    author: org:majlisofai
---

# Definition

An MLflow run is one execution of a piece of code, recorded in an experiment.[^mlflow-tracking] The run also records its start and end times.[^mlflow-tracking] Code opens a run with `mlflow.start_run()` and logs into it.[^mlflow-tracking-api] A run holds five kinds of record:

| Record | What it is | Logged with |
|---|---|---|
| Tags | Free key-value labels that you filter and search on[^mlflow-tracking] | `mlflow.set_tags()`[^mlflow-tracking-api] |
| Parameters | The settings of the run, such as hyperparameters[^mlflow-tracking-api] | `mlflow.log_params()` |
| Metrics | Numbers that the run measured. A metric can have many values, one per step[^mlflow-tracking-api] | `mlflow.log_metrics()` |
| Inputs | The datasets that the run used, with a context such as "training" or "validation"[^mlflow-datasets] | `mlflow.log_input()` |
| Artifacts | Output files, such as model weights, images or reports[^mlflow-tracking] | `mlflow.log_artifact()`, `log_dict()`, `log_text()` |

`mlflow.log_input()` stores the dataset metadata, not the data itself.[^mlflow-tracking] The metadata is a name, a digest (a hash that identifies the dataset), a source, a schema and a profile.[^mlflow-datasets] MLflow stores the context as an input tag with the key `mlflow.data.context`.[^mlflow-python-api]

# Why it matters

A run is the unit of evidence. One run answers: which data, which code, which settings, what result and which files. NIST AI RMF MEASURE 2.1 asks that test sets, metrics and tool details are documented.[^nist-ai-rmf] ISO/IEC 42001 control A.6.2.3 covers the documentation of AI system design and development.[^iso-42001][^advisera-42001] A run puts these records in one place, and the UI can compare runs side by side.[^lab02]

Think of one page in the race engineer's logbook. The page has labels on top (tags), the car setup (parameters), the results (metrics), the timing sheet it used (the input) and printouts clipped to it (artifacts).

# Examples

The lab's run on the original data is named `races-199d7bda`. It holds:[^lab02][^lab02-solution]

- **Tags:** `data.version = 199d7bda0a7b641e0e68ccee5236a3a7`, `data.path`, `git.commit`, `validation.status = passed`.
- **Parameters:** `data_path`, `data_md5`, `rows = 2400`, `columns = 23`.
- **Metrics:** `failed_checks = 0`, `failure_cases = 0`, `points_finish_rate = 0.5`, `dnf_rate = 0.10875`.
- **Inputs:** the dataset `races`, made with `mlflow.data.from_pandas(df, source=..., name="races", targets="points_finish")` and logged with `context="validation"`. The UI shows it under **Datasets used**, with its schema and digest.
- **Artifacts:** `data_version/races.csv.dvc` and `validation/report.json`.

The run after the break, `races-7fec7961`, has `validation.status = failed`, `failed_checks = 1` and `failure_cases = 1`. It also has the artifact `validation/failure_cases.csv`. The one failure case is the `dtype('int64')` check on `quali_gap_ms`: the column is now `float64`.

# Common mistakes

- Putting a number that you want to plot or compare in a tag or a parameter. Use a metric. The UI can chart metrics.
- Putting the data version only in the run name. Names are for people. Log it as a tag and a parameter, so you can search and compare on it.
- Logging the data file as an artifact for each run. That copies 2,400 rows each time. Log the small `.dvc` pointer and the dataset input instead. See [data lineage](/knowledge/mlops/data-lineage.md).
- Logging only when the run passes. Log the failure report too. `failure_cases.csv` tells you which check failed and why.
- Thinking that the MLflow dataset digest is the DVC md5. They are different hashes. Only the DVC md5 lets you get the file back with [data versioning](/knowledge/mlops/data-versioning.md).

[^mlflow-tracking]: MLflow documentation, "ML Experiment Tracking", sections on runs, artifacts, dataset tracking and the FAQ on tags.
[^mlflow-tracking-api]: MLflow documentation, "MLflow Tracking APIs", function tables and the section on metric steps.
[^mlflow-datasets]: MLflow documentation, "ML Dataset Tracking", sections on dataset properties and `mlflow.log_input()`.
[^mlflow-python-api]: MLflow Python API reference, `mlflow.log_input`, argument `context`.
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1).
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.6.2.3.
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.6.2.3.
[^lab02]: Lab 02 exercise README, steps 4 and 5.
[^lab02-solution]: Lab 02 reference solution, function `log_to_mlflow()`.
