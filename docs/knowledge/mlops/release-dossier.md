---
type: Domain Concept
title: Release dossier
description: The evidence pack of one release, with facts, owners, gate results and mapped controls, whose ship decision only a named human approver can set.
tags: [mlops, release, governance, human-oversight, accountability, github-actions]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:GOVERN 2.1", "NIST-AI-RMF:MAP 3.5", "NIST-AI-RMF:MEASURE 1.3", "NIST-AI-RMF:MEASURE 2.8"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T20:20:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: nist-ssdf
    resource: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf
    title: "Secure Software Development Framework (SSDF) Version 1.1, NIST SP 800-218"
    author: org:nist
  - id: gh-deployments
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
    title: Deployments and environments
    author: org:github
  - id: sdaia-summary
    resource: https://regulations.ai/regulations/RAI-SA-NA-PCAESXX-2023
    title: "SDAIA AI Ethics Principles (summary page, secondary source)"
    author: org:regulations-ai
  - id: lab09
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/README.md
    title: "Lesson 09: security gates and production-readiness acceptance"
    author: org:majlisofai
  - id: lab09-decide
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/decide.py
    title: "Lesson 09: decide.py, accept.py and release.yaml"
    author: org:majlisofai
  - id: lab09-scenarios
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/solution/scenarios.md
    title: "Lesson 09: scenario check, answer key"
    author: org:majlisofai
  - id: lab09-workflow
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/.github/workflows/acceptance.yml
    title: "Lesson 09: acceptance.yml workflow"
    author: org:majlisofai
  - id: ci-ship
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43902416527
    title: "GitHub Actions run 43902416527: acceptance, no fault, shipped"
    author: org:majlisofai
---

# Definition

A release dossier is the evidence pack of one release. The [acceptance suite](/knowledge/mlops/acceptance-suite.md) writes it, and a person decides from it. In the lab it has four parts:[^lab09]

1. **The decision block**: the decision, the suite's recommendation, who set it, when, how and why.
2. **The release**: the model version and alias, links to the MLflow run and model version, the data md5, the SHA-256 of the [integrity manifest](/knowledge/mlops/artifact-integrity-manifest.md) and who signed it, who proposed and promoted the model, the git commit, and the image ID of the API.
3. **The owners**: one person each for the model, the data, the service and security, and the approvers.
4. **The gates**: the result and evidence of each gate, the path of its log, and the published controls that the gate gives evidence for.

The suite writes `dossier.md` for people and `dossier.json` for tools. It sets the decision to **do not ship** itself, or leaves it **PENDING**. It never writes **ship**. Only a named approver can set ship, and only when every gate passed.[^lab09-decide]

# Why it matters

The dossier lets a person who did not build the model decide, and lets an auditor see later who decided and on what evidence. The NIST AI RMF asks that roles and responsibilities are documented and clear (GOVERN 2.1), that processes for human oversight are defined and documented (MAP 3.5), that internal experts who were not front-line developers, or independent assessors, take part in assessments (MEASURE 1.3), and that transparency and accountability risks are examined and documented (MEASURE 2.8).[^nist-ai-rmf]

NIST's Secure Software Development Framework asks you to archive, for each release, the files and data that support it, such as integrity verification and provenance data (PS.3.1).[^nist-ssdf] On GitHub Actions the workflow keeps the dossier, the logs, the manifest and the evidence as the artifact `release-dossier`, and the decided dossier as `release-dossier-decided`.[^lab09-workflow]

On GitHub, the human decision is a [deployment approval](/knowledge/mlops/deployment-approval.md). Required reviewers must approve a job that references the environment, and one approval is enough. With **Prevent self-review**, the person who started the deployment cannot approve it. If the environment requires approval, the job cannot read environment secrets before a reviewer approves.[^gh-deployments]

The dossier is the restaurant's inspection folder. It holds the checklist, the photos of the recipe and the names of who cooked, who bought the food and who holds the keys. The last page has one empty line: "Open today? Signed: ____". Only the owner may sign it, and a robot never may.

# Examples

