---
type: Domain Concept
title: Input contract
description: The schema of the inputs a model service accepts, checked on every request, so bad input gets a 422 error and never reaches the model.
tags: [mlops, serving, api, pydantic, fastapi, validation]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 2.2", "NIST-AI-RMF:MEASURE 2.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:15:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: fastapi-body
    resource: https://fastapi.tiangolo.com/tutorial/body/
    title: Request Body
    author: team:fastapi
  - id: fastapi-errors
    resource: https://fastapi.tiangolo.com/tutorial/handling-errors/
    title: Handling Errors
    author: team:fastapi
  - id: pydantic-models
    resource: https://pydantic.dev/docs/validation/latest/concepts/models/
    title: Models
    author: team:pydantic
  - id: rfc9110
    resource: https://www.rfc-editor.org/rfc/rfc9110.html#name-422-unprocessable-content
    title: "RFC 9110: HTTP Semantics, section 15.5.21 422 Unprocessable Content"
    author: org:ietf
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

An input contract is the list of inputs that a [model serving API](/knowledge/mlops/model-serving-api.md) accepts: their names, types and allowed values. The service checks every request against the contract before the model sees it. A request that breaks the contract gets an error that says what to fix.

In FastAPI, you declare the request body as a pydantic model. FastAPI then reads the body as JSON, converts the types, and validates the data. If the data is invalid, it returns a clear error that says where and what the incorrect data was. It also makes a JSON Schema of the model for the automatic documentation page.[^fastapi-body]

When a request has invalid data, FastAPI raises a `RequestValidationError`. You can replace its default handler with your own.[^fastapi-errors] The lab handler answers status 422 with one readable line per problem.[^lab05] HTTP status 422 (Unprocessable Content) means that the server understands the content type and the syntax is correct, but it cannot process the content.[^rfc9110]

# Why it matters

A model answers any numbers you give it. Without a contract, grid 21 or a made-up circuit type gets a prediction, and nobody knows that it is nonsense. The contract stops bad input at the door.

The contract also documents the model's limits. The NIST AI RMF asks that information about an AI system's knowledge limits is documented (MAP 2.2), and that the system can fail safely, particularly if made to operate beyond its knowledge limits (MEASURE 2.6).[^nist-ai-rmf] A 422 that names the bad field is a safe failure. A confident prediction from out-of-range input is not.

The contract is the pit-wall radio protocol. A message must use the agreed words and values. If an engineer asks about "grid 21" or an "oval" circuit, the radio answers "422, say again" and says why, and the predictor never hears the message.

# Examples

The lab contract is the lesson 02 schema (see [DataFrame schema](/knowledge/mlops/dataframe-schema.md)), written as the pydantic model `Entry`:[^lab05]

| Input | Type | Allowed values |
|---|---|---|
| `grid` | integer | 1 to 20 |
| `quali_gap_ms` | integer | 0 or more |
| `driver_form` | number | 1 to 20 |
| `team_form` | number | 0 or more |
| `team_dnf_rate` | number | 0 to 1 |
| `rain_prob` | number | 0 to 1 |
| `circuit_type` | text | `street`, `permanent` or `high_speed` |

- `Entry` sets `extra="forbid"`. By default, pydantic ignores extra data; with `'forbid'`, extra data is not permitted.[^pydantic-models] So a client that sends `finish_position`, an after-race column, gets an error (see [data leakage](/knowledge/mlops/data-leakage.md)).
- A bad entry with grid 21, circuit type `"oval"`, no `rain_prob` and `finish_position` gets status 422 and four lines, for example `entries.0.grid: Input should be less than or equal to 20` and `entries.0.finish_position: Extra inputs are not permitted`.[^lab05]
- The batch must have 1 to 1000 entries.
- The API also refuses to load a model whose inputs differ from the contract. The leaky model of lesson 04 needs `finish_position`, so the API does not start with it.
- The `/docs` page, made by FastAPI from `app.py`, shows the contract with its ranges.

# Common mistakes

- Ignoring unknown fields. A client that sends `finish_position` has a bug. Forbid extra fields so that the client finds out.
- Checking only types, not ranges. Grid 21 is a valid integer and an impossible grid.
- Returning one vague error. One line per problem, with the field name, tells the client what to fix.
- Writing a second set of rules for serving. Use the same schema as the training data, or the two drift apart.
- Changing the contract under the same URL. A new input needs `/v2/`, so that old clients keep working.

[^fastapi-body]: FastAPI documentation, "Request Body", section "Results".
[^fastapi-errors]: FastAPI documentation, "Handling Errors", section "Override request validation exceptions".
[^pydantic-models]: Pydantic documentation, "Models", section "Extra data".
[^rfc9110]: IETF RFC 9110, "HTTP Semantics", section 15.5.21.
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 2.2) and Table 3 (MEASURE 2.6).
[^lab05]: Lesson 05 README, section "The serving architecture" and step 4; `app.py`.
