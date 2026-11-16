---
type: Domain Concept
title: Incident triage
description: Collecting evidence in a fixed order (health, version, logs, inputs, delayed labels) before changing anything, to find what broke and how badly.
tags: [mlops, incident-response, triage, operations, monitoring]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 4.3", "NIST-AI-RMF:MEASURE 2.4", "ISO-42001:A.6.2.6"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:30:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sre-troubleshooting
    resource: https://sre.google/sre-book/effective-troubleshooting/
    title: "Site Reliability Engineering, chapter 12: Effective troubleshooting"
    author: org:google-sre
  - id: sre-incidents
    resource: https://sre.google/sre-book/managing-incidents/
    title: "Site Reliability Engineering, chapter 14: Managing incidents"
    author: org:google-sre
  - id: sre-intro
    resource: https://sre.google/sre-book/introduction/
    title: "Site Reliability Engineering, chapter 1: Introduction"
    author: org:google-sre
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: iso-42001-a6
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-6-ai-system-life-cycle/
    title: "ISO 42001 Annex A control A.6: AI system life cycle (secondary source)"
    author: ISMS.online
  - id: runbook
    resource: https://github.com/majlisofai/mlops-training/blob/07-recovery/exercises/recovery/RUNBOOK.md
    title: "Runbook: the f1-points-finish service has an incident"
    author: org:majlisofai
  - id: lab07
    resource: https://github.com/majlisofai/mlops-training/blob/07-recovery/exercises/recovery/README.md
    title: "Lesson 07: recover the service and train a controlled challenger"
    author: org:majlisofai
---

# Definition

Incident triage is the first part of an incident. You collect the evidence and decide how serious the problem is. You do not change anything yet.

Google's SRE book describes the same order. A problem report comes first. Then you triage: you decide how serious it is and how big a response it needs. Then you examine each component, form hypotheses and test them.[^sre-troubleshooting]

In the lab, the runbook asks five questions, in order: **health** (is the API up, which version does it serve?), **version** (which version is `@champion`, who moved it, did the gates run?), **logs**, **inputs** (do clients send valid inputs?) and **performance on [delayed labels](/knowledge/mlops/delayed-labels.md)**. The script `triage.py` answers them and changes nothing.[^runbook]

# Why it matters

A rollback, a restart or a retrain destroys evidence. So the runbook's first rule is "evidence before action".[^runbook] The SRE book puts it as "stop the bleeding, restore service, and preserve the evidence for root-causing".[^sre-incidents] Quick mitigation and kept logs go together.[^sre-troubleshooting]

Recent changes are a good place to start. Systems tend to stay stable until something acts on them, such as a configuration change.[^sre-troubleshooting] Google SRE found that about 70 % of outages come from changes to a live system.[^sre-intro] That is why question 2 asks who moved `@champion`, and when.

The NIST AI RMF asks that processes for tracking, responding to and recovering from incidents and errors are followed and documented (MANAGE 4.3). It also asks that the AI system is monitored in production (MEASURE 2.4).[^nist-ai-rmf] ISO/IEC 42001 control A.6.2.6 covers the operation and monitoring of an AI system, including tracking errors and failures. We confirmed this only through a secondary source.[^iso-42001-a6]

Kid version: on race morning the car will not start. Before anyone touches it, the race engineer reads the telemetry: is it running, which setup is on it, what do the logs say, are the timing sheets normal, and how good were the predictor's calls against the final classification?

# Examples

The lab measured this evidence after the incident.[^lab07]

| # | Question | What `triage.py` showed |
|---|---|---|
| 1 | Health | `DOWN: no answer: Connection refused`; the container is `restarting`, `last exit code 3` |
| 2 | Version | Version 2 is `@champion`, `promoted by hotfix-script`, `gates: not run`, `inputs: 8, NOT the API v1 inputs: extra ['laps_completed']` |
| 3 | Logs | `POST /admin/reload` answered 500, then at each restart `RuntimeError: ... needs the inputs [..., 'laps_completed', ...]` and `Application startup failed` |
| 4 | Inputs | `160 of 160 entries valid`; only `team_dnf_rate` moved (mean 0.109 to 0.207) |
| 5 | Delayed labels | The API does not answer. Offline, version 1 scores 0.842 on 2025 and 0.706 on 2026; version 2 cannot be evaluated, because `laps_completed` does not exist before a race |

The same five answers, taken while the service was healthy, are the "normal" to compare with. The inputs and the 2026 accuracy were the same before and after. Only the version changed. So the evidence points to a bad release, not to the inputs.

The run metric `accuracy_2026 0.931` of version 2 is not evidence that it is good. It was measured on the same 2026 races that the model trained on, with provisional labels.[^lab07]

# Common mistakes

- Fixing first and looking later. A restart or a rollback wipes the state you needed to find the cause.
- Reading only health. "Down" says that something is wrong, not what. The cause here was in the registry (question 2).
- Trusting a metric that the change itself logged. Measure the version again on data it did not train on.
- No baseline. Without the healthy "normal" you cannot see which answer changed.
- Judging the model on provisional labels, or on races it trained on.[^runbook]
- Letting an AI assistant lead the triage. Give it the evidence, check every line it quotes, and let a person decide.[^runbook]

See also [incident runbook](/knowledge/mlops/incident-runbook.md), [model rollback](/knowledge/mlops/model-rollback.md) and [monitoring alert](/knowledge/mlops/monitoring-alert.md).

[^sre-troubleshooting]: Google SRE book, chapter 12, sections "Triage", "Examine", "Diagnose" and "Recent changes".
[^sre-incidents]: Google SRE book, chapter 14, "Best Practices for Incident Management": "Prioritize".
[^sre-intro]: Google SRE book, chapter 1, "Change Management".
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.4) and Table 4 (MANAGE 4.3).
[^iso-42001-a6]: ISMS.online summary of ISO/IEC 42001 Annex A control A.6.2.6 "AI system operation and monitoring". We did not read the standard itself.
[^runbook]: Lesson 07 runbook, three rules, part 1 (triage) and part 4 (AI assistant).
[^lab07]: Lesson 07 README, steps 2 and 4.
