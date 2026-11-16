"""Quality gates for f1-points-finish@candidate. Every gate must pass before promotion.

Your task: complete TODO 1 to TODO 3. The first four gates are done for you.
The fixtures (criteria, races, holdout, model, input_columns, predictions,
probabilities) come from conftest.py. See exercises/quality-gates/README.md for the steps.

A gate that is still a TODO is skipped. A skipped gate checks nothing.

Usage:
    pytest exercises/quality-gates/test_gates.py
"""

import pytest
from sklearn.metrics import roc_auc_score

from validate_data import validate

TARGET = "points_finish"


def test_data_passes_validation(races, record_property):
    """The data passes the lesson 02 schema."""
    failures = validate(races)
    record_property("failure_cases", len(failures))
    assert failures.empty, f"{len(failures)} failure cases in the data"


def test_model_predicts_0_or_1(predictions, holdout, record_property):
    """The model loads from the registry and returns 0 or 1 for every 2025 entry."""
    record_property("rows", len(predictions))
    assert len(predictions) == len(holdout)
    assert set(predictions.unique()) <= {0, 1}, f"unexpected predictions {sorted(predictions.unique())}"


def test_accuracy(predictions, holdout, criteria, record_property):
    """Accuracy on 2025 is at least min_accuracy."""
    accuracy = (predictions == holdout[TARGET]).mean()
    minimum = criteria["metrics"]["min_accuracy"]
    record_property("accuracy", f"{accuracy:.3f}")
    assert accuracy >= minimum, f"accuracy {accuracy:.3f} is below {minimum}"


def test_roc_auc(probabilities, holdout, criteria, record_property):
    """ROC AUC on 2025 is at least min_roc_auc."""
    auc = roc_auc_score(holdout[TARGET], probabilities)
    minimum = criteria["metrics"]["min_roc_auc"]
    record_property("roc_auc", f"{auc:.3f}")
    assert auc >= minimum, f"roc_auc {auc:.3f} is below {minimum}"


def test_beats_grid_rule(predictions, holdout, criteria, record_property):
    """Accuracy beats the grid rule by at least min_margin_over_grid_rule."""
    # TODO 1: compute the model accuracy, as in test_accuracy, and the grid-rule accuracy:
    #         the grid rule predicts 1 when holdout["grid"] <= 10. Record the difference
    #         with record_property("margin", ...). Assert that the model accuracy is at
    #         least the grid-rule accuracy + criteria["metrics"]["min_margin_over_grid_rule"].
    #         Then delete the pytest.skip line.
    pytest.skip("TODO 1: the gate 'beats the grid rule' is not written yet")


def test_no_forbidden_features(input_columns, criteria, record_property):
    """The model needs no input that is known only after the race."""
    # TODO 2: input_columns is the list of columns in the model signature. Find the
    #         columns that are also in criteria["forbidden_features"]. Record how many
    #         inputs the model has with record_property("inputs", ...). Assert that no
    #         input is forbidden, and name the forbidden ones in the message.
    #         Then delete the pytest.skip line.
    pytest.skip("TODO 2: the gate 'no forbidden features' is not written yet")


def test_rookie_accuracy(predictions, holdout, criteria, record_property):
    """Accuracy on 2025 rookie entries is at least min_accuracy_rookie."""
    # TODO 3: holdout["rookie"] is True for rookie entries. Compute the accuracy on those
    #         rows only. Record it with record_property("rookie_accuracy", ...). Assert
    #         that it is at least criteria["metrics"]["min_accuracy_rookie"].
    #         Then delete the pytest.skip line.
    pytest.skip("TODO 3: the gate 'rookie accuracy' is not written yet")
