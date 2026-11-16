---
type: Learning Package
title: Lab 09 — security gates and production-readiness acceptance
description: A classroom deck for lab 09, where engineers lock the API, fingerprint and audit the release, run every gate and let a person ship.
format: classroom-workshop
audience: engineer
release: 0.1.0
min_trust: human-reviewed
status: draft
uses:
  - /knowledge/mlops/api-access-control
  - /knowledge/mlops/artifact-integrity-manifest
  - /knowledge/mlops/dependency-vulnerability-audit
  - /knowledge/mlops/acceptance-suite
  - /knowledge/mlops/release-dossier
  - /knowledge/mlops/deployment-approval
  - /knowledge/mlops/model-serving-api
  - /knowledge/mlops/model-hot-reload
  - /knowledge/mlops/container-image
  - /knowledge/mlops/contract-test
  - /knowledge/mlops/load-test
  - /knowledge/mlops/service-level-objective
  - /knowledge/mlops/quality-gate
  - /knowledge/mlops/release-criteria
  - /knowledge/mlops/model-registry
  - /knowledge/mlops/data-validation
  - /knowledge/mlops/data-lineage
  - /knowledge/mlops/subgroup-evaluation
  - /knowledge/mlops/model-card
  - /knowledge/mlops/fail-fast-pipeline
  - /knowledge/mlops/ci-cd-pipeline
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T20:35:00+03:00 }
---

# Lab

| Item | Value |
|---|---|
| Branch | `09-acceptance` |
| Exercise | `exercises/acceptance/` (start with `README.md`) |
| Duration | About 2 hours |
| Milestone | A secured API (8 access tests pass), a signed manifest of 10 files, a clean image audit, and a dossier with 10 gates PASS that the trainee sets to ship. The tampered model and the lab 05 image are both blocked. On GitHub Actions, one approved run and one blocked fault run. |

The deck continues the house-price story. In lab 05 the price app opened, and anyone could change the appraiser. In lab 09 the price app gets ready for the bank. Agents get keys, the appraiser's files get a seal, the box is checked against the recall list, every check goes into one release folder, and only a named person signs "go live".

# Deck outline

| # | Title | Key message | Fifth-grader visual metaphor | Concepts |
|---|---|---|---|---|
| 1 | Keys to the price app | Authentication asks "who are you?" (401); authorization asks "may you do this?" (403). A client key predicts, an admin key reloads, and neither can do the other's job. Keys live in the environment, never in code, the image or git. The API fails closed without them. | An agent's key lets you ask the price app for a price. Only the admin key can change the appraiser. A stranger hears "Who are you?"; an agent at the admin door hears "I know you, but not this door". | [API access control](/knowledge/mlops/api-access-control.md), [model serving API](/knowledge/mlops/model-serving-api.md), [model hot reload](/knowledge/mlops/model-hot-reload.md), [contract test](/knowledge/mlops/contract-test.md) |
| 2 | A seal on the appraiser | A SHA-256 manifest of 10 files (7 model files, the data, the criteria, the SLO) catches a model swapped after sign-off, even when it still passes every quality gate. It is a fingerprint, not a signature: keep the proof away from whoever can change the model. Only allowed skops types load. | At sign-off, every file of the approved appraiser gets a seal: change one byte and the seal breaks. A swapped appraiser still prices homes well; only the seal notices. If the seals sit in the same drawer as the files, a thief can swap both. | [Artifact integrity manifest](/knowledge/mlops/artifact-integrity-manifest.md), [model registry](/knowledge/mlops/model-registry.md), [data lineage](/knowledge/mlops/data-lineage.md), [quality gate](/knowledge/mlops/quality-gate.md) |
| 3 | Check the box, not the shopping list | The requirements file had 0 findings; the lab 05 image had 6, all in a pip that the base image brought. Remove what the service does not need. Accept a finding only with a reason, an owner and an expiry. | Check what is really in the price app's box against the recall list, not only the shopping list. The box came with an old tool nobody uses, and it is on the list. Throw it out. | [Dependency vulnerability audit](/knowledge/mlops/dependency-vulnerability-audit.md), [container image](/knowledge/mlops/container-image.md) |
| 4 | Ten checks, three answers | One command runs all 10 gates against the deployed release. Each is PASS, FAIL or EVIDENCE MISSING, and it does not stop at the first failure. Each fault is caught by a different gate while the others pass. | The release folder for the bank has ten checks: tick, cross or "nobody checked". An empty box counts as a cross. | [Acceptance suite](/knowledge/mlops/acceptance-suite.md), [data validation](/knowledge/mlops/data-validation.md), [load test](/knowledge/mlops/load-test.md), [service-level objective](/knowledge/mlops/service-level-objective.md), [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md), [model card](/knowledge/mlops/model-card.md), [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md) |
| 5 | Only a person signs "go live" | All-PASS means PENDING, not ship. The dossier holds the evidence, the owners and the controls. Only a named approver can set ship; bots, strangers and edited dossiers are refused. On GitHub, the environment's required reviewer is the decision. Without one, the dossier says NO REVIEW RECORDED. | The bank's risk officer reads the release folder. It ends with one empty line: "Go live? Signed: ____". Only a named person may sign it, and a robot never may. | [Release dossier](/knowledge/mlops/release-dossier.md), [deployment approval](/knowledge/mlops/deployment-approval.md), [release criteria](/knowledge/mlops/release-criteria.md), [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md) |

