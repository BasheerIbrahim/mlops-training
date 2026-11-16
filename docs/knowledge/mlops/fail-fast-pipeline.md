---
type: Domain Concept
title: Fail-fast pipeline
description: A pipeline whose steps stop at once, with a non-zero exit code, when a check fails, so bad data never reaches training or release.
tags: [mlops, pipeline, fail-fast, exit-code, data-validation, ci-cd]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 2.3", "ISO-42001:A.6.2.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:55:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: shore-failfast
    resource: https://martinfowler.com/ieeeSoftware/failFast.pdf
    title: Fail Fast (IEEE Software, 2004)
    author: Jim Shore
  - id: bash-exit
    resource: https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html
    title: Bash Reference Manual, Exit Status
    author: org:gnu
  - id: bash-pipelines
    resource: https://www.gnu.org/software/bash/manual/html_node/Pipelines.html
    title: Bash Reference Manual, Pipelines
    author: org:gnu
  - id: gh-exit-codes
    resource: https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes
    title: Setting exit codes for actions
    author: org:github
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: iso-42001
    resource: https://www.iso.org/standard/42001
    title: "ISO/IEC 42001:2023 Information technology — Artificial intelligence — Management system"
    author: org:iso
  - id: advisera-42001
    resource: https://advisera.com/articles/iso-42001-mandatory-documents/
    title: List of ISO 42001 mandatory documents (Annex A control list)
    author: org:advisera
  - id: lab02
    resource: https://github.com/majlisofai/mlops-training/blob/02-mlflow/exercises/mlflow/README.md
    title: "Exercise: track data versions and data checks in MLflow"
    author: org:majlisofai
  - id: lab02-solution
    resource: https://github.com/majlisofai/mlops-training/blob/02-mlflow/exercises/mlflow/solution/log_data_checks.py
    title: Lab 02 reference solution, log_data_checks.py
    author: org:majlisofai
---

# Definition

A system that fails fast stops immediately and visibly when a problem occurs. A system that "fails slowly" keeps working after an error and fails in strange ways later.[^shore-failfast]

A fail-fast pipeline applies this idea to ML steps. Each step checks its input. When a check fails, the step exits with a non-zero exit code. In the shell, exit status zero means success, and any non-zero status means failure.[^bash-exit] The pipeline runner reads the code and does not run the next steps. For example, in GitHub Actions a non-zero exit code gives the check run a `failure` status, and later actions are skipped.[^gh-exit-codes]

# Why it matters

Bad data that passes one step quietly can train a bad model, pass a weak test and reach users. Each later step makes the cause harder to find. Failing at once makes the bug easier to find and fix.[^shore-failfast] Google's MLOps guide says that when input data does not match the expected schema, you should stop the pipeline so that the data science team can investigate.[^google-mlops]

NIST AI RMF MANAGE 2.3 asks that procedures are followed to respond to and recover from a previously unknown risk.[^nist-ai-rmf] ISO/IEC 42001 control A.6.2.4 covers verification and validation measures for an AI system.[^iso-42001][^advisera-42001] A step that stops on a failed check, and a known way to roll back, put both into practice.

Think of milk that smells bad. You stop before you bake the cake, not after your friends have eaten it.

# Examples

- `log_data_checks.py` ends with `sys.exit(0 if status == "passed" else 1)`. The comment says: "A non-zero exit lets a pipeline stop on bad data."[^lab02-solution]
- On the original data (md5 `199d7bda…`), the script prints `validation passed (0 failed checks, 0 failure cases)` and `echo $?` shows `0`.[^lab02]
- After the timing feed sends `quali_gap_ms` in seconds (md5 `7fec7961…`), the script prints `validation failed (1 failed checks, 1 failure cases)` and exits with `1`.[^lab02]
- The script logs the failed run to MLflow before it exits. So the pipeline stops, and the evidence stays in the [MLflow run](/knowledge/mlops/mlflow-run.md).[^lab02-solution]
- The fix is a rollback with DVC, not a code change. The next run passes on md5 `199d7bda…` again.[^lab02]
- In lab 04, the [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md) runs validate data, train candidate and the [quality gates](/knowledge/mlops/quality-gate.md) in order on GitHub Actions. A step that fails stops the steps after it.[^gh-exit-codes]

# Common mistakes

- Printing "validation failed" but exiting with `0`. The pipeline reads only the exit code, so it carries on.
- Catching the validation error and continuing "to see what happens". That is failing slowly.[^shore-failfast]
- Stopping without a record. Log the failure report first, then exit, so people can see which check failed.
- Piping the output, for example `python check.py | tee log.txt`. The exit status of a pipeline is the status of its last command, here `tee`, not the check. Use `set -o pipefail`.[^bash-pipelines]
- Treating every warning as a stop. Stop on checks that protect the model. Report the rest. Decide which is which in the [release criteria](/knowledge/mlops/release-criteria.md).

[^shore-failfast]: Jim Shore, "Fail Fast", IEEE Software, 2004, section "Immediate and visible failure".
[^bash-exit]: GNU Bash Reference Manual, "Exit Status".
[^bash-pipelines]: GNU Bash Reference Manual, "Pipelines", on the exit status of a pipeline and the `pipefail` option.
[^gh-exit-codes]: GitHub Docs, "Setting exit codes for actions".
[^google-mlops]: Google Cloud Architecture Center, "MLOps: Continuous delivery and automation pipelines in machine learning", section on data validation.
[^nist-ai-rmf]: NIST AI 100-1, Table 4 (MANAGE 2.3).
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.6.2.4.
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.6.2.4 (AI system verification and validation measures).
[^lab02]: Lab 02 exercise README, steps 3, 5 and 6.
[^lab02-solution]: Lab 02 reference solution, function `main()`.
