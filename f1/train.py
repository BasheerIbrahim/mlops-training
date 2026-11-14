"""python -m projects.f1.train  (or `make train` in this folder)"""
from mlkit.train import run_cli
from projects.f1.contracts import SPEC

if __name__ == "__main__":
    raise SystemExit(run_cli(SPEC))
