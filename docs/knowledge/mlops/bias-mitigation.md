---
type: Domain Concept
title: Bias mitigation
description: Changes to the data, the training or the decision threshold that reduce a fairness gap; each has a cost and must be valid and allowed.
tags: [fairness, mitigation, reweighting, thresholds, trade-offs]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MANAGE 1.3", "NIST-AI-RMF:MEASURE 2.11"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:40:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: fairlearn-mitigation
    resource: https://fairlearn.org/main/user_guide/mitigation/index.html
    title: "Fairlearn user guide: Mitigations"
    author: team:fairlearn
  - id: fairlearn-postprocessing
    resource: https://fairlearn.org/main/user_guide/mitigation/postprocessing.html
    title: "Fairlearn user guide: Postprocessing (ThresholdOptimizer)"
    author: team:fairlearn
  - id: aif360-reweighing
    resource: https://aif360.readthedocs.io/en/stable/modules/generated/aif360.algorithms.preprocessing.Reweighing.html
    title: "AI Fairness 360: aif360.algorithms.preprocessing.Reweighing"
    author: team:aif360
  - id: google-mlcc-mitigating
    resource: https://developers.google.com/machine-learning/crash-course/fairness/mitigating-bias
    title: "Fairness: Mitigating bias"
    author: team:google
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: sdaia-ethics
    resource: https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf
    title: AI Ethics Principles, version 1, May 2025 (document SDAIA-P114E)
    author: org:sdaia
  - id: lab08
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/README.md
    title: "Lesson 08: fairness, transparency and the model card"
    author: org:majlisofai
  - id: lab08-mitigate
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/mitigate.py
    title: "Lesson 08: mitigation test (mitigate.py)"
    author: org:majlisofai
---

# Definition

Bias mitigation is any change that aims to reduce a gap in a [fairness metric](/knowledge/mlops/fairness-metrics.md). The change can act at three points:

- **Before training (pre-processing)**: change the data. Reweighing gives the examples in each (group, label) combination a different weight before training.[^aif360-reweighing] Collecting more data for the group is often the most direct fix, but it can be infeasible.[^google-mlcc-mitigating]
- **During training (in-processing)**: change what the model optimises, for example with a loss that penalises differences between groups.[^google-mlcc-mitigating] Fairlearn's reductions wrap a normal classifier to do this.[^fairlearn-mitigation]
- **After training (post-processing)**: change the decision. Fairlearn's `ThresholdOptimizer` sets a separate threshold for each group. It needs the group at prediction time.[^fairlearn-postprocessing]

Choosing a different model is also a mitigation, and often the cheapest one.

# Why it matters

A fairness gate that fails asks for a response. NIST asks that responses to high-priority AI risks are developed, planned and documented; the options include mitigating, transferring, avoiding or accepting the risk (MANAGE 1.3).[^nist-ai-rmf]

Every fix has a cost, and a fix is not proof of fairness. NIST says that systems in which harmful biases are mitigated are not necessarily fair.[^nist-ai-rmf] Fairlearn says that its algorithms can drive an unfairness metric close to zero, but that this does not mean the results are fair.[^fairlearn-mitigation]

Some fixes are not allowed. A per-group threshold treats two cases with the same inputs differently because of their group. Fairlearn notes that one might argue this is disparate treatment under US law or direct discrimination under EU law, where those laws apply.[^fairlearn-postprocessing] SDAIA asks that sensitive attributes are not used as model data, or that their use is justified.[^sdaia-ethics] The course gives no legal advice: ask your legal and compliance team.

Kid version: to help the new cooks, you can make the critic practise on their dishes ten times as often. The critic gets fairer to them but a little worse overall. Or you can set a higher bar for new cooks only. But that bar was chosen by peeking at the final judging, and the critic must know who cooked each dish.

# Examples

`mitigate.py` retrains the champion forest and tries two mitigations. It logs eight runs to the MLflow experiment `f1-points-finish-fairness`. Limits: FPR gap ≤ 0.55, FNR gap ≤ 0.10.[^lab08-mitigate][^lab08]

