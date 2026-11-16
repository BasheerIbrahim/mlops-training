---
type: Domain Concept
title: Challenger model
description: A new model that must beat the current champion on the same held-out data, by a set margin, before a person may promote it.
tags: [mlops, model-evaluation, champion-challenger, release, uncertainty]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 1.1", "NIST-AI-RMF:MEASURE 2.3", "NIST-AI-RMF:MEASURE 2.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T23:00:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: gama-survey
    resource: https://doi.org/10.1145/2523813
    title: "A survey on concept drift adaptation, ACM Computing Surveys 46(4), article 44, 2014 (accepted manuscript read at https://repositorio.inesctec.pt/server/api/core/bitstreams/7f101638-0b33-4863-9dd2-cf991f192c9f/content)"
    author: João Gama, Indrė Žliobaitė, Albert Bifet, Mykola Pechenizkiy and Abdelhamid Bouchachia
  - id: scipy-bootstrap
    resource: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
    title: scipy.stats.bootstrap
    author: team:scipy
  - id: sklearn-cv
    resource: https://scikit-learn.org/stable/modules/cross_validation.html
    title: "Cross-validation: evaluating estimator performance"
    author: team:scikit-learn
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab07
    resource: https://github.com/majlisofai/mlops-training/blob/07-recovery/exercises/recovery/README.md
    title: "Lesson 07: recover the service and train a controlled challenger"
    author: org:majlisofai
  - id: ci-win
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43899818497
    title: "GitHub Actions run 43899818497: challenger, push (challenger wins)"
    author: org:majlisofai
  - id: ci-blocked
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43900063755
    title: "GitHub Actions run 43900063755: challenger, workflow_dispatch with all_history.yaml (blocked)"
    author: org:majlisofai
---

# Definition

A challenger is a model that competes with the champion, the model in production, on the same evidence before it may replace it.[^lab07] Google's MLOps guide describes this step as offline model validation: compare the metrics of the newly trained model with the current model, and make sure the new model performs better before you promote it to production.[^google-mlops]

A fair comparison has four parts:

1. **The same held-out data** for both models, from a period that neither model trained on. See [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).
2. **A margin** that the challenger must beat, chosen before you look. A gain smaller than the noise of the test set is not a win.
3. **Guard rules**: the challenger may not get much worse on other measures or on [subgroups](/knowledge/mlops/subgroup-evaluation.md).
4. **An honest statement of uncertainty**: how sure can you be, with this many test rows?

A **controlled** challenger changes one thing and keeps the rest. Then a difference in the result comes from that one change.[^lab07]

# Why it matters

A retrained model is not better because it is newer. Only a comparison on the same unseen rows shows it.

A small test set gives a noisy score. Gama and colleagues note that confidence intervals matter most when the sample is small. To compare two classifiers they name the McNemar test, which counts the rows that one model gets right and the other gets wrong.[^gama-survey] A bootstrap gives a similar view: it resamples the test rows many times. With paired resampling, both models are scored on the same resampled rows.[^scipy-bootstrap]

Each extra proposal that you try on the same test rows is another chance to win by luck. When you tune to the test score, knowledge of the test set leaks into the model, and the score no longer measures generalisation.[^sklearn-cv]

The NIST AI RMF asks for a determination of whether the system achieves its objectives and whether its deployment should proceed (MANAGE 1.1). It asks that performance is measured for conditions similar to deployment (MEASURE 2.3), and that test sets and metrics are documented (MEASURE 2.1).[^nist-ai-rmf]

Kid version: a race engineer says a new setup is faster than the race setup. Both setups run in practice on the same laps, on the same day, in the same conditions. The new setup must win clearly, not by a whisker, and the team principal still decides.

# Examples

In lab 07 the challenger keeps the champion's forest (300 trees, depth 8, seed 42) and changes only the training data: 2023-2025 plus 2026 rounds 1 to 4 with final labels (1,520 entries). Both models are tested on 2026 rounds 5 to 8 (80 entries), which neither saw.[^lab07]

