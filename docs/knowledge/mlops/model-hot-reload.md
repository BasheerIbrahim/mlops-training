---
type: Domain Concept
title: Model hot reload
description: Switching a running service to the model version behind a moved alias, loading the new model first and keeping the old one if loading fails.
tags: [mlops, serving, release, rollback, mlflow, alias]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 2.4", "NIST-AI-RMF:MEASURE 2.6", "NIST-AI-RMF:MANAGE 4.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:40:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: mlflow-workflow
    resource: https://mlflow.org/docs/latest/ml/model-registry/workflow/
    title: MLflow Model Registry workflows
    author: team:mlflow
  - id: fowler-bluegreen
    resource: https://martinfowler.com/bliki/BlueGreenDeployment.html
    title: BlueGreenDeployment
    author: Martin Fowler
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab05
    resource: https://github.com/majlisofai/mlops-training/blob/05-serve-model/exercises/serve-model/README.md
    title: "Lesson 05: serve the model and roll back a faulty release"
    author: org:majlisofai
---

# Definition

A model hot reload switches a running [model serving API](/knowledge/mlops/model-serving-api.md) to a new model version without a restart. The service loads the new model first. Only when the load succeeds does it switch. While it loads, and if the load fails, the old model keeps answering.

A reload is needed because the service reads the alias only when it loads the model. An MLflow model URI with an alias resolves to a version at load time, and you can reassign the alias without changing production code.[^mlflow-workflow] So when [alias promotion](/knowledge/mlops/model-alias-promotion.md) or a [rollback](/knowledge/mlops/model-rollback.md) moves `@champion`, the running service keeps the version it loaded until it reloads or restarts.[^lab05]

# Why it matters

A promotion or a rollback changes the registry. It does not change what users get until the service picks up the new version. Teams must know when that happens, and they must not lose the service while it happens.

Martin Fowler describes the same idea for whole environments: prepare and test the new environment, then switch the router to it, and switch back for a rapid rollback.[^fowler-bluegreen] A hot reload does this inside one process: the new model is ready before it gets any request.

The NIST AI RMF asks for mechanisms to supersede, disengage or deactivate AI systems whose performance is inconsistent with intended use (MANAGE 2.4), for systems that can fail safely (MEASURE 2.6), and for recovery and change management in post-deployment plans (MANAGE 4.1).[^nist-ai-rmf] The reload puts a rollback into effect in seconds. A failed reload leaves the old model serving.

A hot reload swaps the chef without closing the restaurant. The new chef puts on the apron and gets ready while the old chef keeps cooking. If the new chef does not show up, the old chef just keeps cooking.

# Examples

In the lab, `POST /admin/reload` calls `load_model` for `models:/f1-points-finish@champion`. On success, it replaces the served model in one assignment and answers with the previous and the new version. On failure, it answers status 500 with `reload failed, still serving version ...`. Each `/v1/predict` call reads the served model once, so one version answers the whole batch, even during a reload.[^lab05]

The faulty release in step 8:[^lab05]

1. The huge forest passes all seven gates (accuracy 0.840) and becomes version 2, `@champion`.
2. `/health` still says `"model_version":"1"`. The alias moved; the service did not.
3. `POST /admin/reload` answers `"previous_version":"1","model_version":"2"`. It takes about two seconds: the model file is 121 MB, against 11 MB for version 1.
4. The load test breaks the [SLO](/knowledge/mlops/service-level-objective.md): p95 1800 ms, 129 requests.
5. `promote.py --rollback` moves `@champion` back to version 1. A second reload answers `"previous_version":"2","model_version":"1"`.
6. The load test meets the SLO again: p95 71 ms, 247 requests.

The README compares three ways to pick up a new champion: reload on command, reload automatically every minute, or restart the container. Version 2 also needs 5.5 s from start to `/health`, against 2.5 s for version 1, so a restart means a longer gap.

A canary goes one step further: Google's MLOps guide says that a newly deployed model can be validated online in a canary deployment or an A/B test before it serves online traffic.[^google-mlops] The lab stretch runs version 2 in a second container on port 8001 and load-tests it before any switch.

# Common mistakes

- Thinking that moving the alias changes the service. It changes only the next load.
- Unloading the old model before the new one is ready. Requests then fail, or the service has no model at all after a failed load.
- Reloading automatically on a timer with no check. A bad champion then reaches users on the next tick.
- Leaving the reload endpoint open to anyone. In the lab, anyone who can reach the API can call `/admin/reload`. A real service limits who can.
- Rolling back the alias and forgetting to reload. The registry says version 1, and users still get version 2.

[^mlflow-workflow]: MLflow documentation, "Model Registry workflows", section on aliases.
[^fowler-bluegreen]: Martin Fowler, "BlueGreenDeployment", bliki.
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "MLOps level 1", subsection "Data and model validation".
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.6) and Table 4 (MANAGE 2.4, MANAGE 4.1).
[^lab05]: Lesson 05 README, sections "The serving architecture", step 8, "Discuss" and "Stretch"; `app.py`.
