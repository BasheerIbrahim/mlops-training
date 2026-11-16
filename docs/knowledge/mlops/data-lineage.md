---
type: Domain Concept
title: Data lineage
description: A record that links each run, check or model to the exact data version, code version and source it came from.
tags: [mlops, data-lineage, provenance, reproducibility, dvc, mlflow]
status: draft
classification: public
framework_refs: ["ISO-42001:A.7.5", "NIST-AI-RMF:MAP 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:45:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: dvc-files
    resource: https://doc.dvc.org/user-guide/project-structure/dvc-files
    title: .dvc Files
    author: team:dvc
  - id: mlflow-datasets
    resource: https://mlflow.org/docs/latest/ml/dataset/
    title: ML Dataset Tracking
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

Data lineage is the record of where a result came from: which data version, which code version and which source. In MLOps, each pipeline run records its metadata to support data and artifact lineage, reproducibility and comparisons.[^google-mlops]

In the lab, lineage is the link between one [MLflow run](/knowledge/mlops/mlflow-run.md) and one exact version of `races.csv`. Three records make the link:

1. The DVC md5. A [`.dvc` pointer file](/knowledge/mlops/dvc-pointer-file.md) holds the hash of the tracked file in `outs.md5`.[^dvc-files] The run logs it as the tag `data.version` and the parameter `data_md5`.[^lab02-solution]
2. The Git commit. The run logs `git rev-parse HEAD` as the tag `git.commit`.[^lab02-solution]
3. The dataset input. `mlflow.log_input()` records the dataset's name, digest, source and schema.[^mlflow-datasets]

# Why it matters

Without lineage, you cannot say which data gave a result, and you cannot get that data back. With lineage, you can go from a run to the data and back again.

ISO/IEC 42001 Annex A has a control for data provenance (A.7.5): a process to record the provenance of the data that an AI system uses.[^iso-42001][^advisera-42001] NIST AI RMF MAP 2.3 asks that data collection and selection are identified and documented.[^nist-ai-rmf] A run that carries the md5 and the commit is that record.

Think of the stamp in a library book. It tells you exactly which copy you borrowed and when. If you want to read the same pages again, you ask for that copy.

# Examples

- Run 1, `races-199d7bda`, has `data.version = 199d7bda0a7b641e0e68ccee5236a3a7`. The run also stores `data_version/races.csv.dvc` as an artifact.[^lab02]
- After the timing feed sends `quali_gap_ms` in seconds, `dvc add` writes a new md5, `7fec79616f5fd84d7113406b0094d400`. Run 2 carries the new md5, so the failed result points to the broken file.
- `git checkout f1/data/races.csv.dvc` and `dvc checkout f1/data/races.csv` restore the old file. Run 3 shows `data.version = 199d7bda…` again, the same as run 1.[^lab02]
- The DVC md5 and the MLflow digest do different jobs. The md5 identifies a file that DVC can restore. The digest identifies the dataset content that MLflow saw.[^mlflow-datasets][^dvc-files]

# Common mistakes

- Logging the file path but not the hash. `f1/data/races.csv` was the path for both the good and the broken data.
- Logging a hash but no way to get the data back. Keep the data in [data versioning](/knowledge/mlops/data-versioning.md), with the `.dvc` file in Git.
- Logging the md5 by hand. Read it from the `.dvc` file in code, as `data_version()` does in the lab.[^lab02-solution]
- Forgetting the code version. The same data with different code can give a different result. Log the Git commit too.
- Running on a file that is not the file in the `.dvc` pointer. Run `dvc add` (or `dvc status`) first, so the pointer matches the file.

[^google-mlops]: Google Cloud Architecture Center, "MLOps: Continuous delivery and automation pipelines in machine learning", section "ML metadata management".
[^dvc-files]: DVC documentation, ".dvc Files", fields of `outs`.
[^mlflow-datasets]: MLflow documentation, "ML Dataset Tracking", dataset properties (name, digest, source, schema, profile).
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 2.3).
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.7.5 (data provenance).
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.7.5.
[^lab02]: Lab 02 exercise README, steps 2, 4 and 6.
[^lab02-solution]: Lab 02 reference solution, functions `data_version()`, `git_commit()` and `log_to_mlflow()`.
