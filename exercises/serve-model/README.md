# Lesson 05: serve the model and roll back a faulty release

In lesson 04 a pipeline made a model the production model, `@champion`, in the MLflow Model Registry. Nobody can use it yet: it is a file in the registry. In this lesson you put it behind an HTTP API, the way an application or a race engineer's dashboard would call it. You test the API contract, package the API as a Docker image, and load-test it against a service-level objective. Then you release a model that passes every lesson 04 quality gate but is too slow to serve, watch the load test fail, and roll it back.

Time: about 90 minutes.

| Part | What you do | What it shows |
|---|---|---|
| Serving architecture | Run the API, call it, read its contract | The API loads `@champion` once, at start-up, and says which version answers |
| Contract tests | Complete three tests with FastAPI's TestClient | Clients can rely on the fields, the types and the errors |
| Docker | Build the image and run the container | The same API, packaged to run anywhere |
| Load test | Run Locust and check the SLO | How fast the API answers, measured, against a written objective |
| Faulty release and rollback | Promote a huge forest, reload, load-test, roll back | Accuracy gates are not enough. Serving checks belong in the release too. |
| GitHub Actions | Run the serving check in your fork | CI blocks the slow model, the same way the gates blocked the leaky one |

Run every command from the repository root, `/workspaces/mlops-training`.

## What you will have at the end

- An API that serves `f1-points-finish@champion`, in your codespace and as a Docker container.
- Eight contract tests in `test_api.py`, three of them written by you.
- A load test with a pass or fail result against the SLO in `slo.yaml`.
- A rollback that you proved: the SLO breaks with the faulty model and is met again after the rollback.
- A GitHub Actions run where the serving check passes, and a run where it blocks the faulty model.

## The serving architecture

```
                          MLflow server (port 5000)
                          f1-points-finish  @champion -> version N
                                   ^
                                   | at start-up and on POST /admin/reload:
                                   | find the version behind @champion, download it
                                   |
client --- POST /v1/predict --->  API (app.py, port 8000)  --- predictions + model version --->
```

| File | What it does |
|---|---|
| [`app.py`](app.py) | The API. A FastAPI application with three endpoints. You do not need to change it. |
| [`conftest.py`](conftest.py) | Starts the API in the test process for the contract tests. You do not need to change it. |
| [`test_api.py`](test_api.py) | The contract tests. **You complete TODO 1 to TODO 3.** |
| [`Dockerfile`](Dockerfile), [`requirements-serve.txt`](requirements-serve.txt) | The container image of the API, with pinned package versions |
| [`locustfile.py`](locustfile.py) | The load test: each simulated user asks for the predictions of one 2025 race (20 cars) at a time |
| [`slo.yaml`](slo.yaml) | The service-level objective: how fast and how reliable the API must be under the load test |
| [`load_test.sh`](load_test.sh) | Runs Locust without its web UI, then [`check_slo.py`](check_slo.py), which exits 1 when the SLO is broken |
| [`examples/huge_forest.yaml`](examples/huge_forest.yaml) | A candidate for the lesson 04 pipeline: 3000 trees of depth 12 |
| [`.github/workflows/serve.yml`](../../.github/workflows/serve.yml) | Runs the whole serving check on GitHub Actions |

The API has three endpoints:

| Endpoint | What it does |
|---|---|
| `GET /health` | Says that the API is up, and which model name, version and alias it serves |
| `POST /v1/predict` | Takes a batch of 1 to 1000 entries and returns one prediction (0 or 1) and one probability per entry, and the model version that answered |
| `POST /admin/reload` | Loads the model behind `@champion` again. The old model answers until the new one is loaded. |

Some design choices, and why:

- **The image holds the code, not the model.** The API loads the model from the registry when it starts. A new model version does not need a new image, and the registry stays the one place that says which model is in production.
- **The model is loaded once.** A FastAPI *lifespan* handler loads it before the API accepts the first request. Loading takes seconds; a prediction takes milliseconds. If the model cannot be loaded, the API does not start, so it never answers without a model.
- **The answer names the model version.** When a prediction looks wrong, you can find the exact model that made it.
- **The alias is read at load time only.** When `promote.py` moves `@champion`, the running API keeps the version it loaded. You tell it to load again with `POST /admin/reload`, or you restart it. You see why that matters in step 8.
- **`/v1/` is the version of the contract, not of the model.** The contract is the list of inputs, their types and ranges, and the fields of the answer. Model versions 1, 2 and 3 can all answer `/v1/predict`. A model that needs a different input needs a new contract, `/v2/`. The API refuses to load a model whose inputs do not match the contract.
- **One process, one model in memory.** That is enough for one codespace. More traffic needs more processes or more containers, and each one holds its own copy of the model.

