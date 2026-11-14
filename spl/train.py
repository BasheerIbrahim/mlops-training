"""python -m projects.spl.train  (or `make train` in this folder)"""
from mlkit.train import run_cli
from projects.spl.contracts import SPEC

if __name__ == "__main__":
    raise SystemExit(run_cli(SPEC))
