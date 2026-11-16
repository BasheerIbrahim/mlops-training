---
type: Domain Concept
title: Container image
description: A Docker image that packages the model service code, its pinned libraries and its start command, so the service runs the same way everywhere.
tags: [mlops, serving, docker, container, packaging]
status: draft
classification: public
framework_refs: ["NIST-AI-RMF:MAP 4.1", "NIST-AI-RMF:MEASURE 2.3"]
generated: { by: majlis-academy-knowledge-harvester/claude-opus-5-5, at: 2026-11-16T18:25:00+03:00 }
stale_after: 2027-05-16T00:00:00+03:00
sources:
  - id: docker-image
    resource: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/
    title: What is an image?
    author: org:docker
  - id: docker-cache
    resource: https://docs.docker.com/build/cache/
    title: Docker build cache
    author: org:docker
  - id: docker-best-practices
    resource: https://docs.docker.com/build/building/best-practices/
    title: Building best practices
    author: org:docker
  - id: dockerfile-ref
    resource: https://docs.docker.com/reference/dockerfile/
    title: Dockerfile reference
    author: org:docker
  - id: docker-host-network
    resource: https://docs.docker.com/network/drivers/host/
    title: Host network driver
    author: org:docker
  - id: fastapi-docker
    resource: https://fastapi.tiangolo.com/deployment/docker/
    title: FastAPI in Containers - Docker
    author: team:fastapi
  - id: google-mlops
    resource: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    title: "MLOps: Continuous delivery and automation pipelines in machine learning"
    author: org:google-cloud
  - id: nist-ai-rmf
    resource: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
    title: Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1
    author: org:nist
  - id: lab05
    resource: https://github.com/majlisofai/mlops-training/blob/05-serve-model/exercises/serve-model/README.md
    title: "Lesson 05: serve the model and roll back a faulty release"
    author: org:majlisofai
---

# Definition

A container image is a standardized package that includes all the files, binaries, libraries and configurations that a container needs. Once an image is built, it cannot be changed. An image is made of layers, and each layer is a set of file system changes.[^docker-image] A `Dockerfile` lists the steps that build the image.

For a [model serving API](/knowledge/mlops/model-serving-api.md), the image holds the service code, the pinned Python packages and the command that starts the service. In the lab, the image holds the code, not the model. The API loads the model from the MLflow registry when the container starts.[^lab05]

# Why it matters

The image runs the same way in the codespace, on GitHub Actions and on a server. Google's MLOps guide asks you to verify, before deployment, that the packages the model needs are installed in the serving environment, and that the required memory and compute are available.[^google-mlops] The lab image pins the same versions as the codespace, so the container loads the model with the scikit-learn that trained it.[^lab05]

The NIST AI RMF asks that the risks of third-party software components are mapped and documented (MAP 4.1), and that performance is demonstrated for conditions similar to the deployment setting (MEASURE 2.3).[^nist-ai-rmf] `requirements-serve.txt` lists every third-party package and its version. CI load-tests the same image that would be deployed.

The image is a packed food truck. It carries the stove, the pans and the cook's instructions, so it cooks the same way in any town. It does not carry the dish: when it opens, it fetches the champion recipe from the recipe book.

# Examples

The lab `Dockerfile`:[^lab05]

- `FROM python:3.12-slim`, then `COPY requirements-serve.txt` and `pip install` before `COPY app.py`. FastAPI's guide says to copy only the requirements file first, because it does not change often, so Docker can use the cache for this step.[^fastapi-docker] If a layer changes, all the layers after it are rebuilt.[^docker-cache]
- `requirements-serve.txt` pins `mlflow-skinny==3.18.0`, `scikit-learn==1.9.1`, `fastapi==0.163.1` and others. `mlflow-skinny` is MLflow without the server and the UI.
- `RUN useradd --create-home api` and `USER api`. Docker's best practices say: if a service can run without privileges, use `USER` to change to a non-root user.[^docker-best-practices]
- `ENV MODEL_URI=models:/f1-points-finish@champion` and `PORT=8000`. Variables set with `ENV` persist when a container runs from the image.[^dockerfile-ref] `EXPOSE 8000` documents the port; it does not publish it.[^dockerfile-ref]
- `docker build -t f1-api:1 exercises/serve-model` takes about a minute the first time. The image is about 810 MB.
- `docker run --rm --name f1-api --network host f1-api:1`. With host networking, the container shares the host's network namespace, and `-p` options are ignored. The host driver works on Linux hosts, and as an opt-in feature in Docker Desktop 4.34 and later.[^docker-host-network] In the codespace, Docker runs in the dev container (the `docker-in-docker` feature), so `127.0.0.1:5000` inside the container is the MLflow server.[^lab05]
- On Docker Desktop without host networking, trainees publish the port with `-p 8000:8000` and set `MLFLOW_TRACKING_URI=http://host.docker.internal:5000`.

# Common mistakes

- Building the model into the image. Each new model then needs a new image, and the registry is no longer the one place that names the production model.
- Unpinned packages. A newer scikit-learn may not load a model that an older one saved.
- Copying the code before installing the packages. Every code change then reinstalls every package.
- Running the service as root.
- Forgetting `--network host` in the codespace. Inside the container, `127.0.0.1` is then the container itself, and the API stops with `Connection refused` to port 5000.
- Using the shell form of `CMD`. FastAPI's guide says to always use the exec form, so that the app shuts down gracefully and lifespan events run.[^fastapi-docker] The lab uses `CMD ["sh", "-c", "exec uvicorn ..."]`, so `exec` replaces the shell with uvicorn.

[^docker-image]: Docker documentation, "What is an image?".
[^docker-cache]: Docker documentation, "Docker build cache".
[^docker-best-practices]: Docker documentation, "Building best practices", section "USER".
[^dockerfile-ref]: Docker documentation, "Dockerfile reference", sections ENV and EXPOSE.
[^docker-host-network]: Docker documentation, "Host network driver".
[^fastapi-docker]: FastAPI documentation, "FastAPI in Containers - Docker", sections on the Docker cache and on the exec form of CMD.
[^google-mlops]: Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning", section "MLOps level 2", subsection "Continuous delivery".
[^nist-ai-rmf]: NIST AI 100-1, Table 2 (MAP 4.1) and Table 3 (MEASURE 2.3).
[^lab05]: Lesson 05 README, step 6; `Dockerfile`, `requirements-serve.txt`, `.devcontainer/devcontainer.json`.
