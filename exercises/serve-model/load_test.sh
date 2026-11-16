#!/usr/bin/env bash
# Load-test the API with Locust (no web UI), then check the result against slo.yaml.
# Exits 1 when the API breaks the service-level objective. GitHub Actions runs the same script.
#
# Usage:
#   bash exercises/serve-model/load_test.sh
#   API_URL=http://127.0.0.1:8001 bash exercises/serve-model/load_test.sh
set -euo pipefail

HERE=exercises/serve-model
API_URL=${API_URL:-http://127.0.0.1:8000}
OUT=${OUT:-results/locust}
# The load that the SLO is defined for, from slo.yaml.
read -r USERS SPAWN_RATE RUN_TIME < <(python -c "
import yaml; l = yaml.safe_load(open('$HERE/slo.yaml'))['load']
print(l['users'], l['spawn_rate'], l['run_time'])")

mkdir -p "$(dirname "$OUT")"
echo "== Locust: $USERS users for $RUN_TIME against $API_URL"
# Locust exits 1 when any request failed. The SLO check decides, so do not stop here.
locust -f $HERE/locustfile.py --host "$API_URL" --headless \
  --users "$USERS" --spawn-rate "$SPAWN_RATE" --run-time "$RUN_TIME" \
  --csv "$OUT" --html "$OUT.html" --only-summary --loglevel WARNING || true

echo "== SLO check"
python $HERE/check_slo.py "${OUT}_stats.csv"
