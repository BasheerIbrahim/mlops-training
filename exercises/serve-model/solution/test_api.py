"""Contract tests for the f1-points-finish API (app.py).

A contract test checks what clients rely on: the URLs, the fields, the types, the
errors. Not how good the model is: the quality gates of lesson 04 check that.

Reference solution. Try exercises/serve-model/test_api.py first.
The fixtures (client, entry, season_2025) come from exercises/serve-model/conftest.py.

Usage:
    pytest exercises/serve-model/solution/test_api.py
"""

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
    for grid in (0, 21):
        entry["grid"] = grid
        response = client.post("/v1/predict", json={"entries": [entry]})
        assert response.status_code == 422, f"grid {grid}: status {response.status_code}"
        assert any(line.startswith("entries.0.grid") for line in response.json()["detail"])


def test_rejects_an_unknown_circuit_type(client, entry):
    """circuit_type 'oval' gets 422, and the message lists the allowed circuit types."""
    entry["circuit_type"] = "oval"
    response = client.post("/v1/predict", json={"entries": [entry]})
    assert response.status_code == 422
    detail = " ".join(response.json()["detail"])
    assert "circuit_type" in detail
    for allowed in ("street", "permanent", "high_speed"):
        assert allowed in detail, f"the message does not list {allowed}: {detail}"


def test_answer_matches_the_batch(client, season_2025):
    """A batch of 20 entries gets 20 predictions and 20 probabilities, from the version /health names."""
    race = season_2025[:20]
    response = client.post("/v1/predict", json={"entries": race})
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["predictions"]) == len(race)
    assert len(body["probabilities"]) == len(race)
    assert body["model_name"] == MODEL_NAME
    assert body["model_version"] == client.get("/health").json()["model_version"]
