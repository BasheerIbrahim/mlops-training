---
type: Domain Concept
title: Prediction logging
description: The serving API records every request, with the inputs, the answer, the model version and the time, so a monitor can check production later.
tags: [mlops, monitoring, serving, logging, observability]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MANAGE 4.1", "ISO-42001:A.6.2.8"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:10:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: rules-of-ml
    resource: https://developers.google.com/machine-learning/guides/rules-of-ml
    title: "Rules of Machine Learning: Best practices for ML engineering"
    author: org:google
  - id: breck-2019
    resource: https://mlsys.org/Conferences/2019/doc/2019/167.pdf
    title: Data validation for machine learning (MLSys 2019)
    author: Eric Breck, Neoklis Polyzotis, Sudip Roy, Steven Euijong Whang, Martin Zinkevich
  - id: evidently-monitoring
    resource: https://www.evidentlyai.com/ml-in-production/model-monitoring
    title: "Model monitoring for ML in production: a comprehensive guide"
    author: org:evidently-ai
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: iso-42001-a6
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-6-ai-system-life-cycle/
    title: "ISO 42001 Annex A control A.6: AI system life cycle"
    author: org:isms-online
  - id: lab06
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/exercises/monitoring/README.md
    title: "Lesson 06: monitor drift, skew and delayed labels"
    author: org:majlisofai
  - id: lab06-app
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/exercises/serve-model/app.py
    title: "exercises/serve-model/app.py on branch 06-monitoring: the API with the prediction log"
    author: org:majlisofai
---

# Definition

Prediction logging means that the serving API records each request it gets. A useful log line holds the time, a request id, the status of the answer, the model name and version, the inputs as the model saw them, and the prediction. The log is the raw material of every monitoring check: drift, skew, service health and accuracy.

Google's Rules of ML say that the best way to make sure that you train like you serve is to save the features used at serving time (Rule #29). Even a small sample of logged examples lets you check that serving and training agree.[^rules-of-ml] In the TFX data validation system, the serving infrastructure logs a sample of the serving data and imports it back into the training pipeline, where it is compared with the training data.[^breck-2019]

# Why it matters

You cannot monitor what you did not record. Without a log, nobody can say later which model answered, with which inputs, or how often the API refused a request.

Evidently says that good logging records the ongoing model performance for later analysis or audits. A batch monitor can query the prediction logs and compute model quality or data quality metrics from them.[^evidently-monitoring]

The NIST AI RMF asks that the functionality and behavior of the AI system are monitored when in production (MEASURE 2.4), and that post-deployment monitoring plans are implemented (MANAGE 4.1).[^nist-ai-rmf] ISO/IEC 42001 control A.6.2.8 asks for event logs during the AI system life cycle, at least while the system is in use.[^iso-42001-a6]

The restaurant now keeps an order book. Each line says the time, the table, what the guest ordered, which cook made it and what came out of the kitchen. It also says which orders the waiter refused, and why.

# Examples

- In lab 06 the lesson 05 API writes the log when the environment variable `PREDICTION_LOG` names a file. It adds one JSON line per entry. Without the variable, the API works exactly as in lesson 05. The change is about 50 lines in `app.py`.[^lab06] [^lab06-app]
- Each line has `ts`, `request_id`, `status`, `model_name`, `model_version`, `entry`, `inputs`, and `prediction` with `probability` for status 200 or `errors` for status 422.[^lab06] The request id is the client's `X-Request-ID` header, or a random id.[^lab06-app]
- Replaying the reference window writes 80 lines: 4 races of 20 cars, all with status 200.[^lab06]
- The new timing feed gets status 422 for all 80 entries. The API logs them too, with the reason for each entry: `76 x quali_gap_ms: Input should be a valid integer`. So the monitor reports `0 of 80 entries answered, 80 rejected (100.0%)`. An API that rejects everything is not healthy.[^lab06]
- The request id joins the log with other data about the same request. In the lab a replay manifest gives the race and driver of each entry and the features that the training pipeline recomputes. The monitor uses them for the [skew check](/knowledge/mlops/training-serving-skew.md) and to join the [delayed labels](/knowledge/mlops/delayed-labels.md).[^lab06]
- The lab changed the real API, not a copy, because the log must come from the service that runs in production.[^lab06]

# Common mistakes

- Logging only the successful requests. The rejected requests are the first sign of a broken feed.
- Logging the prediction but not the inputs. You can then measure accuracy, but you cannot find drift or skew.
- Leaving out the model version. After a [promotion](/knowledge/mlops/model-alias-promotion.md) you can no longer tell which model made which answer.
- Leaving out a request id or a business key. The labels arrive hours later, and you cannot join them to the predictions.
- Logging personal data that the monitor does not need. Log the model inputs, and apply [data minimisation](/knowledge/mlops/data-minimisation.md) to the rest.
- Writing the log in a test copy of the API. Only the production service shows what production received.

[^rules-of-ml]: Google, "Rules of Machine Learning", Rule #29 "The best way to make sure that you train like you serve is to save the set of features used at serving time".
[^breck-2019]: E. Breck et al., "Data validation for machine learning", MLSys 2019, section 4, "Training-Serving Skew".
[^evidently-monitoring]: Evidently AI, "Model monitoring for ML in production: a comprehensive guide", sections on logging and batch monitoring.
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE 2.4) and Table 4 (MANAGE 4.1).
[^iso-42001-a6]: ISMS.online, "ISO 42001 Annex A control A.6: AI system life cycle", control A.6.2.8 "AI system recording of event logs" (secondary source for ISO/IEC 42001:2023).
[^lab06]: Lesson 06 README, steps 3, 4, 7 and the monitoring architecture, branch `06-monitoring`.
[^lab06-app]: `exercises/serve-model/app.py`, function `log_request`, branch `06-monitoring`.
