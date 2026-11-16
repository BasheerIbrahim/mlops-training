---
type: Domain Concept
title: Fairness metrics
description: Group metrics such as selection rate and false positive and false negative rates, compared as gaps or ratios, with their uncertainty for small groups.
tags: [fairness, model-evaluation, subgroups, fairlearn, metrics]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.11", "NIST-AI-RMF:MEASURE 1.1"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:20:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: fairlearn-assessment
    resource: https://fairlearn.org/main/user_guide/assessment/perform_fairness_assessment.html
    title: "Fairlearn user guide: Performing a fairness assessment"
    author: team:fairlearn
  - id: fairlearn-common-metrics
    resource: https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html
    title: "Fairlearn user guide: Common fairness metrics"
    author: team:fairlearn
  - id: fairlearn-ci
    resource: https://fairlearn.org/main/user_guide/assessment/confidence_interval_estimation.html
    title: "Fairlearn user guide: Confidence interval estimation"
    author: team:fairlearn
  - id: fairlearn-fairness
    resource: https://fairlearn.org/main/user_guide/fairness_in_machine_learning.html
    title: "Fairlearn user guide: Fairness in machine learning"
    author: team:fairlearn
  - id: model-cards
    resource: https://arxiv.org/abs/1810.03993
    title: Model Cards for Model Reporting
    author: Margaret Mitchell, Simone Wu, Andrew Zaldivar, Parker Barnes, Lucy Vasserman, Ben Hutchinson, Elena Spitzer, Inioluwa Deborah Raji, Timnit Gebru
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab08
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/README.md
    title: "Lesson 08: fairness, transparency and the model card"
    author: org:majlisofai
---

# Definition

A fairness metric compares how a model treats different groups. You compute one metric for each group, then compare the groups. Lab 08 uses four metrics for each group:

- **Accuracy**: the share of correct predictions.
- **Selection rate**: the share of entries that the model predicts as positive (here, "scores points"). Fairlearn uses it as the basis of demographic parity.[^fairlearn-common-metrics]
- **False positive rate (FPR)**: of the entries that did not score, the share that the model predicted to score.
- **False negative rate (FNR)**: of the entries that scored, the share that the model predicted not to score.

Mitchell et al. list the false positive rate and the false negative rate as error types for classification systems. Equal false negative rates across groups is equality of opportunity. Equal false negative and false positive rates is equality of odds.[^model-cards]

You compare two groups in two ways. A **gap** (difference) subtracts one rate from the other. A **ratio** divides the smaller rate by the larger one. Fairlearn's `MetricFrame` computes both, between the largest and the smallest group value by default. It returns the absolute difference and a ratio below one.[^fairlearn-assessment]

Each group rate has **uncertainty**. A small group gives a wide interval. Fairlearn says that a metric without a confidence interval "should be regarded with suspicion". Splitting the data into groups makes the random noise larger.[^fairlearn-ci]

# Why it matters

One overall number does not show who gets the errors. Two models with the same accuracy can make different kinds of mistakes for one group. Mitchell et al. say that the importance of each error rate depends on the system and the context. They recommend listing all values and saying which ones you chose and why.[^model-cards]

NIST asks that fairness and bias are evaluated and the results documented (MEASURE 2.11). It also asks that approaches and metrics are selected for the most significant risks (MEASURE 1.1). NIST says that statistical biases often come from non-representative samples.[^nist-ai-rmf]

Metrics are not the whole story. Fairlearn says that fairness metrics capture some aspects of fairness but fail to capture all of them. Some metrics, such as demographic parity and equalized odds, cannot both be met at the same time.[^fairlearn-fairness]

Kid version: before each race, the predictor says "points or no points?" for every car. The two rookies had 21 entries that scored no points, and the predictor promised points for 16 of them. For everyone else, it made that mistake only about 1 time in 7. The predictor's average score hides this.

# Examples

The champion forest on the 2025 holdout, rookies against everyone else (lab 08, `fairness_report.py`):[^lab08]

| Group | Entries | Drivers | Accuracy | Selection rate | FPR | FNR |
|---|---:|---:|---:|---:|---:|---:|
| Everyone else | 432 | 18 | 0.863 | 0.500 | 0.142 | 0.131 |
| Rookies | 48 | 2 | 0.646 | 0.875 | 0.762 | 0.037 |
| Gap (rookie minus others) | | | −0.218 | +0.375 | **+0.620** | −0.094 |

- The lab prints the accuracy gap the other way round (others minus rookies, +0.218), so that a positive gap always means worse for rookies.
- The rookie errors are almost all one kind. The model predicts points for 87.5 % of rookie entries. Of the 21 rookie entries that did not score, it predicted points for 16. It misses only 1 of the 27 rookie entries that scored.
- Lab 04 reported rookie accuracy 0.646 only. That single number hid that the errors are false positives.
- The ratios tell the same story in another form: FPR ratio 0.142 / 0.762 ≈ 0.19, selection-rate ratio 0.500 / 0.875 ≈ 0.57.
- The grid rule ("start in the top ten, score points") has an FPR gap of +0.568. The model is more over-optimistic about rookies than a rule anyone can apply without a model.
- Uncertainty: the bootstrap interval (500 resamples) of the rookie FPR is 0.56 to 0.93. It is still too narrow: it resamples entries, but the 48 entries come from two drivers and are not independent. One entry moves the rookie FPR by 1/21 ≈ 0.048.
- The report counts drivers per group with `driver_code`, and warns when a group has fewer than 5 drivers or a rate rests on fewer than 30 entries.
- `rookie` and `team_tier` are subgroups for reporting, not protected characteristics. The course uses them to practise the method on data where nobody is harmed.

See [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md) for the per-group accuracy that lab 03 logs, and [classification metrics](/knowledge/mlops/classification-metrics.md) for the overall metrics.

# Common mistakes

- Comparing accuracy only. Accuracy mixes both error types. Look at the FPR and the FNR for each group.
- Reading every gap as unfair. In lab 08, `team_tier` shows the largest gaps (top teams FPR 1.000, backmarker FNR 1.000). They rest on 17 and 3 entries and follow the task: top cars almost always score. A gap that follows the task, not a person, is not a fairness finding.
- Reporting a rate without its count and interval. "FPR 0.762" means little until you add "on 21 entries from 2 drivers, interval 0.56 to 0.93".
- Treating overlapping intervals as equal. Fairlearn notes that overlapping confidence intervals do not imply statistical equality.[^fairlearn-ci]
- Applying a fixed ratio rule everywhere. Fairlearn says the "four-fifths rule" is not appropriate in most cases outside its original context.[^fairlearn-common-metrics]
- Publishing a group of one. In 2025 the midfield rookies are one driver. A "group" result for them is one person's scorecard, so the lab report suppresses it.

[^fairlearn-assessment]: Fairlearn user guide, "Performing a fairness assessment", section on `MetricFrame` and the `difference()` and `ratio()` methods.
[^fairlearn-common-metrics]: Fairlearn user guide, "Common fairness metrics", sections "Demographic parity" and the note on the four-fifths rule.
[^fairlearn-ci]: Fairlearn user guide, "Confidence interval estimation", introduction and caveats.
[^fairlearn-fairness]: Fairlearn user guide, "Fairness in machine learning", section on fairness metrics.
[^model-cards]: Mitchell et al., "Model Cards for Model Reporting", FAT* 2019 (arXiv:1810.03993), section 4.4.1 "Classification systems".
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 1.1, MEASURE 2.11) and section 3.7 "Fair – with Harmful Bias Managed".
[^lab08]: Lesson 08 README, step 3, and `fairness_report.py`.
