---
type: Domain Concept
title: Model rollback
description: Putting the previous good model version back into use, quickly and with a record, when a released model turns out to be bad.
tags: [mlops, release, rollback, incident-response]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 2.4", "NIST-AI-RMF:MANAGE 4.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:25:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
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

A model rollback puts the previous good model version back into use. With [alias promotion](/knowledge/mlops/model-alias-promotion.md), a rollback moves the `@champion` alias back to the version it replaced. It does not retrain anything.

In the lab, `promote.py --rollback` reads the tag `previous_champion` on the current champion, moves `@champion` to that version, and tags the removed version with `rolled_back_by` and `rolled_back_at`.[^lab04]

# Why it matters

[Quality gates](/knowledge/mlops/quality-gate.md) stop new bad models. They do not remove a bad model that already got through. A team needs a fast way to undo a release.

The NIST AI RMF asks for mechanisms, with assigned responsibilities, to supersede, disengage or deactivate AI systems whose performance or outcomes do not match the intended use (MANAGE 2.4). It also lists recovery and change management in post-deployment plans (MANAGE 4.1).[^nist-ai-rmf]

MLflow lets you reassign an alias to another version through the UI or the client API.[^mlflow-workflow] So a rollback takes about a second. Every program that loads `models:/f1-points-finish@champion` gets the old version on its next load.

A rollback is going back to last weekend's setup. The `@champion` label went to a predictor that knew the finishing order. You move the label back to the last honest predictor, and you write down who moved it and why.

# Examples

- In the lab, the leaky model (accuracy 1.000, uses `finish_position`) became version 2 and `@champion` before the leakage gate existed. Its tag `previous_champion` is `1`.
- `python exercises/quality-gates/promote.py --rollback --approver "<name>"` prints `ROLLED BACK: f1-points-finish version 1 is @champion again (version 2 removed by <name>).`
- Run it again and it prints `REFUSED: version 1 has no previous champion to go back to.` A rollback needs a recorded previous version.

# Common mistakes

- Rolling back by retraining an old model. The new model is not the version that was checked and approved.
- Not recording the previous champion at promotion time. Then there is nothing to roll back to.
- Rolling back with no record of who did it. Tag the removed version.
- Thinking that a rollback fixes the cause. Also write the missing gate, or the same bad model can come back.
- Keeping the registry only for one CI run. In the lab's CI, the MLflow store lives only for that run, so CI has no previous champion to roll back to.

[^mlflow-workflow]: MLflow documentation, "Model Registry workflows", section on aliases.
[^nist-ai-rmf]: NIST AI 100-1, Table 4 (MANAGE 2.4, MANAGE 4.1).
[^lab04]: Lesson 04 README, step 8.
