---
type: Domain Concept
title: Monitoring alert
description: A production check compares a measurement with a written threshold, reports pass or alert with a reason, and fails the job on an alert.
tags: [mlops, monitoring, alerting, thresholds, github-actions]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.4", "NIST-AI-RMF:MANAGE 4.1", "NIST-AI-RMF:MANAGE 4.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:40:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: breck-2019
    resource: https://mlsys.org/Conferences/2019/doc/2019/167.pdf
    title: Data validation for machine learning (MLSys 2019)
    author: Eric Breck, Neoklis Polyzotis, Sudip Roy, Steven Euijong Whang, Martin Zinkevich
  - id: rules-of-ml
    resource: https://developers.google.com/machine-learning/guides/rules-of-ml
    title: "Rules of Machine Learning: Best practices for ML engineering"
    author: org:google
  - id: evidently-monitoring
    resource: https://www.evidentlyai.com/ml-in-production/model-monitoring
    title: "Model monitoring for ML in production: a comprehensive guide"
    author: org:evidently-ai
  - id: gh-exit-codes
    resource: https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes
    title: Setting exit codes for actions
    author: org:github
  - id: gh-events
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
    title: Events that trigger workflows
    author: org:github
  - id: gh-notifications
    resource: https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs
    title: Notifications for workflow runs
    author: org:github
  - id: gh-workflow-commands
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
    title: Workflow commands for GitHub Actions
    author: org:github
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab06
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/exercises/monitoring/README.md
    title: "Lesson 06: monitor drift, skew and delayed labels"
    author: org:majlisofai
  - id: lab06-config
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/exercises/monitoring/monitoring.yaml
    title: "exercises/monitoring/monitoring.yaml: the thresholds of the monitor"
    author: org:majlisofai
  - id: lab06-workflow
    resource: https://github.com/majlisofai/mlops-training/blob/06-monitoring/.github/workflows/monitor.yml
    title: ".github/workflows/monitor.yml: the monitor on GitHub Actions"
    author: org:majlisofai
  - id: run-ok
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43896441266
    title: "GitHub Actions run 43896441266: monitor, reference, MONITOR OK"
    author: org:majlisofai
  - id: run-alert
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43896456941
    title: "GitHub Actions run 43896456941: monitor, wet_race, MONITOR ALERT: input drift"
    author: org:majlisofai
---

# Definition

A monitoring alert is the output of a check on production data that crossed a threshold. Each check measures one thing, compares it with a written threshold, and returns pass or alert with a one-line reason. The monitor exits with a non-zero code when any check alerts, so a scheduler or a pipeline can fail the job and tell a person.

In lab 06 every check returns a status (`pass`, `alert`, `skip` or `todo`), a reason, details and the measured numbers. The thresholds live in `monitoring.yaml`, next to the measurement behind each number. The monitor exits 0 when there is no alert and 1 when there is one.[^lab06] [^lab06-config]

# Why it matters

A threshold is a trade-off. Too tight, and the monitor raises false alarms until people ignore it. Too loose, and it misses real problems.[^lab06] The TFX paper says that on-call engineers tend to ignore alerts that are spammy or not actionable, so important errors go unnoticed. Alerts need high precision and enough context to find the root cause.[^breck-2019] Rules of ML ask for alerts that are actionable.[^rules-of-ml] Evidently suggests alerting on a small number of key metrics.[^evidently-monitoring]

The exit code connects the monitor to the rest of the [CI/CD pipeline](/knowledge/mlops/ci-cd-pipeline.md). On GitHub Actions, exit code 0 means success and any other code means failure.[^gh-exit-codes] The person who triggers a run gets a notification when it finishes, if notifications are on.[^gh-notifications] For a schedule, the notification goes to the person who created the workflow or last changed its cron line.[^gh-notifications] [^gh-events]

The NIST AI RMF asks that the system is monitored in production (MEASURE 2.4), that post-deployment monitoring plans include incident response (MANAGE 4.1), and that incidents and errors are communicated to the relevant AI actors (MANAGE 4.3).[^nist-ai-rmf] An alert is where monitoring hands over to [incident triage](/knowledge/mlops/incident-triage.md).

A good smoke alarm rings when the kitchen is on fire, not every time someone makes toast. You test it on toast first, then on smoke, and you set it between the two.

# Examples

Every lab threshold comes from windows that were measured as normal and windows with a known problem:[^lab06]