The contract checks every entry before the model sees it. The rules are the lesson 02 schema from [`f1/data/README.md`](../../f1/data/README.md):

| Input | Type | Allowed values |
|---|---|---|
| `grid` | integer | 1 to 20 |
| `quali_gap_ms` | integer | 0 or more |
| `driver_form` | number | 1 to 20 |
| `team_form` | number | 0 or more |
| `team_dnf_rate` | number | 0 to 1 |
| `rain_prob` | number | 0 to 1 |
| `circuit_type` | text | `street`, `permanent` or `high_speed` |

Any other field is an error, not ignored. A client that sends `finish_position` has a bug: it sends a value that nobody knows before the race.

## Step 1: start the MLflow server

Open a terminal and run the same command as in lessons 02 to 04:

```bash
mlflow server \
  --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./mlartifacts \
  --allowed-hosts "*.app.github.dev,localhost:*,127.0.0.1:*" \
  --cors-allowed-origins "https://*.app.github.dev"
```

Leave this terminal running. Open the **Ports** tab and click the globe icon next to **MLflow UI**. Open a second terminal (**Terminal → New Terminal**) for the other commands.

## Step 2: make sure there is a champion

This codespace is new, so its registry is empty. Run the lesson 04 pipeline with the good candidate. Use the lesson 04 reference gates, so that all seven gates run:

```bash
GATES=exercises/quality-gates/solution/test_gates.py bash exercises/quality-gates/run_pipeline.sh
```

> **Check:** the output ends with seven `PASSED` gates (accuracy 0.842, roc_auc 0.907, rookie_accuracy 0.646) and
> `PROMOTED: f1-points-finish version 1 is now @champion (previous champion: none).`

The version numbers in this lesson are for a new codespace. If you registered more versions in this codespace already, your numbers are higher. That is fine.

## Step 3: run the API

Start the API in the second terminal:

```bash
uvicorn app:app --app-dir exercises/serve-model --port 8000
```

> **Check:** the log says `Serving f1-points-finish version 1 (models:/f1-points-finish@champion)`, then `Application startup complete.`

Leave it running. Open a third terminal for the next commands.

Open the **Ports** tab, click the globe icon next to **f1 API** (port 8000) and add `/docs` to the address in the browser. FastAPI made this page from `app.py`: it is the API contract. Open **POST /v1/predict** and **Schemas → Entry**: the ranges in the table above are there.

## Step 4: call the API

Ask the API which model it serves:

```bash
curl -s http://127.0.0.1:8000/health
```

> **Check:** `{"status":"ok","model_name":"f1-points-finish","model_version":"1","alias":"champion",...}`

Ask for two predictions: the pole-sitter and the last car on the grid at the first race of 2025:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/predict -H 'Content-Type: application/json' -d '{"entries": [
  {"grid": 1, "quali_gap_ms": 0, "driver_form": 2.33, "team_form": 27.0, "team_dnf_rate": 0.083, "rain_prob": 0.24, "circuit_type": "permanent"},
  {"grid": 20, "quali_gap_ms": 1981, "driver_form": 17.0, "team_form": 0.0, "team_dnf_rate": 0.0, "rain_prob": 0.24, "circuit_type": "permanent"}
]}'
```

> **Check:** `{"model_name":"f1-points-finish","model_version":"1","predictions":[1,0],"probabilities":[0.9582...,0.0091...]}`

Now send a bad entry: grid 21, a circuit type that does not exist, no `rain_prob`, and an after-race column:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/predict -H 'Content-Type: application/json' -d '{"entries": [
  {"grid": 21, "quali_gap_ms": 0, "driver_form": 2.33, "team_form": 27.0, "team_dnf_rate": 0.083, "circuit_type": "oval", "finish_position": 1}
]}'
```

> **Check:** status 422 and one line per problem:
>
> ```
> {"detail":["entries.0.grid: Input should be less than or equal to 20",
>            "entries.0.rain_prob: Field required",
>            "entries.0.circuit_type: Input should be 'street', 'permanent' or 'high_speed'",
>            "entries.0.finish_position: Extra inputs are not permitted"]}
> ```

