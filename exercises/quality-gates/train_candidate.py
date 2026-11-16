"""Train the model in candidate.yaml, log it to MLflow and register it as f1-points-finish@candidate.

Step 2 of the release pipeline. The model code is the same as in lesson 03.

Usage:
    python exercises/quality-gates/train_candidate.py
    python exercises/quality-gates/train_candidate.py --candidate exercises/quality-gates/examples/leaky.yaml
    python exercises/quality-gates/train_candidate.py --tracking-uri sqlite:///mlflow.db
"""

import argparse
import hashlib
import os
import subprocess
from pathlib import Path

import mlflow
import pandas as pd
import yaml
from mlflow import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

MODEL_NAME = "f1-points-finish"
EXPERIMENT = "f1-points-finish"
TARGET = "points_finish"
TRAIN_SEASONS = [2021, 2022, 2023, 2024]
TEST_SEASON = 2025

# Model inputs: all known before the race. See f1/data/README.md.
NUMERIC = ["grid", "quali_gap_ms", "driver_form", "team_form", "team_dnf_rate", "rain_prob"]
CATEGORICAL = ["circuit_type"]
# Known only after the race. leak: true in the candidate file adds it.
LEAK = "finish_position"
# MLflow saves scikit-learn models with skops. You trust the trees you trained yourself.
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]


def data_version(csv_path: Path) -> str:
    """Return the md5 of the file. DVC uses the same hash as the data version."""
    return hashlib.md5(csv_path.read_bytes()).hexdigest()


def git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip() or "unknown"


def build_model(candidate: dict, numeric: list[str]) -> Pipeline:
    """Return an unfitted pipeline. It one-hot encodes circuit_type itself."""
    params = candidate.get("hyperparameters") or {}
    if candidate["model"] == "logreg":
        scaler, clf = StandardScaler(), LogisticRegression(max_iter=1000, **params)
    elif candidate["model"] == "forest":
        scaler, clf = "passthrough", RandomForestClassifier(random_state=42, n_jobs=-1, **params)
    else:
        raise SystemExit(f"model must be logreg or forest, not {candidate['model']!r}")
    prep = ColumnTransformer([
        ("numeric", scaler, numeric),
        ("circuit_type", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    return Pipeline([("prep", prep), ("model", clf)])


def evaluate(model, X: pd.DataFrame, y: pd.Series) -> dict:
    """Metrics on the 2025 holdout. The gates measure them again; these are for the MLflow UI."""
    pred = model.predict(X)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "f1": float(f1_score(y, pred)),
        "roc_auc": float(roc_auc_score(y, model.predict_proba(X)[:, 1])),
    }


def run_name(candidate: dict) -> str:
    params = "-".join(f"{k}{v}" for k, v in (candidate.get("hyperparameters") or {}).items())
    return f"candidate-{candidate['model']}-{params}" + ("-leak" if candidate.get("leak") else "")


def log_and_register(candidate, candidate_path, csv_path, model, features, metrics, X_test):
    """Log the run, register a new model version and point @candidate at it."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run(run_name=run_name(candidate)) as run:
        mlflow.set_tags({
            "data.version": data_version(csv_path),
            "data.path": str(csv_path),
            "git.commit": git_commit(),
            "leakage": str(bool(candidate.get("leak"))).lower(),
            "candidate.file": str(candidate_path),
            "proposed_by": str(candidate.get("proposed_by", "unknown")),
        })
        mlflow.log_params({
            "model_type": candidate["model"],
            "features": ",".join(features),
            "train_seasons": f"{TRAIN_SEASONS[0]}-{TRAIN_SEASONS[-1]}",
            "test_season": TEST_SEASON,
            **(candidate.get("hyperparameters") or {}),
        })
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(candidate_path), artifact_path="candidate")
        info = mlflow.sklearn.log_model(
            model, name="model", input_example=X_test.head(5), skops_trusted_types=TRUSTED_TYPES
        )

    version = mlflow.register_model(info.model_uri, MODEL_NAME)
    client = MlflowClient()
    client.set_registered_model_alias(MODEL_NAME, "candidate", version.version)
    client.set_model_version_tag(MODEL_NAME, version.version, "proposed_by", str(candidate.get("proposed_by", "unknown")))
    client.set_model_version_tag(MODEL_NAME, version.version, "run_name", run_name(candidate))
    return run.info.run_id, version.version


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--candidate", type=Path, default=Path("exercises/quality-gates/candidate.yaml"))
    parser.add_argument("--csv", type=Path, default=Path("f1/data/races.csv"))
    parser.add_argument("--tracking-uri", default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    args = parser.parse_args()
    mlflow.set_tracking_uri(args.tracking_uri)

    candidate = yaml.safe_load(args.candidate.read_text())
    df = pd.read_csv(args.csv)
    train, test = df[df["season"].isin(TRAIN_SEASONS)], df[df["season"] == TEST_SEASON]
    numeric = NUMERIC + ([LEAK] if candidate.get("leak") else [])
    features = numeric + CATEGORICAL

    model = build_model(candidate, numeric).fit(train[features], train[TARGET])
    metrics = evaluate(model, test[features], test[TARGET])
    run_id, version = log_and_register(candidate, args.candidate, args.csv, model, features, metrics, test[features])

    print(
        f"{run_name(candidate)}: accuracy {metrics['accuracy']:.3f}, f1 {metrics['f1']:.3f}, "
        f"roc_auc {metrics['roc_auc']:.3f} on {TEST_SEASON}"
    )
    print(f"Registered {MODEL_NAME} version {version} as @candidate (run {run_id})")


if __name__ == "__main__":
    main()