| Threshold | Value | Normal windows | Problem windows |
|---|---:|---|---|
| Rejected entries | 1 % | 0 % | 100 % (new feed), 25 % (renamed category) |
| Mean shift | 2.0 sd | at most 1.03 sd | 10.41 sd (storm) |
| Spread ratio | x0.5 to x2.0 | x0.76 to x1.27 | x0.0011 (seconds), x0 (stuck feature) |
| Skewed values per feature | 5 % | 0 % | 25 % to 98 % |
| Accuracy drop below 0.842 | 0.05 | | 0.136 (2026: 0.706) |
| Final label coverage | 90 % | 100 % | 38 % (label delay), 0 % (provisional only) |

- The mean-shift threshold of 2.0 sd is twice the largest normal move (1.03 sd) and five times smaller than the storm (10.41 sd).[^lab06]
- **A stricter threshold has a cost.** At 1.0 sd the monitor alerts on 2026 (`team_dnf_rate`, shift 1.03 sd), days before the labels arrive. It also alerts on four ordinary 2025 races (`rain_prob`, shift 1.03 sd).[^lab06]
- **First test: no alert on normal data.** The reference window against itself gives `shift 0.00 sd` for every feature and `MONITOR OK: no alerts`, exit code 0.[^lab06]
- **A check that checks nothing says so.** While a TODO is not written, the monitor prints `WARNING: 3 checks are not written yet and checked nothing`. A monitor that says OK because nothing was checked makes people trust it.[^lab06]
- **On GitHub Actions.** The workflow runs on a push, on demand, and every day at 05:23 UTC on the reference window, to prove that the chain itself still works.[^lab06-workflow] Scheduled workflows run on the latest commit on the default branch.[^gh-events] The monitor writes its table to `GITHUB_STEP_SUMMARY`, which GitHub shows on the run summary page.[^gh-workflow-commands]
- Run 43896441266 (reference) ends with `MONITOR OK: no alerts` and succeeds.[^run-ok] Run 43896456941 (wet race) ends with `MONITOR ALERT: input drift`, `Process completed with exit code 1`, and the job fails.[^run-alert]

# Common mistakes

- Choosing a threshold from a guess, or from a single window. Measure normal windows and problem windows, then write both next to the number.
- Changing a threshold to silence an alert without asking what it costs. Write down the trade-off, so the next person knows.
- An alert with no reason. "Input drift" alone sends people searching. `rain_prob: shift 10.41 sd (max 2.0)` tells them where to look.
- Exiting 0 on an alert. Then the pipeline stays green and nobody is told.
- Sending every alert to one team. Service health belongs to the team that runs the API, skew to the owners of the feeds, accuracy to the owners of the model.
- Never testing the monitor itself. Inject known faults, as in the Drift Detective, and check that each one alerts.

[^breck-2019]: E. Breck et al., "Data validation for machine learning", MLSys 2019, section 1 (Introduction).
[^rules-of-ml]: Google, "Rules of Machine Learning", section "Monitoring": "practice good alerting hygiene, such as making alerts actionable".
[^evidently-monitoring]: Evidently AI, "Model monitoring for ML in production: a comprehensive guide", section on alerting.
[^gh-exit-codes]: GitHub Docs, "Setting exit codes for actions".
[^gh-events]: GitHub Docs, "Events that trigger workflows", section `schedule`.
[^gh-notifications]: GitHub Docs, "Notifications for workflow runs".
[^gh-workflow-commands]: GitHub Docs, "Workflow commands for GitHub Actions", section "Adding a job summary".
[^nist-ai-rmf]: NIST AI 100-1, AI RMF 1.0, Table 3 (MEASURE 2.4) and Table 4 (MANAGE 4.1, MANAGE 4.3).
[^lab06]: Lesson 06 README, steps 5, 9 and 11, branch `06-monitoring`.
[^lab06-config]: `exercises/monitoring/monitoring.yaml`, branch `06-monitoring`.
[^lab06-workflow]: `.github/workflows/monitor.yml`, triggers `push`, `workflow_dispatch` and `schedule`.
[^run-ok]: GitHub Actions run 43896441266 (`workflow_dispatch`, scenario `reference`), step "4. Run the monitor".
[^run-alert]: GitHub Actions run 43896456941 (`workflow_dispatch`, scenario `wet_race`), step "4. Run the monitor".
