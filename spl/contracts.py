"""SPL team: data contracts and the dataset spec.

Serving schema: model inputs only, strict (a leakage column or a unit change fails).
Training schema: the whole table, plus checks that the label agrees with the outcome columns.
Bounds are domain limits, not the training min/max; distribution shift belongs to monitoring.
"""
import pandera.pandas as pa

from mlkit.checks import rows_per_group
from mlkit.spec import DatasetSpec
from projects.spl.model import BASELINE, build_model

SPL_SERVING = pa.DataFrameSchema(
    {
        "home": pa.Column(int, pa.Check.isin([0, 1])),
        "league_position": pa.Column(int, pa.Check.in_range(1, 18)),
        "opponent_position": pa.Column(int, pa.Check.in_range(1, 18)),
        "form_points": pa.Column(float, pa.Check.in_range(0, 3)),
        "squad_value_m": pa.Column(float, pa.Check.in_range(0, 5_000)),
        "travel_km": pa.Column(int, pa.Check.in_range(0, 3_000)),
        "kickoff_temp_c": pa.Column(float, pa.Check.in_range(-10, 55)),
        "kickoff_slot": pa.Column(str, pa.Check.isin(["afternoon", "evening", "night"])),
    },
    strict=True,
    # One direction only: an away club from the venue's own city also travels 0 km.
    checks=[pa.Check(lambda df: (df["home"] == 0) | (df["travel_km"] == 0),
                     error="a home club must have travel_km == 0")],
)

SPL_TRAINING = pa.DataFrameSchema(
    {
        "match_id": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}-[A-Z]{3}-[A-Z]{3}$")),
        "season": pa.Column(int, pa.Check.in_range(2021, 2026)),
        "round": pa.Column(int, pa.Check.in_range(1, 34)),
        "date": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
        "club_code": pa.Column(str, pa.Check.str_length(3, 3)),
        "club": pa.Column(str),
        "opponent_code": pa.Column(str, pa.Check.str_length(3, 3)),
        "opponent": pa.Column(str),
        "venue": pa.Column(str),
        "club_tier": pa.Column(str, pa.Check.isin(["elite", "mid", "small"])),
        "promoted": pa.Column(bool),
        **{k: v for k, v in SPL_SERVING.columns.items()},
        "goals_for": pa.Column(int, pa.Check.in_range(0, 15)),
        "goals_against": pa.Column(int, pa.Check.in_range(0, 15)),
        "result": pa.Column(str, pa.Check.isin(["W", "D", "L"])),
        "points": pa.Column(int, pa.Check.isin([0, 1, 3])),
        "shots_on_target": pa.Column(int, pa.Check.in_range(0, 40)),
        "possession_pct": pa.Column(float, pa.Check.in_range(0, 100)),
        "yellow_cards": pa.Column(int, pa.Check.in_range(0, 12)),
        "red_cards": pa.Column(int, pa.Check.in_range(0, 5)),
        "win": pa.Column(int, pa.Check.isin([0, 1])),
    },
    checks=[
        *SPL_SERVING.checks,
        pa.Check(lambda df: ~df.duplicated(["match_id", "club_code"]), error="duplicate (match_id, club_code)"),
        pa.Check(lambda df: rows_per_group(df, "match_id", 2), error="a match does not have exactly two club rows"),
        pa.Check(lambda df: df["win"] == (df["result"] == "W").astype(int), error="win disagrees with result"),
        pa.Check(lambda df: df["points"] == df["result"].map({"W": 3, "D": 1, "L": 0}),
                 error="points disagree with result"),
        pa.Check(lambda df: df["result"] == (df["goals_for"] - df["goals_against"]).map(
            lambda d: "W" if d > 0 else ("L" if d < 0 else "D")), error="result disagrees with the score"),
    ],
)

SPEC = DatasetSpec(
    name="spl", train_csv="matches.csv", provisional_csv="season_2026_provisional.csv",
    final_csv="season_2026_final.csv", corrections_csv="disciplinary_2026.csv",
    key=["match_id", "club_code"], join_key=["match_id", "club_code"],
    numeric=["home", "league_position", "opponent_position", "form_points", "squad_value_m",
             "travel_km", "kickoff_temp_c"],
    categorical=["kickoff_slot"], target="win",
    scenarios={
        "reference_window": ("scenarios/reference_window.json", "rows"),
        "heatwave_window": ("scenarios/heatwave_window.json", "rows"),
        "serving_skew_window.recomputed": ("scenarios/serving_skew_window.json", "recomputed"),
        "serving_skew_window.served": ("scenarios/serving_skew_window.json", "served"),
    },
    serving_schema=SPL_SERVING, training_schema=SPL_TRAINING, build_model=build_model, baseline=BASELINE,
)
