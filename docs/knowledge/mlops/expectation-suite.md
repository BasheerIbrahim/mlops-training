---
type: Domain Concept
title: Expectation suite
description: In Great Expectations, a named collection of expectations that you run on a batch of data to get one result per check.
tags: [mlops, data-engineering, data-quality, great-expectations]
status: draft
classification: public
framework_refs: ["ISO-42001:A.7.4", "NIST-AI-RMF:MEASURE 2.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:15:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: gx-suite
    resource: https://docs.greatexpectations.io/docs/reference/learn/terms/expectation_suite
    title: Expectation Suite
    author: Great Expectations documentation
  - id: gx-expectation
    resource: https://docs.greatexpectations.io/docs/reference/learn/terms/expectation
    title: Expectation
    author: Great Expectations documentation
  - id: gx-overview
    resource: https://docs.greatexpectations.io/docs/core/introduction/gx_overview
    title: GX Core overview
    author: Great Expectations documentation
  - id: gx-run
    resource: https://docs.greatexpectations.io/docs/core/run_validations/run_a_validation_definition
    title: Run a Validation Definition
    author: Great Expectations documentation
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

An expectation suite is "a collection of verifiable assertions about data".[^gx-suite] Each assertion is an *Expectation*.[^gx-expectation] With a suite, you validate one batch of data against many expectations at once.[^gx-overview]

You run a suite on a batch and get Validation Results. The results tell you how your data corresponds to what you expected of it.[^gx-overview] Each result shows if its expectation passed or failed.[^gx-run] GX stores suites separately from Checkpoints, so you can use one suite in many Checkpoints.[^gx-suite]

# Why it matters

A suite puts all the rules for one dataset in one place, with one name. You can review it, version it with the code, and run the same rules on every new batch. Part of the value is communication: expectations make the hidden assumptions about a dataset explicit.[^gx-expectation]

The NIST AI RMF asks teams to document the test sets, metrics and tools that they use for testing (MEASURE 2.1).[^nist-ai-rmf] ISO/IEC 42001 control A.7.4 covers data quality.[^iso-42001-a7] A suite in Git is a written, repeatable record of the data quality rules.

A suite is like the teacher's checklist for homework: name on the page, every answer filled in, answers in the allowed range. The teacher uses the same checklist for every pupil.

# Examples

- Lab 01 builds one suite, `f1-results`, in `build_expectations()`. It holds 13 expectations.[^lab-01-solution]
  - Seven `ExpectColumnValuesToNotBeNull` checks, one for each model input.
  - `ExpectColumnValuesToBeBetween`: `grid` from 1 to 20, `rain_prob` from 0 to 1.
  - `ExpectColumnValuesToBeInSet`: `circuit_type` in street, permanent, high_speed; `status` in Finished, DNF.
  - `ExpectCompoundColumnsToBeUnique` on `race_id` and `driver_code`: one row per car per race.
  - `ExpectColumnMeanToBeBetween`: the mean of `dnf` from 0.05 to 0.20.
- The same suite gives 13 of 13 on `races.csv` and 12 of 13 on `season_2026.csv`.[^lab-01] One suite, two batches, two different answers.
- The lab runs the suite in an ephemeral GX context on a pandas DataFrame, so it needs no GX project folder.[^lab-01-solution]
- Lab 02 writes the same kind of rules as a pandera [dataframe schema](/knowledge/mlops/dataframe-schema.md). The tool changes; the idea of one named rule set does not.

# Common mistakes

- Building a new suite for each file. Use one suite for one kind of data, so that the training data and the new data meet the same rules.
- Changing the suite to make a failing batch pass. If the 2026 data fails the `dnf` check, first find out why. Then decide on purpose if the rule or the data is wrong.
- Keeping the suite only in a notebook. Put it in a script or module under version control, as the lab does with `quality_checks.py`.
- Reading only the overall result. Read each result. "12 of 13" tells you which rule failed and the observed value (0.275).

[^gx-suite]: Great Expectations, "Expectation Suite", https://docs.greatexpectations.io/docs/reference/learn/terms/expectation_suite
[^gx-expectation]: Great Expectations, "Expectation", https://docs.greatexpectations.io/docs/reference/learn/terms/expectation
[^gx-overview]: Great Expectations, "GX Core overview", https://docs.greatexpectations.io/docs/core/introduction/gx_overview
[^gx-run]: Great Expectations, "Run a Validation Definition", https://docs.greatexpectations.io/docs/core/run_validations/run_a_validation_definition
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 3, branch `01-data-engineering`
[^lab-01-solution]: mlops-training, `exercises/data-engineering/solution/quality_checks.py`, branch `01-data-engineering`
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE function), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
