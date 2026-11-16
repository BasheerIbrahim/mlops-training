# Lesson 04: quality gates and controlled promotion

In lesson 03 you chose the best model by looking at the MLflow UI, and you registered it by hand. In this lesson a pipeline does it. You write the release requirements down, turn them into automated quality gates, and let a model become the production model (`@champion`) only when every gate passes and a person approves. You watch a cheating model slip through a gate that is not written yet, then you write the gate and block it. At the end the pipeline runs on GitHub Actions in your own fork, and you approve the promotion yourself.

Time: about 75 minutes.

| Part | What you do | What it shows |
|---|---|---|
| Local pipeline | Run validate → train → gates → promote in your codespace | A good model is promoted with a record of who and why |
| Leakage trap | Propose the lesson 03 leaky model | A gate that is not written checks nothing |
| Write the gates | Complete three gates and propose three bad models | Each bad model is blocked, each by a different gate |
| GitHub Actions | Push to your fork, approve the promotion, try the leaky model | A bad build is blocked; a good one needs approval |
| Rollback | Move `@champion` back | You can undo a bad release |

Run every command from the repository root, `/workspaces/mlops-training`.

## What you will have at the end

- Seven quality gates in `test_gates.py`, three of them written by you.
- A model version with the alias `@champion` and tags that record who approved it, when, the result of every gate and the previous champion.
- A GitHub Actions run in your fork where you approved the promotion, and a run where the gates blocked the leaky model.
- A rollback: `@champion` back on the honest model.

## The release requirements

A release requirement is a rule that every new model must meet before it may be used. Write the rules down **before** you look at the candidate, so that nobody bends them to fit a model they like. The rules for `f1-points-finish` are in [`criteria.yaml`](criteria.yaml):

| Requirement | Threshold | Grid rule | Honest lesson 03 models | Why this number |
|---|---:|---:|---:|---|
| Data passes validation | 0 failure cases | | | A model trained on broken data is broken. The lesson 02 schema. |
| Accuracy on 2025 | ≥ 0.82 | 0.804 | 0.833 to 0.842 | Above the rule, below every honest tuned model. The lesson 03 default forest (0.819) just misses it: its trees overfit. |
| Margin over the grid rule | ≥ 0.02 | 0 | 0.029 to 0.038 | About 10 more right answers out of 480 than a rule anyone can apply. A model must earn its cost. If the rule gets better on new data, the bar rises with it. |
| ROC AUC on 2025 | ≥ 0.88 | 0.893 | 0.902 to 0.908 | The model must rank the cars well, not only cut at 0.5. |
| Accuracy for rookies | ≥ 0.60 | 0.521 | 0.646 | Lesson 03 showed that every model is much worse for the 48 rookie entries. 0.60 is 29 of 48. The rule is barely better than a coin. |
| Forbidden features | none | | | The columns known only after the race (see [`f1/data/README.md`](../../f1/data/README.md)). A model that needs one can never run before a race. |

## The pipeline

```
validate data  →  train candidate  →  quality gates  →  promote
validate_data.py  train_candidate.py   test_gates.py     promote.py
```

The pipeline stops at the first step that fails. Nothing is promoted unless all four steps succeed.

| File | What it does |
|---|---|
| [`criteria.yaml`](criteria.yaml) | The release requirements |
| [`candidate.yaml`](candidate.yaml) | The model you propose: model type, hyperparameters, and `leak` (the lesson 03 trap) |
| [`examples/`](examples/) | Other candidates to try: `leaky.yaml`, `weak.yaml`, `stumps.yaml`, `logreg.yaml` |
| [`validate_data.py`](validate_data.py) | Step 1. Checks `races.csv` against the lesson 02 schema. |
| [`train_candidate.py`](train_candidate.py) | Step 2. Trains the candidate, logs the run in MLflow, registers a new version of `f1-points-finish` and points the alias `@candidate` at it. |
| [`test_gates.py`](test_gates.py) | Step 3. The quality gates, as pytest tests. **You complete TODO 1 to TODO 3.** |
| [`conftest.py`](conftest.py) | Loads the criteria, the 2025 data and `@candidate` for the gates, and writes the gate report `gate_report.json`. You do not need to change it. |
| [`promote.py`](promote.py) | Step 4. Refuses unless the gate report shows no failed gate. Moves `@champion` to the candidate and tags the version. `--rollback` moves it back. |
| [`run_pipeline.sh`](run_pipeline.sh) | Runs the four steps in your codespace |
| [`.github/workflows/release.yml`](../../.github/workflows/release.yml) | Runs the same steps on GitHub Actions |

