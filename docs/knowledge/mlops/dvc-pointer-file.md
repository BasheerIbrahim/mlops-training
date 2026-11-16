---
type: Domain Concept
title: DVC pointer file
description: The small .dvc text file that Git versions in place of the data; its md5 hash names the data version in the DVC cache.
tags: [mlops, data-engineering, versioning, dvc, git]
status: draft
classification: public
framework_refs: ["ISO-42001:A.7.5"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:15:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: dvc-files
    resource: https://doc.dvc.org/user-guide/project-structure/dvc-files
    title: .dvc files
    author: DVC documentation
  - id: dvc-get-started
    resource: https://doc.dvc.org/start/data-management/data-versioning
    title: "Get started: Data versioning"
    author: DVC documentation
  - id: dvc-add
    resource: https://doc.dvc.org/command-reference/add
    title: dvc add
    author: DVC documentation
  - id: dvc-internal
    resource: https://doc.dvc.org/user-guide/project-structure/internal-files
    title: Internal directories and files
    author: DVC documentation
  - id: dvc-checkout
    resource: https://doc.dvc.org/command-reference/checkout
    title: dvc checkout
    author: DVC documentation
  - id: lab-01
    resource: https://github.com/majlisofai/mlops-training/blob/01-data-engineering/exercises/data-engineering/README.md
    title: "Lesson 01: data engineering"
    author: mlops-training
  - id: iso-42001-a7
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-7-data-for-ai-systems/
    title: "ISO 42001 Annex A control A.7: Data for AI systems"
    author: ISMS.online
---

# Definition

A DVC pointer file (a `.dvc` file) is a small, human-readable text file that stands in for a data file in Git.[^dvc-get-started] DVC calls `.dvc` files "data placeholders that can be versioned with Git".[^dvc-files] The file is YAML. Its `outs` list gives the `path` of the tracked data, its `size`, and its `md5` hash.[^dvc-files]

The data itself goes to the DVC cache, `.dvc/cache`. The cache is content-addressable: the hash of the file gives its place in the cache.[^dvc-internal] So the md5 in the pointer file is the data version.

# Why it matters

Git is good at small text files and bad at large data files. The pointer file lets Git version the data without holding it. Each Git commit holds a pointer, and each pointer names exactly one version of the data in the cache. The Git history of the pointer is a simple provenance record, which ISO/IEC 42001 control A.7.5 (data provenance) asks for.[^iso-42001-a7]

`dvc add` also adds the data file to `.gitignore`, so that Git does not commit the data by mistake.[^dvc-add] `dvc checkout` restores the data that matches the current pointers from the cache to the workspace. You usually run it after `git checkout`.[^dvc-checkout]

Think of the ticket for a timing sheet in the team's archive. Git keeps the ticket (the pointer file). DVC keeps the sheet in the archive (the data). Show the right ticket and you get the right sheet back.

# Examples

- In lab 01, `dvc add f1/data/season_2026.csv` makes the pointer file `f1/data/season_2026.csv.dvc` and adds the CSV to `f1/data/.gitignore`. You commit only these two small files.[^lab-01]
- The pointer for the provisional 2026 results has md5 `1dee862a3599e087b764cfb9ebd79ee8`. After `apply_stewards.py` changes 23 positions and you run `dvc add` again, the md5 is `87ffbc792aeb259333a41f7f573a38e3`.[^lab-01]
- To go back to the provisional results: `git checkout HEAD~1 -- f1/data/season_2026.csv.dvc` moves the ticket, then `dvc checkout f1/data/season_2026.csv` fetches the matching sheet from the cache.[^lab-01]
- Lab 02 logs this md5 to MLflow as the data version of each run. See [Data lineage](/knowledge/mlops/data-lineage.md).

# Common mistakes

- Running `dvc checkout` and expecting a change when the pointer did not change. DVC follows the pointer that Git has checked out.[^lab-01]
- Forgetting to `git add` and commit the `.dvc` file after `dvc add`. The new data is in the cache, but no commit points to it.
- Running `dvc add` on a file that Git already tracks. For `f1/data/races.csv` you must run `git rm --cached f1/data/races.csv` first.[^lab-01]
- Editing the md5 in the pointer file by hand. The hash must come from the data, or it points to nothing.
- Deleting the cache without a remote copy. `dvc checkout` fails for files that are missing from the cache.[^dvc-checkout]

[^dvc-files]: DVC documentation, ".dvc files", https://doc.dvc.org/user-guide/project-structure/dvc-files
[^dvc-get-started]: DVC documentation, "Get started: Data versioning", https://doc.dvc.org/start/data-management/data-versioning
[^dvc-add]: DVC documentation, "dvc add", https://doc.dvc.org/command-reference/add
[^dvc-internal]: DVC documentation, "Internal directories and files", https://doc.dvc.org/user-guide/project-structure/internal-files
[^dvc-checkout]: DVC documentation, "dvc checkout", https://doc.dvc.org/command-reference/checkout
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 2 and the troubleshooting table, branch `01-data-engineering`
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