The model never saw this entry. The API stopped it at the door and told the client what to fix. Without the check, the model would have answered with a number, and nobody would know it was nonsense.

## Step 5: write the contract tests

A contract test checks what clients rely on: the URLs, the fields, the types and the errors. It does not check how good the model is. The quality gates did that.

Open [`test_api.py`](test_api.py). The first five tests are done. Read them: each test gets a `client` from [`conftest.py`](conftest.py), sends a request and checks the answer. `client` is FastAPI's `TestClient`. It runs the API inside pytest, without uvicorn and without a network, and it runs the lifespan handler, so the tests use the real `@champion` from MLflow. Run the tests:

```bash
pytest exercises/serve-model/test_api.py -rs --tb=line
```

> **Check:** `5 passed, 3 skipped`. The three skipped tests are the TODOs.

Complete **TODO 1 to TODO 3**:

| TODO | Test | What it checks |
|---|---|---|
| 1 | `test_rejects_an_out_of_range_grid` | grid 0 and grid 21 get 422, with a message about `entries.0.grid` |
| 2 | `test_rejects_an_unknown_circuit_type` | `"oval"` gets 422, and the message lists the three allowed circuit types |
| 3 | `test_answer_matches_the_batch` | 20 entries in, 20 predictions and 20 probabilities out, from the version that `/health` names |

Delete the `pytest.skip(...)` line in each test when you write it. Use the curl output of step 4 to see what the messages look like. Run the tests again.

> **Check:** `8 passed`.

To see that a test protects something, break the contract: in `app.py`, change `le=20` of `grid` to `le=30` and run the tests. Your TODO 1 test fails, because grid 21 now gets status 200. Change it back.

## Step 6: build and run the Docker image

Stop the API in its terminal with **Ctrl+C**: the container needs port 8000. Build the image:

```bash
docker build -t f1-api:1 exercises/serve-model
```

The first build downloads the Python base image and installs the packages from [`requirements-serve.txt`](requirements-serve.txt). It takes a few minutes. `requirements-serve.txt` pins the same versions as the codespace, so the container loads the model with the scikit-learn that trained it. It uses `mlflow-skinny`: MLflow without the server and the UI, enough to load a model.

> **Check:** `docker image ls f1-api` shows the image `f1-api` with the tag `1`.

Run the container:

```bash
docker run --rm --name f1-api --network host f1-api:1
```

`--network host` lets the container use the network of the codespace. Inside the container, `127.0.0.1:5000` is then your MLflow server, and the API answers on port 8000 of the codespace, so the **f1 API** port works as before. Without `--network host`, `127.0.0.1` inside the container is the container itself, and the API cannot find MLflow.

> **Check:** the container log says `Serving f1-points-finish version 1 (models:/f1-points-finish@champion)`. In the other terminal, `curl -s http://127.0.0.1:8000/health` gives the same answer as in step 4.

Leave the container running. You use it for the rest of the lesson.

> **Not in a codespace?** `--network host` works this way on Linux. Docker Desktop on a Mac or Windows runs containers in a virtual machine, so the "host" is that machine, not your laptop. There, publish the port and point the API at your laptop instead:
> `docker run --rm --name f1-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 f1-api:1`,
> and add `host.docker.internal:*` to `--allowed-hosts` when you start the MLflow server. Without it, MLflow answers `Invalid Host header`.

## Step 7: load-test the API

