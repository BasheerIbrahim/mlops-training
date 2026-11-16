---
type: Domain Concept
title: Fairness gate
description: An automated pass-or-fail check that blocks a model when a fairness metric gap for a defined group exceeds a threshold written down in advance.
tags: [fairness, quality-gate, release, pytest, github-actions]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.11", "NIST-AI-RMF:MANAGE 1.1", "ISO-42001:A.6.2.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:30:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: sdaia-ethics
    resource: https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf
    title: AI Ethics Principles, version 1, May 2025 (document SDAIA-P114E)
    author: org:sdaia
  - id: model-cards
    resource: https://arxiv.org/abs/1810.03993
    title: Model Cards for Model Reporting
    author: Margaret Mitchell, Simone Wu, Andrew Zaldivar, Parker Barnes, Lucy Vasserman, Ben Hutchinson, Elena Spitzer, Inioluwa Deborah Raji, Timnit Gebru
  - id: iso-42001
    resource: https://www.iso.org/standard/42001
    title: "ISO/IEC 42001:2023 Information technology — Artificial intelligence — Management system"
    author: org:iso
  - id: advisera-42001
    resource: https://advisera.com/articles/iso-42001-mandatory-documents/
    title: List of ISO 42001 mandatory documents (Annex A control list)
  - id: lab08
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/README.md
    title: "Lesson 08: fairness, transparency and the model card"
    author: org:majlisofai
  - id: lab08-yaml
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/fairness.yaml
    title: "Lesson 08: fairness and privacy requirements (fairness.yaml)"
    author: org:majlisofai
  - id: ci-fail
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43899389581
    title: "GitHub Actions run 43899389581: fairness workflow, push, forest blocked"
    author: org:majlisofai
  - id: ci-pass
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43899417058
    title: "GitHub Actions run 43899417058: fairness workflow, dispatch with logreg.yaml, passed"
    author: org:majlisofai
---

# Definition

A fairness gate is a [quality gate](/knowledge/mlops/quality-gate.md) for a [fairness metric](/knowledge/mlops/fairness-metrics.md). It measures the gap between one group and everyone else, compares it with a threshold, and passes or fails. When it fails, the model does not move forward.

A fairness gate has four parts:

1. **The group** that the gate protects, defined before the measurement.
2. **The metric** that matches the harm, for example the false positive rate.
3. **The threshold**, written down before anyone compares the candidates, with the reason for the number.
4. **A minimum group size**. Below it the gate fails, because it cannot check the rule.

SDAIA's AI Ethics Principles ask teams to select the fairness metrics and define the allowed threshold in the plan-and-design stage. When the champion model is selected, its fairness metrics should be within the defined threshold. If the champion does not pass, the fairness assessment should be justified.[^sdaia-ethics]

# Why it matters

A model can pass every accuracy gate and still put its errors on one group. Lab 04's gates cannot see which errors a group gets. A fairness gate makes that check automatic and the same every time.

NIST asks that fairness and bias are evaluated and the results documented (MEASURE 2.11), and that someone decides whether deployment should proceed (MANAGE 1.1).[^nist-ai-rmf] ISO/IEC 42001 Annex A has a control for AI system verification and validation measures (A.6.2.4).[^iso-42001][^advisera-42001] A fairness gate is one such measure, and its report is the documented result.

A fairness gate is a second gatekeeper at the kitchen door. The first one checks that the dish tastes good. The second one checks that the critic's mistakes are not all piled on the new cooks.

# Examples

`fairness.yaml` holds the requirements. The numbers were set from the grid rule (a rule anyone can apply without a model), rounded down, before the candidates were compared:[^lab08-yaml][^lab08]

| Requirement | Threshold | Grid rule | Champion forest | Logistic regression |
|---|---:|---:|---:|---:|
| Rookie group size | ≥ 30 entries | 48 | 48 | 48 |
| Rookie FPR gap | ≤ 0.55 | +0.568 | **+0.620 FAIL** | +0.487 |
| Rookie FNR gap | ≤ 0.10 | +0.113 | −0.094 | −0.007 |

- Each gate is one pytest test (`test_rookie_fpr_gap`, `test_rookie_fnr_gap`). Trainees write the FNR gate (TODO 4). The failure message is `rookie false positive rate gap +0.620 is above 0.55`.
- Warnings do not block. They say the number is shaky: 2 drivers, an FPR on 21 entries, an FNR on 27.
- The champion that passed seven lab 04 gates, the contract tests and the load test is blocked. It fails by about one rookie entry: one entry moves the rookie FPR by 0.048.
- Six candidates through both gate sets: the forest is blocked; `logreg` (FPR gap +0.487) and `big_leaves` (+0.525) pass everything; `leaky` passes the fairness gates because it makes no errors, but lab 04's forbidden-features gate blocks it.
- On GitHub Actions, workflow `fairness.yml` runs the gates in step 4. The push run with the forest fails at "4. Fairness and privacy gates" with `1 failed, 4 passed, 1 skipped, 3 warnings`, and the gate table says BLOCKED.[^ci-fail] The dispatch run with `logreg.yaml` succeeds: `5 passed, 1 skipped` (the upstream file keeps TODO 4), FPR gap +0.487.[^ci-pass] Step 5 writes the [model card](/knowledge/mlops/model-card.md) in both runs: a blocked release needs a card too.

# Common mistakes

- Changing the threshold to make a model pass. Write the numbers before you look at the candidates, as for [release criteria](/knowledge/mlops/release-criteria.md).
- Gating on a metric that does not match the harm. Mitchell et al. say that the importance of each error rate depends on the context, and that you should say which ones you chose and why.[^model-cards] Lab 08 gates the false positive gap because a false positive for a rookie is an expectation the rookie did not meet.
- Letting a too-small group pass. A gate that cannot measure must fail, not skip.
- Thinking a fairness gate replaces quality gates. The leaky model is perfectly "fair" and useless. You need both gate sets.
- Hiding the doubt. The gate still decides on two drivers. The warnings and the model card say how sure you are.

[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.11) and Table 4 (MANAGE 1.1).
[^sdaia-ethics]: SDAIA, AI Ethics Principles (2025), Principle 1 Fairness: Plan and Design, items 3 and 4 (p. 13); Build and Validate, item 2 (p. 14, printed page numbers). The sdaia.gov.sa server refused automated download on 2026-11-16; the text was checked against a saved copy of document SDAIA-P114E, version 1.
[^model-cards]: Mitchell et al., "Model Cards for Model Reporting", FAT* 2019 (arXiv:1810.03993), section 4.4.1.
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.6.2.4. The standard is paywalled and was not read directly.
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.6.2.4 (AI system verification and validation measures). Secondary source.
[^lab08]: Lesson 08 README, "The fairness and privacy requirements", steps 5, 7 and 10.
[^lab08-yaml]: Lesson 08 `fairness.yaml`, section `fairness`.
[^ci-fail]: GitHub Actions run 43899389581 (push), job log and gate report.
[^ci-pass]: GitHub Actions run 43899417058 (workflow_dispatch, candidate `exercises/quality-gates/examples/logreg.yaml`), job log.
