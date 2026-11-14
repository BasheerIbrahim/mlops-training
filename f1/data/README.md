# Data: the Synthetic Grand Prix Championship

**Every team, driver and circuit in this folder is fictional.** `lab/data.py` generates all rows from seed 2026 with the Python standard library. Run `make data-check` to prove that these files match the generator. Do not edit `data/`.

The data has the shape of a real championship: 10 teams, 2 cars each, 24 circuits, five seasons. It does not reproduce any real season, team or person. We use synthetic data because real historical results come with licence conditions and are not needed to learn MLOps.

## Files

| File | Rows | When it is used |
|---|---:|---|
| `races.csv` | 2,400 | Training (2021-2024) and the holdout (2025). One row per car per race. |
| `season_2026_provisional.csv` | 160 | Day 3. First 8 races under new regulations, provisional results. |
| `stewards_2026.csv` | 7 | Day 3. Post-race penalties, published 2 to 26 hours after the race. |
| `season_2026_final.csv` | 160 | Day 3. Final classification after the stewards. The correct delayed labels. |
| `scenarios/reference_window.json` | 80 | Monitoring reference: last four 2025 races. |
| `scenarios/wet_race_window.json` | 20 | Storm forecast scenario (input drift). |
| `scenarios/serving_skew_window.json` | 80 + 80 | New timing feed sends seconds, not milliseconds (training-serving skew). |

## Columns in `races.csv`

| Column | Meaning | Known | Model input? |
|---|---|---|---|
| `race_id`, `season`, `round`, `circuit` | Race identity | Before | No (identifiers) |
| `driver_code`, `driver_name`, `team` | Entry identity | Before | No (identifiers) |
| `team_tier` | top, midfield or backmarker | Before | No (subgroup for reporting) |
| `rookie` | First season of the driver | Before | No (subgroup for reporting) |
| `grid` | Starting position after grid penalties, 1-20 | Before | **Yes** |
| `quali_gap_ms` | Gap to pole position in qualifying, milliseconds | Before | **Yes** |
| `driver_form` | Mean finishing position over the driver's last 3 races (DNF = 20) | Before | **Yes** |
| `team_form` | Mean team points per race over the last 3 races | Before | **Yes** |
| `team_dnf_rate` | Share of team cars that did not finish over the last 6 races | Before | **Yes** |
| `rain_prob` | Rain forecast for the race, 0-1 | Before | **Yes** |
| `circuit_type` | street, permanent or high_speed | Before | **Yes** (one-hot) |
| `finish_position` | Classified position, 1-20 | **After** | Leakage |
| `points` | Championship points scored | **After** | Leakage |
| `status` | Finished or DNF | **After** | Leakage |
| `laps_completed` | Laps completed | **After** | Leakage |
| `fastest_lap` | Set the fastest lap | **After** | Leakage |
| `actual_rain` | It rained during the race | **After** | Leakage |
| `points_finish` | **Target.** 1 = finished in the top 10 | **After** | Label |

## Facts you can check

Measured on this data with `make explore` and `python -m scripts.train` on the reference solution:

- 120 races, 2,400 entries, 28 drivers. Half of all entries score points. 10.9 % of entries do not finish.
- The grid-only rule ("start in the top ten, score points") is right for 0.804 of 2025 entries.
- The reference model is right for 0.835 of 2025 entries.
- In 2026, 27.5 % of entries do not finish (new, fragile power units) and Cobalt Racing leads after eight races.

## What the data is not

It is not real motorsport data. It is not a basis for betting, team decisions or claims about any person. Subgroups such as `rookie` exist to teach subgroup measurement; they are not protected characteristics.
