---
type: Domain Concept
title: Data leakage
description: Information about the target that is not available at prediction time gets into the model's inputs, so test scores look better than real use.
tags: [mlops, data-engineering, leakage, evaluation]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 2.3", "NIST-AI-RMF:MEASURE 2.5", "ISO-42001:A.7.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T10:30:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: kaufman-2011
    resource: https://doi.org/10.1145/2020408.2020496
    title: "Leakage in data mining: formulation, detection, and avoidance (KDD '11, pp. 556-563)"
    author: Shachar Kaufman, Saharon Rosset, Claudia Perlich
  - id: sklearn-pitfalls
    resource: https://scikit-learn.org/stable/common_pitfalls.html
    title: "Common pitfalls and recommended practices: data leakage"
    author: scikit-learn developers
  - id: google-monitoring
    resource: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    title: "Machine Learning Crash Course: Production ML systems, monitoring pipelines"
    author: Google for Developers
  - id: f1-data
    resource: https://github.com/majlisofai/mlops-training/blob/main/f1/data/README.md
    title: "Data: the Synthetic Grand Prix Championship"
    author: mlops-training
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

Data leakage is "the introduction of information about the data mining target, which should not be legitimately available to mine from".[^kaufman-2011] scikit-learn puts it more simply: leakage occurs when information that is not available at prediction time is used to build the model.[^sklearn-pitfalls]

A trivial example is a model that uses the target itself as an input and concludes that "it rains on rainy days".[^kaufman-2011] In real projects the leak is usually subtle and comes from the way the data was collected, joined or prepared.[^kaufman-2011]

# Why it matters

Leakage gives overly optimistic test scores and poorer results on new data in production.[^sklearn-pitfalls] At the very least, it makes you overestimate the model's performance. The client finds out only when the model performs worse in use.[^kaufman-2011] Google's crash course warns that leakage is sometimes very difficult to detect, and that very good evaluation metrics are a reason to look for it.[^google-monitoring]

The NIST AI RMF asks teams to document data selection and construct validation (MAP 2.3), and to show that a system is valid and reliable before deployment (MEASURE 2.5).[^nist-ai-rmf] A leaky model fails both. ISO/IEC 42001 control A.7.6 covers the criteria for data preparation, which is where most leaks enter.[^iso-42001-a7]

It is like knowing the finishing order before the race. Your prediction looks perfect, but you learned nothing, and it is useless before the lights go out, when nobody knows the order yet.

# Examples

- In `f1/data/races.csv`, the target `points_finish` is 1 when a car finishes in the top 10.[^f1-data] The rule "`finish_position` ≤ 10" and the rule "`points` > 0" are right for every row (1.0).[^lab-01] They are not clever features. They are the answer.
- The F1 data README has a **Known** column that says if each value is known before or after the race.[^f1-data] The six leakage columns are `finish_position`, `points`, `status`, `laps_completed`, `fastest_lap` and `actual_rain`.[^lab-01]
- `rain_prob` (the forecast) is a legal input. `actual_rain` (it rained during the race) is leakage. The two columns look alike, but only one is known before the race.[^f1-data]
- An honest baseline: the grid-only rule "start in the top ten, score points" is right for 0.804 of 2025 entries, and the reference model is right for 0.835.[^f1-data] A model that scores near 1.0 on this data has almost certainly used a leakage column. See [Baseline model](/knowledge/mlops/baseline-model.md).
- Kaufman et al. propose a learn-predict separation. When legitimacy is defined by time, you tag every observation with a timestamp and cut the data at one point in time.[^kaufman-2011] The F1 data is already cut this way: `races.csv` holds training (2021-2024) and the holdout (2025).[^f1-data] Lab 03 uses this [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).

# Common mistakes

- Judging a column by its name or its correlation, not by when its value is known. Ask "is this known before the race?" for every input.
- Deleting the obvious leaks (`finish_position`, `points`) and keeping a subtle one (`status`, `laps_completed`). A car with few laps completed did not finish, so it did not score.
- Fitting preprocessing on all the data before the split. scikit-learn's rule is to never call `fit` on the test data.[^sklearn-pitfalls]
- Splitting rows at random when the data has time order. Information from later races can then leak into training. See [Temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).
- Treating a near-perfect test score as good news. Treat it as a reason to look for leakage.[^google-monitoring]

[^kaufman-2011]: S. Kaufman, S. Rosset, C. Perlich, "Leakage in data mining: formulation, detection, and avoidance", Proc. KDD '11, pp. 556-563, https://doi.org/10.1145/2020408.2020496
[^sklearn-pitfalls]: scikit-learn, "Common pitfalls and recommended practices", section "Data leakage", https://scikit-learn.org/stable/common_pitfalls.html
[^google-monitoring]: Google, Machine Learning Crash Course, "Production ML systems: Monitoring pipelines", https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
[^f1-data]: mlops-training, `f1/data/README.md`, column table
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 1 and its answers, branch `01-data-engineering`
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Tables 2 and 3 (MAP and MEASURE functions), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
