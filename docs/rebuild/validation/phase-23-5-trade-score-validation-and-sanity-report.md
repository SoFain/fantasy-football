# Phase 23.5 Trade Score Validation and Sanity Report

Date: 2026-06-18

## Final Decision

`TRADE SCORE SANITY PASS WITH WARNINGS`

The materialized Trade Analyzer score v0 rows pass structural validation and are ready for staging UI testing with explicit warnings. They are not production-ready trade advice.

This phase was read-only except for creating this report. No score rows were written. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Target Slice

| Field | Value |
| --- | --- |
| model version | `trade_score_v0_2025_001` |
| season | `2025` |
| week | `18` |
| scoring profile | `ppr` |
| league type | `redraft` |
| roster format | `one_qb` |

## Validation Results

Requested validation commands:

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_score` | pass, 1 of 1 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market` | pass, 9 of 9 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief` | pass, 11 of 11 |

Additional score-object validation run for broader coverage:

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |

Note: the requested `trade_score` pattern currently matches `151_trade_player_scores_trade_score_range.sql`. The broader `trade_player_scores` pattern covers grain, component ranges, confidence range, JSON fields, current-view grain, compatibility-view existence, raw-source dependency checks, and identity coverage.

## Row Counts and Structural Checks

| Metric | Value |
| --- | ---: |
| total rows | 77 |
| duplicate grain rows | 0 |
| `PICK` rows | 0 |
| missing `model_run_id` rows | 0 |
| stale projection rows | 0 |
| invalid `trade_score` rows | 0 |
| missing `confidence_score` rows | 0 |
| missing `component_json` rows | 0 |
| missing `source_freshness_json` rows | 0 |
| missing `missing_flags_json` rows | 0 |
| source freshness missing-flag rows | 0 |

## Score Distribution

| Metric | Value |
| --- | ---: |
| trade score min | 7.9352 |
| trade score max | 60.0659 |
| trade score avg | 33.2663 |
| trade score stddev | 11.9112 |
| confidence min | 28.66 |
| confidence max | 51.41 |
| confidence avg | 46.3644 |
| confidence stddev | 4.8333 |
| confidence >= 70 rows | 0 |

The scores are not all clustered at one value. The range is about 52.13 points, from 7.9352 to 60.0659. Confidence is tightly low, which is expected from the Phase 23.3G low-confidence warning and remains the main limitation.

## Component Ranges

| Component | Min | Max | Avg |
| --- | ---: | ---: | ---: |
| efficiency_score | 37.96 | 100.00 | 67.3827 |
| fraud_score | 0.00 | 100.00 | 50.2597 |
| market_score | 1.39 | 98.61 | 52.1183 |
| normalized_risk_score x100 | 49.57 | 100.00 | 78.6552 |
| positional_scarcity_score | 85.60 | 100.00 | 98.9195 |
| projection_score | 1.39 | 96.15 | 44.4295 |
| recent_production_score | 1.85 | 98.15 | 49.2208 |
| role_usage_score | 14.31 | 82.18 | 50.1144 |

All required component keys were present in `component_json`.

## Tier and Position Distribution

Score tiers:

| Tier | Rows |
| --- | ---: |
| avoid | 34 |
| depth | 30 |
| flex | 12 |
| starter | 1 |

Positions:

| Position | Rows |
| --- | ---: |
| WR | 30 |
| RB | 26 |
| QB | 13 |
| TE | 8 |

QBs do not dominate the top of the board. The top 25 includes a mix of RB, WR, QB, and TE rows, with RB and WR leading the highest scores.

## Top 25 by Trade Score

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Risk |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Bijan Robinson | RB | ATL | 60.0659 | 50.53 | 0.00 | 0.6200 |
| 2 | Ja'Marr Chase | WR | CIN | 55.7722 | 49.35 | 60.00 | 0.8250 |
| 3 | Jahmyr Gibbs | RB | DET | 55.3984 | 50.53 | 0.00 | 0.6200 |
| 4 | Puka Nacua | WR | LAR | 54.3830 | 43.72 | 100.00 | 1.0000 |
| 5 | Jaxon Smith-Njigba | WR | SEA | 53.3932 | 50.53 | 65.00 | 0.8750 |
| 6 | De'Von Achane | RB | MIA | 51.7125 | 49.35 | 0.00 | 0.6200 |
| 7 | Amon-Ra St. Brown | WR | DET | 51.6068 | 50.53 | 100.00 | 1.0000 |
| 8 | Christian McCaffrey | RB | SF | 51.2452 | 50.53 | 0.00 | 0.6200 |
| 9 | Drake Maye | QB | NE | 50.4203 | 43.66 | 100.00 | 1.0000 |
| 10 | Ashton Jeanty | RB | LV | 49.2474 | 50.53 | 25.00 | 0.5950 |
| 11 | Josh Allen | QB | BUF | 49.2100 | 42.97 | 100.00 | 1.0000 |
| 12 | Chase Brown | RB | CIN | 46.5374 | 50.53 | 0.00 | 0.6200 |
| 13 | Chris Olave | WR | NO | 45.6053 | 49.35 | 60.00 | 0.8250 |
| 14 | Omarion Hampton | RB | LAC | 44.5617 | 41.12 | 0.00 | 0.6200 |
| 15 | Malik Nabers | WR | NYG | 44.3408 | 41.86 | 0.00 | 0.5188 |
| 16 | Brock Bowers | TE | LV | 43.8011 | 44.23 | 78.00 | 1.0000 |
| 17 | James Cook | RB | BUF | 43.5172 | 49.90 | 0.00 | 0.6585 |
| 18 | Colston Loveland | TE | CHI | 43.4487 | 49.29 | 43.00 | 0.6550 |
| 19 | Jonathan Taylor | RB | IND | 42.5551 | 50.53 | 0.00 | 0.6200 |
| 20 | Justin Jefferson | WR | MIN | 42.4340 | 50.53 | 35.00 | 0.5950 |
| 21 | Trey McBride | TE | ARI | 41.4666 | 43.72 | 35.00 | 0.6200 |
| 22 | Nico Collins | WR | HOU | 40.9826 | 47.30 | 53.00 | 0.7550 |
| 23 | Caleb Williams | QB | CHI | 39.9651 | 39.91 | 100.00 | 1.0000 |
| 24 | George Pickens | WR | DAL | 39.1878 | 49.64 | 53.00 | 0.7550 |
| 25 | Saquon Barkley | RB | PHI | 38.7306 | 49.35 | 0.00 | 0.6200 |

## Bottom 25 by Trade Score

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Risk |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Chuba Hubbard | RB | CAR | 7.9352 | 47.02 | 45.00 | 0.6750 |
| 2 | Bhayshul Tuten | RB | JAX | 10.6040 | 45.93 | 85.00 | 1.0000 |
| 3 | David Montgomery | RB | HOU | 12.6693 | 49.41 | 60.00 | 0.8250 |
| 4 | Marvin Harrison | WR | ARI | 14.5610 | 40.63 | 0.00 | 0.7153 |
| 5 | Jaylen Waddle | WR | DEN | 15.2744 | 48.32 | 70.00 | 0.9250 |
| 6 | Quentin Johnston | WR | LAC | 16.6338 | 44.96 | 100.00 | 1.0000 |
| 7 | Bo Nix | QB | DEN | 17.0614 | 44.12 | 75.00 | 0.9750 |
| 8 | Jalen Hurts | QB | PHI | 18.4702 | 42.20 | 100.00 | 1.0000 |
| 9 | Christian Watson | WR | GB | 18.6211 | 41.24 | 95.00 | 1.0000 |
| 10 | Brian Thomas | WR | JAX | 19.4932 | 45.42 | 53.00 | 0.7800 |
| 11 | RJ Harvey | RB | DEN | 19.9892 | 50.53 | 85.00 | 1.0000 |
| 12 | Terry McLaurin | WR | WAS | 21.0081 | 41.85 | 35.00 | 0.6230 |
| 13 | D'Andre Swift | RB | CHI | 21.2366 | 49.16 | 0.00 | 0.6320 |
| 14 | Jaxson Dart | QB | NYG | 21.3500 | 46.09 | 100.00 | 1.0000 |
| 15 | Josh Jacobs | RB | GB | 21.5005 | 47.56 | 0.00 | 0.6579 |
| 16 | Alec Pierce | WR | IND | 21.8981 | 47.26 | 85.00 | 1.0000 |
| 17 | Jayden Daniels | QB | WAS | 22.9821 | 30.04 | 80.00 | 1.0000 |
| 18 | Bucky Irving | RB | TB | 23.6254 | 42.30 | 0.00 | 0.6200 |
| 19 | DeVonta Smith | WR | PHI | 24.5245 | 49.69 | 63.00 | 0.8550 |
| 20 | Sam LaPorta | TE | DET | 24.7030 | 51.41 | 53.00 | 0.6300 |
| 21 | Javonte Williams | RB | DAL | 24.7859 | 48.89 | 30.00 | 0.6235 |
| 22 | Kyle Pitts | TE | ATL | 25.0302 | 50.38 | 93.00 | 1.0000 |
| 23 | Ladd McConkey | WR | LAC | 26.0673 | 48.32 | 60.00 | 0.8250 |
| 24 | Jameson Williams | WR | DET | 26.1653 | 50.11 | 25.00 | 0.6207 |
| 25 | Rome Odunze | WR | CHI | 26.8436 | 51.27 | 0.00 | 0.5184 |

## Notable Sanity Checks

High market with lower score:

| Player | Pos | Team | Market | Score | Confidence |
| --- | --- | --- | ---: | ---: | ---: |
| Justin Jefferson | WR | MIN | 7244 | 42.4340 | 50.53 |
| Brock Bowers | TE | LV | 7094 | 43.8011 | 44.23 |
| Malik Nabers | WR | NYG | 6720 | 44.3408 | 41.86 |
| CeeDee Lamb | WR | DAL | 6295 | 38.5290 | 45.06 |
| Drake London | WR | ATL | 5892 | 34.2657 | 44.36 |

Low market with comparatively higher score:

| Player | Pos | Team | Market | Score | Confidence |
| --- | --- | --- | ---: | ---: | ---: |
| Brock Purdy | QB | SF | 2409 | 29.2309 | 34.07 |
| Trevor Lawrence | QB | JAX | 2738 | 32.7971 | 39.64 |
| Kyle Pitts | TE | ATL | 2737 | 25.0302 | 50.38 |

High fraud or risk penalty rows:

| Player | Pos | Team | Score | Fraud | Risk | Risk adjustment |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A.J. Brown | WR | NE | 35.4137 | 100.00 | 1.0000 | -10.0 |
| Amon-Ra St. Brown | WR | DET | 51.6068 | 100.00 | 1.0000 | -10.0 |
| Brock Purdy | QB | SF | 29.2309 | 100.00 | 1.0000 | -10.0 |
| Caleb Williams | QB | CHI | 39.9651 | 100.00 | 1.0000 | -10.0 |
| Drake Maye | QB | NE | 50.4203 | 100.00 | 1.0000 | -10.0 |
| Josh Allen | QB | BUF | 49.2100 | 100.00 | 1.0000 | -10.0 |
| Puka Nacua | WR | LAR | 54.3830 | 100.00 | 1.0000 | -10.0 |

The risk penalty is visible and active. Several elite players have low confidence and high risk penalties, which explains lower-than-market scores.

## Missing Flag Review

Top missing flags:

| Flag | Rows |
| --- | ---: |
| `missing_fumbles_lost` | 71 |
| `missing_interceptions` | 71 |
| `missing_passing_2pt_conversions` | 71 |
| `missing_receiving_2pt_conversions` | 71 |
| `missing_return_tds` | 71 |
| `missing_routes_proxy` | 71 |
| `missing_rushing_2pt_conversions` | 71 |
| `missing_snaps` | 71 |
| `scoring_missing_data_flags_present` | 71 |
| `missing_fraud_context` | 22 |
| `missing_snaps_last_3` | 9 |
| `efficiency_fallback_used` | 6 |
| `missing_recent_trade_history` | 6 |
| `role_usage_fallback_used` | 6 |
| `missing_pigskin_ranking_context` | 4 |
| `missing_snap_share` | 3 |

Missing flags are present and visible. This is good for explainability, but it also confirms why confidence is low.

## Obvious Bug Review

| Check | Result |
| --- | --- |
| all scores cluster too tightly | no, scores range from 7.9352 to 60.0659 |
| all QBs dominate unintentionally | no, RB and WR rows lead the top scores |
| elite players score implausibly low | warning, some elite players score low due to low confidence and risk penalties |
| low-usage players score implausibly high | no obvious structural failure found |
| confidence always 100 despite missing flags | no, confidence ranges from 28.66 to 51.41 |
| risk penalty never applied | no, high-risk rows show `risk_adjustment = -10.0` |
| missing flags absent despite known missing data | no, missing flags are present and numerous |
| tier distribution nonsensical | warning, distribution is conservative but plausible for low-confidence staging review |
| `component_json` missing key components | no, required keys were present |
| stale source or freshness flags | no stale projection or freshness missing-flag rows found |

Sampled score-table team labels matched `compat_player_profiles_current` for the inspected names. The profile table returned duplicate rows for some sampled names, so profile deduplication remains worth monitoring, but this did not produce duplicate score grain rows.

## Staging UI Recommendation

Recommendation: `ready for staging UI with warnings`

The staging UI can proceed if it clearly labels the score output as v0 staging-review data and surfaces confidence plus missing flags. The UI should not present these scores as production trade advice.

Required UI cautions:

- show confidence prominently
- show missing flags or warning count
- indicate score model version `trade_score_v0_2025_001`
- avoid production wording
- keep production score flags off

## Remaining Warnings

- 0 rows have confidence >= 70.
- 71 of 77 rows carry scoring missing-data flags.
- 22 rows lack fraud context.
- Some elite players are suppressed by low confidence and risk penalties.
- The score tier distribution is conservative, with 64 of 77 rows in `avoid` or `depth`.
- This is acceptable for staging UI validation, but not for production recommendations.
