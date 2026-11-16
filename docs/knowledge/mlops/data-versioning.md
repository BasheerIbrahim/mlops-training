---
type: Domain Concept
title: Data versioning
description: Keeping each version of a dataset with an ID, so that you can name, compare and restore the exact data a model used.
tags: [mlops, data-engineering, versioning, reproducibility, dvc]
status: draft
classification: public
framework_refs: ["ISO-42001:A.7.5", "NIST-AI-RMF:MEASURE 2.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:00:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: dvc-use-case
    resource: https://doc.dvc.org/use-cases/versioning-data-and-models
    title: "Use case: Versioning data and models"
    author: DVC documentation
  - id: dvc-get-started
    resource: https://doc.dvc.org/start/data-management/data-versioning
    title: "Get started: Data versioning"
    author: DVC documentation
  - id: dvc-diff
    resource: https://doc.dvc.org/command-reference/diff
    title: dvc diff
    author: DVC documentation
  - id: lab-01
    resource: https://github.com/majlisofai/mlops-training/blob/01-data-engineering/exercises/data-engineering/README.md
    title: "Lesson 01: data engineering"
    author: mlops-training
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: NIST
  - id: iso-42001-a7
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-7-data-for-ai-systems/
    title: "ISO 42001 Annex A control A.7: Data for AI systems"
    author: ISMS.online
---

# Definition

Data versioning gives each version of a dataset an ID and keeps every version. You can then name the exact data that a model used, compare two versions, and restore an old version.

DVC captures the versions of data and models in Git commits. Git holds small metadata files, and DVC holds the data itself in a separate store.[^dvc-use-case] The usual way to go back is `git checkout` to get an old metadata file, then `dvc checkout` to put the matching data in the workspace.[^dvc-get-started] See [DVC pointer file](/knowledge/mlops/dvc-pointer-file.md).

# Why it matters

A model is the result of code plus data. If you version only the code, you cannot repeat a training run or explain a result later. DVC lists "being able to identify past data inputs and processes to understand their results" as a core need.[^dvc-use-case]

The NIST AI RMF asks teams to document the test sets, metrics and tools that they use for testing (MEASURE 2.1).[^nist-ai-rmf] ISO/IEC 42001 has a control to record the provenance of the data that an AI system uses (A.7.5).[^iso-42001-a7] A data version ID is the simplest record of which data you used.

Think of a Grand Prix result sheet. The provisional result comes at the flag, and the final result comes after the stewards. Both are versions of the same timing sheet, and you can always go back to either one.

# Examples

- The 2026 F1 results come out twice: provisional results right after each race, and final results after the stewards' penalties, 2 to 26 hours later.[^lab-01] In lab 01 you keep both as two DVC versions of one file, `f1/data/season_2026.csv`.
- Version 1 (provisional) has md5 `1dee862a3599e087b764cfb9ebd79ee8`. Version 2 (final) has md5 `87ffbc792aeb259333a41f7f573a38e3`.[^lab-01]
- `dvc diff HEAD~1` shows the file as modified.[^lab-01] The command lists the files that were added, modified, renamed or deleted between commits.[^dvc-diff] Between the two versions, 23 finish positions and 6 labels (`points_finish`) changed.
- You train on Monday morning and the stewards publish a penalty on Monday afternoon. The data version in your training record tells you, three months later, that your model used the provisional labels. Lab 02 logs this version with each run. See [Data lineage](/knowledge/mlops/data-lineage.md) and [Experiment tracking](/knowledge/mlops/experiment-tracking.md).

# Common mistakes

- Overwriting a data file in place with no version. The old data is gone, and nobody can repeat the old result.
- Committing large data files directly to Git. Git is not made for large binary files. Put the data under DVC and commit only the pointer.
- Running `dvc checkout` without `git checkout` first. DVC follows the pointer that Git has checked out, so nothing changes.[^lab-01]
- Versioning the data but not recording which version each model used. A version that no training run refers to does not help you explain a model.
- Treating "the 2026 results" as one dataset. Provisional and final results are two versions, and 6 labels differ. See [Delayed labels](/knowledge/mlops/delayed-labels.md).

[^dvc-use-case]: DVC documentation, "Use case: Versioning data and models", https://doc.dvc.org/use-cases/versioning-data-and-models
[^dvc-get-started]: DVC documentation, "Get started: Data versioning", https://doc.dvc.org/start/data-management/data-versioning
[^dvc-diff]: DVC documentation, "dvc diff", https://doc.dvc.org/command-reference/diff
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 2, branch `01-data-engineering`
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE function), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
