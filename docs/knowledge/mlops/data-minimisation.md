---
type: Domain Concept
title: Data minimisation
description: A privacy control that keeps personal identifiers out of model inputs and prediction logs, using only the data the purpose needs, and tests it.
tags: [privacy, data-minimisation, personal-data, logging, purpose-limitation]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.10", "NIST-AI-RMF:MAP 1.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T23:00:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: gdpr
    resource: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679
    title: Regulation (EU) 2016/679 (General Data Protection Regulation)
    author: org:european-union
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: sdaia-ethics
    resource: https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf
    title: AI Ethics Principles, version 1, May 2025 (document SDAIA-P114E)
    author: org:sdaia
  - id: lab08
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/README.md
    title: "Lesson 08: fairness, transparency and the model card"
    author: org:majlisofai
  - id: lab08-privacy
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/test_privacy.py
    title: "Lesson 08: privacy gates (test_privacy.py)"
    author: org:majlisofai
  - id: f1-data
    resource: https://github.com/majlisofai/mlops-training/blob/main/f1/data/README.md
    title: The F1 race dataset (data README)
    author: org:majlisofai
---

# Definition

Data minimisation means that personal data are adequate, relevant and limited to what is necessary for the purpose. The GDPR states it as a principle in Article 5(1)(c).[^gdpr] Article 5(1)(b), purpose limitation, says that data collected for one purpose must not be processed in a way that is incompatible with it.[^gdpr]

For an ML system this means two rules:

1. **No identifiers as model inputs.** The model gets only the inputs that predict the outcome.
2. **No identifiers in logs.** A prediction log keeps only what the model used and what it answered.

In lab 08 these rules are tests, not promises. The privacy gates fail the release when an identifier is a model input or appears in the prediction log, as a field name or as a value.[^lab08-privacy]

# Why it matters

A prediction log is needed for monitoring. Without a control it slowly becomes a register of people. An identifier as an input lets the model decide on who a person is.

NIST asks that the privacy risk of the AI system is examined and documented (MEASURE 2.10). It gives "the system shall respect the privacy of its users" as an example of a system requirement (MAP 1.6). NIST lists data minimising methods, such as de-identification and aggregation of certain model outputs, as support for privacy-enhanced AI.[^nist-ai-rmf]

SDAIA asks that the decision criteria of an AI system are not based on personally identifying information, and that personal information is limited to what is necessary for the system to work. It also asks for a test that the combination of available data does not break anonymity.[^sdaia-ethics] The GDPR asks that, by default, only the personal data necessary for each purpose are processed, including how long they are stored and who can access them (Article 25(2)).[^gdpr]

The pit-wall question says "grid 3, street circuit, rain likely", not the driver's name. The predictor needs only what changes the call, so driver names stay out of the inputs and the telemetry logs.

# Examples

`driver_code` and `driver_name` are synthetic, but the lab treats them as personal data.[^f1-data][^lab08]

| Control | Where | Lab result |
|---|---|---|
| Identifiers are not model inputs | `test_no_personal_identifiers_in_model_inputs` | 7 inputs, none of them an identifier |
| Subgroup columns are reporting-only | `test_no_reporting_only_columns_in_model_inputs` | `rookie`, `team_tier` not used |
| The API refuses unknown fields | lab 05 [input contract](/knowledge/mlops/input-contract.md), `extra="forbid"` | `send_season.py --with-driver-code`: HTTP 422, `Extra inputs are not permitted`, 24 races refused |
| The client sends only the inputs | `send_season.py` | 24 races, 480 entries |
| The log keeps an allowlist of fields | `logged_api.py` | time, model name and version, 7 inputs, predictions, probabilities |
| The log is tested | `test_no_personal_data_in_prediction_log` | 0 problems in 24 records |
| Small groups are suppressed | `min_drivers_per_published_cell: 2` | both rookie x team_tier cells say `suppressed: 1 driver` |

- The gate must be able to fail. On `prediction_log_v0.jsonl`, a log from an imaginary first API that logged the whole request, it fails: `6 personal identifiers ..., first: line 1: field request.driver_code; line 1: dashboard_label = 'Amara Okafor (P1)'`. It found a field called `driver_code` and a name hidden in a free-text value.
- A second log was not covered: uvicorn's access log writes the client's IP address on every request. `uvicorn --no-access-log` turns it off.
- On GitHub Actions, workflow `fairness.yml` checks that a client sending `driver_code` is refused, then runs the privacy gates with the fairness gates.

See [prediction logging](/knowledge/mlops/prediction-logging.md) for what the log is for.

# Common mistakes

- Logging the whole request "just in case". Log an allowlist of fields, not a blocklist.
- Checking field names only. A name can hide inside a free-text value such as a dashboard label. Check the values too.
- Forgetting the other logs. Web server access logs, error traces and the tracking server can hold personal data.
- Publishing a subgroup result for one person. A group of one is a person.
- Thinking minimisation ends at the model. Retention time, who may read the log, access control on the MLflow server and a privacy impact assessment are still decisions to make. The lab does not make them.
- Using a sensitive attribute "to be fair" without a decision. A per-group rule needs the attribute at prediction time. See [bias mitigation](/knowledge/mlops/bias-mitigation.md).

[^gdpr]: Regulation (EU) 2016/679, Article 5(1)(b) "purpose limitation", Article 5(1)(c) "data minimisation" and Article 25(2) "data protection by default". Cited as a widely used legal statement of the principle; the course gives no legal advice.
[^nist-ai-rmf]: NIST AI 100-1, section 3.6 "Privacy-Enhanced", Table 2 (MAP 1.6) and Table 3 (MEASURE 2.10).
[^sdaia-ethics]: SDAIA, AI Ethics Principles (2025), Principle 2 Privacy and Security: Plan and Design, items 1 and 2 (p. 16); Build and Validate, item 3 (p. 18). Printed page numbers. The sdaia.gov.sa server refused automated download on 2026-11-16; the text was checked against a saved copy of document SDAIA-P114E, version 1.
[^lab08]: Lesson 08 README, "Subgroups, not protected characteristics", steps 4 and 9, and "Privacy controls in this course".
[^lab08-privacy]: Lesson 08 `test_privacy.py`.
[^f1-data]: F1 data README, column table and "What the data is not".
