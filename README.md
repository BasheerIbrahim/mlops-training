# mlops-training · Lesson 03: build a model

Synthetic datasets for hands-on MLOps training: data validation, leakage, drift, training-serving skew and delayed labels.

**In this lesson** you train models that predict a points finish for each F1 car before the race, and you record every experiment in MLflow: the data version, the parameters, the metrics and the fitted model. You beat a simple baseline, tune a random forest, fall into a leakage trap on purpose, and register the best honest model in the MLflow Model Registry.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majlisofai/mlops-training?ref=03-build-model)

## Trainees: start here

1. **Open your codespace.** Click the badge above. Check that the branch is **`03-build-model`**, then click **Create codespace**. A copy of VS Code opens in your browser. You need a GitHub account. The codespace runs on your account and uses your free monthly Codespaces hours.
2. **Wait for the setup.** The first start takes a few minutes, because the codespace installs Python packages. Wait until the terminal says the setup has finished before you run any command.
3. **Open the lesson.** In the file explorer, open [`exercises/build-model/README.md`](exercises/build-model/README.md). Right-click it and choose **Open Preview** to read it formatted.
4. **Do the seven steps** in the lesson, in order:

   | Step | What you do | You are done when |
   |---|---|---|
   | 1 | Start the MLflow server and open the MLflow UI | The MLflow UI opens in a browser tab |
   | 2 | Complete TODO 1 to TODO 6 in `exercises/build-model/train.py` and run the grid-rule baseline | The run `grid-rule` shows accuracy 0.804 and `data.version` `199d7bda…` |
   | 3 | Train a logistic regression | The run `logreg-c1.0` shows accuracy 0.835 and has a logged model |
   | 4 | Train a random forest with three hyperparameter settings | Three forest runs, the best at accuracy 0.842 |
   | 5 | Add `finish_position` as an input | The run shows accuracy 1.000 and the tag `leakage = true` |
   | 6 | Compare the runs in the MLflow UI | You can name the best honest run and the subgroup it does worst on |
   | 7 | Register the best honest model | `f1-points-finish` version 1 is in the Model Registry |

5. **Discuss** the four questions at the end of the lesson with your group.

**Rules for this lesson**

- Run every command from the repository root, `/workspaces/mlops-training`.
- Keep the terminal with the MLflow server open while you work. Use a second terminal for the other commands (**Terminal → New Terminal**).
- Commit in your codespace if you like, but **do not push**.
- Try the TODOs before you open the reference solution in `exercises/build-model/solution/`.

**If something goes wrong**

| Problem | Fix |
|---|---|
| `mlflow: command not found` or `No module named 'sklearn'` | The setup has not finished. Wait, or run `pip install -r .devcontainer/requirements.txt`. |
| The MLflow UI shows **403** | Start the server with the full command from step 1, including `--allowed-hosts` and `--cors-allowed-origins`. |
| The MLflow UI does not open | Open the **Ports** tab, find **MLflow UI** (port 5000) and click the globe icon. |
| The script prints the scores, but no run appears in MLflow | Complete TODO 1 to TODO 6. Until then the script trains and scores the model but logs nothing. |
| `MlflowException: ... untrusted types` when the model is logged | Pass `skops_trusted_types=TRUSTED_TYPES` to `mlflow.sklearn.log_model` (TODO 6). |
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
| Model training | scikit-learn |
| Experiment tracking | MLflow tracking and Model Registry (the codespace forwards port 5000 for the MLflow UI) |

## Datasets

| Folder | Dataset | Target |
|---|---|---|
| [`f1/data/`](f1/data/) | Synthetic Grand Prix championship: 10 fictional teams, 24 circuits, five seasons, 2,400 car-race rows | `points_finish` |
| [`spl/data/`](spl/data/) | Synthetic Saudi league: 18 clubs per season, 34 rounds, five seasons, 3,060 club-match rows | `win` |

**All results, players, teams and drivers are synthetic.** They were generated from seed 2026 and describe no real season or person. They are not a basis for betting, club or team decisions, or claims about anyone real.

Each dataset folder has a `README.md` with the file list, the column dictionary, which columns are known before versus after the event (leakage), and the facts you can check. Besides the main training and holdout CSV, each folder holds the 2026 provisional and final results, a corrections file, and `scenarios/*.json` windows for monitoring exercises (a reference window, an input-drift window and a training-serving-skew window).
