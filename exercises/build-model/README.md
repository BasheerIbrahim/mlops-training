# Lesson 03: build a model and track experiments

You now have versioned, checked data. In this lesson you train models that predict `points_finish` (1 = the car finishes in the top 10) **before** the race. You record every experiment in MLflow: the data version, the parameters, the metrics and the fitted model. Then you compare the runs, spot the one that cheats, and register the best honest model.

Time: about 60 minutes.

| Run | Model | What it shows |
|---|---|---|
| Baseline | The grid rule: start in the top 10, score points. No learning. | The score to beat |
| Logistic regression | A simple model on all seven inputs | A model that learns beats the rule |
| Random forest (3 runs) | The same inputs, three hyperparameter settings | Why you track every run |
| Leakage trap | A forest that also sees `finish_position` | A score that is too good to be true |

Run every command from the repository root, `/workspaces/mlops-training`.

## What you will have at the end

- Six runs in the MLflow experiment `f1-points-finish`. Each run records the data version, the model type, the hyperparameters, the feature list, the metrics on 2025 and the fitted model.
- One run tagged `leakage=true` that you know not to trust.
- The best honest model in the MLflow Model Registry as `f1-points-finish`, version 1.

## The data and the model inputs

Open [`f1/data/README.md`](../../f1/data/README.md) and look at the **Known** column again.

| | Seasons | Rows |
|---|---|---:|
| Training data | 2021-2024 | 1,920 |
| Test data (holdout) | 2025 | 480 |

The models use the seven inputs that are known before the race: `grid`, `quali_gap_ms`, `driver_form`, `team_form`, `team_dnf_rate`, `rain_prob` and `circuit_type`. `circuit_type` is text, so the model pipeline turns it into three 0/1 columns (one-hot encoding).

## Step 1: start the MLflow server

Open a terminal and run the same command as in lesson 02:

```bash
mlflow server \
  --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./mlartifacts \
  --allowed-hosts "*.app.github.dev,localhost:*,127.0.0.1:*" \
  --cors-allowed-origins "https://*.app.github.dev"
```

Leave this terminal running. Open the **Ports** tab and click the globe icon next to **MLflow UI**. Without `--allowed-hosts` and `--cors-allowed-origins`, the UI returns **403**.

Open a second terminal (**Terminal → New Terminal**) for the other commands.

## Step 2: complete the TODOs and run the baseline

Open [`train.py`](train.py). It already:

- loads `f1/data/races.csv` and splits it into training (2021-2024) and test (2025) data;
- builds the model: the grid rule, a logistic regression or a random forest;
- computes the metrics on 2025: `accuracy`, `f1`, `roc_auc`, and the accuracy for each `team_tier` and for rookies and non-rookies;
- computes the data version: the md5 hash of `races.csv`. It is the same value that DVC writes into `races.csv.dvc`.

Complete **TODO 1 to TODO 6** in `log_run()`. Then run the baseline:

```bash
python exercises/build-model/train.py --model grid-rule
```

> **Check:** the last line says `grid-rule: accuracy 0.804, f1 0.804, roc_auc 0.893 on 2025 (1920 train rows, 480 test rows)`. This is the grid-rule fact from `f1/data/README.md`.

In the MLflow UI, open the experiment **f1-points-finish** and the run `grid-rule`. Find the tag `data.version = 199d7bda0a7b641e0e68ccee5236a3a7`, the same md5 as in lesson 02. The grid rule learns nothing, so this run has no model.

## Step 3: train a logistic regression

```bash
python exercises/build-model/train.py --model logreg
```

> **Check:** `logreg-c1.0: accuracy 0.835, f1 0.837, roc_auc 0.906`. This is the reference model from `f1/data/README.md`. The run `logreg-c1.0` has a model under **Logged models**.

## Step 4: tune a random forest

A random forest has hyperparameters: the number of trees (`--n-estimators`), how deep each tree may grow (`--max-depth`), and how many rows each leaf must hold (`--min-samples-leaf`). Run three settings:

```bash
python exercises/build-model/train.py --model forest
python exercises/build-model/train.py --model forest --n-estimators 200 --max-depth 5
python exercises/build-model/train.py --model forest --n-estimators 300 --max-depth 8 --min-samples-leaf 5
```

> **Check:**
>
> | Run | Accuracy | F1 | ROC AUC |
> |---|---:|---:|---:|
> | `forest-n100-dNone-l1` (trees grow without limit) | 0.819 | 0.823 | 0.902 |
> | `forest-n200-d5-l1` | 0.833 | 0.839 | 0.908 |
> | `forest-n300-d8-l5` | 0.842 | 0.847 | 0.907 |

