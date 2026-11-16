"""Validate f1/data/races.csv against the lesson 02 schema. Exit 1 if any check fails.

Step 1 of the release pipeline. The gates in test_gates.py use the same schema.

Usage:
    python exercises/quality-gates/validate_data.py f1/data/races.csv
"""

import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

# What a valid races.csv looks like. The same schema as exercises/mlflow/solution/log_data_checks.py.
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


def data_version(csv_path: Path) -> str:
    """Return the md5 of the file. DVC uses the same hash as the data version."""
    return hashlib.md5(csv_path.read_bytes()).hexdigest()


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Run every check and return the failure cases (empty when the data is valid)."""
    try:
        SCHEMA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as err:
        return err.failure_cases
    return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", type=Path, help="Path to races.csv")
    args = parser.parse_args()

    failures = validate(pd.read_csv(args.csv))
    status = "passed" if failures.empty else "failed"
    print(f"data version {data_version(args.csv)}: validation {status} ({len(failures)} failure cases)")
    if not failures.empty:
        print(failures[["column", "check", "failure_case"]].head(10).to_string(index=False))
    # A non-zero exit stops the pipeline before it trains on bad data.
    sys.exit(0 if failures.empty else 1)


if __name__ == "__main__":
    main()
