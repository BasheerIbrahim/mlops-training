---
type: Domain Concept
title: Training-serving skew
description: The API receives a different value than the training pipeline computes for the same example, so the model answers with wrong inputs.
tags: [mlops, monitoring, skew, data-quality, serving]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.3", "NIST-AI-RMF:MEASURE 2.4", "ISO-42001:A.6.2.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:30:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: google-monitoring
    resource: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    title: "Machine Learning Crash Course: Production ML systems, monitoring pipelines"
    author: org:google
  - id: rules-of-ml
    resource: https://developers.google.com/machine-learning/guides/rules-of-ml
    title: "Rules of Machine Learning: Best practices for ML engineering"
    author: org:google
  - id: breck-2019
    resource: https://mlsys.org/Conferences/2019/doc/2019/167.pdf
    title: Data validation for machine learning (MLSys 2019)
    author: Eric Breck, Neoklis Polyzotis, Sudip Roy, Steven Euijong Whang, Martin Zinkevich
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google
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

Training-serving skew is a difference between the data the model gets in serving and the data the training pipeline produces. Google's crash course says that training-serving skew means your input data during training differs from your input data in serving. It names schema skew (the two do not follow the same schema) and feature skew (engineered data differs between training and serving).[^google-monitoring]

The TFX data validation paper names three kinds.[^breck-2019]

| Kind | What happens |
|---|---|
| Feature skew | One feature of one example has a different value in training than at serving time |
| Distribution skew | The distribution of a feature in a training batch differs from the one at serving time |
| Scoring/serving skew | Only some of the scored examples are served, so the training data has labels only for those |

The paper says that the most common cause is different code paths for training data and serving data.[^breck-2019] The lab's skew check is a feature-skew check: it compares each served value with the value that the training pipeline recomputes for the same entry.

Skew is not [data drift](/knowledge/mlops/data-drift.md). With drift the data is correct and the world changed. With skew the data is wrong.

# Why it matters

Skew is a bug, and often a silent one. The model still answers, with full confidence, from wrong inputs. A drift check can miss it, because a wrong value can still look normal.

To detect feature skew, the TFX Data Validator joins training and serving data by key and compares them feature by feature. It sends any skew to the platform's alerting system.[^breck-2019] Rules of ML recommend logging the features at serving time (Rule #29) and reusing code between the training and serving pipelines (Rule #32).[^rules-of-ml] Google's MLOps guide recommends a feature store as the data source for both, to avoid skew.[^google-mlops]

The NIST AI RMF asks that performance is demonstrated for conditions similar to deployment (MEASURE 2.3) and that the system is monitored in production (MEASURE 2.4).[^nist-ai-rmf] Skew means that production conditions are not the ones you tested. ISO/IEC 42001 control A.6.2.6 covers operation and monitoring with production data.[^iso-42001-a6]

The timing sheet says the qualifying gap is 825 milliseconds. A new timing feed sends it in seconds, so the predictor reads 0.825 and thinks the car was almost on pole. The predictor did what the feed said, and the call is still wrong.

# Examples

- **A new timing feed sends seconds.** The `serving_skew` window sends `quali_gap_ms` as 0.825 instead of 825. The [input contract](/knowledge/mlops/input-contract.md) wants an integer, so the API rejects all 80 entries with status 422. The skew check says `quali_gap_ms: 76 of 80 served values differ from the recomputed ones; served / recomputed: median x0.001 (95%, max 5%)`.[^lab06]
- Two checks give two views of one incident. Service health says that the API fails. The skew check says why: values a thousand times too small. The 4 values that match are the pole-sitters, whose gap is 0 in any unit.[^lab06]
- **The same bug, silent.** In the Drift Detective case `units_change` the feed sends whole seconds, such as 1 instead of 825. Every value is a valid integer, so the API answers. The skew check says `76 of 80 values differ, median x0.000939`.[^lab06-key]
- **A renamed category.** The circuit database renames `high_speed` to `high-speed`. The API rejects 20 of 80 entries, and the skew check says `served 'high-speed' where recomputed is 'high_speed' (20 entries)`.[^lab06-key]
- **Blind spots of the drift check.** `quali_gap_ms` multiplied by 0.62 moves the mean only 0.60 sd, with spread x0.62, so input drift passes. The skew check finds 76 of 80 values that differ, median x0.62.[^lab06-key]
- The lab thresholds: a served value may differ from the recomputed one by 1 % (rounding). The check alerts when more than 5 % of the values of one feature differ. One wrong car in a race of 20 is 5 %.[^lab06]

# Common mistakes

- Relying on the API contract alone. It caught 0.825 by luck, because 0.825 is not an integer. Whole seconds pass.
- Relying on drift checks alone. A unit factor such as x0.62 stays inside the normal spread.
- Forgetting that the skew check needs recomputed features for the same requests. In production that is a batch job that runs hours later. For those hours, nothing catches the fault.[^lab06-key]
- Writing the feature code twice, once for training and once for serving. Reuse the code, or use one feature store.[^rules-of-ml] [^google-mlops]
- Comparing only averages of served and training data. Compare value by value, joined by a key, to find the culprit.

[^google-monitoring]: Google, Machine Learning Crash Course, "Production ML systems: Monitoring pipelines", section "Check for training-serving skew".
[^rules-of-ml]: Google, "Rules of Machine Learning", Rule #29 and Rule #32.
[^breck-2019]: E. Breck et al., "Data validation for machine learning", MLSys 2019, section 4, "Training-Serving Skew".
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section on the feature store.
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE 2.3, MEASURE 2.4).
[^iso-42001-a6]: ISMS.online, "ISO 42001 Annex A control A.6: AI system life cycle", control A.6.2.6 "AI system operation and monitoring" (secondary source for ISO/IEC 42001:2023).
[^lab06]: Lesson 06 README, steps 7 and 9, branch `06-monitoring`.
[^lab06-key]: Lesson 06 `solution/ANSWER_KEY.md`, cases `units_change` and `category_renamed`, and "Break the monitor (blind spots, measured)".