Two aliases in the MLflow Model Registry do the work. `@candidate` is the version that is being checked. `@champion` is the version that is in use. Promotion moves `@champion`. It never retrains or copies the model.

The gates measure the model again on the 2025 holdout. They do not trust the metrics that the training script logged.

## Step 1: start the MLflow server

Open a terminal and run the same command as in lessons 02 and 03:

```bash
mlflow server \
  --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./mlartifacts \
  --allowed-hosts "*.app.github.dev,localhost:*,127.0.0.1:*" \
  --cors-allowed-origins "https://*.app.github.dev"
```

Leave this terminal running. Open the **Ports** tab and click the globe icon next to **MLflow UI**. Open a second terminal (**Terminal → New Terminal**) for the other commands.

The version numbers below are for a new codespace. If you already registered `f1-points-finish` in this codespace, your numbers are higher. That is fine.

## Step 2: run the pipeline with a good candidate

Open [`candidate.yaml`](candidate.yaml). It proposes the best honest model from lesson 03: a random forest with 300 trees, depth 8 and 5 rows per leaf. Change `proposed_by` to your GitHub user name. Then run the pipeline:

```bash
bash exercises/quality-gates/run_pipeline.sh
```

MLflow prints a warning about integer columns. You can ignore it.

> **Check:** the output ends like this (shortened):
>
> ```
> candidate-forest-n_estimators300-max_depth8-min_samples_leaf5: accuracy 0.842, f1 0.847, roc_auc 0.907 on 2025
> Registered f1-points-finish version 1 as @candidate (run ...)
> == 3/4 quality gates (exercises/quality-gates/test_gates.py)
> ....sss
> 4 passed, 3 skipped
> == 4/4 promote
> Gate report for f1-points-finish version 1:
>   PASSED       data_passes_validation       failure_cases 0
>   PASSED       model_predicts_0_or_1        rows 480
>   PASSED       accuracy                     accuracy 0.842
>   PASSED       roc_auc                      roc_auc 0.907
>   NOT CHECKED  beats_grid_rule
>   NOT CHECKED  no_forbidden_features
>   NOT CHECKED  rookie_accuracy
> WARNING: 3 gates were not checked: beats_grid_rule, no_forbidden_features, rookie_accuracy
> PROMOTED: f1-points-finish version 1 is now @champion (previous champion: none). Approved by <your name>.
> ```

In the MLflow UI, click **Models**, then `f1-points-finish`, then **Version 1**. It has the aliases `@candidate` and `@champion`, and the tags `promoted_by`, `promoted_at`, `previous_champion = none`, `gates = 4 passed, 3 skipped` and one `gate.<name>` tag per gate. That is the audit trail: anyone can see who released this model, when, and what was checked.

The three gates that say **NOT CHECKED** are the TODOs. promote.py lets a skipped gate through, with a warning. Watch what that costs in the next step.

## Step 3: propose the leaky model

[`examples/leaky.yaml`](examples/leaky.yaml) is the same forest, plus `leak: true`: it adds `finish_position` as an input, the lesson 03 leakage trap. Propose it:

```bash
bash exercises/quality-gates/run_pipeline.sh exercises/quality-gates/examples/leaky.yaml
```

> **Check:** `accuracy 1.000, f1 1.000, roc_auc 1.000`, then `4 passed, 3 skipped`, then
> `PROMOTED: f1-points-finish version 2 is now @champion (previous champion: 1).`

The cheating model is now the production model. Every gate that ran passed: it is very accurate on 2025, because it reads the answer. The gate that would catch it, `no_forbidden_features`, is a TODO, so it was skipped. **A gate that is not written checks nothing**, and a pipeline that passes is not proof that the model is good.

Leave version 2 as champion for now. You roll it back in step 8.

## Step 4: write the missing gates

Open [`test_gates.py`](test_gates.py). The first four gates are done. Read them: each gate is a pytest test that gets its data from fixtures (`predictions`, `holdout`, `criteria`, ...), records what it measured with `record_property`, and fails with a clear message. Complete **TODO 1 to TODO 3**:

