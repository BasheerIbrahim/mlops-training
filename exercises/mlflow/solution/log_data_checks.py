"""Validate f1/data/races.csv and log the data version and the check results to MLflow.

Reference solution. Try exercises/mlflow/log_data_checks.py first.

Usage:
    python exercises/mlflow/solution/log_data_checks.py f1/data/races.csv
"""

import argparse
import subprocess
import sys
from pathlib import Path

import mlflow
import pandas as pd
import pandera.pandas as pa
import yaml

EXPERIMENT = "f1-data-checks"

# What a valid races.csv looks like. See f1/data/README.md for the column dictionary.
SCHEMA = pa.DataFrameSchema(
    {
        "race_id": pa.Column(str),
        "season": pa.Column(int, pa.Check.in_range(2021, 2025)),
        "round": pa.Column(int, pa.Check.in_range(1, 24)),
        "driver_code": pa.Column(str),
        "team_tier": pa.Column(str, pa.Check.isin(["top", "midfield", "backmarker"])),
        "rookie": pa.Column(bool),
        "grid": pa.Column(int, pa.Check.in_range(1, 20)),
        "quali_gap_ms": pa.Column(int, pa.Check.ge(0)),
        "driver_form": pa.Column(float, pa.Check.in_range(1, 20)),
        "team_form": pa.Column(float, pa.Check.ge(0)),
        "team_dnf_rate": pa.Column(float, pa.Check.in_range(0, 1)),
        "rain_prob": pa.Column(float, pa.Check.in_range(0, 1)),
        "circuit_type": pa.Column(str, pa.Check.isin(["street", "permanent", "high_speed"])),
        "finish_position": pa.Column(int, pa.Check.in_range(1, 20)),
        "points": pa.Column(int, pa.Check.in_range(0, 26)),
        "status": pa.Column(str, pa.Check.isin(["Finished", "DNF"])),
        "points_finish": pa.Column(int, pa.Check.isin([0, 1])),
    },
    checks=[
        pa.Check(
            lambda df: df["points_finish"] == (df["finish_position"] <= 10).astype(int),
            name="target_matches_finish_position",
        ),
    ],
    unique=["race_id", "driver_code"],
)


def data_version(csv_path: Path) -> tuple[str, Path]:
    """Return the DVC md5 of the file and the path of its .dvc pointer."""
    dvc_file = csv_path.with_name(csv_path.name + ".dvc")
    if not dvc_file.exists():
        sys.exit(f"{dvc_file} not found. Run `dvc add {csv_path}` first (step 2).")
    return yaml.safe_load(dvc_file.read_text())["outs"][0]["md5"], dvc_file


def git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip() or "unknown"


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Run every check and return the failure cases (empty when the data is valid)."""
    try:
        SCHEMA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as err:
        return err.failure_cases
    return pd.DataFrame()


def log_to_mlflow(csv_path, df, md5, dvc_file, failures, tracking_uri):
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT)
    status = "passed" if failures.empty else "failed"
    failed_checks = 0 if failures.empty else len(failures[["column", "check"]].drop_duplicates())

    with mlflow.start_run(run_name=f"{csv_path.stem}-{md5[:8]}"):
        # Data version: which exact file this run saw.
        mlflow.set_tags({
            "data.version": md5,
            "data.path": str(csv_path),
            "git.commit": git_commit(),
            "validation.status": status,
        })
        mlflow.log_params({"data_path": str(csv_path), "data_md5": md5, "rows": len(df), "columns": df.shape[1]})
        mlflow.log_input(
            mlflow.data.from_pandas(df, source=str(csv_path), name=csv_path.stem, targets="points_finish"),
            context="validation",
        )
        mlflow.log_artifact(str(dvc_file), artifact_path="data_version")

        # Data validation: how many checks failed and on which rows.
        mlflow.log_metrics({
            "failed_checks": failed_checks,
            "failure_cases": len(failures),
            "points_finish_rate": float(df["points_finish"].mean()),
            "dnf_rate": float((df["status"] == "DNF").mean()),
        })
        mlflow.log_dict(
            {"status": status, "failed_checks": failed_checks, "failure_cases": len(failures)},
            "validation/report.json",
        )
        if not failures.empty:
            mlflow.log_text(failures.to_csv(index=False), "validation/failure_cases.csv")

    return status, failed_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", type=Path, help="Path to races.csv")
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5000")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    md5, dvc_file = data_version(args.csv)
    failures = validate(df)
    status, failed_checks = log_to_mlflow(args.csv, df, md5, dvc_file, failures, args.tracking_uri)

    print(f"data version {md5}: validation {status} ({failed_checks} failed checks, {len(failures)} failure cases)")
    # A non-zero exit lets a pipeline stop on bad data.
    sys.exit(0 if status == "passed" else 1)


if __name__ == "__main__":
    main()