`decide.py` sets the decision.[^lab09-decide] In the lab:[^lab09]

| Command | Answer |
|---|---|
| `--decision ship --approver "Somebody Else"` | `REFUSED: 'Somebody Else' is not an approver in release.yaml` |
| `--decision ship --approver "<your name>"`, you are also the model owner | `WARNING: the approver is also the model owner: no separation of duties`, then `DECISION: SHIP` |
| `ship` after the model was tampered with | `REFUSED: the suite says do not ship: ... Nobody can ship this release.` |
| `ship` after a number in `dossier.md` was edited | refused: the dossier changed after `accept.py` wrote it |
| `ship` with an approver called `github-actions` or `...[bot]` | refused: not a person |
| `--decision "do not ship"` without `--reason` | refused: a reason is required |

After a ship, the model version in MLflow has the tags `release.decision = ship`, `release.decided_by`, `release.decided_via` and `release.dossier_sha256`. `accept.py` stores the SHA-256 of the dossier without its decision block, so `decide.py` can tell when somebody edited the evidence.[^lab09-decide]

On GitHub Actions, the job **Ship decision** runs only when every gate passed. It reads the approver from the GitHub API and records it with `decide.py`.[^lab09-workflow] In the course repository, `production` has no required reviewers. So run 43902416527 shipped without a review, and the dossier says so: `via github-environment production, NO REVIEW RECORDED (the environment has no required reviewers; rnrbarbosa started the run)`.[^ci-ship]

The controls column maps each gate to NIST AI RMF subcategories and to five of the seven SDAIA AI Ethics Principles: Fairness; Privacy & Security; Reliability & Safety; Transparency & Explainability; Accountability & Responsibility. The dossier says the mapping is not a compliance claim.[^lab09-decide] The lab took the SDAIA names from a secondary summary page, because the SDAIA site refused the automated download. That page lists the seven principles and dates them September 2023.[^sdaia-summary] Read the SDAIA original before you quote it. The NCA Essential Cybersecurity Controls (ECC-2:2024) are not mapped: whether they apply to this system is still to be confirmed.[^lab09]

# Common mistakes

- The author approves the release. In scenario card 8, the decision stands on the evidence, but the process failed. Add an independent approver, and turn on **Prevent self-review**.[^lab09-scenarios]
- An environment without required reviewers. The ship job then runs at once. Is that still a human decision? The dossier records `NO REVIEW RECORDED` so that an auditor can see it.
- Editing the dossier to fix a number. Run the suite again instead.
- Naming a bot, a team alias or nobody as the approver. A release decision needs a named person.
- Reading the controls column as a certificate. It shows which published control a gate gives evidence for. It does not prove compliance.
- Attaching evidence for another version, such as last release's model card. The suite marks it EVIDENCE MISSING, and the approver should refuse it too.[^lab09-scenarios]
- Throwing the dossier away after the release. Keep it with the release, so you can explain the decision during an incident or an audit.

[^nist-ai-rmf]: NIST AI 100-1, Table 1 (GOVERN 2.1), Table 2 (MAP 3.5) and Table 3 (MEASURE 1.3, MEASURE 2.8).
[^nist-ssdf]: NIST SP 800-218, practice PS.3, task PS.3.1.
[^gh-deployments]: GitHub Docs, "Deployments and environments", sections "Required reviewers", "Prevent self-review" and "Environment secrets".
[^sdaia-summary]: regulations.ai, summary of the SDAIA AI Ethics Principles (secondary source; the SDAIA original at https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf was not readable by automated download).
[^lab09]: Lesson 09 README, step 8 and section "Sources".
[^lab09-decide]: Lesson 09 `decide.py`, `accept.py` (functions `write`, `render`, `body_sha256`, table `CONTROLS`) and `release.yaml`.
[^lab09-scenarios]: Lesson 09 `solution/scenarios.md`, cards 5 and 8.
[^lab09-workflow]: Lesson 09 `.github/workflows/acceptance.yml`, job `ship` and the upload steps.
[^ci-ship]: GitHub Actions run 43902416527, job "Ship decision", step "8. Record the decision".
