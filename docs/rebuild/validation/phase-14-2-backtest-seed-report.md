# Phase 14.2 Backtest Seed Report

Final decision: GO WITH WARNINGS

## Purpose

Seed one small bounded backtest so the feature-flagged backtest dashboard is no longer an empty-state.

Scope:

- Horizon: `weekly`
- Season: `2025`
- Week: `1`
- Scoring profile: `ppr`
- League type: `redraft`
- Roster format: `one_qb`
- Projection seed limit: `25`

No LLM calls were made. No Firebase artifacts were created. No Cloud Run Jobs were triggered.

## Row Counts Before

| Table | Rows before |
| --- | ---: |
| `projections_player_weekly` | 0 |
| `projection_rankings_current` | 0 |
| `analytics_player_fantasy_points_by_profile` | 55,617 |
| `backtest_runs` | 0 |
| `backtest_result_player_week` | 0 |
| `backtest_result_summary` | 0 |

## Dry Runs

Projection dry-run:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 25 --dry-run
```

Result:

- `projection_rows = 25`
- `ranking_rows = 25`
- No LLM calls.
- Reads were from compatibility and curated tables.

Initial backtest dry-run before projection materialization:

```powershell
.\venv\Scripts\python.exe -m src.backtesting --horizon weekly --season-start 2025 --season-end 2025 --week-start 1 --week-end 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Result:

- `projection_rows = 0`
- `actual_rows = 1071`
- `missing_data_flags = ["missing_projection_rows"]`

Backtest dry-run after bounded projection materialization:

```powershell
.\venv\Scripts\python.exe -m src.backtesting --model-run-id weekly_projection-2025-1-20260616T114422Z-a25a92c1 --horizon weekly --season-start 2025 --season-end 2025 --week-start 1 --week-end 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Result:

- `projection_rows = 25`
- `actual_rows = 1071`
- `player_week_rows = 25`
- `summary_rows = 6`
- `calibration_rows = 16`
- `missing_data_flags = []`

## Materialization

Projection materialization command:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 25
```

Successful projection model run:

- `model_run_id = weekly_projection-2025-1-20260616T114422Z-a25a92c1`
- `source_freshness_snapshot_id = freshness-20260616T114411Z-c773d2bd`
- `projection_rows = 25`
- `ranking_rows = 25`

Backtest materialization command:

```powershell
.\venv\Scripts\python.exe -m src.backtesting --model-run-id weekly_projection-2025-1-20260616T114422Z-a25a92c1 --horizon weekly --season-start 2025 --season-end 2025 --week-start 1 --week-end 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --backtest-name phase_14_2_seed_week_2025_1
```

Successful backtest run:

- `backtest_run_id = backtest-weekly-2025-2025-20260616T114527Z-2093e839`
- `status = complete`
- `projection_rows = 25`
- `actual_rows = 1071`
- `player_week_rows = 25`
- `summary_rows = 6`
- `calibration_rows = 16`

## Row Counts After

| Table | Rows after |
| --- | ---: |
| `projections_player_weekly` | 50 |
| `projection_rankings_current` | 50 |
| `analytics_player_fantasy_points_by_profile` | 55,617 |
| `backtest_runs` | 1 |
| `backtest_result_player_week` | 25 |
| `backtest_result_summary` | 6 |
| `backtest_calibration_bins` | 16 |

The projection tables show 50 rows because the first bounded projection materialization attempt inserted 25 rows before a run-status update failed on a BigQuery streaming-buffer limitation. The valid seeded model run is `weekly_projection-2025-1-20260616T114422Z-a25a92c1`.

## Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
```

Result:

- 11 validations passed.
- 0 validations failed.
- `139_backtest_dashboard_latest_runs.sql` now reports `latest_backtest_runs = 1`.
- `140_backtest_dashboard_summary_available.sql` now reports `backtest_summary_rows = 6` and `backtest_run_count = 1`.
- `141_backtest_dashboard_no_raw_source_dependencies.sql` passed.

## Reader Smoke Check

Backtest dashboard helper calls:

- `list_backtest_runs(limit=5)` returned 1 run.
- `get_backtest_summary(backtest_run_id=backtest-weekly-2025-2025-20260616T114527Z-2093e839)` returned 6 rows.
- `get_backtest_player_errors(backtest_run_id, limit=5)` returned 5 rows.

## Warnings

- A failed partial projection run remains temporarily visible:
  - `model_run_id = weekly_projection-2025-1-20260616T113848Z-f07a0ccb`
  - `projections_player_weekly = 25 rows`
  - `projection_rankings_current = 25 rows`
- Targeted cleanup by `model_run_id` was attempted, but BigQuery rejected `DELETE` and status `UPDATE` because those rows were still in the streaming buffer.
- Cleanup should be retried later with targeted DML once the streaming buffer clears.

## Final Status

The backtest dashboard empty-state warning is resolved.

The project is ready for the next phase with one warning: retry cleanup for the failed partial projection run after BigQuery streaming-buffer rows become mutable.
