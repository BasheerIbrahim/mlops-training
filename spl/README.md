# SPL: Synthetic Saudi league

Your team owns this folder. Everything you need is here; you never have to touch another team's folder.

```bash
make status     # do the files in data/ still match the committed DVC version?
make validate   # run the data contracts, log the result to MLflow (spl-data-validation)
make train      # validate, then train the baseline and log lineage to MLflow (spl-win)
make test       # run this team's tests
```

From the repository root the same targets are `make spl-status`, `spl-validate`, `spl-train` and `spl-test`.

| File | What it is | Edit it? |
|---|---|---|
| `contracts.py` | Pandera schemas and the dataset spec | yes |
| `model.py` | the baseline model and the rule it has to beat | yes |
| `tests/` | tests of your contracts | yes |
| `data/`, `data.dvc` | the dataset and its DVC version | no: data changes go through `dvc add` |
| `validate.py`, `train.py` | three-line entry points into the shared `mlkit/` | rarely |

Full guide: [docs/projects/spl.md](../../docs/projects/spl.md).
