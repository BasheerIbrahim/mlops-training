"""Contract tests for the f1-points-finish API (app.py).

A contract test checks what clients rely on: the URLs, the fields, the types, the
errors. Not how good the model is: the quality gates of lesson 04 check that.

Your task: complete TODO 1 to TODO 3. The first five tests are done for you.
The fixtures (client, entry, season_2025) come from conftest.py. See
exercises/serve-model/README.md for the steps.

A test that is still a TODO is skipped. A skipped test checks nothing.

Usage:
    pytest exercises/serve-model/test_api.py
"""

import pytest

MODEL_NAME = "f1-points-finish"


def test_health_names_the_model(client):
    """GET /health says which model version answers."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_name"] == MODEL_NAME
    assert body["model_version"].isdigit(), f"model_version {body['model_version']!r} is not a version number"


def test_predict_one_entry(client, entry):
    """One entry in, one prediction (0 or 1) and one probability (0 to 1) out."""
    response = client.post("/v1/predict", json={"entries": [entry]})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["predictions"] in ([0], [1])
    assert 0 <= body["probabilities"][0] <= 1


def test_prediction_follows_probability(client, season_2025):
    """For all 480 entries of 2025: the prediction is 1 exactly when the probability is above 0.5."""
    response = client.post("/v1/predict", json={"entries": season_2025})
    assert response.status_code == 200, response.text
    body = response.json()
    for prediction, probability in zip(body["predictions"], body["probabilities"]):
        assert prediction == int(probability > 0.5), f"prediction {prediction} for probability {probability}"


def test_rejects_a_missing_input(client, entry):
    """An entry without rain_prob gets 422, and the message names the field."""
    del entry["rain_prob"]
    response = client.post("/v1/predict", json={"entries": [entry]})
    assert response.status_code == 422
    assert "entries.0.rain_prob: Field required" in response.json()["detail"]


def test_rejects_an_after_race_column(client, entry):
    """An entry with finish_position gets 422: the API accepts only inputs known before the race."""
    entry["finish_position"] = 4
    response = client.post("/v1/predict", json={"entries": [entry]})
    assert response.status_code == 422
    assert "entries.0.finish_position: Extra inputs are not permitted" in response.json()["detail"]


def test_rejects_an_out_of_range_grid(client, entry):
    """grid 0 and grid 21 get 422: a grid has positions 1 to 20."""
    # TODO 1: for grid 0 and grid 21, set entry["grid"], post {"entries": [entry]} to
    #         /v1/predict, and assert that the status code is 422 and that one line of
    #         response.json()["detail"] starts with "entries.0.grid".
    #         Then delete the pytest.skip line.
    pytest.skip("TODO 1: the test 'rejects an out-of-range grid' is not written yet")


def test_rejects_an_unknown_circuit_type(client, entry):
    """circuit_type 'oval' gets 422, and the message lists the allowed circuit types."""
    # TODO 2: set entry["circuit_type"] = "oval" and post it. Assert 422, and that the
    #         detail mentions circuit_type and the three allowed values
    #         (street, permanent, high_speed).
    #         Then delete the pytest.skip line.
    pytest.skip("TODO 2: the test 'rejects an unknown circuit type' is not written yet")


def test_answer_matches_the_batch(client, season_2025):
    """A batch of 20 entries gets 20 predictions and 20 probabilities, from the version /health names."""
    # TODO 3: post the first 20 entries of season_2025 (one race). Assert that the answer
    #         has 20 predictions and 20 probabilities, that model_name is MODEL_NAME, and
    #         that model_version is the model_version from GET /health.
    #         Then delete the pytest.skip line.
    pytest.skip("TODO 3: the test 'answer matches the batch' is not written yet")
