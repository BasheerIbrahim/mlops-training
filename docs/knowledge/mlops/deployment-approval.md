---
type: Domain Concept
title: Deployment approval
description: A human sign-off, enforced by the pipeline, that a release must get before it goes to production, such as a GitHub environment's required reviewers.
tags: [mlops, ci-cd, github-actions, human-oversight, governance]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 3.5", "NIST-AI-RMF:GOVERN 2.1", "NIST-AI-RMF:MANAGE 1.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:35:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: gh-deployments
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
    title: Deployments and environments
    author: org:github
  - id: gh-manage-env
    resource: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
    title: Managing environments for deployment
    author: org:github
  - id: gh-review
    resource: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments
    title: Reviewing deployments
    author: org:github
  - id: gh-workflow-syntax
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
    title: Workflow syntax for GitHub Actions
    author: org:github
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab04
    resource: https://github.com/majlisofai/mlops-training/blob/04-quality-gates/exercises/quality-gates/README.md
    title: "Lesson 04: quality gates and controlled promotion"
    author: org:majlisofai
---

# Definition

A deployment approval is a human sign-off that a release must get before it goes to production. The pipeline enforces it: the release step waits until an authorized person approves.

On GitHub Actions, a job that references an environment must pass all deployment protection rules of that environment before it is sent to a runner.[^gh-workflow-syntax] One rule is required reviewers: a specific person or team must approve jobs that reference the environment.[^gh-deployments] You can list up to six reviewers, and one approval is enough.[^gh-manage-env] The reviewer clicks **Review deployments**, then **Approve and deploy**. If a reviewer rejects the job, the workflow fails.[^gh-review]

# Why it matters

[Quality gates](/knowledge/mlops/quality-gate.md) check what a machine can check. A person still decides to release, and the record shows who. The NIST AI RMF asks that processes for human oversight are defined and documented (MAP 3.5), and that roles and responsibilities are clear (GOVERN 2.1).[^nist-ai-rmf] An approval also records the decision that deployment may proceed (MANAGE 1.1).

Google's MLOps guide describes a common progression: automated deployment to a test environment, then manual deployment to production after several successful pipeline runs.[^google-mlops]

The option **Prevent self-review** stops the person who started a deployment from approving it, even if they are a required reviewer.[^gh-deployments] This separates the author from the approver.

A deployment approval is a grown-up's stamp. The gatekeeper says the dish passed the checklist. The dish becomes the champion only after the grown-up looks at it and stamps it.

# Examples

- The lab job `promote` has `environment: production`. In their fork, trainees create the environment `production`, tick **Required reviewers** and add themselves.[^lab04]
- The run page shows **Waiting for review: production needs approval**. The trainee reads the gate table (seven gates PASS, accuracy 0.842, ROC AUC 0.907, margin 0.038, rookie accuracy 0.646), then approves.
- A step reads the approver from the GitHub API (`/actions/runs/<id>/approvals`). `promote.py` writes it to the model version tag `promoted_by`.
- When the gates fail, as with the leaky or the weak candidate, `promote` is skipped. There is nothing to approve.
- In the upstream repository, the `production` environment has no protection rules. So push run 43871972909 promoted without waiting, and the log says `Approved by rnrbarbosa (no review recorded)`.

# Common mistakes

- Creating the environment without a required reviewer. The promotion then runs without waiting, as in the upstream run.
- Approving without reading the gate table. The approval is the control, not a formality.
- Approving your own release in a real team. Turn on **Prevent self-review** and name an approver who did not write the change.
- Using environments in a private repository on GitHub Free. Free accounts can configure environments only for public repositories.[^gh-manage-env]
- Letting an approval replace a gate. A person cannot reliably see a leaked column in a run page. Write the gate too.

[^gh-deployments]: GitHub Docs, "Deployments and environments", sections "Deployment protection rules", "Required reviewers" and "Prevent self-review".
[^gh-manage-env]: GitHub Docs, "Managing environments for deployment".
[^gh-review]: GitHub Docs, "Reviewing deployments".
[^gh-workflow-syntax]: GitHub Docs, "Workflow syntax for GitHub Actions", section `jobs.<job_id>.environment`.
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "MLOps level 2".
[^nist-ai-rmf]: NIST AI 100-1, Table 1 (GOVERN 2.1), Table 2 (MAP 3.5) and Table 4 (MANAGE 1.1).
[^lab04]: Lesson 04 README, steps 5 and 6.
