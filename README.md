# mlops-training · Lesson 04: quality gates and controlled promotion

Synthetic datasets for hands-on MLOps training: data validation, leakage, drift, training-serving skew and delayed labels.

**In this lesson** you write the release requirements for the F1 points-finish model and turn them into automated quality gates. A pipeline validates the data, trains the candidate model, runs the gates and promotes the model to `@champion` in the MLflow Model Registry only when every gate passes. You watch the lesson 03 cheating model slip through a gate that is not written yet, write the gate, and block it. Then you run the pipeline on GitHub Actions in your own fork, approve the promotion yourself, and roll back a bad release.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majlisofai/mlops-training?ref=04-quality-gates)

## Trainees: start here

1. **Open your codespace.** Click the badge above. Check that the branch is **`04-quality-gates`**, then click **Create codespace**. A copy of VS Code opens in your browser. You need a GitHub account. The codespace runs on your account and uses your free monthly Codespaces hours.
2. **Wait for the setup.** The first start takes a few minutes, because the codespace installs Python packages. Wait until the terminal says the setup has finished before you run any command.
3. **Open the lesson.** In the file explorer, open [`exercises/quality-gates/README.md`](exercises/quality-gates/README.md). Right-click it and choose **Open Preview** to read it formatted.
4. **Do the eight steps** in the lesson, in order:

   | Step | What you do | You are done when |
   |---|---|---|
   | 1 | Start the MLflow server and open the MLflow UI | The MLflow UI opens in a browser tab |
   | 2 | Run the pipeline with the good candidate | `PROMOTED: f1-points-finish version 1 is now @champion`, with 4 gates passed and 3 not checked |
   | 3 | Propose the leaky model | It is promoted too: version 2 is `@champion`, with accuracy 1.000 |
   | 4 | Complete TODO 1 to TODO 3 in `exercises/quality-gates/test_gates.py` and propose three bad models | The leaky, weak and stumps candidates are each blocked at step 3 of the pipeline |
   | 5 | Push to your own fork, enable Actions, create the `production` environment | Your fork has the branch `04-quality-gates`, Actions enabled and the `production` environment with you as reviewer |
   | 6 | Run the pipeline on GitHub Actions and approve the promotion | Seven gates PASS, and the job **Promote to champion** says `Approved by <your-user>` |
   | 7 | Run the workflow with the leaky candidate | The job **Quality gates** fails and **Promote to champion** is skipped |
   | 8 | Roll back in your codespace | Version 1 is `@champion` again |

5. **Discuss** the four questions at the end of the lesson with your group.

**Rules for this lesson**

- Run every command from the repository root, `/workspaces/mlops-training`.
- Keep the terminal with the MLflow server open while you work. Use a second terminal for the other commands (**Terminal → New Terminal**).
- In this lesson you **push to your own fork** (step 5). You cannot push to `majlisofai/mlops-training`.
- Do not change `criteria.yaml` to make a candidate pass. Do not change `.github/workflows/release.yml`.
- Try the TODOs before you open the reference solution in `exercises/quality-gates/solution/`.

**If something goes wrong**

| Problem | Fix |
|---|---|
| `mlflow: command not found`, `No module named 'sklearn'` or `No module named pytest` | The setup has not finished. Wait, or run `pip install -r .devcontainer/requirements.txt`. |
| The MLflow UI shows **403** | Start the server with the full command from step 1, including `--allowed-hosts` and `--cors-allowed-origins`. |
| The MLflow UI does not open | Open the **Ports** tab, find **MLflow UI** (port 5000) and click the globe icon. |
| The pipeline seems to hang, then after about 4 minutes fails with `Max retries exceeded` | The MLflow server is not running. Press **Ctrl+C**, start the server again (step 1), then run the pipeline again. |
| The gates show `ERROR` with `Registered Model with name=f1-points-finish not found` or `alias candidate not found` | No candidate is registered yet. Run the pipeline, or `python exercises/quality-gates/train_candidate.py`, first. |
| `REFUSED: the gate report is for version 3, but @candidate is version 4` | You trained a new candidate after the gates ran. Run the gates again, or run the whole pipeline. |
| pytest says `import file mismatch` | You collected `test_gates.py` and `solution/test_gates.py` in one run. Run one file at a time. |
| `git push` fails with `Permission denied` or `403`, and no fork is offered | Push from **Source Control** (**Sync Changes** or **Publish Branch**) and click **Create Fork** when the codespace asks. |
| You pushed to your fork, but no workflow run started | Actions are off in a new fork. Open the **Actions** tab of your fork and click **I understand my workflows, go ahead and enable them**. Then start a run with **Run workflow** (step 6). |
| There is no **Run workflow** button | Make `04-quality-gates` the default branch of your fork (**Settings → General → Default branch**), then reload the **Actions** page. |
| **Promote to champion** ran without waiting for you | The `production` environment has no required reviewer. Add yourself (**Settings → Environments → production → Required reviewers**), then run the workflow again. |
| You cannot find the **Approve and deploy** button | Open the run page and click **Review deployments** at the top. Only a required reviewer of `production` sees it. |
| The push is rejected with `refusing to allow ... to create or update workflow` | You changed `.github/workflows/release.yml`. Undo your change to that file, commit, and push again. |
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
| Quality gates and CI | pytest for the gates, GitHub Actions for the release pipeline ([`.github/workflows/release.yml`](.github/workflows/release.yml)) |

## Datasets

| Folder | Dataset | Target |
|---|---|---|
| [`f1/data/`](f1/data/) | Synthetic Grand Prix championship: 10 fictional teams, 24 circuits, five seasons, 2,400 car-race rows | `points_finish` |
| [`spl/data/`](spl/data/) | Synthetic Saudi league: 18 clubs per season, 34 rounds, five seasons, 3,060 club-match rows | `win` |

**All results, players, teams and drivers are synthetic.** They were generated from seed 2026 and describe no real season or person. They are not a basis for betting, club or team decisions, or claims about anyone real.

Each dataset folder has a `README.md` with the file list, the column dictionary, which columns are known before versus after the event (leakage), and the facts you can check. Besides the main training and holdout CSV, each folder holds the 2026 provisional and final results, a corrections file, and `scenarios/*.json` windows for monitoring exercises (a reference window, an input-drift window and a training-serving-skew window).
