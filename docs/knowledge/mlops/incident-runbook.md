---
type: Domain Concept
title: Incident runbook
description: A written plan for incidents that says how to triage, decide, recover and verify, plus a blameless report that turns each incident into actions.
tags: [mlops, incident-response, runbook, postmortem, operations]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 4.1", "NIST-AI-RMF:MANAGE 4.3", "NIST-AI-RMF:MANAGE 2.3", "ISO-42001:A.8.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:40:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: sre-intro
    resource: https://sre.google/sre-book/introduction/
    title: "Site Reliability Engineering, chapter 1: Introduction"
    author: org:google-sre
  - id: sre-emergency
    resource: https://sre.google/sre-book/emergency-response/
    title: "Site Reliability Engineering, chapter 13: Emergency response"
    author: org:google-sre
  - id: sre-incidents
    resource: https://sre.google/sre-book/managing-incidents/
    title: "Site Reliability Engineering, chapter 14: Managing incidents"
    author: org:google-sre
  - id: sre-postmortem
    resource: https://sre.google/sre-book/postmortem-culture/
    title: "Site Reliability Engineering, chapter 15: Postmortem culture: learning from failure"
    author: org:google-sre
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: iso-42001-a8
    resource: https://www.isms.online/iso-42001/annex-a-controls/a-8-information-for-interested-parties-of-ai-systems/
    title: "ISO 42001 Annex A control A.8: Information for interested parties of AI systems (secondary source)"
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

An incident runbook is a plan, written before the incident, that tells the person on call what to do. It has the steps, the commands and what "healthy" looks like.

The lab runbook has five parts: triage, decide, recover and verify, ask an AI assistant, and write the incident report. It sets three rules: evidence before action, write the time down, and change one thing at a time and check after each change.[^runbook]

The **decide** part is a table. Each row joins a kind of evidence to a likely cause, one action and one "do not". For example: the service broke right after `@champion` moved, and the previous champion was healthy. Cause: a bad release. Action: roll back. Do not: retrain in a hurry.[^runbook]

The **incident report** (a postmortem) closes the incident. Google's SRE book defines a postmortem as a written record of an incident, its impact, the actions taken to mitigate or resolve it, the root causes, and the follow-up actions to prevent it from happening again.[^sre-postmortem]

# Why it matters

A plan written in calm time works better than one made up under stress. Google SRE reports that best practices recorded in a playbook give roughly a 3x improvement in mean time to repair (MTTR) compared with "winging it".[^sre-intro] The SRE book also says to develop and document incident procedures in advance.[^sre-incidents]

The report makes the team learn. It is blameless: it assumes that everyone acted with good intentions and did the right thing with the information they had. You cannot "fix" people, but you can fix systems and processes.[^sre-postmortem] A release rollback by the on-call engineer is one of the usual triggers for a postmortem.[^sre-postmortem]

A rollback that nobody tested can make an outage longer, so test the recovery steps too.[^sre-emergency]

The NIST AI RMF asks for post-deployment plans that include incident response, recovery and change management (MANAGE 4.1). It asks that incidents and errors are communicated to the relevant AI actors, and that the processes for tracking, responding and recovering are followed and documented (MANAGE 4.3). It also asks for procedures to respond to and recover from a risk that was not known before (MANAGE 2.3).[^nist-ai-rmf] ISO/IEC 42001 control A.8.4 covers the communication of incidents to users and other interested parties. We confirmed this only through a secondary source.[^iso-42001-a8]

Kid version: the team keeps a runbook on the pit wall. It says what to check when the car will not start, who to call, and how to know it is fixed. After each bad weekend, the team writes one page: what went wrong, what we did, and what we change so it does not happen again. Nobody gets told off.

# Examples

The lab incident, as a report would record it:[^lab07]

| Part of the report | Lab 07 |
|---|---|
| What users saw | The race engineers' dashboard showed no predictions for the next race |
| Root cause | A "weekend hotfix" moved `@champion` to version 2 directly, without gates or approval. Version 2 needs `laps_completed`, an after-race input that API v1 does not accept |
| Contributing factors | `/admin/reload` refused version 2 (500) and kept version 1, so nothing broke on Sunday. The nightly restart loaded `@champion` and the container crash-looped. Version 2 also trained on provisional labels |
| Decision | Decision table row "bad release": `promote.py --rollback --approver "<name>"` |
| Recovery and proof | `/health` back to version 1 in 27 seconds; contract tests `8 passed`; `SLO MET` (247 requests, p95 81 ms); 2026 accuracy 0.706, as before |
| Actions | Prevent: only the gated path may move `@champion`. Detect: alert when `@champion` has no `gates` tag. Respond: keep the runbook and test the rollback |

The incident ends when every check in part 3 passes, not when someone typed the rollback.[^runbook]

The "Do not" column matters as much as the action. Retraining in a hurry would ship a second untested model. A rollback is wrong when a client feed sends bad inputs, because the model is not the problem.[^runbook]

# Common mistakes

- Writing the runbook during the incident.
- A runbook with actions but no checks. Write what "recovered" looks like, with numbers.
- Ending the incident at the fix, not at the proof.
- A report that names a culprit. Name the missing control instead: here, nothing stopped a script from moving `@champion`.
- A report without times. Note the time of every observation and action, in UTC.[^runbook]
- Actions with no owner and no date. Then nothing changes.
- Letting an AI assistant run commands that change the registry or the service. A person reads each command, runs it, and is named.[^runbook]

See also [incident triage](/knowledge/mlops/incident-triage.md), [model rollback](/knowledge/mlops/model-rollback.md), [contract test](/knowledge/mlops/contract-test.md) and [service-level objective](/knowledge/mlops/service-level-objective.md).

[^sre-intro]: Google SRE book, chapter 1, "Emergency Response".
[^sre-emergency]: Google SRE book, chapter 13, "Details" of the test-induced emergency and "Keep a History of Outages".
[^sre-incidents]: Google SRE book, chapter 14, "Best Practices for Incident Management": "Prepare".
[^sre-postmortem]: Google SRE book, chapter 15, introduction and "Blameless postmortems".
[^nist-ai-rmf]: NIST AI 100-1, Table 4 (MANAGE 2.3, MANAGE 4.1, MANAGE 4.3).
[^iso-42001-a8]: ISMS.online summary of ISO/IEC 42001 Annex A control A.8.4 "Communication of incidents". We did not read the standard itself.
[^runbook]: Lesson 07 runbook, three rules, part 2 (decision table), part 3 (recover and verify), part 4 (AI assistant) and part 5 (incident report).
[^lab07]: Lesson 07 README, steps 3 to 6.
