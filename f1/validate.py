"""python -m projects.f1.validate  (or `make validate` in this folder)"""
from mlkit.validate import run_cli
from projects.f1.contracts import SPEC

if __name__ == "__main__":
    raise SystemExit(run_cli(SPEC))
