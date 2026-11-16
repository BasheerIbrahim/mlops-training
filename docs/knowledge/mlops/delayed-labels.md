---
type: Domain Concept
title: Delayed labels
description: The true outcome of an event arrives, or changes, some time after it, so early labels can be wrong and model quality is measured late.
tags: [mlops, data-engineering, labels, ground-truth, monitoring]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "ISO-42001:A.7.5", "ISO-42001:A.6.2.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:45:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: evidently-monitoring
    resource: https://www.evidentlyai.com/ml-in-production/model-monitoring
    title: "Model monitoring for ML in production: a comprehensive guide"
    author: Evidently AI
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
  - id: iso-42001-a6
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-6-ai-system-life-cycle/
    title: "ISO 42001 Annex A control A.6: AI system life cycle"
    author: ISMS.online
---

# Definition

A label is delayed when the true outcome of an event is known only some time after the event. Sometimes a first label arrives quickly and a corrected label arrives later. Until the final label arrives, you cannot measure the model's real quality, and an early label can be wrong.

In production it is typical for feedback on model performance to arrive with a delay, so you cannot measure true quality in real time.[^evidently-monitoring] Google's crash course notes that testing quality in serving is hard because real-world data is not always labeled.[^google-monitoring]

# Why it matters

Delayed labels cause two problems.

1. **Wrong labels in training.** If you train before the final labels arrive, the model learns from provisional labels. You must record which version you used. See [Data versioning](/knowledge/mlops/data-versioning.md).
2. **Late quality measurement.** You learn that the model got worse only when the labels arrive. Evidently recommends two loops: a real-time loop that watches inputs and outputs as proxies, and a delayed loop that runs when the labels are available.[^evidently-monitoring] Data and prediction drift are the usual proxies while you wait.[^evidently-monitoring]

The NIST AI RMF asks teams to monitor the system's behaviour in production (MEASURE 2.4).[^nist-ai-rmf] ISO/IEC 42001 has controls for AI system operation and monitoring (A.6.2.6) and for data provenance (A.7.5).[^iso-42001-a6] [^iso-42001-a7] With delayed labels, both need a plan for when the labels arrive and which label version counts.

Think of a football match where the referee checks the video after the final whistle and changes the result. The score you saw at the end of the match was not the final score.

# Examples

- The 2026 F1 results come out twice. The provisional results come right after each race. The final results come after the stewards' penalties, 2 to 26 hours later.[^lab-01] The data README calls the final classification "the correct delayed labels".[^f1-data]
- `stewards_2026.csv` holds 7 post-race penalties.[^f1-data] Applying them changes 23 finish positions and 6 labels (`points_finish`) in the 160 rows of the first 8 races.[^lab-01]
- You train on Monday morning and the stewards publish a penalty on Monday afternoon. Your model used the provisional labels. The DVC version in the training record lets you prove this three months later.[^lab-01]
- To evaluate a model, use the final labels. The 6 changed labels are exactly the cases where the provisional result was wrong. Lab 03 evaluates models with [classification metrics](/knowledge/mlops/classification-metrics.md) on labelled holdout data.

# Common mistakes

- Treating the first label as the truth. In the F1 data, 6 of 160 provisional labels are wrong.
- Overwriting provisional labels with final labels in place, with no version. You can no longer tell which labels a model learned from.
- Waiting for labels before you monitor anything. Watch input drift and prediction drift while the labels are on their way.[^evidently-monitoring]
- Measuring a model on a window whose labels are not final yet. The score changes when the corrections arrive.
- Using a late correction as an input feature. A penalty that is known only after the race is [data leakage](/knowledge/mlops/data-leakage.md) for a model that predicts before the race.

[^evidently-monitoring]: Evidently AI, "Model monitoring for ML in production: a comprehensive guide", https://www.evidentlyai.com/ml-in-production/model-monitoring
[^google-monitoring]: Google, Machine Learning Crash Course, "Production ML systems: Monitoring pipelines", https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
[^f1-data]: mlops-training, `f1/data/README.md`, files table
[^lab-01]: mlops-training, "Lesson 01: data engineering", part 2 and the discussion questions, branch `01-data-engineering`
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE function), https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
[^iso-42001-a7]: ISMS.online, "ISO 42001 Annex A control A.7: Data for AI systems" (control list for ISO/IEC 42001:2023)
[^iso-42001-a6]: ISMS.online, "ISO 42001 Annex A control A.6: AI system life cycle" (control list for ISO/IEC 42001:2023)
