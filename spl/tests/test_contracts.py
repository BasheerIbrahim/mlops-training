"""SPL contracts must accept the real data and reject each failure the dataset was built to teach."""
import pandas as pd
import pytest

from mlkit.lineage import dvc_state
from mlkit.testing import scenario_frame
from mlkit.validate import _schema_failures, gate_ok, validate_dataset
from projects.spl.contracts import SPEC


def test_real_data_passes_the_gate():
    results = validate_dataset(SPEC)
    assert gate_ok(results), [(r.name, r.failures) for r in results if r.gate and not r.passed]


@pytest.mark.parametrize("scenario,expected_flagged", [
    ("reference_window", False),
    ("heatwave_window", False),                  # drift, not a contract violation
    ("serving_skew_window.recomputed", False),
    ("serving_skew_window.served", True),        # travel_km sent in miles instead of kilometres
])
def test_scenarios(scenario, expected_flagged):
    assert bool(_schema_failures(SPEC.serving_schema, scenario_frame(SPEC, scenario))) is expected_flagged


def test_known_blind_spot_integer_miles_pass_the_schema():
    """The miles feed is caught only because it sends floats. Rounded miles are a valid-looking
    payload, so unit skew needs a distribution check against the reference window (monitoring)."""
    served = scenario_frame(SPEC, "serving_skew_window.served")
    served["travel_km"] = served["travel_km"].round().astype(int)
    assert _schema_failures(SPEC.serving_schema, served) == []


def test_leakage_column_in_a_serving_payload_is_rejected():
    payload = scenario_frame(SPEC, "reference_window").assign(goals_for=1)
    failures = _schema_failures(SPEC.serving_schema, payload)
    assert [(f["check"], f["example"]) for f in failures] == [("column_in_schema", "goals_for")]


def test_label_that_disagrees_with_the_result_is_rejected():
    data = pd.read_csv(SPEC.path(SPEC.train_csv))
    data.loc[0, "win"] = 1 - data.loc[0, "win"]
    assert any("win disagrees" in f["check"] for f in _schema_failures(SPEC.training_schema, data))


def test_home_club_must_not_travel_but_a_same_city_away_club_may():
    payload = scenario_frame(SPEC, "reference_window")
    assert (payload[payload["home"] == 0]["travel_km"] == 0).any()   # same-city away rows exist in the data
    bad = payload.assign(travel_km=payload["travel_km"].where(payload["home"] == 0, 50))
    assert any("home club" in f["check"] for f in _schema_failures(SPEC.serving_schema, bad))


def test_dvc_pointer_describes_the_dataset_folder():
    state = dvc_state(SPEC)
    assert state["md5"].endswith(".dir") and state["nfiles"] == 8 and state["clean"]
