---
type: Domain Concept
title: Release criteria
description: The written rules that every new model must meet before it may be used, fixed before anyone looks at the candidate.
tags: [mlops, release, governance, requirements]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 1.5", "NIST-AI-RMF:MEASURE 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:10:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab04
    resource: https://github.com/majlisofai/mlops-training/blob/04-quality-gates/exercises/quality-gates/README.md
    title: "Lesson 04: quality gates and controlled promotion"
    author: org:majlisofai
---

# Definition

Release criteria are the written rules that a new model must meet before a team may use it. Each rule has a measure, a threshold and a reason. The team writes the rules down before it looks at the candidate model, so that nobody bends a rule to fit a model they like.

In the lab, the release criteria are in one file, `criteria.yaml`. The quality gates read their thresholds from this file.[^lab04]

# Why it matters

Google's MLOps guide says that a team must validate a new model before it serves predictions. The team produces metrics on a test dataset, compares them to the current model, and checks that the model performs well on different segments of the data.[^google-mlops] Release criteria turn these checks into numbers that a machine can test.

The NIST AI RMF asks an organization to determine and document its risk tolerances (MAP 1.5). It also asks that performance criteria are measured and documented for conditions similar to the deployment setting (MEASURE 2.3).[^nist-ai-rmf] A criteria file in version control is such a record.

Think of the technical regulations in a Grand Prix. The officials write them before the season, before any car is tested. If they wrote them after they saw the cars, they could bend them to fit a favourite team. The strategy team writes its release criteria the same way: before it tests any predictor.

# Examples

The release criteria for `f1-points-finish` are measured on the 2025 holdout season (480 entries):

| Rule | Threshold | Why this number |
|---|---:|---|
| Data passes validation | 0 failure cases | A model trained on broken data is broken. |
| Accuracy | ≥ 0.82 | Above the grid rule (0.804), below every honest tuned model (0.833 to 0.842). |
| Margin over the grid rule | ≥ 0.02 | A model must earn its cost: about 10 more right answers out of 480 than a simple rule. |
| ROC AUC | ≥ 0.88 | The model must rank the cars well, not only cut at 0.5. |
| Rookie accuracy | ≥ 0.60 | Every model is worse for the 48 rookie entries. 0.60 is 29 of 48. |
| Forbidden features | none | Columns such as `finish_position` are known only after the race. |

The margin rule refers to the [baseline model](/knowledge/mlops/baseline-model.md). The rookie rule comes from [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md). The forbidden-features rule blocks [data leakage](/knowledge/mlops/data-leakage.md). The data rule uses [data validation](/knowledge/mlops/data-validation.md). A [quality gate](/knowledge/mlops/quality-gate.md) checks each rule.

# Common mistakes

- Choosing the thresholds after you see the candidate's results. Then the rules prove nothing.
- Writing only an overall metric. In the lab, the stumps model has accuracy 0.829 and passes every overall rule, but its rookie accuracy is 0.583.
- Writing a threshold without a reason. A reviewer cannot judge a number that has no reason.
- Letting the same person change the candidate and the criteria in one commit without a review. They can lower `min_accuracy` to make their own model pass.

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section on model validation.
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 1.5) and Table 3 (MEASURE 2.3).
[^lab04]: Lesson 04 README, section "The release requirements".