# Numbers to quote

| What | Number | Source |
|---|---:|---|
| Access answers | no key or unknown key 401; wrong role 403; right role 200 | lab 09 README, step 4 |
| Access tests | `3 failed, 3 passed, 2 skipped` (lab 05 API), `6 passed, 2 skipped` after TODO 1 and 2, `8 passed` after TODO 3 and 4 | lab 09 README, step 3 |
| Keys | 32 random bytes, 43 characters, minimum 32; `.secrets/api.env` mode 600, git-ignored; fingerprint = first 12 hex digits of SHA-256 | `keys.py`, `security.py` |
| Image `lab09-api:1` | about 830 MB, no keys, no pip | lab 09 README, step 4 |
| Manifest | 10 files: 7 model files (`model.skops` about 10.6 MB), `races.csv`, `criteria.yaml`, `slo.yaml` | lab 09 README, step 5 |
| Dependency audit | requirements 55 packages, 0 findings; `lab09-api:1` 56 packages, 0; lab 05 image 57 packages, 6 findings in `pip 25.0.1`; codespace tools 3 advisories (2 `setuptools`, 1 `diskcache`, no fix) | lab 09 README, step 6 (November 2026) |
| Subgroups | 5 of 5 pass the 0.60 floor; lowest rookie=true 0.646; backmarkers 0.979 accuracy but 0 of 3 scorers found | lab 09 README, step 7 |
| Good release, measured locally | 10 PASS: accuracy 0.842, ROC AUC 0.907, margin 0.037, rookie accuracy 0.646, p95 75 ms, 247 requests, then PENDING, then SHIP | lab 09 README, step 8 |
| Tampered model (30 of 300 trees) | integrity FAIL; quality gates pass (ROC AUC 0.905), SLO met (p95 33 ms); pole-sitter probability 0.933 instead of 0.958 | lab 09 README, step 9 |
| Lab 05 image redeployed | access FAIL (4 passed, 4 failed), audit FAIL (6 findings); contract tests and SLO pass (p95 97 ms) | lab 09 README, step 9 |
| One data value changed (8.0 to 8.01) | data md5 FAIL (`1885fafd92e1` vs `199d7bda0a7b`) and integrity FAIL; validation still 0 failure cases | `scenarios.md`, card 4 |
| Run [43902416527](https://github.com/majlisofai/mlops-training/actions/runs/43902416527), no fault | 10 PASS (p95 130 ms, 251 requests), then SHIP `via github-environment production, NO REVIEW RECORDED` | GitHub Actions log |
| Run [43901405659](https://github.com/majlisofai/mlops-training/actions/runs/43901405659), `tamper` | `model/model.skops: CHANGED`; quality gates pass (accuracy 0.846, ROC AUC 0.904), SLO p95 26 ms; do not ship | GitHub Actions log |
| Run [43901421252](https://github.com/majlisofai/mlops-training/actions/runs/43901421252), `no-auth` | access 4 passed, 4 failed; audit 57 packages, 6 open findings; SLO p95 270 ms; do not ship | GitHub Actions log |
| Run [43902432849](https://github.com/majlisofai/mlops-training/actions/runs/43902432849), `no-evidence` | model card and fairness report EVIDENCE MISSING; 8 other gates pass; do not ship | GitHub Actions log |

Note for the trainer: the course repository's `production` environment has no required reviewers, so the passing upstream run shipped with `NO REVIEW RECORDED`. In a trainee fork with a required reviewer, the job waits for **Approve and deploy**. The dossier's SDAIA principle names come from a secondary summary page, because the SDAIA site refused the automated download; the NCA ECC-2:2024 controls are deliberately not mapped.

# Discussion questions

1. The manifest's fingerprint is a tag in MLflow, next to the files it protects. Who could change both? Where would you keep the fingerprint, or a real signature, so that the person who can change the model cannot also change the proof?
2. Each role has one shared key. Compare that with one key per client application, and with OAuth2 tokens from an identity provider. What happens in each case when one application's key leaks?
3. A finding in `diskcache` has no fix. Should a finding without a fix block a release? Who may accept it, and for how long?
4. The upstream ship job ran with `NO REVIEW RECORDED`. Is that still a human decision? What would an auditor say?
5. Which gate would you drop if the suite took too long, and what could then slip through? Use the three faults to argue.
