---
type: Domain Concept
title: Model alias promotion
description: Releasing a model by moving a named registry alias such as @champion to a new model version, without retraining or copying the model.
tags: [mlops, mlflow, model-registry, release, alias]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 1.1", "NIST-AI-RMF:GOVERN 1.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:20:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: mlflow-registry
    resource: https://mlflow.org/docs/latest/ml/model-registry/
    title: MLflow Model Registry
    author: team:mlflow
  - id: mlflow-workflow
    resource: https://mlflow.org/docs/latest/ml/model-registry/workflow/
    title: MLflow Model Registry workflows
    author: team:mlflow
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

A model alias is a mutable, named reference to one version of a registered model.[^mlflow-registry] Programs load the model by the alias, for example `models:/f1-points-finish@champion`, and get the version that the alias points to now.[^mlflow-workflow]

Model alias promotion is a release that moves an alias to a new version. The lab uses two aliases in the [model registry](/knowledge/mlops/model-registry.md):

- `@candidate`: the version that the [quality gates](/knowledge/mlops/quality-gate.md) check.
- `@champion`: the version that is in use.

Promotion moves `@champion` to the candidate version. It does not retrain or copy the model.[^lab04]

# Why it matters

MLflow says that you can update the model that serves production traffic by reassigning the `champion` alias to a different version.[^mlflow-registry] Alias assignments can change independently of the production code.[^mlflow-workflow] So a release is one small, fast step, and the code that loads `@champion` does not change.

MLflow deprecated model stages (such as Staging and Production) in version 2.9.0. Aliases and model version tags replace them.[^mlflow-workflow] Tags annotate a version with its status.[^mlflow-workflow] The lab uses tags as an audit trail: who promoted the version, when, the previous champion and the result of each gate. This supports transparent procedures and controls (NIST AI RMF GOVERN 1.4) and a recorded decision that deployment may proceed (MANAGE 1.1).[^nist-ai-rmf]

In the cook-off, the official recipe book has a "champion" ribbon bookmark. Promotion moves the ribbon to a new recipe page. Nobody rewrites the recipe.

# Examples

- `train_candidate.py` registers a new version of `f1-points-finish` and points `@candidate` at it.
- `promote.py` reads the gate report. It refuses when any gate failed or when the report is for a different version than `@candidate`. Otherwise it calls `set_registered_model_alias(..., "champion", version)`.
- After the first promotion, version 1 (the forest with accuracy 0.842 and ROC AUC 0.907) has `@candidate`, `@champion` and the tags `promoted_by`, `promoted_at`, `previous_champion = none`, `gates = 4 passed, 3 skipped` and one `gate.<name>` tag per gate.
- With the leakage gate still a TODO, the leaky model (accuracy 1.000) becomes version 2 and `@champion`, with `previous_champion = 1`. A [rollback](/knowledge/mlops/model-rollback.md) moves `@champion` back to version 1.

# Common mistakes

- Copying or retraining the model to "promote" it. Then the released model is not the model that the gates checked.
- Promoting from a stale gate report. `promote.py` refuses when the report is for version 3 but `@candidate` is version 4.
- Moving `@champion` with no record. Without the tags, nobody can tell who released the model, or why.
- Using deprecated stages in new code. Use aliases and tags.
- Hard-coding a version number in the serving code. Then each release needs a code change.

[^mlflow-registry]: MLflow documentation, "MLflow Model Registry", section on model aliases.
[^mlflow-workflow]: MLflow documentation, "Model Registry workflows", sections on aliases, tags and the deprecation of stages.
[^nist-ai-rmf]: NIST AI 100-1, Table 1 (GOVERN 1.4) and Table 4 (MANAGE 1.1).
[^lab04]: Lesson 04 README, section "The pipeline" and step 2.
