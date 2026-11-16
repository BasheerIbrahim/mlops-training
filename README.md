# mlops-training · Lesson 05: serve the model and roll back a faulty release

Synthetic datasets for hands-on MLOps training: data validation, leakage, drift, training-serving skew and delayed labels.

**In this lesson** you put the F1 points-finish model behind a versioned HTTP API. The API loads the production model, `@champion`, from the MLflow Model Registry when it starts, and every answer says which model version made it. You write contract tests for the API, package it as a Docker image and load-test it with Locust against a service-level objective. Then you release a model that passes every lesson 04 quality gate but is too slow to serve, watch the load test fail, roll it back and prove that the service recovers. At the end the same serving check runs on GitHub Actions in your fork.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majlisofai/mlops-training?ref=05-serve-model)

## Trainees: start here

1. **Open your codespace.** Click the badge above. Check that the branch is **`05-serve-model`**, then click **Create codespace**. A copy of VS Code opens in your browser. You need a GitHub account. The codespace runs on your account and uses your free monthly Codespaces hours.
2. **Wait for the setup.** The first start takes a few minutes, because the codespace installs Docker and the Python packages. Wait until the terminal says the setup has finished before you run any command.
3. **Open the lesson.** In the file explorer, open [`exercises/serve-model/README.md`](exercises/serve-model/README.md). Right-click it and choose **Open Preview** to read it formatted.
4. **Do the nine steps** in the lesson, in order:

   | Step | What you do | You are done when |
   |---|---|---|
   | 1 | Start the MLflow server and open the MLflow UI | The MLflow UI opens in a browser tab |
   | 2 | Run the lesson 04 pipeline with the good candidate | `PROMOTED: f1-points-finish version 1 is now @champion`, with 7 gates passed |
   | 3 | Run the API with uvicorn and open its `/docs` page | The log says `Serving f1-points-finish version 1` |
   | 4 | Call the API with curl | `/v1/predict` answers `"predictions":[1,0]`, and a bad entry gets 422 with one line per problem |
   | 5 | Complete TODO 1 to TODO 3 in `exercises/serve-model/test_api.py` | `8 passed` |
   | 6 | Build the Docker image and run the container | `curl http://127.0.0.1:8000/health` answers from the container |
   | 7 | Load-test the API with Locust and check the SLO | `SLO MET` |
   | 8 | Promote the huge forest, reload, load-test, roll back, reload, load-test | `SLO BROKEN` with version 2, `SLO MET` again with version 1 |
   | 9 | Run the workflow **serve** in your fork, with the good and the huge candidate | The good run succeeds; the huge run fails at **5. Load test and SLO check** |

5. **Discuss** the four questions at the end of the lesson with your group.

**Rules for this lesson**

- Run every command from the repository root, `/workspaces/mlops-training`.
- Keep the terminal with the MLflow server open while you work. Use other terminals for the API, the container and the commands (**Terminal → New Terminal**).
- In this lesson you **push to your own fork** (step 9). You cannot push to `majlisofai/mlops-training`.
- Do not change `slo.yaml` to make a model pass. Do not change `.github/workflows/serve.yml`.
- Try the TODOs before you open the reference solution in `exercises/serve-model/solution/`.

**If something goes wrong**

