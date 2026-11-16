---
type: Domain Concept
title: Quality gate
description: An automated pass-or-fail check of one release criterion that stops a model from moving forward when the check fails.
tags: [mlops, testing, release, pytest]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 1.1", "NIST-AI-RMF:MEASURE 2.3", "NIST-AI-RMF:MEASURE 2.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:15:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: pytest-skipping
    resource: https://docs.pytest.org/en/stable/how-to/skipping.html
    title: How to use skip and xfail to deal with tests that cannot succeed
    author: team:pytest
  - id: pytest-output
    resource: https://docs.pytest.org/en/stable/how-to/output.html
    title: Managing pytest's output
    author: team:pytest
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

A quality gate is an automated check of one [release criterion](/knowledge/mlops/release-criteria.md). It passes or it fails. When a gate fails, the pipeline stops and the model does not move forward.

In the lab, each gate is one pytest test in `test_gates.py`. The gates load the model `models:/f1-points-finish@candidate` from the [model registry](/knowledge/mlops/model-registry.md) and measure it again on the 2025 holdout. They do not trust the metrics that the training script logged.[^lab04]

Each gate records what it measured with the pytest fixture `record_property`, which adds a property to the test report.[^pytest-output] A small hook writes the results to a gate report, `gate_report.json`, that the promotion step reads.

# Why it matters

Google's MLOps guide says that continuous integration in ML is not only about testing code. It is also about testing and validating data and models.[^google-mlops] A quality gate is that test for a model.

The NIST AI RMF asks for a determination of whether an AI system achieves its stated objectives and whether its deployment should proceed (MANAGE 1.1).[^nist-ai-rmf] A gate makes this decision the same way every time, and its report documents the metrics and the test set (MEASURE 2.1).

A quality gate is a gatekeeper with a checklist at the kitchen door. Each dish must tick every box on the list, or it does not go to the judges.

# Examples

The lab has seven gates: `data_passes_validation`, `model_predicts_0_or_1`, `accuracy`, `roc_auc`, `beats_grid_rule`, `no_forbidden_features` and `rookie_accuracy`. Trainees write the last three.

| Candidate | Blocked by | Measured |
|---|---|---|
| Leaky forest (uses `finish_position`) | `no_forbidden_features` | accuracy 1.000, but uses an after-race column |
| Weak forest (5 unlimited trees) | `accuracy`, `roc_auc`, `beats_grid_rule` | accuracy 0.806, ROC AUC 0.876, margin 0.002 |
| Stumps (10 one-split trees) | `rookie_accuracy` | rookie accuracy 0.583 (accuracy 0.829, ROC AUC 0.886) |
| Best honest forest | none | accuracy 0.842, ROC AUC 0.907, margin 0.038, rookie accuracy 0.646 |

Before trainees write `no_forbidden_features`, the leaky model scores 1.000, passes the four written gates, and becomes `@champion`. A gate that is not written checks nothing. The leaky case is [data leakage](/knowledge/mlops/data-leakage.md). The rookie gate is [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md) as a test. The metrics are [classification metrics](/knowledge/mlops/classification-metrics.md).

# Common mistakes

- Treating a skipped test as a pass. pytest skips a test when a condition is not met.[^pytest-skipping] A skipped gate checks nothing. In the lab, `promote.py` lets a skipped gate through with a warning, and the leaky model gets through.
- Trusting the metrics that the training step logged. Measure the registered model again, on data it never saw.
- Checking only overall metrics. The stumps model passes every overall gate and fails only for rookies.
- Thinking that gates undo a bad release. Gates stop new bad models. To remove a bad model that already got through, use a [rollback](/knowledge/mlops/model-rollback.md).
- Writing a failure message without numbers. "accuracy 0.806 is below 0.82" tells a reviewer what to fix.

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "CI/CD pipeline automation".
[^pytest-skipping]: pytest documentation, "How to use skip and xfail".
[^pytest-output]: pytest documentation, "Managing pytest's output", section on `record_property`.
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1, MEASURE 2.3) and Table 4 (MANAGE 1.1).
[^lab04]: Lesson 04 README, steps 3 and 4.
