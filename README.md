# mlops-training · Stage 02: MLflow

Synthetic datasets for hands-on MLOps training: data validation, leakage, drift, training-serving skew and delayed labels.

**In this stage** you start an MLflow tracking server, version the F1 race data with DVC, check it with pandera, and log the data version and the check results to MLflow. Then you break the data on purpose, see the checks catch it, and roll back to the good version.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majlisofai/mlops-training?ref=02-mlflow)

## Trainees: start here

1. **Open your codespace.** Click the badge above. Check that the branch is **`02-mlflow`**, then click **Create codespace**. A copy of VS Code opens in your browser. You need a GitHub account. The codespace runs on your account and uses your free monthly Codespaces hours.
2. **Wait for the setup.** The first start takes a few minutes, because the codespace installs Python packages. Wait until the terminal says the setup has finished before you run any command.
3. **Open the exercise.** In the file explorer, open [`exercises/mlflow/README.md`](exercises/mlflow/README.md). Right-click it and choose **Open Preview** to read it formatted.
4. **Do the six steps** in the exercise, in order:

   | Step | What you do | You are done when |
   |---|---|---|
   | 1 | Start the MLflow server and open the MLflow UI | The MLflow UI opens in a browser tab |
   | 2 | Move `f1/data/races.csv` into DVC | `races.csv.dvc` shows md5 `199d7bda…` |
   | 3 | Complete TODO 1 to TODO 5 in `exercises/mlflow/log_data_checks.py` and run it | The script says `validation passed` |
   | 4 | Find the run in the MLflow UI | You can see the data version, the metrics and the artifacts |
   | 5 | Corrupt the data and run the checks again | The script says `validation failed` |
   | 6 | Roll back with DVC | The checks pass again on md5 `199d7bda…` |

5. **Discuss** the three questions at the end of the exercise with your group.

**Rules for this stage**

- Run every command from the repository root, `/workspaces/mlops-training`.
- Keep the terminal with the MLflow server open while you work. Use a second terminal for the other commands (**Terminal → New Terminal**).
- Commit in your codespace if the exercise tells you to, but **do not push**.
- Try the TODOs before you open the reference solution in `exercises/mlflow/solution/`.

**If something goes wrong**

| Problem | Fix |
|---|---|
| `mlflow: command not found` | The setup has not finished. Wait, or run `pip install -r .devcontainer/requirements.txt`. |
| The MLflow UI shows **403** | Start the server with the full command from step 1, including `--allowed-hosts` and `--cors-allowed-origins`. |
| The MLflow UI does not open | Open the **Ports** tab, find **MLflow UI** (port 5000) and click the globe icon. |
| The script says `races.csv.dvc not found` | Do step 2 first. |
| The script seems to hang, then after about 4 minutes fails with `MlflowException: API request ... Max retries exceeded` | The MLflow server is not running. Press **Ctrl+C**, start the server again (step 1), then run the script again. |
| You closed the browser tab | Go to [github.com/codespaces](https://github.com/codespaces) and open your codespace again. Your work is still there. |

When you finish, stop the codespace (**Codespaces** menu at the bottom left → **Stop Current Codespace**) so it does not use your hours.

## Tools in the codespace

The codespace runs Python 3.12 and installs the tools from [`.devcontainer/requirements.txt`](.devcontainer/requirements.txt):

| Task | Tools |
|---|---|
| Data exploration | pandas, DuckDB, JupyterLab, matplotlib, seaborn, ydata-profiling, and the Data Wrangler and Rainbow CSV extensions (right-click a CSV → **Open in Data Wrangler**) |
| Data versioning | DVC and the DVC extension |
| Data quality | pandera and Great Expectations for validation, Evidently for drift and training-serving skew reports |
| Experiment tracking | MLflow (the codespace forwards port 5000 for the MLflow UI) |

## Datasets

| Folder | Dataset | Target |
|---|---|---|
| [`f1/data/`](f1/data/) | Synthetic Grand Prix championship: 10 fictional teams, 24 circuits, five seasons, 2,400 car-race rows | `points_finish` |
| [`spl/data/`](spl/data/) | Synthetic Saudi league: 18 clubs per season, 34 rounds, five seasons, 3,060 club-match rows | `win` |

**All results, players, teams and drivers are synthetic.** They were generated from seed 2026 and describe no real season or person. They are not a basis for betting, club or team decisions, or claims about anyone real.

Each dataset folder has a `README.md` with the file list, the column dictionary, which columns are known before versus after the event (leakage), and the facts you can check. Besides the main training and holdout CSV, each folder holds the 2026 provisional and final results, a corrections file, and `scenarios/*.json` windows for monitoring exercises (a reference window, an input-drift window and a training-serving-skew window).
