---
type: Domain Concept
title: Validity vs distribution checks
description: Validity checks ask if each value is allowed; distribution checks ask if the batch looks like the training data. Valid data can still fail the second.
tags: [mlops, data-engineering, data-quality, validation, drift]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MEASURE 2.5", "ISO-42001:A.7.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:30:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: breck-2019
    resource: https://mlsys.org/Conferences/2019/doc/2019/167.pdf
    title: Data validation for machine learning (MLSys 2019)
    author: Eric Breck, Neoklis Polyzotis, Sudip Roy, Steven Euijong Whang, Martin Zinkevich
  - id: google-monitoring
    resource: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    title: "Machine Learning Crash Course: Production ML systems, monitoring pipelines"
    author: Google for Developers
  - id: evidently-monitoring
    resource: https://www.evidentlyai.com/ml-in-production/model-monitoring
    title: "Model monitoring for ML in production: a comprehensive guide"
    author: Evidently AI
  - id: lab-01
    resource: https://github.com/majlisofai/mlops-training/blob/01-data-engineering/exercises/data-engineering/README.md
    title: "Lesson 01: data engineering"
    author: mlops-training
  - id: f1-data
    resource: https://github.com/majlisofai/mlops-training/blob/main/f1/data/README.md
    title: "Data: the Synthetic Grand Prix Championship"
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

A **validity check** looks at each value or row and asks: is this value allowed? Examples are not-null checks, range checks, allowed-value sets and uniqueness checks. One batch is enough to run them.

A **distribution check** looks at a statistic of the whole batch and asks: does this batch look like the data the model learned from? Examples are a mean, a share of a category, or a distance between two distributions. It needs a reference, usually the training data.

The TFX data validation paper makes the same split. Single-batch validation asks if there are anomalies in one batch. Inter-batch validation asks if there are significant changes between the training and the serving data.[^breck-2019] Distribution skew occurs when the distribution of feature values in training is different from the one at serving time.[^breck-2019]

# Why it matters

A batch where every value is valid can still be very different from the training data. A model trained on the old distribution then makes worse predictions, and no validity check warns you. Google's crash course says to check separately the statistics that your schema does not check.[^google-monitoring] Evidently describes data drift as a change in the statistical properties of the input data, and uses drift as a proxy sign of model quality problems.[^evidently-monitoring]

The NIST AI RMF asks teams to monitor the system's behaviour in production (MEASURE 2.4) and to document the limits of generalization beyond the conditions of development (MEASURE 2.5).[^nist-ai-rmf] A distribution check is a simple way to see when data leaves those conditions. ISO/IEC 42001 control A.7.4 covers data quality for AI systems.[^iso-42001-a7]

Allowed is not the same as normal. Every 2026 car passes scrutineering, yet 27.5 % retire instead of 10.9 %. Each car is legal, but something has changed.

# Examples

- The lab 01 suite has 12 validity checks and 1 distribution check.[^lab-01] The validity checks are the not-null, range, allowed-value and uniqueness checks. The distribution check is the mean of `dnf` between 0.05 and 0.20.
- On `season_2026.csv` all 12 validity checks pass: no nulls, no values out of range, no duplicates. The `dnf` mean is 0.275, so the distribution check fails (12 of 13).[^lab-01]
- In training, 10.9 % of entries do not finish. In 2026, 27.5 % do not finish, because of new, fragile power units.[^f1-data] Each DNF row is valid. The share of DNF rows is not normal.
- The F1 data also has a serving-skew scenario: a new timing feed sends `quali_gap_ms` in seconds, not milliseconds.[^f1-data] A range check of 0 to 5,000 still passes on values divided by 1,000. A distribution check on the mean of `quali_gap_ms` would catch it. This is the lab's stretch exercise.[^lab-01]

# Common mistakes

- Writing only validity checks and calling the data "validated". The 2026 data passes every validity check in the lab.
- Setting the distribution range from a guess. The lab uses 0.05 to 0.20 around a training value of 0.109. In a real system, base the range on the variation seen between past batches, and review it with domain experts.
- Using a distribution check on a batch that is too small. A mean over a few rows changes a lot by chance, and the check gives false alarms.
- Treating every distribution alarm as bad data. A distribution check says "different", not "wrong". In 2026 the data is correct; the world changed. The right action can be to retrain, not to reject the data.

[^breck-2019]: E. Breck et al., "Data validation for machine learning", MLSys 2019, sections 2 and 4, https://mlsys.org/Conferences/2019/doc/2019/167.pdf
[^google-monitoring]: Google, Machine Learning Crash Course, "Production ML systems: Monitoring pipelines", https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
[^evidently-monitoring]: Evidently AI, "Model monitoring for ML in production", https://www.evidentlyai.com/ml-in-production/model-monitoring
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 3 and the stretch exercises, branch `01-data-engineering`
[^f1-data]: mlops-training, `f1/data/README.md`, files and facts you can check
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE function), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
