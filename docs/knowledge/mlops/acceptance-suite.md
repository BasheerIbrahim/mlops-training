---
type: Domain Concept
title: Acceptance suite
description: One run of every release gate against the deployed release, where each gate is PASS, FAIL or EVIDENCE MISSING, and anything but all-PASS blocks.
tags: [mlops, release, testing, production-readiness, github-actions]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 1.1", "NIST-AI-RMF:MEASURE 2.1", "NIST-AI-RMF:MEASURE 2.7"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T20:05:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: ml-test-score
    resource: https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/
    title: "The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction"
    author: Eric Breck, Shanqing Cai, Eric Nielsen, Michael Salib, D. Sculley (Google), IEEE Big Data 2017
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: gh-workflow-commands
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
    title: Workflow commands for GitHub Actions
    author: org:github
  - id: lab09
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/README.md
    title: "Lesson 09: security gates and production-readiness acceptance"
    author: org:majlisofai
  - id: lab09-accept
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/accept.py
    title: "Lesson 09: accept.py"
    author: org:majlisofai
  - id: lab09-workflow
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/.github/workflows/acceptance.yml
    title: "Lesson 09: acceptance.yml workflow"
    author: org:majlisofai
  - id: lab09-scenarios
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/solution/scenarios.md
    title: "Lesson 09: scenario check, answer key"
    author: org:majlisofai
  - id: ci-ship
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43902416527
    title: "GitHub Actions run 43902416527: acceptance, no fault, shipped"
    author: org:majlisofai
  - id: ci-tamper
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43901405659
    title: "GitHub Actions run 43901405659: acceptance, fault tamper"
    author: org:majlisofai
  - id: ci-no-auth
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43901421252
    title: "GitHub Actions run 43901421252: acceptance, fault no-auth"
    author: org:majlisofai
  - id: ci-no-evidence
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43902432849
    title: "GitHub Actions run 43902432849: acceptance, fault no-evidence"
    author: org:majlisofai
---

# Definition

An acceptance suite runs every release gate, in one command, against the release as it is deployed: the model version, its files and the running service. It records the evidence of each gate.

Each gate has one of three results:

- **PASS**: the check ran and met its criterion.
- **FAIL**: the check ran and did not meet it.
- **EVIDENCE MISSING**: the check did not run, a test was skipped, or a document is absent, unsigned or for another version.

Only all-PASS can go forward. Any FAIL or EVIDENCE MISSING sets the decision to **do not ship**. All-PASS does not ship either: it sets the decision to **PENDING** until a named person decides in the [release dossier](/knowledge/mlops/release-dossier.md).[^lab09-accept]

# Why it matters

Lessons 02 to 05 built one gate for each risk, and each ran on its own.[^lab09] The ML Test Score paper says that testing and monitoring are key to the production readiness of an ML system, and gives 28 specific tests and monitoring needs.[^ml-test-score] An acceptance suite puts the gates of one release in one place, so that none is forgotten.

The NIST AI RMF asks for a determination of whether a system achieves its stated objectives and whether its deployment should proceed (MANAGE 1.1). It asks that test sets, metrics and tools are documented (MEASURE 2.1), and that security is evaluated (MEASURE 2.7).[^nist-ai-rmf] The suite's log for each gate is that documentation.

Missing evidence must block. In lab 04, a skipped gate let a cheating model through. Here, a check that did not run is never a pass.[^lab09] The faults in the lab show why one gate is not enough: each fault is caught by a different gate, and every other gate passes.

Before the restaurant opens, an inspector walks through a checklist with ten boxes. Each box gets a tick, a cross or "nobody checked". An empty box counts as a cross. Even ten ticks do not open the doors: the owner does.

# Examples

The lab's ten gates, in `accept.py`:[^lab09]

| # | Gate | From lesson | Passes when |
|---|---|---|---|
| 1 | Data validation and lineage | 02, 04 | 0 failure cases, and the md5 of the data is the md5 the model was trained on |
| 2 | Integrity | 09 | Every file matches the [manifest](/knowledge/mlops/artifact-integrity-manifest.md); only allowed skops types |
| 3 | Quality gates | 04 | All seven [quality gates](/knowledge/mlops/quality-gate.md) pass on `@champion`, measured again |
| 4 | Deployed version | 05 | The API serves the version under acceptance |
| 5 | API contract tests | 05 | The [contract tests](/knowledge/mlops/contract-test.md) pass against the container |
| 6 | Access tests | 09 | The [access tests](/knowledge/mlops/api-access-control.md) pass, none skipped |
| 7 | Load test and SLO | 05 | [SLO](/knowledge/mlops/service-level-objective.md) met |
| 8 | Dependency audit | 09 | No open finding in the image ([audit](/knowledge/mlops/dependency-vulnerability-audit.md)) |
| 9 | Model card | 08, 09 | A [model card](/knowledge/mlops/model-card.md) for this version, without `TODO` |
| 10 | Subgroup and fairness evidence | 08 | A passing report for this version |

