"""F1 team: the baseline model and the rule it has to beat. Change this file freely; it is yours."""
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# What a model with no learning would say; the dataset README quotes it as the bar to beat.
BASELINE = ("grid <= 10 scores points", lambda X: (X["grid"] <= 10).astype(int))


def build_model(spec) -> Pipeline:
    pre = ColumnTransformer([("num", StandardScaler(), spec.numeric),
                             ("cat", OneHotEncoder(handle_unknown="ignore"), spec.categorical)])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
