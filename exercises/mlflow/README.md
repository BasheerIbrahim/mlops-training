# Exercise: track data versions and data checks in MLflow

Before you train a model, you need to know two things about the data: **which exact version** you used, and **whether it passed its checks**. In this exercise you start an MLflow tracking server, version `f1/data/races.csv` with DVC, run data validation checks with pandera, and log the version and the results to MLflow. Then you break the data, watch the checks catch it, and roll back.

Time: about 45 minutes.

## What you will have at the end

- An MLflow server running in your codespace, with the UI open in your browser.
- `races.csv` tracked by DVC. Its md5 hash is the data version.
- Two runs in the MLflow experiment `f1-data-checks`: one on the original data that **passes**, one on corrupted data that **fails**. Each run records the data version.

## Before you start

Open a codespace on the **`02-mlflow`** branch: click the badge in the top-level README and check that the branch is `02-mlflow`. Wait until the terminal says the setup has finished: the codespace installs MLflow, DVC and pandera on first start.

Run all commands from the repository root (`/workspaces/mlops-training`).

## Step 1: start the MLflow server

Open a terminal and run:

```bash
mlflow server \
  --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./mlartifacts \
  --allowed-hosts "*.app.github.dev,localhost:*,127.0.0.1:*" \
  --cors-allowed-origins "https://*.app.github.dev"
```

| Option | Why |
|---|---|
| `--backend-store-uri sqlite:///mlflow.db` | Runs, params, metrics and tags go into a SQLite file. |
| `--artifacts-destination ./mlartifacts` | Files you log (reports, the `.dvc` pointer) go into this folder. |
| `--allowed-hosts`, `--cors-allowed-origins` | MLflow rejects browser requests from unknown hosts. Codespaces serves the UI from a `*.app.github.dev` address, so allow it. Without these options the UI returns **403**. |

Leave this terminal running. Codespaces shows a notice for port 5000. Open the **Ports** tab and click the globe icon next to **MLflow UI**. The MLflow UI opens in a new browser tab.

## Step 2: version the data with DVC

Open a second terminal. `races.csv` is in Git at the moment. Move it into DVC:

```bash
dvc init
git rm --cached f1/data/races.csv
dvc add f1/data/races.csv
git add .dvc f1/data/races.csv.dvc f1/data/.gitignore
git commit -m "Track races.csv with DVC"
```

Open `f1/data/races.csv.dvc`. The `md5` value is the data version. If the file changes, the hash changes.

> **Check:** the md5 is `199d7bda0a7b641e0e68ccee5236a3a7`. If yours is different, the file was changed.

You commit only on your codespace's local branch. Do not push.

## Step 3: log the version and the checks to MLflow

Open [`log_data_checks.py`](log_data_checks.py). It already:

- defines the pandera schema: types, ranges, allowed values, one row per car per race, and `points_finish` matching `finish_position`;
- reads the md5 from the `.dvc` file;
- runs every check and collects the failures.

Complete **TODO 1 to TODO 5** in `log_to_mlflow()`. Then run:

```bash
python exercises/mlflow/log_data_checks.py f1/data/races.csv
```

> **Check:** the last line says `validation passed (0 failed checks, 0 failure cases)` and the exit code (`echo $?`) is `0`.

## Step 4: look at the run in MLflow

In the MLflow UI, open the experiment **f1-data-checks** and the run `races-199d7bda`. Find:

- **Tags:** `data.version`, `git.commit`, `validation.status = passed`
- **Parameters:** `data_md5`, `rows = 2400`, `columns = 23`
- **Metrics:** `failed_checks = 0`, `points_finish_rate = 0.5`, `dnf_rate = 0.10875`
- **Datasets used:** `races`, with its schema and a digest
- **Artifacts:** `data_version/races.csv.dvc` and `validation/report.json`

## Step 5: break the data

The data team plugs in a new timing feed. It sends `quali_gap_ms` in **seconds**, not milliseconds (see `f1/data/scenarios/serving_skew_window.json`). Simulate it:

```bash
python - <<'EOF'
import pandas as pd
df = pd.read_csv("f1/data/races.csv")
df["quali_gap_ms"] = df["quali_gap_ms"] / 1000
df.to_csv("f1/data/races.csv", index=False)
EOF
dvc add f1/data/races.csv
python exercises/mlflow/log_data_checks.py f1/data/races.csv
```

> **Check:** the md5 is now different, the script says `validation failed`, and the exit code is `1`.

In MLflow, select both runs and click **Compare**. Look at `data_md5`, `validation.status` and `failed_checks`. Open `validation/failure_cases.csv` in the failed run. Which check failed, and why?

## Step 6: roll back to the good version

```bash
git checkout f1/data/races.csv.dvc
dvc checkout f1/data/races.csv
python exercises/mlflow/log_data_checks.py f1/data/races.csv
```

> **Check:** the run passes again and its `data.version` is `199d7bda…` again, the same as the first run.

## Discuss

1. Which check caught the timing feed change? Would a range check (`quali_gap_ms >= 0`) catch it alone? What check would catch it if the feed sent whole seconds as integers?
2. The script exits with `1` on failed checks. Where would you use that exit code in a pipeline?
3. MLflow logs its own dataset digest, and DVC logs an md5. Why log both? Which one can you use to get the file back?

## Stretch

- Add a check that `laps_completed` is the full race distance for every `Finished` entry at the same race.
- Write a schema for `spl/data/matches.csv` (see `spl/data/README.md`) and log it to a second experiment.

## Stuck?

There is a reference solution in [`solution/log_data_checks.py`](solution/log_data_checks.py). Try the TODOs first.
