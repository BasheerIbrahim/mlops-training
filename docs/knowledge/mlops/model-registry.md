---
type: Domain Concept
title: MLflow Model Registry
description: A central store that keeps chosen models under a name with numbered versions, a link to the run that made each one, aliases and tags.
tags: [mlflow, model-registry, model-versioning, lineage]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:GOVERN 1.6", "NIST-AI-RMF:MANAGE 4.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T11:10:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: mlflow-registry
    resource: https://mlflow.org/docs/latest/ml/model-registry/
    title: MLflow Model Registry
    author: team:mlflow
  - id: mlflow-sklearn
    resource: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html
    title: mlflow.sklearn (MLflow 3.18.0 Python API)
    author: team:mlflow
  - id: nist-ai-rmf
    resource: https://doi.org/10.6028/NIST.AI.100-1
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: team:nist
---

# Definition

The MLflow Model Registry is a centralised model store, a set of APIs and a UI. It records lineage (which experiment and run produced the model), versions, aliases, tags and annotations.[^mlflow-registry]

- A **registered model** has a unique name and holds versions, aliases, tags and other metadata.[^mlflow-registry]
- A **model version** is one model under that name. The first registration is version 1. Each new model under the same name increments the version number.[^mlflow-registry]
- A **model alias** is a mutable name that points to one version, for example `champion`. Code loads it with `models:/<name>@<alias>`.[^mlflow-registry]
- **Tags** are key-value pairs on a registered model or a version, for example `validation_status:approved`.[^mlflow-registry]

You register a model from a run in the UI (**Register model**, then **Create New Model**) or in code with `mlflow.register_model(model_uri=..., name=...)`. You load a version with `models:/<name>/<version>`.[^mlflow-registry]

# Why it matters

Experiment tracking keeps every try, good or bad. The registry keeps only the models that you choose to use. It answers three questions for the team: which models exist, which version is which, and which run (data, code, parameters) produced it. NIST asks for mechanisms to inventory AI systems.[^nist-ai-rmf] NIST also asks for post-deployment plans that include recovery and change management.[^nist-ai-rmf] Numbered versions and aliases make it possible to promote and roll back a model (lab 04).

Kid version: MLflow tracking is the race engineer's logbook, where every try is written down. The Model Registry is the team's homologation register: only the best honest predictor goes in, with a number (the version), so every garage runs the same one.

# Examples

- In lab 03 you register the run `forest-n300-d8-l5` as `f1-points-finish`, version 1. The **Models** page in the MLflow UI shows it.
- You load it with `mlflow.pyfunc.load_model("models:/f1-points-finish/1")` and test it on 2025. The script prints `accuracy: 0.842`, the same score as the run.
- MLflow may print that it registers the logged model `models:/m-...` instead of the run path. That is the same model.
- You do not register the leakage run. It has the best score (1.000) and is useless.
- MLflow 3.18 saves scikit-learn models in the skops format by default (outside Databricks). Skops gives safe deserialisation; pickle-based formats can run arbitrary code when you load them.[^mlflow-sklearn] A forest contains `sklearn.tree._tree.Tree` objects, so `train.py` passes `skops_trusted_types=["sklearn.tree._tree.Tree"]` to `mlflow.sklearn.log_model`.[^mlflow-sklearn] Without it, the logging fails with an "untrusted types" error.

# Common mistakes

- Registering every run. The registry is for chosen models; the experiment keeps the rest.
- Choosing by the top score only. Sort by accuracy and the leakage run is first. Filter with `tags.leakage = "false"` before you choose.
- Loading "the latest" in production. Load a fixed version or an alias, so a new registration does not change production by surprise. See [Model alias promotion](/knowledge/mlops/model-alias-promotion.md).
- Losing the link to the run. Register from the run so that the version keeps its lineage to the data version, parameters and metrics.
- Trusting any type to skip the skops error. List only the types that you trained yourself.

[^mlflow-registry]: MLflow documentation, "MLflow Model Registry" (concepts, UI workflow and API workflow).
[^mlflow-sklearn]: MLflow 3.18.0 Python API, `mlflow.sklearn.log_model` (parameters `serialization_format` and `skops_trusted_types`).
[^nist-ai-rmf]: NIST AI 100-1, GOVERN 1.6 (mechanisms to inventory AI systems) and MANAGE 4.1 (post-deployment monitoring plans, including recovery and change management).
