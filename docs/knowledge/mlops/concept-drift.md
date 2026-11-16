---
type: Domain Concept
title: Concept drift
description: The link between a model's inputs and the true outcome changes over time, so a model that was right becomes wrong on valid inputs.
tags: [mlops, monitoring, drift, model-decay, retraining]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MEASURE 3.1", "NIST-AI-RMF:MANAGE 2.2"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:50:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: gama-survey
    resource: https://doi.org/10.1145/2523813
    title: "A survey on concept drift adaptation, ACM Computing Surveys 46(4), article 44, 2014 (accepted manuscript read at https://repositorio.inesctec.pt/server/api/core/bitstreams/7f101638-0b33-4863-9dd2-cf991f192c9f/content)"
    author: João Gama, Indrė Žliobaitė, Albert Bifet, Mykola Pechenizkiy and Abdelhamid Bouchachia
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: f1-data
    resource: https://github.com/majlisofai/mlops-training/blob/07-recovery/f1/data/README.md
    title: "Data: the Synthetic Grand Prix Championship"
    author: org:majlisofai
  - id: lab07
    resource: https://github.com/majlisofai/mlops-training/blob/07-recovery/exercises/recovery/README.md
    title: "Lesson 07: recover the service and train a controlled challenger"
    author: org:majlisofai
---

# Definition

Concept drift is a change, over time, in the relation between the input data and the target. Gama and colleagues separate two kinds:[^gama-survey]

- **Real concept drift**: the probability of the outcome given the inputs, p(y|X), changes. The inputs may look the same. The old decision rule is now wrong.
- **Virtual drift**: the distribution of the inputs, p(X), changes, but p(y|X) does not.

This course calls a change in p(X) [data drift](/knowledge/mlops/data-drift.md). You can see data drift in the inputs alone. Real concept drift is often invisible in the inputs. You see it only when the true outcomes arrive and the model's accuracy falls. Methods for real concept drift usually need this feedback on performance.[^gama-survey]

Drift can be sudden, incremental, gradual or recurring. A one-off outlier or noise is not drift, and it needs no change to the model.[^gama-survey]

# Why it matters

A model learns the world as it was in the training data. When the world changes, the model gets worse, even when the code and the inputs are fine. Google's MLOps guide says that models can decay in more ways than conventional software. It lists significant changes in the data distributions (concept drift) as a trigger to retrain, because the model has gone stale.[^google-mlops]

The NIST AI RMF says that AI systems may need more frequent maintenance, and triggers for corrective maintenance, because of data, model or concept drift.[^nist-ai-rmf] It asks that the system is monitored in production (MEASURE 2.4), that emergent risks are tracked against actual performance in deployment (MEASURE 3.1), and that mechanisms sustain the value of deployed systems (MANAGE 2.2).[^nist-ai-rmf]

Because real concept drift shows up in the outcomes, it shows up late. In the lab, a final label arrives 2 to 26 hours after a race.[^lab07] See [delayed labels](/knowledge/mlops/delayed-labels.md) and [performance monitoring](/knowledge/mlops/performance-monitoring.md).

Kid version: the restaurant's best dish won every prize last year. This year the customers' tastes changed. The ingredients are as fresh as ever, but fewer plates come back empty. The recipe did not get worse; the world around it moved.

# Examples

The 2026 season in the lab data starts under new regulations. 27.5 % of entries do not finish, against 10.9 % in 2021-2025, and Cobalt Racing, a backmarker team, leads after eight races.[^f1-data]

| Evidence (lab 07, `triage.py`) | What it shows |
|---|---|
| `160 of 160 entries valid` | The inputs keep the API contract. No client fault. |
| `team_dnf_rate` mean 0.109 in history, 0.207 in 2026 (shift +0.98) | Data drift: one input moved, for a real reason |
| Accuracy 0.842 on the 2025 holdout, 0.706 on the 160 2026 entries with final labels (0.60 to 0.80 per race) | The old rule now makes more mistakes: the relation between inputs and outcome changed |
| No release explains the drop | It is not a bad deployment |

So the evidence points to concept drift. The runbook's row for it reads: all inputs are valid, some moved for a real reason, and accuracy on final labels fell over several races. The action is to retrain a challenger and compare it, not to roll back.[^lab07] See [retraining strategy](/knowledge/mlops/retraining-strategy.md) and [challenger model](/knowledge/mlops/challenger-model.md).

The drift here is sudden: it came with the new regulations. A team that was weak in 2021-2025 is strong in 2026, so a history window that ends in 2025 teaches the model the old pecking order.

# Common mistakes

- Treating data drift and concept drift as the same thing. An input can move while the model stays right, and the model can go wrong while no input moves.
- Watching only the inputs. Real concept drift needs the true outcomes to show up.[^gama-survey]
- Acting on one or two races, or on provisional labels. Tell drift from noise first.[^gama-survey]
- Calling a broken feed "drift". A unit change in one input is a client fault. Fix the input; do not retrain on it.[^lab07]
- Retraining on all history. Old seasons can teach the old relation. Weigh how much history still applies.
- Thinking a rollback fixes drift. The previous model learned the same old world.

[^gama-survey]: Gama et al. (2014), sections 1, 2.1 "Setting and definitions" and 2.2 "Changes in data over time".
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", sections "DevOps versus MLOps" and "ML pipeline triggers".
[^nist-ai-rmf]: NIST AI 100-1, Appendix B (how AI risks differ from traditional software risks), Table 3 (MEASURE 2.4, MEASURE 3.1) and Table 4 (MANAGE 2.2).
[^f1-data]: F1 data README, "Facts you can check".
[^lab07]: Lesson 07 README, steps 2 and 7, and the runbook decision table (part 2).
