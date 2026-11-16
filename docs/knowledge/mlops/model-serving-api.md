---
type: Domain Concept
title: Model serving API
description: An HTTP service that answers prediction requests online with a model it loaded once at start-up, and names the model version in every answer.
tags: [mlops, serving, fastapi, online-inference, api]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MEASURE 2.8"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:10:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: fastapi-events
    resource: https://fastapi.tiangolo.com/advanced/events/
    title: Lifespan Events
    author: team:fastapi
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
  - id: lab05
    resource: https://github.com/majlisofai/mlops-training/blob/05-serve-model/exercises/serve-model/README.md
    title: "Lesson 05: serve the model and roll back a faulty release"
    author: org:majlisofai
---

# Definition

A model serving API is an HTTP service that gives predictions on request, while the client waits. This is online inference. Google's MLOps guide lists a microservice with a REST API as one way to serve online predictions.[^google-mlops]

The service loads the model once, when it starts, and keeps it in memory. Each request then uses the model that is already loaded. FastAPI runs code in a *lifespan* handler once, before the application starts to receive requests. Its documentation uses an ML model as the example: loading takes time, and the same model is shared by all requests.[^fastapi-events]

In the lab, `app.py` is a FastAPI service with three endpoints:[^lab05]

| Endpoint | What it does |
|---|---|
| `GET /health` | Says that the API is up, and which model name, version and alias it serves |
| `POST /v1/predict` | Takes 1 to 1000 entries and returns one prediction and one probability per entry, and the model version |
| `POST /admin/reload` | Loads the model behind `@champion` again (see [model hot reload](/knowledge/mlops/model-hot-reload.md)) |

The `/v1/` in the URL is the version of the [input contract](/knowledge/mlops/input-contract.md), not of the model. Model versions 1, 2 and 3 can all answer `/v1/predict`. A model that needs other inputs needs a new contract, `/v2/`.[^lab05]

# Why it matters

A model in the [model registry](/knowledge/mlops/model-registry.md) is only a file. Nobody can use it until a service answers with it.

The service loads `models:/f1-points-finish@champion`. An MLflow alias is a mutable, named reference to one model version. You can move the alias to another version, and production code does not change.[^mlflow-registry] The alias is resolved when the model loads.[^mlflow-workflow] So [alias promotion](/knowledge/mlops/model-alias-promotion.md) decides which version the service loads next.

Every answer names the model version. When a prediction looks wrong, you can find the exact model that made it. `/health` lets you watch which version is in production. The NIST AI RMF asks that the functionality and behavior of an AI system are monitored when in production (MEASURE 2.4), and that transparency and accountability risks are examined (MEASURE 2.8).[^nist-ai-rmf]

The serving API is the restaurant counter. The kitchen cooks the champion dish, and each plate comes with a ticket that says which recipe version made it.

# Examples

- Start the API with `uvicorn app:app --app-dir exercises/serve-model --port 8000`. The log says `Serving f1-points-finish version 1 (models:/f1-points-finish@champion)`.[^lab05]
- `curl -s http://127.0.0.1:8000/health` answers `{"status":"ok","model_name":"f1-points-finish","model_version":"1","alias":"champion",...}`.
- The two-car request (pole-sitter and last car of the first 2025 race) answers `"model_version":"1","predictions":[1,0]`, with probabilities 0.96 and 0.01.
- `load_model` first finds the version behind the alias, then loads exactly that version. So the version in the answer is the version that really answers, even if someone moves the alias during the load.
- If the model cannot be loaded, the API does not start. It never answers without a model.

# Common mistakes

- Loading the model inside the request handler. Loading takes seconds; a prediction takes milliseconds.
- Answering without the model version. Then nobody can tell which model made a bad prediction.
- Thinking that the running service follows the alias. In the lab, `promote.py` moved `@champion` to version 2, and `/health` still said version 1 until `/admin/reload`.
- Putting the model version in the URL. Clients then change their code for each new model. Version the contract instead.
- Building the model into the image. The lab image holds the code only, so the registry stays the one place that says which model is in production.

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "Data science steps for ML", step "Model serving".
[^fastapi-events]: FastAPI documentation, "Lifespan Events", sections "Use Case" and "Lifespan".
[^mlflow-registry]: MLflow documentation, "MLflow Model Registry", section on model aliases.
[^mlflow-workflow]: MLflow documentation, "Model Registry workflows", section on aliases.
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.4, MEASURE 2.8).
[^lab05]: Lesson 05 README, section "The serving architecture" and steps 3 and 4.