| Run | Accuracy | Rookie accuracy | FPR gap | FNR gap | Lab 04 | Fairness | Works on API v1 |
|---|---:|---:|---:|---:|---|---|---|
| baseline | 0.842 | 0.646 | +0.620 | −0.094 | pass | FAIL | yes |
| reweight-x2 | 0.840 | 0.667 | +0.616 | −0.136 | pass | FAIL | yes |
| reweight-x5 | 0.838 | 0.688 | +0.573 | −0.150 | pass | FAIL | yes |
| reweight-x10 | 0.825 | 0.625 | +0.473 | +0.026 | pass | pass | yes |
| rookie-threshold-0.6 | 0.846 | 0.688 | +0.477 | −0.057 | pass | pass | no |
| rookie-threshold-0.7 | 0.838 | 0.604 | +0.335 | +0.202 | pass | FAIL | no |
| rookie-threshold-0.8 | 0.829 | 0.521 | +0.097 | +0.535 | FAIL | FAIL | no |
| past-rookies-0.3 | 0.835 | 0.583 | +0.811 | −0.131 | FAIL | FAIL | no |

- **Sample weighting** (`reweight-xW`: rookie rows count W times) barely helps until W = 10. Then the gap passes, accuracy drops by 0.017 (0.842 to 0.825), and the FNR gap turns positive. `rookie` is used only in training, so the API does not change.
- **A per-group threshold trades one error for the other.** A higher rookie threshold cuts false positives and adds false negatives. At 0.8, rookie accuracy is 0.521, as bad as the grid rule.
- **`rookie-threshold-0.6` looks perfect and is not valid.** 0.6 was picked by looking at the 2025 holdout: that is tuning on the test set. Picked honestly on 2021 to 2024 (`past-rookies`), the threshold is 0.3 and the gap gets worse (+0.811). It also needs `rookie` at prediction time, which API v1 does not accept, and `fairness.yaml` lists `rookie` as reporting-only.
- **A different model** was the cheapest fix: the logistic regression passes the lab 04 gates and the fairness gates (FPR gap +0.487) with accuracy 0.835. See [fairness gate](/knowledge/mlops/fairness-gate.md).

# Common mistakes

- Choosing the mitigation on the holdout. A threshold or weight tuned on the test season is [data leakage](/knowledge/mlops/data-leakage.md) in another form. Tune on earlier seasons only, as in a [temporal holdout split](/knowledge/mlops/temporal-holdout-split.md).
- Watching one gap only. Fixing the FPR gap can break the FNR gap (`rookie-threshold-0.7`).
- Forgetting the cost. Report accuracy and the lab 04 gates next to the fairness gap for every variant.
- Adding the group as a model input or a decision rule without a decision. For a protected characteristic this can be direct differential treatment. It is a decision for the model owner and the approver, written in the [model card](/knowledge/mlops/model-card.md), not a code change.
- Calling a mitigated model "fair". It passes a gate on a metric. Say which metric, on which data, and how sure you are.

[^fairlearn-mitigation]: Fairlearn user guide, "Mitigations", introduction and the list of algorithms.
[^fairlearn-postprocessing]: Fairlearn user guide, "Postprocessing", `ThresholdOptimizer`.
[^aif360-reweighing]: AI Fairness 360 documentation, `Reweighing`, after F. Kamiran and T. Calders, "Data Preprocessing Techniques for Classification without Discrimination", Knowledge and Information Systems, 2012.
[^google-mlcc-mitigating]: Google Machine Learning Crash Course, "Fairness: Mitigating bias".
[^nist-ai-rmf]: NIST AI 100-1, section 3.7 "Fair – with Harmful Bias Managed" and Table 4 (MANAGE 1.3).
[^sdaia-ethics]: SDAIA, AI Ethics Principles (2025), Principle 1 Fairness, Prepare Input Data, item 2 (p. 14, printed page number). The sdaia.gov.sa server refused automated download on 2026-11-16; the text was checked against a saved copy of document SDAIA-P114E, version 1.
[^lab08]: Lesson 08 README, steps 6 and 7.
[^lab08-mitigate]: Lesson 08 `mitigate.py`.
