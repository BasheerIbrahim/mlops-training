---
type: Domain Concept
title: Service-level objective
description: A written target for how fast and how reliable a service must be, measured by indicators such as p95 latency and failure rate.
tags: [mlops, serving, sre, slo, reliability, release]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 1.5", "NIST-AI-RMF:MEASURE 2.3", "NIST-AI-RMF:MANAGE 1.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:35:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sre-slo
    resource: https://sre.google/sre-book/service-level-objectives/
    title: "Site Reliability Engineering, chapter 4: Service Level Objectives"
    author: org:google
  - id: gh-workflow-commands
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
    title: Workflow commands for GitHub Actions
    author: org:github
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

A service-level objective (SLO) writes down how good a service must be. The Google SRE book defines a service-level indicator (SLI) as a carefully defined quantitative measure of some aspect of the level of service. An SLO is a target value or range of values for a service level that is measured by an SLI.[^sre-slo] Request latency, error rate and throughput are common SLIs.[^sre-slo]

An SLO is a [release criterion](/knowledge/mlops/release-criteria.md) for the service, not for the model alone. The lab writes it in `slo.yaml`, with the load that it is defined for, and `check_slo.py` checks a [load test](/knowledge/mlops/load-test.md) against it. The check exits 1 when the SLO is broken.[^lab05]

# Why it matters

Without a written target, nobody can say whether 1800 ms is too slow. With one, a load test passes or fails, and a pipeline can stop a slow model the same way a [quality gate](/knowledge/mlops/quality-gate.md) stops an inaccurate one.

The NIST AI RMF asks that organizational risk tolerances are determined and documented (MAP 1.5), that performance criteria are demonstrated for conditions similar to deployment (MEASURE 2.3), and that a determination is made whether deployment should proceed (MANAGE 1.1).[^nist-ai-rmf] `slo.yaml` documents the tolerance. The SLO check makes the decision.

The SRE book gives advice for choosing targets: do not pick a target based on current performance, keep it simple, have as few SLOs as possible, and perfection can wait.[^sre-slo] It also says that a tighter internal SLO than the one you promise users gives you room to respond.[^sre-slo]

The SLO is the restaurant's promise: "food on your table within 5 minutes, and almost no wrong orders, even at lunch time." The kitchen checks the clock against that promise, not against a feeling.

# Examples

The lab SLO for `POST /v1/predict`, under 10 users for 30 seconds:[^lab05]

| Objective | Threshold | Why this number |
|---|---:|---|
| p95 latency | ≤ 500 ms | A person waits for the answer. Half a second still feels immediate. |
| Failure rate | ≤ 1 % | A failed request is a race with no prediction. |
| Requests in 30 s | ≥ 150 | 10 users ask for about 250. Fewer means the API could not keep up. |

Measured results:

| Run | Model | Requests | p95 | Failures | Result |
|---|---|---:|---:|---:|---|
| Codespace container, 2 CPUs | 300 trees | 245 to 263 | 71 to 190 ms | 0 % | SLO MET |
| Codespace container, 2 CPUs | 3000 trees | 129 | 1800 ms | 0 % | SLO BROKEN: requests, p95 latency |
| After the rollback | 300 trees | 247 | 71 ms | 0 % | SLO MET |
| GitHub Actions run 43890454930[^run-pass] | 300 trees | 247 | 140 ms | 0 % | SLO MET |
| GitHub Actions run 43890470443[^run-fail] | 3000 trees | 97 | 2300 ms | 0 % | SLO BROKEN: requests, p95 latency |

- The good model keeps more than half of the 500 ms in reserve, for a busy codespace or a busier day.
- The huge forest broke the SLO with every answer right and no failures. It was too slow and handled too few requests.
- On GitHub Actions, `check_slo.py` writes the SLO table to the run page. A step can add Markdown to the file that `GITHUB_STEP_SUMMARY` names, and GitHub shows it on the summary page of the run.[^gh-workflow-commands]

# Common mistakes

- Changing `slo.yaml` to make a model pass. The lab rules forbid it. Change the model, not the promise.
- Writing an SLO with no load. "p95 ≤ 500 ms" means nothing without "10 users for 30 seconds".
- Using the average latency. The SRE book says that averages hide the slow tail.[^sre-slo]
- Setting the target to what the system does today. Ask what the users need.
- Letting only the data scientists choose the numbers. The team that runs the API and the people who use the predictions should agree on them too.

[^sre-slo]: Google, "Site Reliability Engineering", chapter 4 "Service Level Objectives", sections "Service Level Terminology", "Indicators in Practice", "Choosing Targets" and "SLOs Set Expectations".
[^gh-workflow-commands]: GitHub Docs, "Workflow commands for GitHub Actions", section "Adding a job summary".
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 1.5), Table 3 (MEASURE 2.3) and Table 4 (MANAGE 1.1).
[^run-pass]: GitHub Actions run 43890454930, step "5. Load test and SLO check".
[^run-fail]: GitHub Actions run 43890470443, step "5. Load test and SLO check".
[^lab05]: Lesson 05 README, steps 7 to 9; `slo.yaml`, `check_slo.py`.