| Measure | Champion v1 | Challenger | Rule |
|---|---:|---:|---|
| Accuracy | 0.688 | 0.738 (+0.050) | gain at least +0.050 |
| ROC AUC | 0.763 | 0.756 (-0.008) | drop at most 0.02 |
| Margin over the grid rule (0.675) | 0.012 | 0.062 | at least 0.02 |
| Accuracy, top teams (24) | 0.583 | 0.750 (+0.167) | drop at most 0.10 |

All nine challenger gates pass, and `compare.py` says `PROMOTE`.[^lab07] Read it honestly:

- The gain is exactly the margin: 4 more right calls in 80.
- The 90 % bootstrap interval of the gain is [-0.025, +0.125]. It includes zero.
- The challenger wins three races and loses one (2026-08: 0.65 against 0.75).
- The rookie group has 8 entries. Both models got all 8 right. That says almost nothing.

So the rules say promote, and the evidence says "probably not worse, perhaps better, from four races". A person decides. The lab promotes through the [quality gate](/knowledge/mlops/quality-gate.md) report and `promote.py`, with a named approver, and writes down when to look again: after rounds 9 to 12 have final labels.[^lab07]

Other proposals, compared with the new champion:[^lab07]

| Proposal | Result | Blocked by |
|---|---|---|
| All history 2021-2025 + rounds 1-4 | accuracy 0.713 (-0.025) | `accuracy_gain`, top teams fall by 0.125 |
| Each 2026 entry weighted 5x | accuracy 0.750 (+0.012), ROC AUC 0.712 (-0.044) | `accuracy_gain`, `roc_auc_not_worse` |
| Trained on all eight 2026 races | accuracy 0.800 (+0.062), ROC AUC 0.901 | `time_split`: it saw the test races |

On GitHub Actions, the workflow `challenger` builds the champion, trains the challenger and compares them in one job. Run 43899818497 shows the same 0.688 against 0.738 and `PROMOTE`.[^ci-win] Run 43900063755, with the all-history proposal against version 1, shows a gain of +0.025 (interval [+0.000, +0.050]) and fails step 3: `KEEP the champion`.[^ci-blocked] The workflow never promotes; promotion stays in the gated path with an approval.

# Common mistakes

- Comparing on different data. The champion's old 2025 score and the challenger's 2026 score cannot be compared.
- Testing the challenger on rows it trained on. The "peek" proposal is the best model on paper because it saw the answers.
- A margin chosen after you see the result.
- Reading `PROMOTE` as proof. Report the interval. A gain whose interval includes zero is a close call.
- Trying many proposals on one small test window and keeping the winner. Write the proposal down first, then measure it once.
- Changing many things at once. Then you cannot say which change made the difference.
- Letting the comparison promote by itself. The comparison recommends; the gates and a person decide. See [deployment approval](/knowledge/mlops/deployment-approval.md).
- Trusting monitoring numbers after a retrain. Version 3 shows 0.885 on 2025 and 0.738 on 2026, but it trained on 2025 and on rounds 1 to 4. Only the test window is fair.[^lab07]

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", the "Offline model validation" step under "Model validation".
[^gama-survey]: Gama et al. (2014), section 4.2.3 "Statistical significance".
[^scipy-bootstrap]: SciPy documentation, `scipy.stats.bootstrap`, parameters `paired` and `method`.
[^sklearn-cv]: scikit-learn, "Cross-validation: evaluating estimator performance", introduction.
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1, MEASURE 2.3) and Table 4 (MANAGE 1.1).
[^lab07]: Lesson 07 README, steps 7 to 9.
[^ci-win]: GitHub Actions log of run 43899818497, step "3. Compare champion and challenger".
[^ci-blocked]: GitHub Actions log of run 43900063755, step "3. Compare champion and challenger".
