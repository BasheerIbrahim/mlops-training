---
type: Domain Concept
title: Artifact integrity manifest
description: A list of the SHA-256 of every release file, checked again before release, so that a file changed after sign-off fails the release.
tags: [mlops, security, integrity, sha-256, mlflow, skops, supply-chain]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.7", "NIST-AI-RMF:MEASURE 2.8"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:35:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: nist-ssdf
    resource: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf
    title: "Secure Software Development Framework (SSDF) Version 1.1, NIST SP 800-218"
    author: org:nist
  - id: slsa-build
    resource: https://slsa.dev/spec/v1.2/build-track-basics
    title: "SLSA v1.2: Build track basics"
    author: org:openssf
  - id: skops-persistence
    resource: https://skops.readthedocs.io/en/stable/persistence.html
    title: Secure persistence with skops
    author: team:skops
  - id: py-hmac
    resource: https://docs.python.org/3/library/hmac.html
    title: "hmac — Keyed-Hashing for Message Authentication"
    author: org:python
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab09
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/README.md
    title: "Lesson 09: security gates and production-readiness acceptance"
    author: org:majlisofai
  - id: lab09-manifest
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/manifest.py
    title: "Lesson 09: manifest.py, tamper.py and release.yaml"
    author: org:majlisofai
  - id: lab09-scenarios
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/solution/scenarios.md
    title: "Lesson 09: scenario check, answer key"
    author: org:majlisofai
  - id: ci-tamper
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43901405659
    title: "GitHub Actions run 43901405659: acceptance, fault tamper"
    author: org:majlisofai
---

# Definition

An artifact integrity manifest is a list of the files of a release, with the SHA-256 of each file. If one byte of a file changes, its SHA-256 changes completely. Equal hashes mean equal files.[^lab09-manifest]

The manifest is used twice:

1. **Sign-off.** After the gates pass, hash every file and record the manifest. Record the SHA-256 of the manifest itself in a second place.
2. **Verify.** Before the release, hash every file again and compare. Each file is `OK`, `CHANGED`, `MISSING` (in the manifest, not on disk) or `NEW` (on disk, not in the manifest). Anything but `OK` fails.[^lab09-manifest]

A plain SHA-256 manifest is a **fingerprint, not a cryptographic signature**. Anybody who can change both the files and the recorded hash can make them match again.[^lab09] A signature, for example an HMAC with a key that only the release manager has, cannot be recomputed without that key.[^py-hmac]

# Why it matters

The [quality gates](/knowledge/mlops/quality-gate.md) check a model file. If somebody changes that file after the gates, nothing else notices: the API loads whatever is in the artifact store behind the [model registry](/knowledge/mlops/model-registry.md).[^lab09] The NIST AI RMF names data poisoning as a common security concern. It calls a system secure when protection mechanisms against unauthorized access and use keep its confidentiality, integrity and availability (section 3.3). MEASURE 2.7 asks that security is evaluated and documented, and MEASURE 2.8 that accountability risks are examined.[^nist-ai-rmf] The manifest records which files were gated and who signed them off.

NIST's Secure Software Development Framework asks for a way to verify release integrity, for example by posting cryptographic hashes of release files (PS.2.1). It also says to protect the integrity data, for example by keeping it in a separate location from the release files or by signing it (PS.3.1).[^nist-ssdf] SLSA Build L3 goes further: the secret material that signs the provenance must not be accessible to user-defined build steps.[^slsa-build]

The model file needs a second check. skops says that pickle is not secure, because loading some objects can run arbitrary code. skops constructs only the types that are trusted, by default or by the user. You should always review the types that `get_untrusted_types` reports, and load skops files only from sources you trust.[^skops-persistence]

The head chef takes a photo of each page of the winning recipe and keeps the list of photos. Before service, a helper compares each page with its photo. One extra pinch of salt and the page no longer matches. But if the photos sit in the same drawer as the recipe, a thief can swap both.

# Examples