| TODO | Gate | Requirement in `criteria.yaml` |
|---|---|---|
| 1 | `test_beats_grid_rule` | `min_margin_over_grid_rule` |
| 2 | `test_no_forbidden_features` | `forbidden_features` |
| 3 | `test_rookie_accuracy` | `min_accuracy_rookie` |

Delete the `pytest.skip(...)` line in each gate when you write it. `input_columns` (TODO 2) is the list of inputs in the model signature: the columns the model needs at prediction time.

Test your gates on the model that is `@candidate` now, the leaky version 2. You do not need to train again:

```bash
pytest exercises/quality-gates/test_gates.py -rs --tb=line
```

> **Check:** `1 failed, 6 passed`. The failure says `AssertionError: the model uses after-race columns: finish_position`.

Now propose three bad candidates. Each one should be blocked, each by a different gate:

```bash
bash exercises/quality-gates/run_pipeline.sh exercises/quality-gates/examples/leaky.yaml
bash exercises/quality-gates/run_pipeline.sh exercises/quality-gates/examples/weak.yaml
bash exercises/quality-gates/run_pipeline.sh exercises/quality-gates/examples/stumps.yaml
```

> **Check:** each run ends with `PIPELINE STOPPED at step 3/4 quality gates (...). Nothing was promoted.`
>
> | Candidate | Version | Blocked by | Measured |
> |---|---:|---|---|
> | `leaky.yaml`: the best forest + `finish_position` | 3 | `no_forbidden_features` | uses `finish_position` (accuracy 1.000) |
> | `weak.yaml`: 5 unlimited trees | 4 | `accuracy`, `roc_auc`, `beats_grid_rule` | accuracy 0.806, roc_auc 0.876, margin 0.002 |
> | `stumps.yaml`: 10 one-split trees | 5 | `rookie_accuracy` | rookie accuracy 0.583 (accuracy 0.829, roc_auc 0.886) |

Open `gate_report.md` after each run to see the whole table. The stumps model is the interesting one. It passes every overall check, and only the rookie gate stops it: overall accuracy hides a subgroup that the model serves badly.

`@champion` is still version 2, the leaky model. Gates stop new bad models. They do not undo a bad model that already got through. Step 8 does that.

## Step 5: set up your fork

The pipeline now runs on GitHub Actions. The workflow [`release.yml`](../../.github/workflows/release.yml) has two jobs:

| Job | What it does |
|---|---|
| **Quality gates** | Installs the packages from [`requirements-ci.txt`](requirements-ci.txt), then runs validate data → train candidate → gates. It writes the gate table to the run page and keeps the MLflow store as the artifact `registry`. |
| **Promote to champion** | Runs only after the gates pass. It uses the environment `production`, so it waits until a reviewer approves. Then it runs `promote.py` and keeps the updated store as the artifact `registry-promoted`. |

CI runs **your** `test_gates.py`, the file you just completed. In CI, MLflow stores everything in a file, `sqlite:///mlflow.db`, that lives only for that run. That is why the CI version number is always 1.

You cannot push to `majlisofai/mlops-training`, so you push to your own copy of it, a **fork**.

1. **Commit your work.** In the terminal:

   ```bash
   git add exercises/quality-gates
   git commit -m "Write the quality gates"
   ```

2. **Push and create the fork.** Open **Source Control** in the left bar and click **Sync Changes** (or **Publish Branch**). The codespace sees that you cannot push to `majlisofai/mlops-training` and asks whether to create a fork and push to it instead. Click **Create Fork**. The codespace creates `<your-user>/mlops-training`, pushes your branch there, and from now on pushes to your fork. `git remote -v` now lists your fork.
3. **Enable Actions in your fork.** Open `https://github.com/<your-user>/mlops-training` and click the **Actions** tab. GitHub disables workflows in a new fork until you allow them. Click **I understand my workflows, go ahead and enable them**. Your push in step 2 came before this, so it did not start a run.
4. **Create the `production` environment.** In your fork, open **Settings → Environments → New environment**. Name it `production` and click **Configure environment**. Tick **Required reviewers**, add your own GitHub user, and click **Save protection rules**. Leave **Prevent self-review** off: in this lesson you are the only reviewer.
5. **Make `04-quality-gates` the default branch of your fork.** Open **Settings → General**. Under **Default branch**, click the switch icon, choose `04-quality-gates` and confirm. GitHub shows the **Run workflow** button only for workflows on the default branch. This changes only your fork.

