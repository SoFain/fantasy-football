# Phase 23.3A Trade Score Dry-Run Warning Investigation Report

Date: 2026-06-17

## Final Decision

`TRADE SCORE MATERIALIZATION NOT RECOMMENDED`

The main Fraud Watch attachment bug was found and fixed. The bounded 2025 week 18 dry-run now attaches Fraud Watch context to 55 of 100 candidate rows, and `missing_fraud_context` dropped from 100 rows to 45 rows.

Materialization is still not recommended because 98 of 100 rows still lack model-run context, projection context is stale at week 1 for the only 2 rows with projection model runs, all confidence scores remain below 70, and draft-pick assets need a separate product decision before public score use.

No score rows were written. No `--write` command was run. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or BigQuery data mutation was performed.

## Commands Run

Dry-run only:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Local checks:

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 16 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

## Root Cause: Missing Fraud Context

Before this phase, the source query joined Fraud Watch with:

```sql
COALESCE(a.player_id_internal, a.source_player_key) = f.player_key
```

For most market assets, `player_id_internal` is a Sleeper key like `sleeper:7564`, while `analytics_fraud_watch.player_id` uses a GSIS-style ID like `00-0036900`. Because `COALESCE` chose the Sleeper key first, the GSIS `source_player_key` was never considered.

Read-only match-rate checks for the top 100 candidate assets showed:

| Match route | Matches |
| --- | ---: |
| `source_player_key` to Fraud Watch `player_id` | 55 |
| `gsis_id` to Fraud Watch `player_id` | 55 |
| unique name, position, team fallback | 0 additional unique matches |

Name fallback did not add unique matches beyond stable source keys, so it was not added. This avoids unsafe name-based fraud attachment.

## Fraud Join Fix

Changed `src/trade_player_scores.py`:

- Added `gsis_id` to the asset source fields.
- Added a `fraud_match` CTE that matches Fraud Watch by stable identity keys:
  - `source_player_key`
  - `gsis_id`
  - `player_id_internal`
- Records `fraud_join_key` and `fraud_join_strategy` in source freshness JSON.
- Removes stale inherited `missing_fraud_context` flags when row-level fraud context successfully attaches.
- Leaves `missing_fraud_context` intact when no reliable fraud match exists.

Fraud context after fix:

| Metric | Before | After |
| --- | ---: | ---: |
| candidate rows | 100 | 100 |
| rows with `missing_fraud_context` | 100 | 45 |
| rows with nonzero `fraud_score` | 0 | 55 |
| `fraud_score` min | 0.0 | 0.0 |
| `fraud_score` max | 0.0 | 100.0 |
| `fraud_score` avg | 0.0 | 38.7 |

Remaining `missing_fraud_context` rows are expected for assets without matching Fraud Watch rows, including draft picks and players not present in the 2025 Fraud Watch slice.

## Projection And Model-Run Context

Read-only checks showed:

| Metric | Value |
| --- | ---: |
| top 100 candidate rows with `asset_model_run_id` | 0 |
| top 100 candidate rows with `projection_model_run_id` | 2 |
| top 100 candidate rows with any model run | 2 |
| `projection_rankings_current` rows for 2025 PPR redraft one-QB | 50 |
| `projection_rankings_current` week range | week 1 only |
| rows flagged `stale_projection_context` after fix | 2 |

Decision: keep the builder deterministic and allow latest available projection context, but explicitly flag stale projection context. Do not materialize review-ready scores until projection rankings are rebuilt for the target scoring context or the operator accepts v0 as low-confidence.

No projection rebuild was run in this phase.

## Confidence Penalty Review

The dry-run still has all confidence scores below 70.

After-fix confidence distribution:

| Metric | Value |
| --- | ---: |
| min | 36.5 |
| max | 57.0 |
| avg | 51.8061 |
| rows below 70 | 100 |

Primary penalty drivers after fix:

| Flag | Rows |
| --- | ---: |
| `missing_model_run_id` | 98 |
| `temporary_name_join_identity` | 87 |
| scoring missing data flags such as fumbles, interceptions, routes, snaps | 71 |
| `missing_fraud_context` | 45 |
| `missing_recent_trade_history` | 29 |
| `missing_pigskin_ranking_context` | 27 |
| `stale_projection_context` | 2 |

Changed `component_json` to include `confidence_breakdown`, which records:

- starting confidence
- blend steps
- sample size
- sample-size penalty
- missing flag count
- missing flag penalty
- final confidence score

Decision: do not tune confidence weights in this phase. The low confidence is explainable from real source gaps and stale projection context, not from an obvious formula contradiction.

## Draft-Pick Behavior

