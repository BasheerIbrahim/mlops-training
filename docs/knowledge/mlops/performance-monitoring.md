---
type: Domain Concept
title: Performance monitoring
description: Measuring a model's quality in production by joining its predictions with the true labels when they arrive, and checking that enough final labels arrived.
tags: [mlops, monitoring, labels, accuracy, ground-truth]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MEASURE 3.1", "NIST-AI-RMF:MEASURE 4.3", "ISO-42001:A.6.2.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:50:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: google-monitoring
    resource: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    title: "Machine Learning Crash Course: Production ML systems, monitoring pipelines"
    author: org:google
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google
  - id: evidently-monitoring
    resource: https://www.evidentlyai.com/ml-in-production/model-monitoring
    title: "Model monitoring for ML in production: a comprehensive guide"
    author: org:evidently-ai
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
---

# Definition

Performance monitoring measures how good the model is in production. It joins each logged prediction with the true label when the label arrives, computes a quality metric such as accuracy, and compares it with a baseline. Because labels come late, it also measures **label coverage**: the share of predictions that already have a final label.

Google's crash course says that testing quality in serving is hard, because real-world data is not always labeled. It asks you to watch for both sudden and slow degradation.[^google-monitoring] Evidently notes that feedback on model performance typically arrives with a delay, so you cannot measure true quality in real time. It recommends a real-time loop with proxies, such as data and prediction drift, and a delayed loop that runs when the labels arrive.[^evidently-monitoring]

# Why it matters

Some problems show only in the labels. When the relation between the inputs and the result changes, the inputs can look normal while the model is wrong more often. That is [concept drift](/knowledge/mlops/concept-drift.md), and no input check can see it.

Google's MLOps guide says that monitoring detects performance degradation and model staleness, and that noticeable degradation is one trigger to retrain.[^google-mlops] The NIST AI RMF asks that the system is monitored in production (MEASURE 2.4), that risks are tracked from actual performance in deployed contexts (MEASURE 3.1), and that performance improvements or declines are identified and documented from field data (MEASURE 4.3).[^nist-ai-rmf] ISO/IEC 42001 control A.6.2.6 asks for monitoring that the system performs within expected parameters on production data.[^iso-42001-a6]

Label coverage protects the verdict. A score on a few labels, or on provisional labels, can change when the rest arrive. See [delayed labels](/knowledge/mlops/delayed-labels.md).

The restaurant learns how good the food was only when the reviews come in, days later. The owner waits until most reviews are in before deciding that the new menu failed.

# Examples

- The lab baseline is the champion's accuracy on the 2025 holdout, 0.842. The monitor alerts when accuracy on the final labels falls more than 0.05 below it, so below 0.792. It also alerts when fewer than 90 % of the predictions have a final label.[^lab06]
- **2026 with the final labels.** The monitor says `accuracy 0.706 on the final labels, baseline 0.842 (alert below 0.792)`, for 160 predictions with 160 final labels.[^lab06]
- Before the labels arrived, the same window gave `MONITOR OK`. The largest input move was `team_dnf_rate`, 1.03 sd. The cause is in the sport: 27.5 % of the cars do not finish (10.9 % before), and a backmarker team leads.[^lab06]
- **Provisional against final.** Accuracy is 0.706 on both, but the stewards changed 6 labels: 3 predictions went from right to wrong, 3 from wrong to right. With other penalties, the provisional number could be too high or too low.[^lab06]
- **Provisional labels only.** The monitor says `labels late: 0 of 160 predictions have a final label (0%, need 90%)`. It still shows the provisional accuracy, 0.706, but gives no final verdict.[^lab06]
- **A stalled label feed.** In the Drift Detective case `label_delay` the stewards' feed stopped after race 3. The monitor says `60 of 160 predictions have a final label (38%, need 90%)` and `accuracy 0.733 on the final labels`, measured on only three races.[^lab06-key]
- **Why 0.05.** With 160 predictions, accuracy moves by about ±0.03 by chance alone (one standard error). 0.05 is beyond that, and 0.792 is below the [grid baseline](/knowledge/mlops/baseline-model.md) of 0.804 on 2025.[^lab06]
- **Prediction drift as a proxy.** The share of cars predicted in the points was 0.61 in 2026, inside 0.5 ± 0.15. It did not alert in any window of the lab: a cheap early warning, not a replacement for labels.[^lab06]

# Common mistakes

- Reporting accuracy on provisional labels as the final number. Report on final labels, and say which labels you used.
- Judging the model on too few labels. Three races of 2026 gave 0.733; eight gave 0.706.
- Comparing with the wrong baseline. Use the [holdout](/knowledge/mlops/temporal-holdout-split.md) score of the released model, not its training score.
- Waiting for labels and watching nothing in the meantime. Watch [data drift](/knowledge/mlops/data-drift.md) and prediction drift as proxies.[^evidently-monitoring]
- Thinking that quiet input checks mean a healthy model. In 2026 every input check passed.
- Watching one overall number only. A model can hold its accuracy overall and fail a group, as [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md) shows.

[^google-monitoring]: Google, Machine Learning Crash Course, "Production ML systems: Monitoring pipelines", section "Test the quality of live model on served data".
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", sections on model monitoring and pipeline triggers.
[^evidently-monitoring]: Evidently AI, "Model monitoring for ML in production: a comprehensive guide", sections on ground truth delay and proxy metrics.
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE 2.4, MEASURE 3.1, MEASURE 4.3).
[^iso-42001-a6]: ISMS.online, "ISO 42001 Annex A control A.6: AI system life cycle", control A.6.2.6 "AI system operation and monitoring" (secondary source for ISO/IEC 42001:2023).
[^lab06]: Lesson 06 README, steps 8 and 9, branch `06-monitoring`.
[^lab06-key]: Lesson 06 `solution/ANSWER_KEY.md`, case `label_delay`.
