#!/usr/bin/env bash
# Run the release pipeline in your codespace, the same steps as GitHub Actions:
# validate data -> train candidate -> quality gates -> promote. Stops at the first failure.
#
# Usage:
#   bash exercises/quality-gates/run_pipeline.sh
#   bash exercises/quality-gates/run_pipeline.sh exercises/quality-gates/examples/leaky.yaml
#   GATES=exercises/quality-gates/solution/test_gates.py bash exercises/quality-gates/run_pipeline.sh
set -euo pipefail

HERE=exercises/quality-gates
CANDIDATE=${1:-$HERE/candidate.yaml}
GATES=${GATES:-$HERE/test_gates.py}
APPROVER=${APPROVER:-$(git config user.name || echo "$USER")}
export MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-http://127.0.0.1:5000}

step=""
trap 'echo; echo "PIPELINE STOPPED at step $step. Nothing was promoted."' ERR

step="1/4 validate data"
echo "== $step"
python $HERE/validate_data.py f1/data/races.csv

step="2/4 train candidate ($CANDIDATE)"
echo "== $step"
python $HERE/train_candidate.py --candidate "$CANDIDATE"

step="3/4 quality gates ($GATES)"
echo "== $step"
python -m pytest "$GATES" -q -rs --tb=line --no-header

step="4/4 promote"
echo "== $step"
python $HERE/promote.py --approver "$APPROVER"
