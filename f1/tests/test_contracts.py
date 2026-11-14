"""F1 contracts must accept the real data and reject each failure the dataset was built to teach."""
import pandas as pd
import pytest

from mlkit.lineage import dvc_state
from mlkit.testing import scenario_frame
from mlkit.validate import _schema_failures, gate_ok, validate_dataset
from projects.f1.contracts import SPEC


def test_real_data_passes_the_gate():
    results = validate_dataset(SPEC)
    assert gate_ok(results), [(r.name, r.failures) for r in results if r.gate and not r.passed]


@pytest.mark.parametrize("scenario,expected_flagged", [
    ("reference_window", False),
    ("wet_race_window", False),                  # drift, not a contract violation
    ("serving_skew_window.recomputed", False),
    ("serving_skew_window.served", True),        # quali_gap_ms sent in seconds instead of milliseconds
])
def test_scenarios(scenario, expected_flagged):
    assert bool(_schema_failures(SPEC.serving_schema, scenario_frame(SPEC, scenario))) is expected_flagged


def test_leakage_column_in_a_serving_payload_is_rejected():
    payload = scenario_frame(SPEC, "reference_window").assign(finish_position=1)
    failures = _schema_failures(SPEC.serving_schema, payload)
    assert [(f["check"], f["example"]) for f in failures] == [("column_in_schema", "finish_position")]


def test_label_that_disagrees_with_the_outcome_is_rejected():
    data = pd.read_csv(SPEC.path(SPEC.train_csv))
    data.loc[0, "points_finish"] = 1 - data.loc[0, "points_finish"]
    assert any("points_finish disagrees" in f["check"] for f in _schema_failures(SPEC.training_schema, data))


def test_duplicate_key_is_rejected():
    data = pd.read_csv(SPEC.path(SPEC.train_csv))
    data = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    assert any("duplicate" in f["check"] for f in _schema_failures(SPEC.training_schema, data))


def test_dvc_pointer_describes_the_dataset_folder():
    state = dvc_state(SPEC)
    assert state["md5"].endswith(".dir") and state["nfiles"] == 8 and state["clean"]
