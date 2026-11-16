---
type: Domain Concept
title: Load test
description: A test that sends many requests at the same time to a running service and measures its latency percentiles, throughput and failures under that load.
tags: [mlops, serving, testing, performance, locust]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.3", "NIST-AI-RMF:MEASURE 2.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:30:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: locust-quickstart
    resource: https://docs.locust.io/en/stable/quickstart.html
    title: Your first test
    author: team:locust
  - id: locust-locustfile
    resource: https://docs.locust.io/en/stable/writing-a-locustfile.html
    title: Writing a locustfile
    author: team:locust
  - id: locust-headless
    resource: https://docs.locust.io/en/stable/running-without-web-ui.html
    title: Running without the web UI
    author: team:locust
  - id: locust-config
    resource: https://docs.locust.io/en/stable/configuration.html
    title: Configuration
    author: team:locust
  - id: sre-slo
    resource: https://sre.google/sre-book/service-level-objectives/
    title: "Site Reliability Engineering, chapter 4: Service Level Objectives"
    author: org:google
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: run-pass
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43890454930
    title: "GitHub Actions run 43890454930: serve, good candidate, SLO MET"
    author: org:majlisofai
  - id: run-fail
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43890470443
    title: "GitHub Actions run 43890470443: serve, huge forest, SLO BROKEN"
    author: org:majlisofai
  - id: lab05
    resource: https://github.com/majlisofai/mlops-training/blob/05-serve-model/exercises/serve-model/README.md
    title: "Lesson 05: serve the model and roll back a faulty release"
    author: org:majlisofai
---

# Definition

A load test sends many requests at the same time to a running service, the way many clients would. It measures how fast the service answers (latency), how many requests it handles (throughput) and how many fail.

A test with one request shows that the service works. A load test shows how it behaves when it is busy.[^lab05] Google's MLOps guide lists load testing of the prediction service, to capture metrics such as queries per second and model latency, as a test for continuous delivery.[^google-mlops]

The lab uses Locust. A Locust test is a Python program that makes requests to the system under test.[^locust-quickstart] A locustfile defines a user class, often an `HttpUser`, with tasks marked `@task`. `wait_time = between(min, max)` makes each user wait a random time between tasks. A task can take a weight, and `catch_response` lets the test mark a request as failed.[^locust-locustfile]

The usual latency number is a percentile. The 95th percentile (p95) is the time within which 95 of 100 requests answer. The Google SRE book says that a simple average can hide the slow requests, and a high percentile shows a plausible worst case.[^sre-slo]

# Why it matters

A model can be accurate and still too slow to serve. Accuracy gates measure the model alone, one batch at a time. Only a load test shows the queue that builds up when many clients call at once.

The NIST AI RMF asks that performance criteria are measured and demonstrated for conditions similar to the deployment setting (MEASURE 2.3), and that test sets, metrics and tools are documented (MEASURE 2.1).[^nist-ai-rmf] The load test runs against the same container image, with a written load, and keeps the Locust report.

The load test is the race start. One engineer on the radio tells you nothing. Every engineer on the radio at once shows you whether the pit wall keeps up.

# Examples

- `locustfile.py` defines one user, `RaceEngineer`. It asks for the predictions of one real 2025 race (20 cars) in one `POST /v1/predict`, then waits 0.5 to 1.5 seconds. Now and then it calls `/health` (weights 10 and 1). It marks a request as failed when the status is not 200 or the number of predictions is wrong.[^lab05]
- `load_test.sh` runs Locust with `--headless --users 10 --spawn-rate 5 --run-time 30s --csv results/locust --html results/locust.html`. `--headless` runs Locust without the web UI.[^locust-headless] With `--csv`, Locust writes a stats file for the whole run, with one row per endpoint and an aggregated row.[^locust-config] `check_slo.py` reads the `POST /v1/predict` row of `results/locust_stats.csv` and checks it against the [service-level objective](/knowledge/mlops/service-level-objective.md).
- By default, Locust exits with code 1 when any request failed.[^locust-headless] `load_test.sh` ignores that exit code, so that the SLO check decides.
- Ten users ask for about 250 requests in 30 seconds. The good model (300 trees) had a p95 of 71 to 190 ms in a container with 2 CPUs.[^lab05] On GitHub Actions, run 43890454930 measured 247 requests and p95 140 ms.[^run-pass]
- The huge forest (3000 trees of depth 12) answers one request in about 0.2 seconds. Under load, the requests queue: in the container it had 129 requests and p95 1800 ms. On GitHub Actions, run 43890470443 measured 97 requests and p95 2300 ms, with 0 failures.[^run-fail]

# Common mistakes

- Calling the service once and calling it fast. The huge forest looked fine in a one-request smoke test.
- Reporting the average latency. It hides the slow requests that users feel.
- Counting only failures. The huge forest had 0 % failures and still broke the objective, because it was slow and handled fewer requests.
- Running the load test on a busy machine. The good model can break the SLO if the Locust web UI or another load test runs at the same time.
- Load-testing without a written objective. A number with no limit cannot pass or fail.

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "MLOps level 2", subsection "Continuous delivery".
[^locust-quickstart]: Locust documentation, "Your first test".
[^locust-locustfile]: Locust documentation, "Writing a locustfile", sections on `HttpUser`, `wait_time`, `@task` and validating responses.
[^locust-headless]: Locust documentation, "Running without the web UI".
[^locust-config]: Locust documentation, "Configuration", section "Save test statistics in CSV format".
[^sre-slo]: Google, "Site Reliability Engineering", chapter 4 "Service Level Objectives", section on aggregation.
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1, MEASURE 2.3).
[^run-pass]: GitHub Actions run 43890454930, step "5. Load test and SLO check".
[^run-fail]: GitHub Actions run 43890470443, step "5. Load test and SLO check".
[^lab05]: Lesson 05 README, steps 7 and 8; `locustfile.py`, `load_test.sh`, `check_slo.py`.
