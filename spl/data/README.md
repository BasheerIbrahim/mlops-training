# Data: a synthetic Saudi league

**Every result in this folder is synthetic.** The 24 clubs and their home cities are real. The tiers, strengths, squad values, players, tables and results are invented by `lab/data.py` from seed 2026 with the Python standard library, and they describe no real season. Run `make data-check` to prove that these files match the generator. Do not edit `data/`.

The data has the shape of a real league: 18 clubs in the top flight, a double round robin of 34 rounds, three clubs relegated and three promoted every season, five seasons. The clubs' 18 home cities are real, so `travel_km` and `kickoff_temp_c` feel right. The data does not reproduce any real season or person, and a club's synthetic tier or table position says nothing about the real club. We use synthetic results because real results and squad values come with licence conditions and are not needed to learn MLOps.

A season is named by the year it starts: season 2025 is the 2025-26 season.

## Files

| File | Rows | When it is used |
|---|---:|---|
| `matches.csv` | 3,060 | Training (2021-22 to 2024-25) and the holdout (2025-26). One row per club per match: 1,530 matches, two rows each. |
| `season_2026_provisional.csv` | 144 | Day 3. First 8 rounds of 2026-27 after a spending wave, provisional results. |
| `disciplinary_2026.csv` | 7 | Day 3. Matches awarded 3-0 by the disciplinary committee, published 2 to 7 days after the final whistle. |
| `season_2026_final.csv` | 144 | Day 3. Final results after the committee. The correct delayed labels. |
| `scenarios/reference_window.json` | 144 | Monitoring reference: the first eight rounds of 2025-26, the same part of the calendar as the 2026-27 start. |
| `scenarios/heatwave_window.json` | 18 | Heatwave scenario: round 3 of 2025-26 with every kickoff at 44 C (input drift). |
| `scenarios/serving_skew_window.json` | 144 + 144 | A new logistics feed sends miles, not kilometres (training-serving skew). |

## Columns in `matches.csv`

| Column | Meaning | Known | Model input? |
|---|---|---|---|
| `match_id`, `season`, `round`, `date` | Match identity. `2025-03-RYF-JDM` is round 3 of 2025-26, home club first. | Before | No (identifiers) |
| `club_code`, `club`, `opponent_code`, `opponent`, `venue` | Who plays whom, and where | Before | No (identifiers) |
| `club_tier` | elite, mid or small | Before | No (subgroup for reporting) |
| `promoted` | The club's first season back in the top flight | Before | No (subgroup for reporting) |
| `home` | 1 when the club plays at its own ground, else 0 | Before | **Yes** |
| `league_position` | The club's place in the table before kickoff, 1-18. Round 1 uses last season's final table; promoted clubs start at 16-18. | Before | **Yes** |
| `opponent_position` | The opponent's place in the table before kickoff, 1-18 | Before | **Yes** |
| `form_points` | Mean points per match over the club's last 5 matches (1.2 before any history) | Before | **Yes** |
| `squad_value_m` | Estimated market value of the squad, millions | Before | **Yes** |
| `travel_km` | Distance from the club's city to the venue; 0 at home | Before | **Yes** |
| `kickoff_temp_c` | Forecast temperature at kickoff, degrees C | Before | **Yes** |
| `kickoff_slot` | afternoon, evening or night | Before | **Yes** (one-hot) |
| `goals_for`, `goals_against` | The score | **After** | Leakage |
| `result` | W, D or L | **After** | Leakage |
| `points` | 3, 1 or 0 | **After** | Leakage |
| `shots_on_target`, `possession_pct` | Match statistics | **After** | Leakage |
| `yellow_cards`, `red_cards` | Cards for the club | **After** | Leakage |
| `win` | **Target.** 1 = the club won the match | **After** | Label |

## Facts you can check

Measured on this data with `make explore` and `python -m scripts.train` on the reference solution:

- 1,530 matches, 3,060 club-rows, 23 clubs over five seasons. 40.8 % of club-rows are wins. The home side wins 53 % of matches, 18 % are drawn.
- The table-only rule ("the side higher in the table wins") is right for 0.693 of 2025-26 club-rows.
- The reference model is right for 0.748 of 2025-26 club-rows.
- In 2026-27 the squad values jump after a privatisation wave, the model's accuracy falls to 0.597 on final labels, and newly promoted Neom SC sit second after eight rounds behind Al-Tai.

## What the data is not

It is not real football data. It is not a basis for betting, club decisions or claims about any club or person. Subgroups such as `promoted` exist to teach subgroup measurement; they are not protected characteristics.