The dry-run includes 13 `PICK` rows with null teams. These are not ordinary player rows and should not be treated as fully comparable player scores yet.

Changed `src/trade_player_scores.py`:

- `PICK` rows now receive `draft_pick_asset`.
- `PICK` rows now receive `draft_pick_score_lane_pending`.
- The existing source-key fallback remains, so picks can still be inspected in dry-run output without fabricated player IDs.

Decision: keep picks in the dry-run candidate set for inspection, but do not materialize them as review-ready player scores yet. A future `trade_pick_scores` lane or pick-specific scoring rules should be considered.

## Before And After Dry-Run Comparison

| Metric | Before Phase 23.3A | After Phase 23.3A |
| --- | ---: | ---: |
| source rows | 100 | 100 |
| score rows written | 0 | 0 |
| `trade_player_scores` table rows | 0 | 0 |
| `missing_fraud_context` | 100 | 45 |
| nonzero `fraud_score` rows | 0 | 55 |
| `missing_model_run_id` | 98 | 98 |
| `stale_projection_context` | not flagged | 2 |
| draft-pick rows | 13 | 13, explicitly flagged |
| trade score min | 12.3592 | 9.2092 |
| trade score max | 65.0709 | 65.0709 |
| trade score avg | 36.6446 | 34.3197 |
| confidence min | 37.5 | 36.5 |
| confidence max | 57.0 | 57.0 |
| confidence avg | 51.7661 | 51.8061 |

The score average moved lower because Fraud Watch risk penalties now attach to matched players.

## After-Fix Top 25

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Risk | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Bijan Robinson | RB | ATL | 65.0709 | 55.5 | 0.0 | 0.25 | starter |
| 2 | Jahmyr Gibbs | RB | DET | 61.3680 | 55.5 | 0.0 | 0.25 | starter |
| 3 | Ja'Marr Chase | WR | CIN | 58.3188 | 54.5 | 60.0 | 0.85 | flex |
| 4 | De'Von Achane | RB | MIA | 57.1991 | 54.5 | 0.0 | 0.25 | flex |
| 5 | Puka Nacua | WR | LAR | 57.1046 | 57.0 | 100.0 | 1.0 | flex |
| 6 | Jaxon Smith-Njigba | WR | SEA | 56.3304 | 55.5 | 65.0 | 0.9 | flex |
| 7 | Amon-Ra St. Brown | WR | DET | 54.3284 | 55.5 | 100.0 | 1.0 | flex |
| 8 | Christian McCaffrey | RB | SF | 54.3168 | 55.5 | 0.0 | 0.25 | flex |
| 9 | Trey McBride | TE | ARI | 54.0498 | 57.0 | 35.0 | 0.6 | flex |
| 10 | Josh Allen | QB | BUF | 53.5178 | 49.5 | 100.0 | 1.0 | flex |
| 11 | Ashton Jeanty | RB | LV | 52.8090 | 55.5 | 25.0 | 0.5 | flex |
| 12 | James Cook | RB | BUF | 51.2054 | 55.5 | 0.0 | 0.25 | flex |
| 13 | Jonathan Taylor | RB | IND | 50.4553 | 55.5 | 0.0 | 0.25 | flex |
| 14 | Drake Maye | QB | NE | 50.4203 | 50.5 | 100.0 | 1.0 | flex |
| 15 | Omarion Hampton | RB | LAC | 50.0482 | 47.5 | 0.0 | 0.25 | flex |
| 16 | Malik Nabers | WR | NYG | 49.4704 | 41.5 | 0.0 | 0.175 | flex |
| 17 | Justin Jefferson | WR | MIN | 48.6220 | 55.5 | 35.0 | 0.6 | flex |
| 18 | Jeremiyah Love | RB | ARI | 48.5240 | 52.0 | 0.0 | 0.2 | flex |
| 19 | 2026 Pick 1.01 | PICK |  | 48.0620 | 49.0 | 0.0 | 0.25 | flex |
| 20 | CeeDee Lamb | WR | DAL | 47.6865 | 51.5 | 43.0 | 0.68 | flex |
| 21 | Brock Bowers | TE | LV | 46.9119 | 50.5 | 78.0 | 1.0 | flex |
| 22 | 2026 Pick 1.02 | PICK |  | 45.9088 | 49.0 | 0.0 | 0.25 | flex |
| 23 | Drake London | WR | ATL | 45.1472 | 50.5 | 0.0 | 0.25 | flex |
| 24 | Chase Brown | RB | CIN | 44.3002 | 55.5 | 0.0 | 0.25 | depth |
| 25 | Nico Collins | WR | HOU | 43.9184 | 53.5 | 53.0 | 0.78 | depth |

