---
type: Domain Concept
title: Contract test
description: An automated test that checks what clients of a service rely on, such as URLs, fields, types and errors, not model quality.
tags: [mlops, testing, api, pytest, fastapi]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.1", "NIST-AI-RMF:MEASURE 2.5"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:20:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: fowler-contract
    resource: https://martinfowler.com/bliki/ContractTest.html
    title: ContractTest
    author: Martin Fowler
  - id: fastapi-testing
    resource: https://fastapi.tiangolo.com/tutorial/testing/
    title: Testing
    author: team:fastapi
  - id: fastapi-testing-events
    resource: https://fastapi.tiangolo.com/advanced/testing-events/
    title: "Testing Events: lifespan and startup - shutdown"
    author: team:fastapi
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

A contract test checks what the clients of a service rely on: the URLs, the fields, the types and the errors. Martin Fowler says that contract tests check the contract of a service, not necessarily the exact data: the format must stay the same, even when the data changes.[^fowler-contract]

For a [model serving API](/knowledge/mlops/model-serving-api.md), a contract test does not check how good the model is. The [quality gates](/knowledge/mlops/quality-gate.md) do that. It checks that the API keeps its [input contract](/knowledge/mlops/input-contract.md) and the shape of its answers.[^lab05]

FastAPI's `TestClient` is based on HTTPX, and you use it with pytest directly.[^fastapi-testing] When you use the `TestClient` in a `with` block, it runs the lifespan handler.[^fastapi-testing-events] The lab's `conftest.py` does this, so the tests load the real `@champion` from MLflow, without uvicorn.[^lab05]

# Why it matters

Clients write code against the contract. If a field disappears or a check gets looser, their code breaks, or worse, keeps running with wrong data. A contract test catches the change before a release.

Google's MLOps guide lists, for continuous delivery, testing the prediction service by calling the service API with the expected inputs and making sure that you get the response you expect.[^google-mlops] The NIST AI RMF asks that test sets, metrics and tools used during testing are documented (MEASURE 2.1), and that the AI system to be deployed is demonstrated to be valid and reliable (MEASURE 2.5).[^nist-ai-rmf] The test file is that record.

A contract test is a mystery shopper at the restaurant counter. The shopper does not judge the taste. The shopper checks that the counter takes orders from the menu, refuses dishes that are not on it, and gives one plate per order.

# Examples

`test_api.py` has eight tests. Five are done, and trainees write three:[^lab05]

| Test | What it checks |
|---|---|
| `test_health_names_the_model` | `/health` names the model and a version number |
| `test_predict_one_entry` | One entry in, one prediction (0 or 1) and one probability out |
| `test_prediction_follows_probability` | For all 480 entries of 2025, the prediction is 1 exactly when the probability is above 0.5 |
| `test_rejects_a_missing_input` | No `rain_prob` gets 422 and `entries.0.rain_prob: Field required` |
| `test_rejects_an_after_race_column` | `finish_position` gets 422 |
| TODO 1 `test_rejects_an_out_of_range_grid` | Grid 0 and grid 21 get 422, with a message about `entries.0.grid` |
| TODO 2 `test_rejects_an_unknown_circuit_type` | `"oval"` gets 422, and the message lists the three allowed types |
| TODO 3 `test_answer_matches_the_batch` | 20 entries in, 20 predictions and 20 probabilities out, from the version that `/health` names |

- Before the TODOs: `5 passed, 3 skipped`. After: `8 passed`.
- To prove that a test protects something, change `le=20` of `grid` to `le=30` in `app.py`. The TODO 1 test fails, because grid 21 now gets status 200.
- On GitHub Actions, step "2. Contract tests" of `serve.yml` runs the trainee's own `test_api.py`. The upstream runs show `5 passed, 3 skipped`, because the upstream branch still has the TODOs.

# Common mistakes

- Testing model accuracy in a contract test. Accuracy changes with each model version; the contract must not.
- Testing only the happy path. Most of the lab tests check that bad input is refused.
- Treating a skipped test as a pass. A skipped test checks nothing.
- Testing against a fake model only. The lab tests run the lifespan handler, so they also prove that the real champion matches the contract.
- Collecting `test_api.py` and `solution/test_api.py` in one pytest run. Two files with the same name give `import file mismatch`.

[^fowler-contract]: Martin Fowler, "ContractTest", bliki.
[^fastapi-testing]: FastAPI documentation, "Testing", section "Using TestClient".
[^fastapi-testing-events]: FastAPI documentation, "Testing Events: lifespan and startup - shutdown".
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "MLOps level 2", subsection "Continuous delivery".
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1, MEASURE 2.5).
[^lab05]: Lesson 05 README, step 5 and step 9; `test_api.py`, `conftest.py`; GitHub Actions run 43890454930.
