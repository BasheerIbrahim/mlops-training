"""Train a model that predicts points_finish before the race and track the run in MLflow.

Your task: complete the TODOs in log_run(). Loading the data, the 2021-2024 / 2025 split,
the feature preparation, the models and the metrics are done for you.
See exercises/build-model/README.md for the steps.

Usage:
    python exercises/build-model/train.py --model grid-rule
    python exercises/build-model/train.py --model logreg
    python exercises/build-model/train.py --model forest --n-estimators 200 --max-depth 5
    python exercises/build-model/train.py --model forest --leak
"""

import argparse
import hashlib
import subprocess
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

EXPERIMENT = "f1-points-finish"
TARGET = "points_finish"
TRAIN_SEASONS = [2021, 2022, 2023, 2024]
TEST_SEASON = 2025

# Model inputs: all known before the race. See f1/data/README.md.
NUMERIC = ["grid", "quali_gap_ms", "driver_form", "team_form", "team_dnf_rate", "rain_prob"]
CATEGORICAL = ["circuit_type"]
# Known only after the race. Used by --leak to show what leakage looks like.
LEAK = "finish_position"
SUBGROUPS = ["team_tier", "rookie"]
# MLflow saves scikit-learn models with skops. You trust the trees you trained yourself.
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]


class GridRule:
    """Baseline with no learning: a car that starts in the top ten scores points."""

    def fit(self, X, y):
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        # A score that falls with the grid position, above 0.5 for grid 1 to 10.
        p = ((20.5 - X["grid"].to_numpy()) / 20).clip(0, 1)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (X["grid"].to_numpy() <= 10).astype(int)


def data_version(csv_path: Path) -> str:
    """Return the md5 of the file. DVC uses the same hash as the data version."""
    return hashlib.md5(csv_path.read_bytes()).hexdigest()


def git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip() or "unknown"


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train on 2021-2024, test on the 2025 holdout."""
    return df[df["season"].isin(TRAIN_SEASONS)], df[df["season"] == TEST_SEASON]


def hyperparameters(args) -> dict:
    if args.model == "grid-rule":
        return {"grid_cutoff": 10}
    if args.model == "logreg":
        return {"C": args.c, "max_iter": 1000}
    return {
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "min_samples_leaf": args.min_samples_leaf,
        "random_state": 42,
    }


def build_model(args, numeric: list[str]):
    """Return an unfitted model. The pipeline one-hot encodes circuit_type itself."""
    if args.model == "grid-rule":
        return GridRule()
    if args.model == "logreg":
        scaler, clf = StandardScaler(), LogisticRegression(**hyperparameters(args))
    else:
        scaler, clf = "passthrough", RandomForestClassifier(**hyperparameters(args), n_jobs=-1)
    prep = ColumnTransformer([
        ("numeric", scaler, numeric),
        ("circuit_type", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    return Pipeline([("prep", prep), ("model", clf)])


def evaluate(model, X: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Metrics on the 2025 holdout, overall and per subgroup."""
    y = test[TARGET].to_numpy()
    pred = model.predict(X)
    metrics = {
        "accuracy": accuracy_score(y, pred),
        "f1": f1_score(y, pred),
        "roc_auc": roc_auc_score(y, model.predict_proba(X)[:, 1]),
    }
    correct = pd.Series(pred == y, index=test.index)
    for col in SUBGROUPS:
        for value, acc in correct.groupby(test[col]).mean().items():
            metrics[f"accuracy_{col}_{str(value).lower()}"] = acc
    return {name: float(value) for name, value in metrics.items()}


def run_name(args) -> str:
    name = args.model
    if args.model == "logreg":
        name += f"-c{args.c}"
    if args.model == "forest":
        name += f"-n{args.n_estimators}-d{args.max_depth}-l{args.min_samples_leaf}"
    return name + ("-leak" if args.leak else "")


def log_run(args, csv_path, model, features, metrics, md5, X_test, tracking_uri):
    # TODO 1: point MLflow at the server you started (tracking_uri) and select the
    #         experiment EXPERIMENT (mlflow.set_tracking_uri, mlflow.set_experiment).

    # TODO 2: start a run named run_name(args) (mlflow.start_run) and, inside it,
    #         do TODO 3 to TODO 6.

    # TODO 3: tags (mlflow.set_tags). Record which data and code this run saw:
    #         data.version (md5), data.path, git.commit (git_commit()), and
    #         leakage ("true" or "false", from args.leak).

    # TODO 4: params (mlflow.log_params). Record how the model was built:
    #         model_type (args.model), features (",".join(features)),
    #         train_seasons ("2021-2024"), test_season (TEST_SEASON), and every
    #         hyperparameter (**hyperparameters(args)).

    # TODO 5: metrics (mlflow.log_metrics). Log the whole metrics dict: accuracy, f1,
    #         roc_auc and the accuracy per team_tier and rookie subgroup on 2025.

    # TODO 6: the fitted model. Skip it for the grid rule (it learns nothing). Otherwise:
    #         mlflow.sklearn.log_model(model, name="model", input_example=X_test.head(5),
    #                                  skops_trusted_types=TRUSTED_TYPES)
    pass


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", choices=["grid-rule", "logreg", "forest"], required=True)
    parser.add_argument("--c", type=float, default=1.0, help="logreg: inverse regularisation strength")
    parser.add_argument("--n-estimators", type=int, default=100, help="forest: number of trees")
    parser.add_argument("--max-depth", type=int, default=None, help="forest: maximum tree depth")
    parser.add_argument("--min-samples-leaf", type=int, default=1, help="forest: minimum rows per leaf")
    parser.add_argument("--leak", action="store_true", help=f"add {LEAK} as a feature (leakage)")
    parser.add_argument("--csv", type=Path, default=Path("f1/data/races.csv"))
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5000")
    args = parser.parse_args()
    if args.leak and args.model == "grid-rule":
        parser.error("--leak needs a model that learns: use --model logreg or --model forest")

    df = pd.read_csv(args.csv)
    train, test = split(df)
    numeric = NUMERIC + ([LEAK] if args.leak else [])
    features = ["grid"] if args.model == "grid-rule" else numeric + CATEGORICAL

    model = build_model(args, numeric).fit(train[features], train[TARGET])
    metrics = evaluate(model, test[features], test)
    log_run(args, args.csv, model, features, metrics, data_version(args.csv), test[features], args.tracking_uri)

    print(
        f"{run_name(args)}: accuracy {metrics['accuracy']:.3f}, f1 {metrics['f1']:.3f}, "
        f"roc_auc {metrics['roc_auc']:.3f} on {TEST_SEASON} ({len(train)} train rows, {len(test)} test rows)"
    )


if __name__ == "__main__":
    main()