## Step 6: run the pipeline on GitHub and approve the promotion

1. In your fork, open **Actions**, click **release** in the left list, then **Run workflow**. Keep the branch `04-quality-gates` and the candidate `exercises/quality-gates/candidate.yaml`, and click **Run workflow**. Pushes also start the workflow when they change a file in `exercises/quality-gates/`.
2. Open the run. **Quality gates** runs for about a minute. The run page then shows the gate table.
3. **Promote to champion** waits with **Waiting for review: production needs approval**. Read the gate table. Then click **Review deployments**, tick **production** and click **Approve and deploy**.

> **Check:** the gate table says `Quality gates: f1-points-finish version 1: passed` and shows seven gates as PASS: accuracy 0.842, roc_auc 0.907, margin 0.038, inputs 7, rookie_accuracy 0.646. After your approval, the job **Promote to champion** prints `PROMOTED: f1-points-finish version 1 is now @champion (previous champion: none). Approved by <your-user>.`

The approval is the control. The gates check what a machine can check. A person still decides to release, and the tag `promoted_by` records who.

To look at the registry from the run, download the artifact `registry-promoted` from the run page and unzip it in an empty folder. Start `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001` in that folder. You see the run, the version, its aliases and its tags. The model files point to folders on the GitHub runner, so the UI cannot show them.

## Step 7: try the leaky model on GitHub

Try a candidate without committing it. Open **Actions → release → Run workflow**, set the candidate to `exercises/quality-gates/examples/leaky.yaml`, and click **Run workflow**.

> **Check:** the job **Quality gates** fails at step **3. Quality gates**. Its log shows `AssertionError: the model uses after-race columns: finish_position`. The job **Promote to champion** is **skipped**: there is nothing to approve.

That is the milestone of this lesson: the bad build is blocked, and the good build is promoted only after approval. Try `examples/weak.yaml` too: it fails `accuracy` (0.806) and `roc_auc` (0.876).

## Step 8: roll back

Back in your codespace. In your local MLflow, `@champion` is still the leaky version 2 from step 3. Move it back to the version it replaced:

```bash
python exercises/quality-gates/promote.py --rollback --approver "<your name>"
```

> **Check:** `ROLLED BACK: f1-points-finish version 1 is @champion again (version 2 removed by <your name>).` In the MLflow UI, version 1 has `@champion`, and version 2 has the tags `rolled_back_by` and `rolled_back_at`.

Run the same command again:

> **Check:** `REFUSED: version 1 has no previous champion to go back to.`

A rollback only moves an alias, so it takes a second. Every program that loads `models:/f1-points-finish@champion` gets version 1 from its next load. You build such a program in lesson 05.

## Discuss

1. In step 3, `promote.py` let three skipped gates through, and the cheating model became champion. Should a skipped gate block a release? What would a team lose if it did?
2. Anyone who can change `candidate.yaml` can also change `criteria.yaml`, and lower `min_accuracy` in the same commit. How would you stop that? (Think of reviews, branch protection and who owns which file.)
3. The grid rule has ROC AUC 0.893, above the floor of 0.88. Should a model be allowed to rank the cars worse than the rule? What floor would you choose, and why?
4. In step 6 you approved your own model. In a real team, who should approve a release, and what should they look at before they click **Approve and deploy**?

## Stretch

- Add a gate that the candidate must be at least as accurate as the current `@champion`, measured on the same 2025 data. What should happen when there is no champion yet?
- Break the data gate: change one `rain_prob` in `f1/data/races.csv` to `1.5` and run the pipeline. It stops at step 1. Undo the change with `git checkout f1/data/races.csv`.
- Add a gate for the midfield teams (`team_tier == "midfield"`). Pick its threshold from the lesson 03 subgroup table, and write the reason in `criteria.yaml`.
- Make the registry survive between CI runs: in the job **Quality gates**, download the artifact `registry-promoted` of the last successful run before training. Then CI has a previous champion, and you can roll back in CI too.

## Stuck?

There is a reference solution in [`solution/test_gates.py`](solution/test_gates.py). Try the TODOs first. To run the pipeline with the reference gates:

```bash
GATES=exercises/quality-gates/solution/test_gates.py bash exercises/quality-gates/run_pipeline.sh
```

Run one gates file at a time. pytest cannot collect `test_gates.py` and `solution/test_gates.py` in one run, because the two files have the same name.
