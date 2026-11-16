---
type: Domain Concept
title: API access control
description: Checking who calls a model API (authentication) and what that caller may do (authorization), with least-privilege keys that never enter code or git.
tags: [mlops, serving, security, api-keys, fastapi, least-privilege]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.7"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T19:20:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: rfc9110
    resource: https://www.rfc-editor.org/rfc/rfc9110.html
    title: "RFC 9110: HTTP Semantics"
    author: org:ietf
  - id: owasp-rest
    resource: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
    title: REST Security Cheat Sheet
    author: org:owasp
  - id: owasp-api-top10
    resource: https://api-security.owasp.org/editions/2023/en/0x11-t10
    title: OWASP Top 10 API Security Risks – 2023
    author: org:owasp
  - id: owasp-secrets
    resource: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
    title: Secrets Management Cheat Sheet
    author: org:owasp
  - id: nist-least-privilege
    resource: https://csrc.nist.gov/glossary/term/least_privilege
    title: "Glossary: least privilege"
    author: org:nist
  - id: fastapi-security
    resource: https://fastapi.tiangolo.com/reference/security/
    title: Security Tools (FastAPI reference)
    author: team:fastapi
  - id: py-hmac
    resource: https://docs.python.org/3/library/hmac.html
    title: "hmac — Keyed-Hashing for Message Authentication"
    author: org:python
  - id: py-secrets
    resource: https://docs.python.org/3/library/secrets.html
    title: "secrets — Generate secure random numbers for managing secrets"
    author: org:python
  - id: docker-run
    resource: https://docs.docker.com/reference/cli/docker/container/run/
    title: docker container run
    author: org:docker
  - id: gh-workflow-commands
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
    title: Workflow commands for GitHub Actions
    author: org:github
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab09
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/README.md
    title: "Lesson 09: security gates and production-readiness acceptance"
    author: org:majlisofai
  - id: lab09-security
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/security.py
    title: "Lesson 09: security.py and keys.py"
    author: org:majlisofai
  - id: lab09-scenarios
    resource: https://github.com/majlisofai/mlops-training/blob/09-acceptance/exercises/acceptance/solution/scenarios.md
    title: "Lesson 09: scenario check, answer key"
    author: org:majlisofai
  - id: ci-no-auth
    resource: https://github.com/majlisofai/mlops-training/actions/runs/43901421252
    title: "GitHub Actions run 43901421252: acceptance, fault no-auth"
    author: org:majlisofai
---

# Definition

Access control decides who may call which endpoint of an API. It has two steps:

1. **Authentication** asks "who are you?". The caller shows a credential, here an API key.
2. **Authorization** asks "may you do this?". The API compares the caller's role with what the endpoint needs.

HTTP has a status code for each step. 401 (Unauthorized) means that the request lacks valid credentials, and the server must send a `WWW-Authenticate` header with it. 403 (Forbidden) means that the server understood the request but refuses it. If the request had credentials, the server considers them insufficient.[^rfc9110] OWASP says the same in short: 401 for a wrong or missing credential, 403 when authentication succeeded but the user has no permission.[^owasp-rest]

**Least privilege** gives each user or process only the access it needs for its task.[^nist-least-privilege] In the lab, each key has one role and can do one job.[^lab09]

# Why it matters

In lab 05, anyone who could reach the [model serving API](/knowledge/mlops/model-serving-api.md) could call `/admin/reload` and trigger a [hot reload](/knowledge/mlops/model-hot-reload.md) of the served model. OWASP lists this class of risk as API5:2023, Broken Function Level Authorization: gaps in roles and groups expose admin functions. API2:2023, Broken Authentication, covers credentials that attackers can guess or steal.[^owasp-api-top10] OWASP also says that non-public REST services must perform access control at each endpoint.[^owasp-rest]

The NIST AI RMF calls an AI system secure when it keeps confidentiality, integrity and availability through mechanisms that prevent unauthorized access and use. It names the exfiltration of models through AI system endpoints as a common concern. MEASURE 2.7 asks that security and resilience are evaluated and documented.[^nist-ai-rmf] The access tests are that evaluation, gate 6 of the [acceptance suite](/knowledge/mlops/acceptance-suite.md), and the [release dossier](/knowledge/mlops/release-dossier.md) is the record.

A key is a secret, so the rules for secrets apply. OWASP says that secrets must never be logged, that exposed keys must be revoked at once, and that secrets should be rotated so that a stolen one works only for a short time.[^owasp-secrets]

The restaurant now gives out badges. A waiter's badge lets you place orders. Only the head chef's key opens the recipe cupboard. A stranger at the kitchen door hears "Who are you?" (401). A waiter at the recipe cupboard hears "I know you, but not this door" (403).

# Examples

The lab API, `security.py` and `app.py`:[^lab09-security]

