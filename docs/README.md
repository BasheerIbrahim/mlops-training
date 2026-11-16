---
type: Reference
title: How the docs folder works
description: The docs folder records the concepts of each lab as an OKF bundle, and each lab deck is built from it.
---

# How the docs folder works

This folder is the knowledge base of the training. It records the concepts that trainees learn in each lab. We use it to make the slide decks for the classroom.

The folder is one bundle in Google's [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog), with the Majlis Academy profile `majlis-academy/1`. A plain OKF reader can read every file.

## What is in it

| Path | OKF type | What it holds |
|---|---|---|
| `index.md` | (bundle root) | The OKF version and the profile |
| `log.md` | (log) | One line for each change, newest first |
| `knowledge/mlops/<slug>.md` | Domain Concept | One concept, such as data versioning or a quality gate |
| `packages/lab-<nn>-<name>.md` | Learning Package | One classroom deck: the concepts it uses and the slide outline |
| `references/skills/validate_bundle.py` | (tool) | The validator |

| Lab | Branch | Deck |
|---|---|---|
| 01 Data engineering | `01-data-engineering` | [Lab 01](packages/lab-01-data-engineering.md) |
| 02 MLflow | `02-mlflow` | [Lab 02](packages/lab-02-mlflow.md) |
| 03 Build a model | `03-build-model` | [Lab 03](packages/lab-03-build-model.md) |
| 04 Quality gates | `04-quality-gates` | [Lab 04](packages/lab-04-quality-gates.md) |
| 05 Serve the model | `05-serve-model` | [Lab 05](packages/lab-05-serve-model.md) |

## Rules for a concept

1. One concept per file, in Markdown with YAML frontmatter.
2. `type: Domain Concept`, a sentence-case `title`, and a `description` of one sentence (25 words or fewer).
3. `classification: public`, at least one `framework_refs` entry (for MLOps we use `NIST-AI-RMF:<subcategory>` and `ISO-42001:<clause or control>`), and a `stale_after` date.
4. `sources`: every claim from outside the labs has a footnote `[^id]` that matches a `sources[].id`. Use official documentation first.
5. `generated` records who wrote the file. An agent writes `majlis-academy-knowledge-harvester/<model>`. Only a person adds `verified: { by: human:<id>, at: ... }`, after they review the file.
6. New concepts start as `status: draft`. Only a person moves a concept to `stable`.
7. Body sections: `# Definition`, `# Why it matters`, `# Examples`, `# Common mistakes`. Examples use the lab data and the numbers measured in the lab.
8. Links to other files start with `/`, from the folder root: `/knowledge/mlops/data-versioning.md`.
9. Add one line to `log.md` for each change.

## Validate

```bash
python docs/references/skills/validate_bundle.py docs
python docs/references/skills/validate_bundle.py docs --package /packages/lab-01-data-engineering --now 2026-11-16
```

The first command checks the format. The second also runs the release gates for one deck: G1 needs every concept at the deck's `min_trust` and out of `draft`, and G5 fails when a concept is past its `stale_after` date. A deck is ready for the classroom when the second command passes.

## Make a deck from a package

1. Open the package. `uses` lists the concepts, and `# Deck outline` gives one row per slide.
2. Build the slides from the outline, and use the concept files for the facts, the examples and the speaker notes.
3. Use the Elm template for the classroom decks.
