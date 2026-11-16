---
type: Domain Concept
title: Retraining strategy
description: "Choosing how to respond when a model gets worse: roll back, recalibrate, retrain on a time-aware window, or wait for final labels."
tags: [mlops, retraining, model-maintenance, drift, calibration]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 2.2", "NIST-AI-RMF:MANAGE 2.4", "NIST-AI-RMF:MANAGE 4.2"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T23:10:00+03:00 }
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
  - id: sklearn-calibration
    resource: https://scikit-learn.org/stable/modules/calibration.html
    title: Probability calibration
    author: team:scikit-learn
  - id: sre-incidents
    resource: https://sre.google/sre-book/managing-incidents/
    title: "Site Reliability Engineering, chapter 14: Managing incidents"
    author: org:google-sre
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab07
    resource: https://github.com/majlisofai/mlops-training/blob/07-recovery/exercises/recovery/README.md
    title: "Lesson 07: recover the service and train a controlled challenger"
    author: org:majlisofai
---

# Definition

A retraining strategy says what you do when a model gets worse, and when. Lab 07 compares four options:[^lab07]

| Option | What it changes | Choose it when |
|---|---|---|
| **Roll back** | Which version serves: one alias | A release broke the service or its answers |
| **Recalibrate** | The probabilities, not the order of the cases | People use the probabilities and they are off |
| **Retrain a challenger** | What the model learned | The inputs are valid, the world changed, and accuracy on final labels fell over several races |
| **Wait for labels** | Nothing, yet | The drop is in one or two races, or only on provisional labels |

A retrain also needs a **training window**: which past data the new model learns from. A time-aware window uses only data from before the period you test on, and keeps the data that still describes the world.

# Why it matters

None of the options is free, and the fastest one does not fix the cause.[^lab07]

- **Roll back** stops the harm fast. The SRE book's first priority in an incident is to stop the bleeding and restore service.[^sre-incidents] But you go back to the previous model, with its weaknesses. See [model rollback](/knowledge/mlops/model-rollback.md).
- **Recalibrate** fixes probabilities. A well calibrated classifier gives about 80 % positives among the cases it scores near 0.8. The sigmoid (Platt) method is strictly monotonic, so it keeps the ranking and the ROC AUC.[^sklearn-calibration] Fit the calibrator on data that the model did not train on.[^sklearn-calibration]
- **Retrain** updates what the model learned. Google's MLOps guide lists triggers for a retraining pipeline: on demand, on a schedule, on new training data, on performance degradation, and on significant changes in the data distributions (concept drift).[^google-mlops]
- **Wait** costs time. With few labels, a drop can be noise.

Gama and colleagues call periodic retraining with a fixed window "blind" adaptation. It reacts slowly to drift and forgets old data at a constant speed. "Informed" adaptation acts when a trigger, such as a change detector, fires.[^gama-survey] The window size is a trade-off: a short window follows the current world and adapts fast, but in stable times it is too small. A large window is better in stable times but reacts slowly to change.[^gama-survey] Instead of cutting old data, you can give recent rows more weight.[^gama-survey]

The NIST AI RMF asks for mechanisms that sustain the value of deployed AI systems (MANAGE 2.2), and for mechanisms and assigned responsibilities to supersede, disengage or deactivate systems that perform inconsistently with their intended use (MANAGE 2.4). It asks that measurable activities for continual improvement are part of system updates (MANAGE 4.2).[^nist-ai-rmf]

Kid version: when the dish goes wrong, the restaurant can put back yesterday's recipe, add a pinch of salt, learn a new recipe from this season's customers, or wait for more customers before changing anything. Each one helps in a different situation.

# Examples

Lab 07 uses two options in a row. First a **rollback** stops the outage: the crash-looping API came back in 27 seconds, to a model that gets 0.706 of the 2026 entries right. Then a **challenger** deals with the slow decline.[^lab07]

**Recalibrate.** In rounds 5 to 8 the champion predicts points for 0.61 of the entries, and 0.50 scored. Recalibration would fix that share, but it barely changes which cars are predicted to score, and with few labels the calibration itself is noisy.[^lab07]

**Time-aware windows.** All candidates trained only on races before the test window (2026 rounds 5 to 8, 80 entries). Measured against the champion:[^lab07]

| Window | Accuracy on rounds 5-8 | Comparison result |
|---|---:|---|
| Champion: 2021-2024 | 0.688 | (reference) |
| 2023-2025 + 2026 rounds 1-4 | 0.738 | PROMOTE: +0.050, exactly the margin |
| 2021-2025 + 2026 rounds 1-4 | 0.713 | blocked on GitHub Actions: +0.025 is below the margin |
| 2023-2025 + rounds 1-4, 2026 weighted 5x | 0.750 vs the new champion's 0.738 | blocked: ROC AUC falls by 0.044 |
| 2023-2025 + all eight 2026 rounds | 0.800 | blocked: it trained on the test races |

Before the test window, the lab also checked each history window on rounds 2, 3 and 4, one race at a time: 2021-2025 got 0.683 right, the last three seasons 0.667. The earlier races did not favour the recent window. The choice of window is a judgement, not a sure thing.[^lab07]

**Wait for labels.** Final labels arrive 2 to 26 hours after a race. 6 of the 160 provisional 2026 labels changed. The challenger trains and is judged on final labels only.[^lab07]

# Common mistakes

- Retraining during an outage. You ship a second untested model. Roll back first, then retrain with time.[^lab07]
- Rolling back a model that is out of date. The previous model learned the same old world.
- Retraining on broken inputs. If a feed changed its units, fix the input, not the model.[^lab07]
- Using all history by default. Old seasons can teach the old pecking order.
- Using the test period in training. A window must end before the test window starts.
- Retraining on a schedule only. A blind schedule reacts slowly when the world changes fast.[^gama-survey]
- Recalibrating to fix ranking. Calibration changes the probabilities, not the order of the cases.[^sklearn-calibration]
- Waiting without a date. Tell the users how good the model is now, and when you look again.[^lab07]

See also [concept drift](/knowledge/mlops/concept-drift.md), [challenger model](/knowledge/mlops/challenger-model.md), [delayed labels](/knowledge/mlops/delayed-labels.md) and [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).

[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "ML pipeline triggers".
[^gama-survey]: Gama et al. (2014), sections 3.1.1 (windows, the window size trade-off), 3.1.2 (gradual forgetting with example weights) and 3.3.2 (blind and informed adaptation).
[^sklearn-calibration]: scikit-learn, "Probability calibration", introduction, "Fitting a calibrator", and the note on ROC AUC and `method="sigmoid"`.
[^sre-incidents]: Google SRE book, chapter 14, "Best Practices for Incident Management": "Prioritize".
[^nist-ai-rmf]: NIST AI 100-1, Table 4 (MANAGE 2.2, MANAGE 2.4, MANAGE 4.2).
[^lab07]: Lesson 07 README, steps 6 to 9, "Trade-offs: what to do when the model gets worse", and the runbook decision table.