- The key travels in the `X-API-Key` header. FastAPI's `APIKeyHeader` reads the header and adds it to the OpenAPI page, so `/docs` gets an **Authorize** button. With the default `auto_error=True`, a missing header stops the request. With `auto_error=False`, the dependency gets `None` instead.[^fastapi-security] The lab sets `auto_error=False` and answers 401 itself, with a clear message and the header `WWW-Authenticate: APIKey`.
- Two roles: a **client** key for `POST /v1/predict` and an **admin** key for `POST /admin/reload`. `/health` and `/docs` stay public: a load balancer must check the API, and the contract is not a secret.[^lab09]
- The API keeps only the SHA-256 of each key and compares with `hmac.compare_digest`. This function avoids content-based short-circuiting, so the response time does not show which character is wrong.[^py-hmac] The logs name a key by its fingerprint: the first 12 hex digits of its SHA-256.
- The API fails closed. Without both keys, or with a key shorter than 32 characters, it stops with `RuntimeError: API_CLIENT_KEY is not set or shorter than 32 characters.`[^lab09]
- `keys.py` makes each key with `secrets.token_urlsafe(32)`: 32 random bytes, about 43 characters. Python's documentation says that 32 bytes (256 bits) is enough for the typical use case.[^py-secrets] The file `.secrets/api.env` has mode 600 (`-rw-------`), git ignores it, and `keys.py` refuses to write a file that git does not ignore.[^lab09-security]
- `docker run --env-file .secrets/api.env` loads the variables from the file when the container starts.[^docker-run] The image holds no keys.

The seven `curl` calls of step 4:[^lab09]

| Call | Answer |
|---|---|
| `/v1/predict`, no key | 401 `missing API key: send it in the X-API-Key header` |
| `/v1/predict`, client key | 200, predictions `[1,0]` |
| `/v1/predict`, admin key | 403 `this key has the role 'admin'; /v1/predict needs the role 'client'` |
| `/admin/reload`, no key | 401 |
| `/admin/reload`, client key | 403 |
| `/admin/reload`, `wrong-key` | 401 `unknown API key` |
| `/admin/reload`, admin key | 200 |

The access tests go from `3 failed, 3 passed, 2 skipped` (the lab 05 API) to `6 passed, 2 skipped` after TODO 1 and 2, and to `8 passed` after TODO 3 and 4.[^lab09]

On GitHub Actions, the workflow makes throwaway keys for each run and masks them with `add-mask`, so the log prints `***` instead of the value.[^gh-workflow-commands] When the lab 05 image is deployed instead (fault `no-auth`), the contract tests and the SLO still pass, and the access tests fail with `4 passed, 4 failed`.[^ci-no-auth]

# Common mistakes

- Testing only that the right key works. The [contract tests](/knowledge/mlops/contract-test.md) and the [load test](/knowledge/mlops/load-test.md) send a client key, and the lab 05 API ignores it, so they pass. Only the tests without a key, or with the wrong role, find the open API.[^ci-no-auth]
- An API that starts without its keys. It is open to everyone, and nobody notices. Fail closed.
- Mixing up 401 and 403. A missing or unknown key is 401. A known key with the wrong role is 403.
- One key for every job. If a client key leaks from an application, it must not be able to change the model.
- Comparing keys with `==`, or logging the key itself. Use `hmac.compare_digest` and log a fingerprint.
- Putting a key in the code, the image, a URL or git. OWASP says that keys must not appear in URLs.[^owasp-rest] In scenario card 6, a key in `slo.yaml` fails `test_keys_are_not_committed`. Deleting the line in a new commit is not enough: the key stays in the history and in every fork. Rotate it with `keys.py --rotate`.[^lab09-scenarios]
- Relying only on API keys for high-value resources. OWASP says not to.[^owasp-rest] One shared key per role also cannot tell two client applications apart; per-client keys or tokens from an identity provider can.

[^rfc9110]: RFC 9110, sections 15.5.2 (401 Unauthorized) and 15.5.4 (403 Forbidden).
[^owasp-rest]: OWASP REST Security Cheat Sheet, sections "Access Control", "API Keys", "Sensitive information in HTTP requests" and "HTTP Return Codes".
[^owasp-api-top10]: OWASP API Security Top 10 2023, API2:2023 and API5:2023.
[^owasp-secrets]: OWASP Secrets Management Cheat Sheet, sections 2.7.2 (Rotation), 8.3 and 9.2 (Remediation).
[^nist-least-privilege]: NIST CSRC Glossary, "least privilege", definitions from CNSSI 4009-2022 and NIST SP 800-53 Rev. 5.
[^fastapi-security]: FastAPI reference, "Security Tools", `APIKeyHeader`, parameters `name`, `auto_error` and `description`.
[^py-hmac]: Python documentation, `hmac.compare_digest`.
[^py-secrets]: Python documentation, `secrets.token_urlsafe` and "How many bytes should tokens use?".
[^docker-run]: Docker documentation, `docker container run`, option `--env-file`.
[^gh-workflow-commands]: GitHub Docs, "Workflow commands for GitHub Actions", section "Masking a value in a log".
[^nist-ai-rmf]: NIST AI 100-1, section 3.3 (Secure and Resilient) and Table 3 (MEASURE 2.7).
[^lab09]: Lesson 09 README, steps 2, 3 and 4.
[^lab09-security]: Lesson 09 `security.py`, `keys.py` and `solution/app.py`.
[^lab09-scenarios]: Lesson 09 `solution/scenarios.md`, card 6.
[^ci-no-auth]: GitHub Actions run 43901421252, job "Acceptance suite", step "7. Acceptance suite".