A test with one request shows that the API works. A load test shows how it behaves when many clients call it at the same time. You use [Locust](https://locust.io). [`locustfile.py`](locustfile.py) describes one user: a race engineer who asks for the predictions of a whole race, 20 cars, then waits 0.5 to 1.5 seconds and asks again. Ten users send about 10 requests per second.

**With the web UI.** Start Locust:

```bash
locust -f exercises/serve-model/locustfile.py --host http://127.0.0.1:8000
```

Open the **Ports** tab and click the globe icon next to **Locust UI** (port 8089). Set **Number of users** to `10` and **Ramp up** to `5`, and click **Start**. Watch the **Statistics** and **Charts** tabs for a minute. Then click **Stop**, and press **Ctrl+C** in the Locust terminal.

> **Check:** the **Failures** column stays at 0, and the 95th percentile of `/v1/predict` stays far below 500 ms.

**Without the UI, against the SLO.** A service-level objective (SLO) writes down how good the service must be. [`slo.yaml`](slo.yaml) holds it, and the load that it is defined for:

| Objective | Threshold | Measured with the good model | Why this number |
|---|---:|---:|---|
| 95th percentile latency of `POST /v1/predict` | ≤ 500 ms | 190 ms in a container with 2 CPUs, like a codespace; 53 ms on a 10-core laptop | A person waits for the answer. Half a second still feels immediate. The good model keeps more than half of it in reserve, for a busy codespace or a busier day. |
| Failure rate | ≤ 1 % | 0 % | A failed request is a race with no prediction. One in a hundred is the most a dashboard should show. |
| Requests in 30 seconds | ≥ 150 | 241 to 263 | 10 users ask for about 250. Fewer than 150 means the API could not keep up with the load. |

The 95th percentile is the time within which 95 of 100 requests answer. It shows what the slow requests feel like. The average hides them.

Run the load test and the SLO check:

```bash
bash exercises/serve-model/load_test.sh
```

It runs Locust for 30 seconds with 10 users, without the UI, and writes the results to `results/`. Then [`check_slo.py`](check_slo.py) reads `results/locust_stats.csv` and compares the `POST /v1/predict` row with `slo.yaml`.

> **Check:** the output ends like this. Your numbers differ: they depend on the machine.
>
> ```
> SLO check for POST /v1/predict (results/locust_stats.csv):
>   PASS  requests            250   at least 150
>   PASS  p95 latency      190 ms   at most 500 ms
>   PASS  failure rate      0.00%   at most 1.00%
> SLO MET
> ```

`results/locust.html` is the full Locust report. Right-click it and choose **Download** to open it in your browser.

## Step 8: release a faulty model and roll it back

[`examples/huge_forest.yaml`](examples/huge_forest.yaml) proposes a forest of 3000 trees of depth 12, ten times as many trees as the champion. Propose it with the lesson 04 pipeline:

```bash
GATES=exercises/quality-gates/solution/test_gates.py bash exercises/quality-gates/run_pipeline.sh exercises/serve-model/examples/huge_forest.yaml
```

> **Check:** all seven gates pass: accuracy 0.840, roc_auc 0.906, margin 0.035, rookie_accuracy 0.667. Then
> `PROMOTED: f1-points-finish version 2 is now @champion (previous champion: 1).`

It is as accurate as the champion, and better for rookies. Every gate that lesson 04 wrote is happy.

Ask the API which model it serves:

```bash
curl -s http://127.0.0.1:8000/health
```

> **Check:** `"model_version":"1"`. The alias moved, but the running API still serves the model it loaded at start-up.

Tell the API to load `@champion` again:

```bash
curl -s -X POST http://127.0.0.1:8000/admin/reload
```

> **Check:** `{"model_name":"f1-points-finish","previous_version":"1","model_version":"2","alias":"champion",...}`. It takes a few seconds: the model file is 121 MB, against 11 MB for version 1.

Call it once, as a quick smoke test. Repeat the two-car `curl` of step 4.

> **Check:** the answer is right (`"predictions":[1,0]`) and says `"model_version":"2"`. It takes a fraction of a second. One request looks fine.

Now run the load test:

```bash
bash exercises/serve-model/load_test.sh
```

> **Check:** `SLO BROKEN`. In a container with 2 CPUs we measured:
>
> ```
>   FAIL  requests             75   at least 150
>   FAIL  p95 latency     4300 ms   at most 500 ms
>   PASS  failure rate      0.00%   at most 1.00%
> SLO BROKEN: requests, p95 latency
> ```

Each request now walks through 3000 trees instead of 300. Alone, that takes a few hundred milliseconds. With ten users, the requests queue behind each other, and the slowest wait seconds. Nothing failed, and every answer was right. The model is just too slow for this service.

Roll back with the lesson 04 script, then reload:

```bash
python exercises/quality-gates/promote.py --rollback --approver "<your name>"
curl -s -X POST http://127.0.0.1:8000/admin/reload
```

> **Check:** `ROLLED BACK: f1-points-finish version 1 is @champion again (version 2 removed by <your name>).`, then `"previous_version":"2","model_version":"1"`.

Run the load test again:

```bash
bash exercises/serve-model/load_test.sh
```

> **Check:** `SLO MET` again, with a p95 latency like the one in step 7.

That is the milestone of this lesson: a versioned API, and a rollback you proved with a measurement. The quality gates checked accuracy, and accuracy was fine. The fault was in serving. **A release needs serving checks too**: the contract tests and the load test belong in the release pipeline, next to the quality gates.

## Step 9: run the serving check on GitHub Actions

The workflow [`serve.yml`](../../.github/workflows/serve.yml) runs everything you just did, in one job:

| Step | What it does |
|---|---|
| Start the MLflow server | An MLflow server for this run only, with its registry in `sqlite:///mlflow.db` |
| 1. Promote the candidate | The lesson 04 pipeline with the reference gates. The candidate becomes version 1, `@champion`. |
| 2. Contract tests | **Your** `test_api.py` |
| 3. Build the Docker image | `docker build` |
| 4. Run the container | `docker run --network host`, then waits for `/health` and calls `/v1/predict` once |
| 5. Load test and SLO check | `load_test.sh`. The job fails when the SLO is broken. |

It writes the SLO table to the run page and keeps `results/` as the artifact `load-test`. It is a separate workflow from `release.yml`: the release workflow decides **which model** may be champion; this one checks that the champion **can be served**. A real pipeline runs this check before the promotion, or before traffic reaches a new version.

1. **Commit your work.**

   ```bash
   git add exercises/serve-model
   git commit -m "Write the contract tests"
   ```

2. **Push to your fork.** Open **Source Control** and click **Sync Changes** (or **Publish Branch**). If you made a fork in lesson 04, the codespace pushes there; otherwise click **Create Fork**. If this is a new fork, open its **Actions** tab and enable the workflows, as in lesson 04 step 5.
3. **Make `05-serve-model` the default branch of your fork** (**Settings → General → Default branch**), so that GitHub shows the **Run workflow** button.
4. Your push changed `exercises/serve-model/`, so it started the workflow **serve**. If it did not (Actions were still off), open **Actions → serve → Run workflow** and keep the candidate `exercises/quality-gates/candidate.yaml`.

> **Check:** the job **Serve and load-test** succeeds in about four minutes. The run page shows `Service-level objective: SLO MET` and the table, with 0.00 % failures.

Now try the faulty model. Open **Actions → serve → Run workflow**, set the candidate to `exercises/serve-model/examples/huge_forest.yaml`, and click **Run workflow**.

> **Check:** step **1. Promote the candidate** passes: the huge forest passes all seven gates. Step **5. Load test and SLO check** fails with `SLO BROKEN`, and the job fails.

## Discuss

1. The huge forest passed every quality gate and was better for rookies. Where would you check latency: as a gate in `release.yml` before promotion, or on the running service after deployment? What does each catch that the other misses?
2. After the promotion, the API kept serving version 1 until you called `/admin/reload`. Is that a bug or a safety feature? Compare three ways to pick up a new champion: reload on command, reload automatically every minute, restart the container.
3. Anyone who can reach the API can call `/admin/reload`. Who should be allowed to, and what could go wrong if anyone can?
4. Who should choose the numbers in `slo.yaml`: the data scientists, the team that runs the API, or the people who use the predictions? What would you ask them?

## Stretch

- Run the faulty model side by side: start a second container with `-e MODEL_URI=models:/f1-points-finish/2 -e PORT=8001 --name f1-api-2`, and load-test it with `API_URL=http://127.0.0.1:8001 bash exercises/serve-model/load_test.sh`. This is how a canary release compares a new version with the old one before it gets real traffic.
- Capacity: the forests were trained with `n_jobs=-1`, so each prediction spreads over every CPU. With ten requests at the same time that may cost more than it gains. In `load_model`, set `model[-1].n_jobs = 1` after loading, rebuild the image and measure both models again. Does the huge forest meet the SLO now? Is that a reason to release it?
- Try to serve a model that breaks the contract: train `exercises/quality-gates/examples/leaky.yaml` with `train_candidate.py` (no gates, no promotion) and start the API with `MODEL_URI=models:/f1-points-finish/<its version>`. Why does the API refuse to start?
- Add the load test to the release: in a copy of `release.yml`, run the container and `load_test.sh` in the job **Quality gates**, after the gates and before **Promote to champion**.

## Stuck?

There is a reference solution in [`solution/test_api.py`](solution/test_api.py). Try the TODOs first. To run it:

```bash
pytest exercises/serve-model/solution/test_api.py
```

Run one test file at a time. pytest cannot collect `test_api.py` and `solution/test_api.py` in one run, because the two files have the same name.