The default forest is worse than the logistic regression: its trees learn the training data too closely. Limits on depth and leaf size help. Without MLflow you would now have to remember which setting gave which score.

## Step 5: the leakage trap

Add `finish_position` to the inputs:

```bash
python exercises/build-model/train.py --model forest --leak
```

> **Check:** `forest-n100-dNone-l1-leak: accuracy 1.000, f1 1.000, roc_auc 1.000`. The run has the tag `leakage = true`.

A perfect score on a hard problem is too good to be true. `finish_position` is known only **after** the race, and `points_finish` is defined from it (top 10). The model reads the answer. It could never run before a race.

## Step 6: compare the runs in the MLflow UI

1. Open the experiment **f1-points-finish**. You see six runs.
2. Click **Columns** and add the metrics `accuracy`, `f1`, `roc_auc`, `accuracy_rookie_true` and `accuracy_team_tier_midfield`, and the tag `leakage`.
3. Sort by `accuracy`. The leakage run is at the top.
4. Hide it. Type this filter into the search box and press **Enter**:

   ```
   tags.leakage = "false"
   ```

5. Select all five honest runs and click **Compare**. Look at the parameters and the metrics side by side.

> **Check:** the filter leaves five runs. `forest-n300-d8-l5` has the highest accuracy (0.842), then `logreg-c1.0` (0.835).

Look at the subgroups too. Every model is much worse for rookies than for other drivers:

| Run | All entries | Rookies | Non-rookies | Midfield teams |
|---|---:|---:|---:|---:|
| `grid-rule` | 0.804 | 0.521 | 0.836 | 0.667 |
| `logreg-c1.0` | 0.835 | 0.646 | 0.856 | 0.714 |
| `forest-n300-d8-l5` | 0.842 | 0.646 | 0.863 | 0.714 |

## Step 7: register the best honest model

The Model Registry keeps the models you choose to use, with a name and a version number.

1. Open the run `forest-n300-d8-l5`.
2. Click **Register model** at the top right. If a list opens, pick the run's model.
3. Choose **Create New Model**, type `f1-points-finish` and click **Register**.

You can also register it from the terminal. Copy the run ID from the run page:

```bash
python -c "
import mlflow
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.register_model('runs:/<RUN_ID>/model', 'f1-points-finish')
"
```

MLflow may print a warning that it registers the logged model `models:/m-...` instead. That is the same model.

Load the registered model and test it on 2025:

```bash
python - <<'EOF'
import mlflow
import pandas as pd

mlflow.set_tracking_uri("http://127.0.0.1:5000")
model = mlflow.pyfunc.load_model("models:/f1-points-finish/1")
df = pd.read_csv("f1/data/races.csv")
test = df[df["season"] == 2025]
inputs = ["grid", "quali_gap_ms", "driver_form", "team_form", "team_dnf_rate", "rain_prob", "circuit_type"]
print("accuracy:", round((model.predict(test[inputs]) == test["points_finish"]).mean(), 3))
EOF
```

> **Check:** the model registry (**Models** in the MLflow navigation) shows `f1-points-finish`, version 1, and the script prints `accuracy: 0.842`.

Do not register the leakage run. It has the best score and it is useless.

## Discuss

1. The leakage run scored 1.000. Which parameter in the run shows the cause? Which check from lesson 01 or 02 would stop `finish_position` from getting into the inputs?
2. The best models are right for about 65 % of rookie entries, against about 86 % for other drivers. Is overall accuracy enough to choose a model? What would you tell the team that uses it?
3. The best forest beats the logistic regression by 0.007 on 480 entries: about 3 more right answers. Is that a real difference? Which model would you put in production, and why?
4. You chose the model by its 2025 score. Is 2025 still an honest test of that model? What would you do instead?

## Stretch

- Try the logistic regression with `--c 0.1` and `--c 0.01`. Does the simple model catch up with the forest?
- Add `--model boosting` to `train.py` with scikit-learn's `GradientBoostingClassifier`. Log two runs with different `learning_rate` values.
- Find runs with a richer filter, for example `metrics.accuracy > 0.83 and tags.leakage = "false"`.
- Add `rookie` as a model input. Does the rookie accuracy improve? Should it be an input at all? (See "What the data is not" in `f1/data/README.md`.)

## Stuck?

There is a reference solution in [`solution/train.py`](solution/train.py). Try the TODOs first.
