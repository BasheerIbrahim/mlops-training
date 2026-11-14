"""F1 team: data contracts and the dataset spec.

Serving schema: model inputs only, strict (a leakage column or a unit change fails).
Training schema: the whole table, plus checks that the label agrees with the outcome columns.
Bounds are domain limits, not the training min/max; distribution shift belongs to monitoring.
"""
import pandera.pandas as pa

from mlkit.checks import rows_per_group
from mlkit.spec import DatasetSpec
from projects.f1.model import BASELINE, build_model

F1_SERVING = pa.DataFrameSchema(
    {
        "grid": pa.Column(int, pa.Check.in_range(1, 20)),
        "quali_gap_ms": pa.Column(int, pa.Check.in_range(0, 10_000)),
        "driver_form": pa.Column(float, pa.Check.in_range(1, 20)),
        "team_form": pa.Column(float, pa.Check.in_range(0, 50)),
        "team_dnf_rate": pa.Column(float, pa.Check.in_range(0, 1)),
        "rain_prob": pa.Column(float, pa.Check.in_range(0, 1)),
        "circuit_type": pa.Column(str, pa.Check.isin(["street", "permanent", "high_speed"])),
    },
    strict=True,
)

F1_TRAINING = pa.DataFrameSchema(
    {
        "race_id": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}$")),
        "season": pa.Column(int, pa.Check.in_range(2021, 2026)),
        "round": pa.Column(int, pa.Check.in_range(1, 24)),
        "circuit": pa.Column(str),
        "driver_code": pa.Column(str, pa.Check.str_length(3, 3)),
        "driver_name": pa.Column(str),
        "team": pa.Column(str),
        "team_tier": pa.Column(str, pa.Check.isin(["top", "midfield", "backmarker"])),
        "rookie": pa.Column(bool),
        **{k: v for k, v in F1_SERVING.columns.items()},
        "finish_position": pa.Column(int, pa.Check.in_range(1, 20)),
        "points": pa.Column(int, pa.Check.in_range(0, 26)),
        "status": pa.Column(str, pa.Check.isin(["Finished", "DNF"])),
        "laps_completed": pa.Column(int, pa.Check.in_range(0, 80)),
        "fastest_lap": pa.Column(bool),
        "actual_rain": pa.Column(bool),
        "points_finish": pa.Column(int, pa.Check.isin([0, 1])),
    },
    checks=[
        pa.Check(lambda df: ~df.duplicated(["race_id", "driver_code"]), error="duplicate (race_id, driver_code)"),
        pa.Check(lambda df: rows_per_group(df, "race_id", 20), error="a race does not have 20 entries"),
        pa.Check(lambda df: df["points_finish"] == (df["finish_position"] <= 10).astype(int),
                 error="points_finish disagrees with finish_position <= 10"),
    ],
)

SPEC = DatasetSpec(
    name="f1", train_csv="races.csv", provisional_csv="season_2026_provisional.csv",
    final_csv="season_2026_final.csv", corrections_csv="stewards_2026.csv",
    key=["race_id", "driver_code"], join_key=["race_id", "driver_code"],
    numeric=["grid", "quali_gap_ms", "driver_form", "team_form", "team_dnf_rate", "rain_prob"],
    categorical=["circuit_type"], target="points_finish",
    scenarios={
        "reference_window": ("scenarios/reference_window.json", "rows"),
        "wet_race_window": ("scenarios/wet_race_window.json", "rows"),
        "serving_skew_window.recomputed": ("scenarios/serving_skew_window.json", "recomputed"),
        "serving_skew_window.served": ("scenarios/serving_skew_window.json", "served"),
    },
    serving_schema=F1_SERVING, training_schema=F1_TRAINING, build_model=build_model, baseline=BASELINE,
)
