---
type: Domain Concept
title: Data drift
description: The inputs in production move away from the data the model learned from. The data can be correct; the world changed.
tags: [mlops, monitoring, drift, data-quality, evidently]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MEASURE 2.5", "ISO-42001:A.6.2.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:20:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: evidently-drift
    resource: https://www.evidentlyai.com/ml-in-production/data-drift
    title: "What is data drift in ML, and how to detect and handle it"
    author: org:evidently-ai
  - id: evidently-methods
    resource: https://docs.evidentlyai.com/metrics/explainer_drift
    title: "Evidently documentation: data drift explainer"
    author: org:evidently-ai
  - id: breck-2019
    resource: https://mlsys.org/Conferences/2019/doc/2019/167.pdf
    title: Data validation for machine learning (MLSys 2019)
    author: Eric Breck, Neoklis Polyzotis, Sudip Roy, Steven Euijong Whang, Martin Zinkevich
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: iso-42001-a6
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-6-ai-system-life-cycle/
    title: "ISO 42001 Annex A control A.6: AI system life cycle"
    author: org:isms-online
  - id: lab06
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/exercises/monitoring/README.md
    title: "Lesson 06: monitor drift, skew and delayed labels"
    author: org:majlisofai
  - id: lab06-key
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/exercises/monitoring/solution/ANSWER_KEY.md
    title: "Drift Detective: answer key for the trainer"
    author: org:majlisofai
  - id: run-alert
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43896456941
    title: "GitHub Actions run 43896456941: monitor, wet_race, MONITOR ALERT: input drift"
    author: org:majlisofai
---

# Definition

Data drift is a change in the inputs that a model gets in production, compared with a reference such as the training data or a recent normal window. Evidently defines it as a shift in the distributions of the model input features.[^evidently-drift]

Data drift is about the inputs alone. Concept drift is a change in the relation between the inputs and the target.[^evidently-drift] See [concept drift](/knowledge/mlops/concept-drift.md). Data drift is also not the same as [training-serving skew](/knowledge/mlops/training-serving-skew.md): with drift the values are correct and the world changed; with skew the values are wrong.

A drift check is a [distribution check](/knowledge/mlops/validity-vs-distribution-checks.md) on production data. It compares a statistic of a window, such as a mean or a spread, with the same statistic in the reference.

# Why it matters

When the inputs leave the region that the model learned from, its answers rest on little experience. The NIST AI RMF says that AI systems may need more frequent maintenance because of data, model or concept drift.[^nist-ai-rmf] It asks teams to monitor the system in production (MEASURE 2.4) and to document the limits of generalization beyond the conditions of development (MEASURE 2.5).[^nist-ai-rmf] ISO/IEC 42001 control A.6.2.6 covers AI system operation and monitoring with production data.[^iso-42001-a6]

Drift is a warning, not a verdict. Evidently notes that data drift can happen without concept drift, and that prediction drift does not always mean that the model got worse.[^evidently-drift] It also warns against using drift alerts as an automatic retraining trigger, because data quality problems are common in production pipelines.[^evidently-drift]

Statistical tests need care. With many rows, a test calls even tiny differences significant.[^breck-2019] [^evidently-drift] With few rows, any new sample can look different. Choose the reference window and the window size on purpose.

On a normal race weekend the rain forecast is low for most cars. Then a storm race comes and the forecast jumps to 0.92 for every car. The timing sheets are right, and the rain is real, but the strategy team should know.

# Examples

- The lab drift check measures, for each numeric feature, how far the mean moved in reference standard deviations, and how the spread changed. It alerts above 2.0 sd, or when the spread falls below x0.5 or grows above x2.[^lab06]
- **Storm.** The `wet_race` window sets `rain_prob` to 0.92 for every car. The reference races have 0.10 to 0.29. The monitor says `rain_prob: mean 0.92 vs 0.185 in the reference, shift 10.41 sd (max 2.0)`. No other feature moves more than 0.25 sd.[^lab06] GitHub Actions run 43896456941 shows the same numbers and fails the job.[^run-alert]
- The storm data is correct: it really will rain. The model saw forecasts up to 0.55 in training, never 0.92. Whether to warn the race engineers is a decision for people, not for the monitor.[^lab06]
- **Evidently as a second opinion.** With reference data of 1000 rows or fewer, Evidently uses a two-sample Kolmogorov-Smirnov test for numeric columns and a chi-square test for categorical ones. A p-value of 0.05 or less means drift.[^evidently-methods] On the storm it flags `rain_prob` and `circuit_type`. The second flag is not drift: one race has one circuit type, so the window is too small.[^lab06]
- **Normal variation.** Four ordinary 2025 races move `rain_prob` by 1.03 sd, under the threshold. Evidently flags `team_dnf_rate` and `rain_prob`, because four races give only four rain forecasts.[^lab06-key]
- **No drift, worse model.** In 2026 the largest move is `team_dnf_rate`, shift 1.03 sd and spread x1.27. Input drift passes, but accuracy falls from 0.842 to 0.706. Only the labels show it.[^lab06]
- **The mean hides a stuck value.** When `driver_form` is stuck at 10.0, its mean moves only 0.14 sd. The spread falls to x0, and the spread check alerts.[^lab06-key]

# Common mistakes

- Treating every drift alert as bad data. The storm is real. Ask "is it different?" first, then "is it wrong?".
- Checking only the mean. A stuck feature keeps a normal mean and loses all its spread.
- Checking a spread that is constant by design. All 20 cars in a race have the same rain forecast, so the lab does not check the spread of `rain_prob`.[^lab06]
- Using a reference or a window that is too small. Four forecasts make Evidently flag normal races.
- Using a test on a huge window without a practical threshold. The test calls tiny differences significant.[^breck-2019]
- Thinking that no drift means no problem. In 2026 the inputs barely moved, and the model got much worse. Watch [performance](/knowledge/mlops/performance-monitoring.md) too.

[^evidently-drift]: Evidently AI, "What is data drift in ML, and how to detect and handle it", sections on data drift, concept drift, training-serving skew and drift detection.
[^evidently-methods]: Evidently documentation, "Data drift" explainer, default drift detection methods for small data (1000 observations or fewer).
[^breck-2019]: E. Breck et al., "Data validation for machine learning", MLSys 2019, section 4, "Quantifying Distribution Distance".
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Appendix B (drift) and Table 3 (MEASURE 2.4, MEASURE 2.5).
[^iso-42001-a6]: ISMS.online, "ISO 42001 Annex A control A.6: AI system life cycle", control A.6.2.6 "AI system operation and monitoring" (secondary source for ISO/IEC 42001:2023).
[^lab06]: Lesson 06 README, steps 5, 6, 8 and 9, branch `06-monitoring`.
[^lab06-key]: Lesson 06 `solution/ANSWER_KEY.md`, cases `normal_weekend` and `stuck_feature`.
[^run-alert]: GitHub Actions run 43896456941 (`workflow_dispatch`, scenario `wet_race`), step "4. Run the monitor".
