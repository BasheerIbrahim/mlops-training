---
type: Domain Concept
title: Model card
description: A short document that travels with a model and records its intended use, limits, evaluation by group, and who approved its release.
tags: [transparency, documentation, model-card, accountability, mlflow]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 1.1", "NIST-AI-RMF:MAP 3.3", "NIST-AI-RMF:MEASURE 2.9", "NIST-AI-RMF:GOVERN 2.1", "ISO-42001:A.6.2.7"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T22:50:00+03:00 }
stale_after: 2027-11-16T00:00:00+03:00
sources:
  - id: model-cards
    resource: https://arxiv.org/abs/1810.03993
    title: Model Cards for Model Reporting
    author: Margaret Mitchell, Simone Wu, Andrew Zaldivar, Parker Barnes, Lucy Vasserman, Ben Hutchinson, Elena Spitzer, Inioluwa Deborah Raji, Timnit Gebru
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: sdaia-ethics
    resource: https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf
    title: AI Ethics Principles, version 1, May 2025 (document SDAIA-P114E)
    author: org:sdaia
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
  - id: lab08-card
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/model_card.yaml
    title: "Lesson 08: the human-written part of the model card (model_card.yaml)"
    author: org:majlisofai
  - id: lab08-card-py
    resource: https://github.com/majlisofai/mlops-training/blob/08-fairness/exercises/fairness/model_card.py
    title: "Lesson 08: model card generator (model_card.py)"
    author: org:majlisofai
---

# Definition

A model card is a short document that accompanies a trained model. It gives the model's evaluation in a variety of conditions, including groups and intersectional groups. It also says in which context the model is meant to be used and how it was evaluated.[^model-cards]

Mitchell et al. propose these sections: model details, intended use (primary uses, primary users, out-of-scope uses), factors, metrics, evaluation data, training data, quantitative analyses, ethical considerations, and caveats and recommendations.[^model-cards] The out-of-scope section is inspired by warning labels on food and toys.[^model-cards] Quantitative analyses should be broken down by the chosen factors and give confidence intervals when possible.[^model-cards]

The lab adds one section for the release: **accountability and sign-off**, with an owner, an approver and the decision.[^lab08]

# Why it matters

Numbers in a registry do not tell a reviewer what the model is for, where it is weak, or who said yes. A model card does, in one place, next to the model.

NIST asks that intended purposes and context are documented (MAP 1.1), that the targeted application scope is documented (MAP 3.3), and that the model is explained, validated and documented (MEASURE 2.9). It asks that roles and responsibilities are documented (GOVERN 2.1).[^nist-ai-rmf] NIST adds that transparency covers how and when deployment decisions were made and by whom, and that a transparent system is not necessarily accurate or fair.[^nist-ai-rmf]

SDAIA asks that performance metrics and the measured impact on individuals and communities are documented and accessible to stakeholders (Principle 6), and that owners review and sign off a model before production (Principle 7).[^sdaia-ethics] ISO/IEC 42001 Annex A has a control for AI system technical documentation (A.6.2.7).[^iso-42001][^advisera-42001]

A model card is the car's technical passport: what the predictor is, what it is for, what it must never be used for, how it performs and for whom, and who signed it off.

# Examples

`model_card.py` builds the card from MLflow, so nobody types a number by hand. People write only what a machine cannot know, in `model_card.yaml`.[^lab08-card-py][^lab08-card]

| Card section | Where it comes from |
|---|---|
| Release status | Lab 04 gate tags, the fairness gate report, the human decision and approver |
| Model details | Registry (version, aliases, `promoted_by`, previous champion) and run (model type, hyperparameters, data version, git commit) |
| Intended use, out-of-scope uses, factors | `model_card.yaml`, written by people |
| Quantitative analyses | Run metrics and the fairness report logged to the run (`fairness/fairness_report.json`) |
| Ethical considerations, caveats | `model_card.yaml`, plus the warnings of the fairness report |
| Accountability and sign-off | `model_card.yaml`: owner, approver, contact, decision, date |

- Out of scope in the lab card: judging an individual driver (performance reviews, contracts, seat decisions), betting, and seasons under new regulations (2026) before a new check.
- Caveat in the lab card: the 2025 rookie group is two drivers (48 entries); one entry moves the rookie FPR by about 0.05.
- The first run prints `Placeholders still to fill in model_card.yaml: 7`, and the card starts with **Not ready for review**. After trainees fill in the owner, approver, decision and their note on the rookie gap, it says 0.
- `model_card.py` logs the card to the model's run under `model_card/` and tags the registry version with `model_card` and `fairness_gates = passed` (version 8, the logistic regression).
- On GitHub Actions, step 5 writes the card even when the fairness gate fails. A blocked release needs a card too. The card is kept in the artifact `fairness-dossier`.

# Common mistakes

- Typing numbers into the card by hand. They drift from the model. Generate them from the registry and the run.
- Overall metrics only. Mitchell et al. ask for disaggregated results with confidence intervals.[^model-cards] Use the [fairness metrics](/knowledge/mlops/fairness-metrics.md) and [subgroup evaluation](/knowledge/mlops/subgroup-evaluation.md).
- No out-of-scope uses. Say what the model must not be used for, especially judging a person.
- No owner, no approver, no decision. Without them the card describes a model but does not record a release decision. See [deployment approval](/knowledge/mlops/deployment-approval.md).
- Writing the card once. A new version needs a new card. Regenerate it on every promotion.
- Hiding a failed gate. When the gate fails and the model is still approved, the card must say why. SDAIA asks that the fairness assessment is justified when the champion does not pass.[^sdaia-ethics]

[^model-cards]: Mitchell et al., "Model Cards for Model Reporting", FAT* 2019 (arXiv:1810.03993), abstract, section 4 (sections of a card), section 4.2 (out-of-scope uses) and section 4.7 (quantitative analyses).
[^nist-ai-rmf]: NIST AI 100-1, section 3.4 "Accountable and Transparent", Table 1 (GOVERN 2.1), Table 2 (MAP 1.1, MAP 3.3) and Table 3 (MEASURE 2.9).
[^sdaia-ethics]: SDAIA, AI Ethics Principles (2025), Principle 6 Transparency and Explainability, Deploy and Monitor, item 1 (p. 25); Principle 7 Accountability and Responsibility, Build and Validate, item 4 (p. 27); Principle 1 Fairness, Build and Validate, item 2 (p. 14). Printed page numbers. The sdaia.gov.sa server refused automated download on 2026-11-16; the text was checked against a saved copy of document SDAIA-P114E, version 1.
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.6.2.7. The standard is paywalled and was not read directly.
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.6.2.7 (AI system technical documentation). Secondary source.
[^lab08]: Lesson 08 README, step 8.
[^lab08-card]: Lesson 08 `model_card.yaml`.
[^lab08-card-py]: Lesson 08 `model_card.py`.
