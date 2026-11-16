---
type: Domain Concept
title: CI/CD pipeline
description: An automated sequence of steps that validates, builds, tests and releases a change the same way each time, stopping at the first failure.
tags: [mlops, ci-cd, github-actions, jenkins, automation]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:GOVERN 1.4", "NIST-AI-RMF:MANAGE 1.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:30:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: gh-understand
    resource: https://docs.github.com/en/actions/get-started/understand-github-actions
    title: Understanding GitHub Actions
    author: org:github
  - id: gh-workflow-syntax
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
    title: Workflow syntax for GitHub Actions
    author: org:github
  - id: jenkins-pipeline
    resource: https://www.jenkins.io/doc/book/pipeline/
    title: Jenkins User Handbook, Pipeline
    author: org:jenkins
  - id: pytest-output
    resource: https://docs.pytest.org/en/stable/how-to/output.html
    title: Managing pytest's output
    author: team:pytest
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

A CI/CD pipeline is an automated sequence of steps that takes a change from version control to use. Continuous integration (CI) builds the change and runs tests. Continuous delivery (CD) deploys what CI produced to the target environment.[^google-mlops] The pipeline stops at the first step that fails.

For ML, CI also tests and validates data and models, not only code.[^google-mlops] The lab pipeline has four steps: validate data, train candidate, [quality gates](/knowledge/mlops/quality-gate.md), promote.[^lab04]

The lab runs the pipeline on GitHub Actions, a CI/CD platform. A workflow is an automated process that runs one or more jobs. An event, such as a push, triggers a workflow run. A job is a set of steps that runs on one runner.[^gh-understand] The course plan names Jenkins as the CI server. A Jenkins Pipeline is defined in a `Jenkinsfile` in source control, with stages such as Build, Test and Deploy.[^jenkins-pipeline] The ideas in this concept are the same on both tools.

# Why it matters

A pipeline runs the same checks in the same order every time. Nobody can skip a step because they are in a hurry. This is a documented control based on organizational priorities (NIST AI RMF GOVERN 1.4), and it decides each time whether a deployment may proceed (MANAGE 1.1).[^nist-ai-rmf]

Google says that a rapid and reliable update of pipelines in production needs a robust automated CI/CD system. That system automatically builds, tests and deploys the new pipeline components to the target environment.[^google-mlops]

A CI/CD pipeline is a kitchen conveyor belt. Each dish goes past the same stations in the same order. If one station rejects the dish, the belt stops and the dish never reaches the table.

# Examples

The lab workflow `.github/workflows/release.yml`:

- Triggers: a push that changes `exercises/quality-gates/**`, and `workflow_dispatch` with an input `candidate` (a candidate file to try). A `workflow_dispatch` trigger takes optional inputs, and it works only when the workflow file is on the default branch.[^gh-workflow-syntax] That is why trainees make `04-quality-gates` the default branch of their fork.
- Job `gates`: install packages, validate data, train candidate, run `pytest ... --junitxml=gate_report.xml`. pytest can write JUnit XML files that Jenkins and other CI servers read.[^pytest-output] The job writes the gate table to the run page.
- Job `promote`: `needs: gates`. If a job fails or is skipped, all jobs that need it are skipped.[^gh-workflow-syntax] It uses `environment: production`, so it waits for a [deployment approval](/knowledge/mlops/deployment-approval.md).

Real runs on `majlisofai/mlops-training`:

- Push run 43871972909: `gates` passed (accuracy 0.842, ROC AUC 0.907, 4 passed, 3 skipped, because the upstream branch still has the TODOs), and `promote` made version 1 `@champion`.
- Dispatch run 43872014499 with `weak.yaml`: step "3. Quality gates" failed with `accuracy 0.806 is below 0.82` and `roc_auc 0.876 is below 0.88`. The job `promote` was skipped.

Each CI run uses its own MLflow store, `sqlite:///mlflow.db`, so the CI version number is always 1. The store travels from `gates` to `promote` as the workflow artifact `registry`.

# Common mistakes

- Testing only the code. An ML pipeline must also test the data and the model.
- Letting the pipeline continue after a failed step. Each step must stop the pipeline when it fails (see [fail-fast pipeline](/knowledge/mlops/fail-fast-pipeline.md)).
- Running different steps locally and in CI. The lab's `run_pipeline.sh` and `release.yml` run the same four steps.
- Expecting a new fork to run workflows at once. GitHub disables workflows in a new fork until the owner enables them in the Actions tab.
- Thinking that a green pipeline proves a good model. The upstream push run was green with three gates not checked.

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", sections "CI/CD pipeline automation" and "MLOps level 2".
[^gh-understand]: GitHub Docs, "Understanding GitHub Actions".
[^gh-workflow-syntax]: GitHub Docs, "Workflow syntax for GitHub Actions", sections `on.workflow_dispatch` and `jobs.<job_id>.needs`.
[^jenkins-pipeline]: Jenkins User Handbook, "Pipeline".
[^pytest-output]: pytest documentation, "Managing pytest's output", section on JUnit XML.
[^nist-ai-rmf]: NIST AI 100-1, Table 1 (GOVERN 1.4) and Table 4 (MANAGE 1.1).
[^lab04]: Lesson 04 README, sections "The pipeline" and steps 5 to 7.
