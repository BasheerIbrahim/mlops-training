---
type: Domain Concept
title: MLflow tracking server
description: A stand-alone MLflow HTTP server that stores runs in a backend store, keeps logged files in an artifact store and serves the tracking UI.
tags: [mlops, mlflow, experiment-tracking, infrastructure, security]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MEASURE 2.1", "ISO-42001:A.4.4"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T16:35:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: mlflow-server
    resource: https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/
    title: MLflow Tracking Server
    author: team:mlflow
  - id: mlflow-cli
    resource: https://mlflow.org/docs/latest/api_reference/cli.html
    title: MLflow command-line interface, `mlflow server`
    author: team:mlflow
  - id: mlflow-network
    resource: https://mlflow.org/docs/latest/self-hosting/security/network/
    title: Protect Your Tracking Server from Network Exposure
    author: team:mlflow
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
  - id: lab02-readme
    resource: https://github.com/majlisofai/mlops-training/blob/02-mlflow/README.md
    title: "mlops-training · Stage 02: MLflow"
    author: org:majlisofai
---

# Definition

The MLflow tracking server is a stand-alone HTTP server. It serves REST API endpoints for tracking runs and experiments, and it serves the tracking UI.[^mlflow-server] It has two stores:

- The backend store keeps the run metadata: parameters, metrics, tags and run records. The default is a SQLite database, `sqlite:///mlflow.db`.[^mlflow-server] The option `--backend-store-uri` sets the URI where the server persists experiment and run data.[^mlflow-cli]
- The artifact store keeps the files that runs log. The default is a local folder, `./mlartifacts`.[^mlflow-server] The option `--artifacts-destination` sets the base location for artifact uploads and downloads, for example an S3 bucket.[^mlflow-cli] The server then acts as a proxy for the artifacts, so clients do not access the storage directly.[^mlflow-server]

Since MLflow 3.5.0, the server has security middleware against DNS rebinding and cross-origin (CORS) attacks.[^mlflow-network] `--allowed-hosts` lists the `Host` headers that the server accepts. The default is localhost and private IP addresses.[^mlflow-cli] `--cors-allowed-origins` lists the web origins that can call the API from a browser.[^mlflow-network]

# Why it matters

One server gives the whole team one place to log runs and one UI to compare them.[^mlflow-server] Each trainee and each pipeline sends runs to the same URL. NIST AI RMF MEASURE 2.1 asks that the details of the tools used during TEVV are documented.[^nist-ai-rmf] ISO/IEC 42001 control A.4.4 asks the organization to document the tooling resources of an AI system.[^iso-42001][^advisera-42001] A tracking server is one of those tools, and its address and stores are part of that record.

The security options matter when the UI is not on `localhost`. A codespace serves the UI from a `*.app.github.dev` address. That host is not in the default list, so the server rejects the browser requests. In the lab, the UI then shows **403**.[^lab02][^lab02-readme]

Think of the team's data room behind the pit wall. Every engineer puts logbook pages on its shelves (the backend store) and files in its archive boxes (the artifact store). The door lets in only the passes that are on the list (`--allowed-hosts`).

# Examples

The lab starts MLflow 3.18 with this command:[^lab02]

```bash
mlflow server \
  --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./mlartifacts \
  --allowed-hosts "*.app.github.dev,localhost:*,127.0.0.1:*" \
  --cors-allowed-origins "https://*.app.github.dev"
```

- Runs, parameters, metrics and tags go into `mlflow.db`. The `.dvc` pointer, `report.json` and `failure_cases.csv` go into `./mlartifacts`.[^lab02]
- The codespace forwards port 5000 with the label **MLflow UI**.[^lab02-readme]
- The script connects with `mlflow.set_tracking_uri("http://127.0.0.1:5000")`. When the server is not running, the script retries for about 4 minutes and then fails with `Max retries exceeded`.[^lab02-readme]

# Common mistakes

- Leaving out `--allowed-hosts` and `--cors-allowed-origins` behind a proxy or a Codespaces URL. The UI returns 403.[^lab02-readme]
- Using `--allowed-hosts "*"` to make the error go away. MLflow marks "allow all" as not recommended. List only the hosts that you use.[^mlflow-network]
- Closing the terminal that runs the server. Then the scripts cannot log. Keep the server in its own terminal.[^lab02-readme]
- Using SQLite for a busy, shared production server. MLflow recommends PostgreSQL or MySQL for high concurrency.[^mlflow-server]
- Using the lab settings in production. MLflow says that the default settings are for local development, and production needs explicit configuration.[^mlflow-network] The lab server has no login. A shared server needs authentication.

[^mlflow-server]: MLflow documentation, "MLflow Tracking Server", sections on the backend store, the artifact store and proxied artifact access.
[^mlflow-cli]: MLflow documentation, command-line interface, `mlflow server` options.
[^mlflow-network]: MLflow documentation, "Protect Your Tracking Server from Network Exposure".
[^nist-ai-rmf]: NIST AI 100-1, Table 3 (MEASURE 2.1).
[^iso-42001]: ISO/IEC 42001:2023, Annex A, control A.4.4.
[^advisera-42001]: Advisera, "List of ISO 42001 mandatory documents", Annex A control A.4.4 (utilized tooling resources).
[^lab02]: Lab 02 exercise README, steps 1 and 3.
[^lab02-readme]: Lab 02 top-level README, "If something goes wrong" and "Tools in the codespace".
