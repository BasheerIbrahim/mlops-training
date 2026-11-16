---
type: Domain Concept
title: Data profiling
description: Summarising every column of a dataset (types, ranges, missing values, distributions, correlations) before you train, to learn what normal data looks like.
tags: [mlops, data-engineering, profiling, exploration, ydata-profiling, duckdb]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 2.3", "ISO-42001:A.7.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:45:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: ydata-home
    resource: https://docs.profiling.ydata.ai/latest/
    title: ydata-profiling documentation
    author: YData
  - id: ydata-concepts
    resource: https://docs.profiling.ydata.ai/latest/getting-started/concepts/
    title: "ydata-profiling: Concepts"
    author: YData
  - id: ydata-big-data
    resource: https://docs.profiling.ydata.ai/latest/features/big_data/
    title: "ydata-profiling: Profiling large datasets"
    author: YData
  - id: duckdb-pandas
    resource: https://duckdb.org/docs/stable/guides/python/sql_on_pandas
    title: SQL on pandas
    author: DuckDB documentation
  - id: google-numerical
    resource: https://developers.google.com/machine-learning/crash-course/numerical-data/first-steps
    title: "Machine Learning Crash Course: Numerical data, first steps"
    author: Google for Developers
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

Data profiling is a summary of each column in a dataset: its type, its range, its missing values, its distribution, and how it relates to other columns. You make a profile before you train a model, and you use it to learn what normal data looks like.

ydata-profiling makes this summary with one line of code, as an HTML report or a Jupyter widget.[^ydata-home] The report has sections for data types, single variables, correlations between pairs of numerical variables, missing data, and automatic data quality alerts.[^ydata-concepts] Google's crash course recommends the same first step: plot the data, and compute basic statistics such as the mean, the median and the quartiles. The 0th percentile is the minimum and the 100th percentile is the maximum.[^google-numerical]

# Why it matters

You cannot write a good quality check if you do not know what good data looks like. The profile gives you the facts: the ranges, the share of missing values, the outliers. These facts become the rules of your [data validation](/knowledge/mlops/data-validation.md).

The NIST AI RMF asks teams to document data collection and selection, including availability, representativeness and suitability (MAP 2.3).[^nist-ai-rmf] ISO/IEC 42001 control A.7.4 covers the quality of data for AI systems.[^iso-42001-a7] A profile is the first evidence for both.

A profile is like studying the timing sheets before you predict: how many races, how many cars, how many do not finish. You write the facts down, so that a later change stands out.

# Examples

- In lab 01, DuckDB runs SQL directly on the pandas DataFrame `races`. DuckDB can query a DataFrame in a local variable as if it were a table.[^duckdb-pandas] The first query gives 120 races, 2,400 entries, 28 drivers, a points share of 0.5 and a DNF rate of 0.10875.[^lab-01]
- The same DNF query on the provisional 2026 results gives 0.275, against 0.109 in training. The rate is high for every team tier.[^lab-01] Profiling found the change in the data before any model saw it.
- The ydata-profiling report of the seven model inputs shows that `rain_prob` goes from 0 to 0.55 and `quali_gap_ms` from 0 to 2,839.[^lab-01] In part 3 these ranges become checks.
- The lab uses `minimal=True`. Minimal mode turns off the most expensive computations and is the recommended start for large datasets.[^ydata-big-data]

# Common mistakes

- Profiling only the training data. Profile each new batch too, and compare it with the training profile. The 2026 DNF rate is the lesson.
- Reading the profile and not writing down the numbers. A range that you do not turn into a check does not protect you.
- Copying observed minimum and maximum values into checks without thought. `rain_prob` is 0 to 0.55 in training, but a valid probability is 0 to 1. A storm forecast of 0.9 is valid data, not an error.
- Profiling every column, including leakage columns and identifiers, and then using strong correlations to pick features. A strong correlation with the target can be a sign of [data leakage](/knowledge/mlops/data-leakage.md).

[^ydata-home]: YData, ydata-profiling documentation, https://docs.profiling.ydata.ai/latest/
[^ydata-concepts]: YData, ydata-profiling, "Concepts", https://docs.profiling.ydata.ai/latest/getting-started/concepts/
[^ydata-big-data]: YData, ydata-profiling, "Profiling large datasets", https://docs.profiling.ydata.ai/latest/features/big_data/
[^duckdb-pandas]: DuckDB documentation, "SQL on pandas", https://duckdb.org/docs/stable/guides/python/sql_on_pandas
[^google-numerical]: Google, Machine Learning Crash Course, "Numerical data: First steps", https://developers.google.com/machine-learning/crash-course/numerical-data/first-steps
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 1, `explore.ipynb` and the answers, branch `01-data-engineering`
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 2 (MAP function), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
