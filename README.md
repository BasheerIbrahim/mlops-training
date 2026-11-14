# mlops-training-dataset

Synthetic datasets and starter code for hands-on MLOps training. Two independent team projects, each with its own data, data contracts, baseline model and tests.

| Folder | Project | Task |
|---|---|---|
| [`f1/`](f1/) | Synthetic Grand Prix championship: 10 fictional teams, 24 circuits, five seasons | Predict a points finish (`points_finish`) |
| [`spl/`](spl/) | Synthetic Saudi league: 18 clubs per season, 34 rounds, five seasons | Predict a win (`win`) |

**All results, players, teams and drivers are synthetic.** They were generated from seed 2026 and describe no real season or person. They are not a basis for betting, club or team decisions, or claims about anyone real. See each project's `data/README.md` for the column dictionary, what is known before versus after a match, and the day-3 drift and delayed-label files.

## Layout of each project

| Path | What it is |
|---|---|
| `contracts.py` | Pandera schemas and the dataset spec |
| `model.py` | The baseline model and the rule it has to beat |
| `tests/` | Tests of the contracts |
| `data/` | The dataset: training and holdout CSVs, 2026 provisional and final results, monitoring scenarios in `scenarios/` |
| `data.dvc` | The DVC version record for `data/` |
| `validate.py`, `train.py` | Short entry points into the shared `mlkit/` package |
| `Makefile` | `make status`, `validate`, `train`, `test` |

## Not included in this repository

The `mlkit/` package, the `lab/data.py` generator, the root `Makefile` and the `docs/` guides that the project READMEs refer to live elsewhere, so `make` targets and those links will not work from this repository alone.

The `data/` folders are committed to git here. Their `data.dvc` files still point at DVC remotes (`f1-store`, `spl-store`) that are not part of this repository.
