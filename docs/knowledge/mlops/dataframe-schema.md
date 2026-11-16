---
type: Domain Concept
title: DataFrame schema
description: A pandera object that states in code the columns, types, value checks and uniqueness rules that a valid table must meet.
tags: [mlops, pandera, data-validation, schema, data-quality]
status: draft
classification: public
framework_refs: ["ISO-42001:A.7.4", "NIST-AI-RMF:MAP 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:50:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: pandera-schemas
    resource: https://pandera.readthedocs.io/en/stable/dataframe_schemas.html
    title: DataFrame Schemas
    author: team:pandera
  - id: pandera-checks
    resource: https://pandera.readthedocs.io/en/stable/checks.html
    title: Validating with Checks
    author: team:pandera
  - id: pandera-lazy
    resource: https://pandera.readthedocs.io/en/stable/lazy_validation.html
    title: Lazy Validation
    author: team:pandera
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

A DataFrame schema is a pandera object that verifies the columns and the index of a pandas DataFrame.[^pandera-schemas] It is a form of [data validation](/knowledge/mlops/data-validation.md) written as code. It has these parts:

- **Columns.** Each `Column` can check its data type, its null values and its duplicates.[^pandera-schemas]
- **Column checks.** A check runs a function on the column values, for example `Check.isin([...])`. Pandera has built-in checks for common tasks.[^pandera-checks]
- **Wide checks.** A check on the whole DataFrame can compare columns. Its function returns a boolean, a Series of booleans or a DataFrame of booleans.[^pandera-checks]
- **Uniqueness.** `unique=[...]` makes a group of columns unique together.[^pandera-schemas]

`schema.validate(df, lazy=True)` runs every check and does not stop at the first error. It raises `SchemaErrors`. Its `failure_cases` DataFrame has one row per failure, with the columns `schema_context`, `column`, `check`, `check_number`, `failure_case` and `index`.[^pandera-lazy]

# Why it matters

A schema turns "what good data looks like" into a test that a program can run on each new file. ISO/IEC 42001 control A.7.4 asks the organization to define and meet requirements for data quality.[^iso-42001][^advisera-42001] NIST AI RMF MAP 2.3 asks that data selection, including its suitability, is documented.[^nist-ai-rmf] The schema is that requirement, kept in Git next to the code, and the failure cases are the evidence.

Think of the technical regulations for a car. Each part must be the right type and inside its limits, and each car is entered once per race. The scrutineers check every car against the rules before it races.

# Examples

The lab schema for `races.csv` has 17 column rules and 2 table rules:[^lab02-solution]

- Types and ranges: `season` is an integer from 2021 to 2025, `grid` from 1 to 20, `quali_gap_ms` an integer ≥ 0, `rain_prob` from 0 to 1.
- Allowed values: `team_tier` is `top`, `midfield` or `backmarker`. `status` is `Finished` or `DNF`.
- One row per car per race: `unique=["race_id", "driver_code"]`.
- A wide check, `target_matches_finish_position`: `points_finish` is 1 exactly when `finish_position` is 10 or better.

On the original data (2,400 rows, 23 columns), the schema finds 0 failure cases.[^lab02] After the timing feed sends `quali_gap_ms` in seconds, the values are decimals such as 1.08 instead of 1080. The schema finds 1 failure case: the check `dtype('int64')` on `quali_gap_ms`, with the failure case `float64`. The range check `ge(0)` still passes, because seconds are not negative.

# Common mistakes

- Checking types only. The wide check catches a wrong target that each column alone cannot show.
- Trusting a range check to catch a unit change. `quali_gap_ms >= 0` passes for seconds too. If the feed sent whole seconds as integers, the type check would also pass. Add a check on the scale, for example on the median, or a distribution check. See [validity vs distribution checks](/knowledge/mlops/validity-vs-distribution-checks.md).
- Using `coerce=True` without thought. Pandera then converts the column to the type before it checks.[^pandera-schemas] That can hide the change of the timing feed.
- Validating without `lazy=True`. Then you see only the first error, and you fix the data one error at a time.[^pandera-lazy]
- Writing the schema once and never changing it. When the column dictionary in `f1/data/README.md` changes, change the schema in the same commit.

[^pandera-schemas]: pandera documentation, "DataFrame Schemas", sections on columns, uniqueness and coercion.
[^pandera-checks]: pandera documentation, "Validating with Checks", sections on built-in checks and wide checks.
[^pandera-lazy]: pandera documentation, "Lazy Validation".
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 2.3).
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.7.4 (quality of data for AI systems).
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.7.4.
[^lab02]: Lab 02 exercise README, steps 3 and 5.
[^lab02-solution]: Lab 02 reference solution, `SCHEMA`.