## After-Fix Bottom 25

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Risk | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Chuba Hubbard | RB | CAR | 9.2092 | 53.5 | 45.0 | 0.7 | avoid |
| 2 | Bhayshul Tuten | RB | JAX | 11.0870 | 53.5 | 85.0 | 1.0 | avoid |
| 3 | Quentin Johnston | WR | LAC | 12.3553 | 51.5 | 100.0 | 1.0 | avoid |
| 4 | RJ Harvey | RB | DEN | 14.1960 | 55.5 | 85.0 | 1.0 | avoid |
| 5 | David Montgomery | RB | HOU | 14.4249 | 55.5 | 60.0 | 0.85 | avoid |
| 6 | Bo Nix | QB | DEN | 14.7333 | 50.5 | 75.0 | 1.0 | avoid |
| 7 | Alec Pierce | WR | IND | 15.2873 | 53.5 | 85.0 | 1.0 | avoid |
| 8 | Denzel Boston | WR | CLE | 15.6198 | 52.0 | 0.0 | 0.2 | avoid |
| 9 | Jonah Coleman | RB | DEN | 16.2148 | 52.0 | 0.0 | 0.2 | avoid |
| 10 | Brock Purdy | QB | SF | 16.3089 | 42.5 | 100.0 | 1.0 | avoid |
| 11 | Christian Watson | WR | GB | 17.0656 | 48.5 | 95.0 | 1.0 | avoid |
| 12 | Kenyon Sadiq | TE | NYJ | 18.3806 | 52.0 | 0.0 | 0.2 | avoid |
| 13 | Jalen Hurts | QB | PHI | 18.4702 | 49.5 | 100.0 | 1.0 | avoid |
| 14 | Omar Cooper | WR | NYJ | 19.3676 | 52.0 | 0.0 | 0.2 | avoid |
| 15 | Jaylen Waddle | WR | DEN | 20.5439 | 54.5 | 70.0 | 0.95 | avoid |
| 16 | 2026 Pick 1.11 | PICK |  | 20.5639 | 49.0 | 0.0 | 0.25 | avoid |
| 17 | D'Andre Swift | RB | CHI | 21.0140 | 54.5 | 0.0 | 0.25 | avoid |
| 18 | KC Concepcion | WR | CLE | 21.2968 | 52.0 | 0.0 | 0.2 | avoid |
| 19 | Jaxson Dart | QB | NYG | 21.3500 | 52.5 | 100.0 | 1.0 | avoid |
| 20 | Marvin Harrison | WR | ARI | 22.0952 | 57.0 | 0.0 | 0.25 | avoid |
| 21 | Terry McLaurin | WR | WAS | 22.3366 | 48.5 | 35.0 | 0.6 | avoid |
| 22 | Brian Thomas | WR | JAX | 22.6055 | 52.5 | 53.0 | 0.78 | avoid |
| 23 | 2026 Pick 1.10 | PICK |  | 22.9229 | 49.0 | 0.0 | 0.25 | avoid |
| 24 | Tucker Kraft | TE | GB | 23.6684 | 41.61 | 100.0 | 1.0 | avoid |
| 25 | Trevor Lawrence | QB | JAX | 24.1815 | 50.5 | 100.0 | 1.0 | avoid |

## Code And Test Changes

Files changed:

- `src/trade_player_scores.py`
- `tests/test_trade_player_scores.py`

Implementation changes:

- Fraud Watch joins now consider `source_player_key`, `gsis_id`, and `player_id_internal` with stable key priority.
- Successful fraud attachment removes stale inherited `missing_fraud_context`.
- Successful model-run attachment removes stale inherited `missing_model_run_id`.
- Stale projection context is flagged when projection rows exist but are older than the target week.
- Draft-pick rows are explicitly flagged as `draft_pick_asset` and `draft_pick_score_lane_pending`.
- `component_json` now includes `confidence_breakdown`.

Test coverage added:

- fraud context attaches when identity matches
- missing fraud context remains when no reliable match exists
- source query matches Fraud Watch by stable source keys
- stale projection context flag
- confidence penalty breakdown
- draft-pick pending lane behavior

## Materialization Recommendation

Do not materialize scores yet.

The Fraud Watch join bug is fixed, but materialization should wait for one of these paths:

1. Rebuild or refresh `projection_rankings_current` for 2025 week 18 PPR redraft one-QB.
2. Decide that v0 can intentionally ship as low-confidence with stale or missing model-run context.
3. Decide how draft-pick assets should be represented, either in this table with low confidence or in a future pick-specific score lane.

Final decision: `TRADE SCORE MATERIALIZATION NOT RECOMMENDED`.