| Problem | Fix |
|---|---|
| `mlflow: command not found`, `uvicorn: command not found` or `locust: command not found` | The setup has not finished. Wait, or run `pip install -r .devcontainer/requirements.txt`. |
| The MLflow UI shows **403** | Start the server with the full command from step 1, including `--allowed-hosts` and `--cors-allowed-origins`. |
| A port does not open | Open the **Ports** tab, find **MLflow UI** (5000), **f1 API** (8000) or **Locust UI** (8089) and click the globe icon. If the port is not listed, click **Forward a Port** and type the number. |
| The API or the tests stop with `Registered Model with name=f1-points-finish not found` or `Registered model alias champion not found` | There is no champion yet. Do step 2. |
| The API or the tests stop with `Max retries exceeded` or `Connection refused` on port 5000 | The MLflow server is not running. Start it (step 1), then start the API again. |
| `[Errno 98] address already in use` or `bind: address already in use` on port 8000 | Something else uses port 8000: the uvicorn API of step 3, or a container. Stop uvicorn with **Ctrl+C**, or run `docker stop f1-api`. |
| `Cannot connect to the Docker daemon` | Docker is still starting. Wait a minute and try again. If it does not help, rebuild the codespace (**Ctrl+Shift+P** → **Codespaces: Rebuild Container**). |
| `docker: Error response from daemon: Conflict. The container name "/f1-api" is already in use` | An old container with that name exists. Run `docker rm -f f1-api`, then run the container again. |
| The container starts, then stops with `Connection refused` to `127.0.0.1:5000` | You left out `--network host`. Without it, the container cannot reach the MLflow server. |
| `/health` still shows the old version after `promote.py` | That is expected. The API loads the model once. Run `curl -s -X POST http://127.0.0.1:8000/admin/reload`, or restart the API. |
| `/admin/reload` answers `reload failed, still serving version ...` | The API could not load the new champion and kept the old one. Read the reason in the message. The MLflow server must be running. |
| `check_slo.py` says `has no row for POST /v1/predict` | Locust sent no request: the API was not running at `http://127.0.0.1:8000`. Start the container (step 6) and run the load test again. |
| The good model breaks the SLO | The codespace was busy: close the Locust web UI and other load tests, wait a minute and run `load_test.sh` again. |
| pytest says `import file mismatch` | You collected `test_api.py` and `solution/test_api.py` in one run. Run one file at a time. |
| You pushed to your fork, but no workflow run started | Actions are off in a new fork. Open the **Actions** tab of your fork and click **I understand my workflows, go ahead and enable them**. Then start a run with **Run workflow** (step 9). |
| There is no **Run workflow** button | Make `05-serve-model` the default branch of your fork (**Settings → General → Default branch**), then reload the **Actions** page. |
| The push is rejected with `refusing to allow ... to create or update workflow` | You changed a file in `.github/workflows/`. Undo your change to that file, commit, and push again. |
| You closed the browser tab | Go to [github.com/codespaces](https://github.com/codespaces) and open your codespace again. Your work is still there. Start the MLflow server and the container again. |

When you finish, stop the codespace (**Codespaces** menu at the bottom left → **Stop Current Codespace**) so it does not use your hours.

## Tools in the codespace

The codespace runs Python 3.12 and installs the tools from [`.devcontainer/requirements.txt`](.devcontainer/requirements.txt):

| Task | Tools |
|---|---|
| Data exploration | pandas, DuckDB, JupyterLab, matplotlib, seaborn, ydata-profiling, and the Data Wrangler and Rainbow CSV extensions (right-click a CSV → **Open in Data Wrangler**) |
| Data versioning | DVC and the DVC extension |
| Data quality | pandera and Great Expectations for validation, Evidently for drift and training-serving skew reports |
| Model training | scikit-learn |
| Experiment tracking | MLflow tracking and Model Registry (the codespace forwards port 5000 for the MLflow UI) |
| Quality gates and CI | pytest for the gates, GitHub Actions for the release pipeline ([`.github/workflows/release.yml`](.github/workflows/release.yml)) |
| Model serving | FastAPI and uvicorn for the API (port 8000), Docker (docker-in-docker) for the container image, pytest with FastAPI's TestClient for the contract tests |
| Load testing and CI | Locust (web UI on port 8089), GitHub Actions for the serving check ([`.github/workflows/serve.yml`](.github/workflows/serve.yml)) |

## Datasets

| Folder | Dataset | Target |
|---|---|---|
| [`f1/data/`](f1/data/) | Synthetic Grand Prix championship: 10 fictional teams, 24 circuits, five seasons, 2,400 car-race rows | `points_finish` |
| [`spl/data/`](spl/data/) | Synthetic Saudi league: 18 clubs per season, 34 rounds, five seasons, 3,060 club-match rows | `win` |

**All results, players, teams and drivers are synthetic.** They were generated from seed 2026 and describe no real season or person. They are not a basis for betting, club or team decisions, or claims about anyone real.

Each dataset folder has a `README.md` with the file list, the column dictionary, which columns are known before versus after the event (leakage), and the facts you can check. Besides the main training and holdout CSV, each folder holds the 2026 provisional and final results, a corrections file, and `scenarios/*.json` windows for monitoring exercises (a reference window, an input-drift window and a training-serving-skew window).
