---
type: Domain Concept
title: Data validation
description: Automatic checks that each batch of data must pass before a pipeline uses it, with a pass or a fail for each check.
tags: [mlops, data-engineering, data-quality, validation, great-expectations, pandera]
status: draft
classification: public
framework_refs: ["ISO-42001:A.7.4", "NIST-AI-RMF:MAP 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:00:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: breck-2019
    resource: https://mlsys.org/Conferences/2019/doc/2019/167.pdf
    title: Data validation for machine learning (MLSys 2019)
    author: Eric Breck, Neoklis Polyzotis, Sudip Roy, Steven Euijong Whang, Martin Zinkevich
  - id: gx-overview
    resource: https://docs.greatexpectations.io/docs/core/introduction/gx_overview
    title: GX Core overview
    author: Great Expectations documentation
  - id: gx-expectation
    resource: https://docs.greatexpectations.io/docs/reference/learn/terms/expectation
    title: Expectation
    author: Great Expectations documentation
  - id: pandera
    resource: https://pandera.readthedocs.io/en/stable/
    title: Pandera documentation
    author: Pandera
  - id: google-monitoring
    resource: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    title: "Machine Learning Crash Course: Production ML systems, monitoring pipelines"
    author: Google for Developers
  - id: lab-01
    resource: https://github.com/majlisofai/mlops-training/blob/01-data-engineering/exercises/data-engineering/README.md
    title: "Lesson 01: data engineering"
    author: mlops-training
  - id: lab-01-solution
    resource: https://github.com/majlisofai/mlops-training/blob/01-data-engineering/exercises/data-engineering/solution/quality_checks.py
    title: "Lesson 01 reference solution: quality_checks.py"
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

Data validation runs automatic checks on each batch of data before a pipeline uses it. Each check gives a pass or a fail. If a check fails, the pipeline stops or raises an alert.

Great Expectations (GX) calls each check an *Expectation*, "a verifiable assertion about data". GX applies Expectations to data in the way that unit tests apply to code.[^gx-expectation] GX Core is a Python library for building and running data validation workflows.[^gx-overview] pandera does the same job for dataframes with a schema in Python code.[^pandera] Google's TFX data validation system asks two questions: are there anomalies in one batch, and are there significant changes between the training data and the serving data?[^breck-2019]

# Why it matters

Errors in the input data can cancel every benefit of a good training algorithm.[^breck-2019] A bad batch that gets into training gives a bad model, and nothing in the training code warns you. Validation finds the problem at the door, before training, and tells you which rule failed.

ISO/IEC 42001 control A.7.4 covers the quality of data for AI systems.[^iso-42001-a7] The NIST AI RMF asks teams to document data suitability (MAP 2.3).[^nist-ai-rmf] A validation suite that runs on every batch turns these requirements into code, and its results are the evidence.

Think of a rule checker at the door, or a teacher who checks homework before marking it. Missing name? Answer outside the allowed range? The homework goes back before anybody grades it.

# Examples

- In lab 01, `quality_checks.py` runs 13 checks with Great Expectations: not-null checks for the seven model inputs, ranges for `grid` and `rain_prob`, allowed values for `circuit_type` and `status`, one row per `race_id` and `driver_code`, and the mean of `dnf`.[^lab-01-solution]
- On `f1/data/races.csv`, 13 of 13 checks pass and the exit code is 0. On `f1/data/season_2026.csv`, 12 of 13 pass. The `dnf` mean check fails with 0.275, and the exit code is 1.[^lab-01]
- The non-zero exit code lets a pipeline stop on bad data.[^lab-01-solution] Lab 02 uses this idea in a [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md), and lab 04 uses it in a [quality gate](/knowledge/mlops/quality-gate.md).
- The course's tech pack pairs DVC with pandera. Lab 01 uses Great Expectations, and lab 02 uses pandera to define a [dataframe schema](/knowledge/mlops/dataframe-schema.md). The idea is the same in both tools.

# Common mistakes

- Checking only the schema and the types. Google's crash course says to check separately the statistics that your schema does not check.[^google-monitoring] See [Validity vs distribution checks](/knowledge/mlops/validity-vs-distribution-checks.md).
- Running the checks but not acting on the result. A check that prints "FAIL" and lets the pipeline go on is a log line, not a control.
- Validating the training data once and never the new batches. Each new batch needs the same checks.
- Writing checks that fail on good data. Too many false alarms teach people to ignore the checks. The suite must pass on the training data, as the lab's suite does (13 of 13).
- Putting leakage columns into the model-input checks. `status` is checked in the lab for validity, but it is not a model input. See [Data leakage](/knowledge/mlops/data-leakage.md).

[^breck-2019]: E. Breck et al., "Data validation for machine learning", MLSys 2019, https://mlsys.org/Conferences/2019/doc/2019/167.pdf
[^gx-overview]: Great Expectations, "GX Core overview", https://docs.greatexpectations.io/docs/core/introduction/gx_overview
[^gx-expectation]: Great Expectations, "Expectation", https://docs.greatexpectations.io/docs/reference/learn/terms/expectation
[^pandera]: Pandera documentation, https://pandera.readthedocs.io/en/stable/
[^google-monitoring]: Google, Machine Learning Crash Course, "Production ML systems: Monitoring pipelines", https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 3, branch `01-data-engineering`
[^lab-01-solution]: mlops-training, `exercises/data-engineering/solution/quality_checks.py`, branch `01-data-engineering`
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 2 (MAP function), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