`manifest.py sign --signer "<your name>"` hashes ten files: the seven files of the model version (`model/model.skops`, about 10.6 MB, `model/MLmodel` and five small files), `f1/data/races.csv`, `criteria.yaml` and `slo.yaml`. It downloads the model files again from the registry, because that is what the API loads. It logs the manifest to the model's MLflow run as `integrity/manifest-v1.json` and tags the version with `integrity.manifest_sha256`, `integrity.signed_by`, `integrity.signed_at` and `integrity.files = 10`.[^lab09]

`manifest.py verify` prints ten `OK` lines and `INTEGRITY OK: 10 files match the manifest signed by <your name>`. It also fails when the manifest no longer matches its tag.[^lab09-manifest]

The data and the release criteria are in the manifest too. A model gated against changed data, or against a lowered `min_accuracy` in `criteria.yaml`, was not gated against what was signed.[^lab09]

| Fault | Integrity gate | What still passed |
|---|---|---|
| `tamper.py --target model`: 30 of the 300 trees, still loads | `model/model.skops: CHANGED` | 7 quality gates (ROC AUC 0.905 instead of 0.907), contract and access tests, SLO (p95 33 ms instead of 75 ms). The pole-sitter's probability is 0.933 instead of 0.958. |
| Same fault on GitHub Actions | `model/model.skops: CHANGED` | 7 quality gates (accuracy 0.846, ROC AUC 0.904), SLO (p95 26 ms) |
| `tamper.py --target data`: one `driver_form` from 8.0 to 8.01 | `f1/data/races.csv: CHANGED` | [Data validation](/knowledge/mlops/data-validation.md): 0 failure cases. The [lineage](/knowledge/mlops/data-lineage.md) check fails too: md5 `1885fafd92e1`, trained on `199d7bda0a7b`. |

Sources: lab 09 README step 9,[^lab09] run 43901405659,[^ci-tamper] scenario card 4.[^lab09-scenarios]

The tampered model is a real, working model, and it is even faster. Only the fingerprint shows that it is not the model that was gated.[^lab09-scenarios]

The skops allowlist: `sklearn.tree._tree.Tree` is not on skops' built-in list, so lab 03 trusted it. The model's `MLmodel` file stores its own list of trusted types, but anyone who can change the model can change that list. So the allowed list lives in git, in `release.yaml` (`allowed_skops_types`), and `verify` fails on any other type.[^lab09-manifest]

# Common mistakes

- Signing again to clear the alarm. `sign` refuses a version that is already signed. `--force` hides a change; use it only when you know why the files changed.[^lab09-scenarios]
- Hashing a local copy instead of the files the API loads.
- Fingerprinting only the model. A change to the data or to `criteria.yaml` also changes what the gates meant.
- Calling a hash next to the files a signature. In the lab the tag is in MLflow, next to the model it protects. Keep the proof where the person who can change the model cannot change it, or sign it with a key that person does not have.[^nist-ssdf]
- Trusting the type list inside the model file, or loading models with pickle.
- Thinking that the manifest proves the model is good. It proves only that the files did not change after the sign-off. The gates prove the rest, and the [acceptance suite](/knowledge/mlops/acceptance-suite.md) runs them all together.

[^nist-ssdf]: NIST SP 800-218, practices PS.2 (task PS.2.1, example 1) and PS.3 (task PS.3.1, example 2).
[^slsa-build]: SLSA v1.2, "Build track basics", Build L2 and Build L3 requirements.
[^skops-persistence]: skops documentation, "Secure persistence with skops".
[^py-hmac]: Python documentation, `hmac` module.
[^nist-ai-rmf]: NIST AI 100-1, section 3.3 (Secure and Resilient) and Table 3 (MEASURE 2.7, MEASURE 2.8).
[^lab09]: Lesson 09 README, steps 5 and 9, and Discuss question 1.
[^lab09-manifest]: Lesson 09 `manifest.py`, `tamper.py` and `release.yaml`.
[^lab09-scenarios]: Lesson 09 `solution/scenarios.md`, cards 2 and 4.
[^ci-tamper]: GitHub Actions run 43901405659, step "7. Acceptance suite".