What the suite measured:

| Release | Result | Gates that blocked | What still passed |
|---|---|---|---|
| Good release, codespace | 10 PASS, PENDING | none | accuracy 0.842, ROC AUC 0.907, p95 75 ms, 247 requests |
| Good release, GitHub Actions[^ci-ship] | 10 PASS, PENDING | none | p95 130 ms, 251 requests |
| Model file replaced (`tamper`)[^ci-tamper] | do not ship | 2 Integrity | 7 quality gates (accuracy 0.846), contract and access tests, SLO (p95 26 ms) |
| Lab 05 image deployed (`no-auth`)[^ci-no-auth] | do not ship | 6 Access (4 passed, 4 failed), 8 Audit (6 findings) | contract tests, SLO (p95 270 ms) |
| No model card, no report (`no-evidence`)[^ci-no-evidence] | do not ship | 9 and 10 EVIDENCE MISSING | everything else |
| One data value changed (`tamper.py --target data`)[^lab09-scenarios] | do not ship | 1 Data md5, 2 Integrity | data validation: 0 failure cases |

Without a model card, the codespace run says `MISSING exercises/acceptance/evidence/model_card.md: 11 TODO left; it describes version TODO, not 1`.[^lab09] A run takes about 40 seconds in the codespace, most of it the load test, and about three minutes as a GitHub Actions job.[^lab09]

How `accept.py` decides:[^lab09-accept]

- It does not stop at the first failure. The dossier must show all the evidence.
- A skipped pytest test makes the gate EVIDENCE MISSING. A gate that crashes is FAIL.
- It exits 1 when the decision is do not ship. On GitHub Actions the job then fails, and the job **Ship decision** is skipped: there is nothing to approve.[^lab09-workflow]
- It writes the gate table to the run page with `GITHUB_STEP_SUMMARY`, so a reviewer does not need to read the logs.[^gh-workflow-commands]
- It tags the model version in MLflow with `acceptance.result` (`passed` or `blocked`).

# Common mistakes

- Stopping at the first failure. A [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md) saves time when it trains. At acceptance, a reviewer needs every result.
- Treating a skipped test, an unsigned manifest or an old model card as a pass.
- Testing something other than what runs. Gate 4 checks that the API serves the version under acceptance, and gates 5 to 8 call the running container and audit its image.
- Letting the suite write "ship". The suite recommends; a person decides.
- Dropping a gate because the suite is slow. Each fault in the lab was caught by only one or two gates. Without the integrity gate, the tampered model ships.[^lab09-scenarios]
- Reading only the count of passed gates. The tampered model's clues are in the evidence: ROC AUC 0.907 to 0.905 and p95 75 ms to 33 ms in the codespace.[^lab09-scenarios]

[^ml-test-score]: Breck et al., "The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction", IEEE Big Data 2017, abstract.
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1, MEASURE 2.7) and Table 4 (MANAGE 1.1).
[^gh-workflow-commands]: GitHub Docs, "Workflow commands for GitHub Actions", section "Adding a job summary".
[^lab09]: Lesson 09 README, steps 8, 9 and 10.
[^lab09-accept]: Lesson 09 `accept.py`, docstring and functions `pytest_gate`, `run_all` and `write`.
[^lab09-workflow]: Lesson 09 `.github/workflows/acceptance.yml`, jobs `accept` and `ship`.
[^lab09-scenarios]: Lesson 09 `solution/scenarios.md`, cards 2 and 4.
[^ci-ship]: GitHub Actions run 43902416527, step "7. Acceptance suite".
[^ci-tamper]: GitHub Actions run 43901405659, step "7. Acceptance suite".
[^ci-no-auth]: GitHub Actions run 43901421252, step "7. Acceptance suite".
[^ci-no-evidence]: GitHub Actions run 43902432849, step "7. Acceptance suite".
