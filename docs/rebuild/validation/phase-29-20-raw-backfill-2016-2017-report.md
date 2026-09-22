# Phase 29.20 Raw Backfill 2016-2017 Report

Date: 2026-06-29

Final decision: **2016-2017 RAW BACKFILL READY WITH WARNINGS**

## Scope

Authorized raw-only nflverse historical backfill for seasons 2016 and 2017.

Preset: `core_historical`

Written objects were limited to `raw_nflverse_*` tables. No staging transforms, advanced metrics materialization, Pigskin packet refresh, deployments, Cloud Run Jobs, Scheduler jobs, score materialization, ingestion pipeline runs, LLM actions, Pigskin prompts, scraping, Firebase artifacts, or commits were run.

Latest commit before and after this phase:

`67f37e7 Expand nflverse Pigskin pipeline to 2015`

## Authorization Gates

Initial gate state:

| Gate | State |
| --- | --- |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Write authorization was set only inside the PowerShell wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"
  .\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2016 --season-end 2017 --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

Final gate state: all gates listed above were unset after the wrapper completed.

## Baseline Checks

All baseline checks passed before write:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile app.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest discover tests` | PASS, 483 tests |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Plan And Dry Runs

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2016 --season-end 2017 --output-json %TEMP%\phase29_20_plan_prepare\plan_only.json
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2016 --season-end 2017 --dry-run
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2016 --season-end 2017 --prepare-only --skip-source-family-on-error
```

Selected source families:

`schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`

Prepare-only result:

| Family | Fetched | Prepared | Skipped | Target | Warnings |
| --- | ---: | ---: | ---: | --- | --- |
| schedules | 534 | 534 | 0 | `raw_nflverse_schedules` | none |
| teams | 36 | 36 | 0 | `raw_nflverse_teams` | none |
| players | 25033 | 25033 | 0 | `raw_nflverse_players` | none |
| ff_playerids | 12465 | 69060 | 9686 | `raw_nflverse_ff_playerids` | 9641 missing `nflverse_player_id`; 45 source rows deduped |
| rosters | 6143 | 6143 | 0 | `raw_nflverse_rosters` | none |
| rosters_weekly | 86341 | 86341 | 0 | `raw_nflverse_rosters_weekly` | none |
| weekly | 35029 | 34987 | 42 | `raw_nflverse_weekly` | 42 rows missing `player_id` |
| pbp | 94896 | 94896 | 0 | `raw_nflverse_pbp` | none |
| snap_counts | 47752 | 47752 | 0 | `raw_nflverse_snap_counts` | none |

Prepare-only source refresh ID:

`nflverse_core_historical_2016_2017_20260629T215359Z`

## Pre-Write Raw Coverage

Before the write, all season-grained raw tables had zero 2016 and 2017 rows.

| Table | Total Rows Before | 2016 Rows Before | 2017 Rows Before | Season Range Before |
| --- | ---: | ---: | ---: | --- |
| `raw_nflverse_schedules` | 534 | 0 | 0 | 2014-2015 |
| `raw_nflverse_rosters` | 4341 | 0 | 0 | 2014-2015 |
| `raw_nflverse_rosters_weekly` | 60396 | 0 | 0 | 2014-2015 |
| `raw_nflverse_weekly` | 35193 | 0 | 0 | 2014-2015 |
| `raw_nflverse_pbp` | 95751 | 0 | 0 | 2014-2015 |
| `raw_nflverse_snap_counts` | 47706 | 0 | 0 | 2014-2015 |

Static/global table state before write:

| Table | Rows Before |
| --- | ---: |
| `raw_nflverse_players` | 25033 |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_ff_playerids` | 69060 |

## Raw Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2016 --season-end 2017 --write --strict
```

Result:

| Field | Value |
| --- | --- |
| Exit code | 0 |
| Elapsed seconds | 285.41 |
| Source refresh ID | `nflverse_core_historical_2016_2017_20260629T215810Z` |
| Source families attempted | 9 |
| Source families succeeded | 9 |
| Source families failed | 0 |
| Source families skipped | 0 |
| Wrote rows | true |

Write family summary:

| Family | Prepared | Written Or Merged | Target Rows After | Duplicate Groups After | Warnings |
| --- | ---: | ---: | ---: | ---: | --- |
| schedules | 534 | 534 | 1068 | 0 | none |
| teams | 36 | 0 | 36 | 0 | static table already current |
| players | 25033 | 0 | 25033 | 0 | static table already current |
| ff_playerids | 69060 | 0 | 69060 | 0 | skipped missing IDs; deduped source rows |
| rosters | 6143 | 6143 | 10484 | 0 | none |
| rosters_weekly | 86341 | 86341 | 146737 | 0 | none |
| weekly | 34987 | 34987 | 70180 | 0 | skipped 42 non-player or aggregate rows missing `player_id` |
| pbp | 94896 | 94896 | 190647 | 0 | none |
| snap_counts | 47752 | 47752 | 95458 | 0 | none |

Runtime warning observed, non-fatal:

`Loading pandas DataFrame into BigQuery will require pandas-gbq package version 0.26.1 or greater in the future. Tried to import pandas-gbq and got: No module named 'pandas_gbq'`

## Post-Write Raw Verification

| Table | Total Rows | 2016 Rows | 2017 Rows | Week Range For 2016-2017 | Metadata Rows Checked | Metadata Complete | Duplicate Key Groups |
| --- | ---: | ---: | ---: | --- | ---: | --- | ---: |
| `raw_nflverse_schedules` | 1068 | 267 | 267 | 1-21 | 534 | yes | 0 |
| `raw_nflverse_rosters` | 10484 | 3061 | 3082 | n/a | 6143 | yes | 0 |
| `raw_nflverse_rosters_weekly` | 146737 | 35020 | 51321 | 1-21 | 86341 | yes | 0 |
| `raw_nflverse_weekly` | 70180 | 17531 | 17456 | 1-21 | 34987 | yes | 0 |
| `raw_nflverse_pbp` | 190647 | 47651 | 47245 | 1-21 | 94896 | yes | 0 |
| `raw_nflverse_snap_counts` | 95458 | 23890 | 23862 | 1-21 | 47752 | yes | 0 |
| `raw_nflverse_teams` | 36 | n/a | n/a | n/a | 36 | yes | 0 |
| `raw_nflverse_players` | 25033 | n/a | n/a | n/a | 25033 | yes | 0 |
| `raw_nflverse_ff_playerids` | 69060 | n/a | n/a | n/a | 69060 | yes | 0 using `nflverse_player_id, platform, platform_player_id` |

All checked metadata fields were populated in the target scope: `source_refresh_id`, `loaded_at`, and `row_hash`.

Source loaders and versions:

| Table | Loader | Source Version |
| --- | --- | --- |
| `raw_nflverse_schedules` | `nflreadpy.load_schedules` | `0.1.5` |
| `raw_nflverse_rosters` | `nflreadpy.load_rosters` | `0.1.5` |
| `raw_nflverse_rosters_weekly` | `nflreadpy.load_rosters_weekly` | `0.1.5` |
| `raw_nflverse_weekly` | `nflreadpy.load_player_stats` | `0.1.5` |
| `raw_nflverse_pbp` | `nflreadpy.load_pbp` | `0.1.5` |
| `raw_nflverse_snap_counts` | `nflreadpy.load_snap_counts` | `0.1.5` |
| `raw_nflverse_teams` | `nflreadpy.load_teams` | `0.1.5` |
| `raw_nflverse_players` | `nflreadpy.load_players` | `0.1.5` |
| `raw_nflverse_ff_playerids` | `nflreadpy.load_ff_playerids` | `0.1.5` |

## Non-Target Object Verification

No downstream staging or mart rows were created for 2016 or 2017.

| Object | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `stg_player_identity` | 60396 | 0 | 0 |
| `stg_game_context` | 534 | 0 | 0 |
| `stg_player_week_stats` | 35193 | 0 | 0 |
| `stg_team_week_stats` | 1068 | 0 | 0 |
| `stg_play_player_events` | 234469 | 0 | 0 |
| `stg_participation_context` | 47706 | 0 | 0 |
| `player_week_advanced_metrics` | 35193 | 0 | 0 |
| `team_week_context_metrics` | 1068 | 0 | 0 |
| `qb_week_environment_metrics` | 1261 | 0 | 0 |
| `player_recent_advanced_metrics_current` | 2309 | 0 | 0 |
| `player_role_usage_metrics_current` | 2309 | 0 | 0 |
| `pigskin_player_context_packet_current` | 980 | 0 | 0 |
| `compat_pigskin_player_context_current` | 980 | 0 | 0 |

Score tables were unchanged:

| Object | Rows |
| --- | ---: |
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validations

| Command | Result |
| --- | --- |
| `run_bigquery_validations.py --run --pattern raw_nflverse` | PASS with review warning |
| `run_bigquery_validations.py --run --pattern stg_` | PASS |
| `run_bigquery_validations.py --run --pattern advanced_metrics` | PASS |
| `run_bigquery_validations.py --run --pattern compat_pigskin` | PASS |
| `run_bigquery_validations.py --run --pattern trade_player_scores` | PASS |
| `run_bigquery_validations.py --run --pattern trade_pick_scores` | PASS with informational warning |

Validation warnings:

| Validation | Warning |
| --- | --- |
| `181_raw_nflverse_season_week_coverage.sql` | Informational review query returned expanded raw coverage through 2017, expected after this phase. |
| `178_trade_pick_scores_model_version_coverage.sql` | Informational model-version coverage query returned existing `trade_pick_score_v0_2026_001` rows. |

No validation command failed.

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile app.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_plan` | PASS |
| `unittest tests.test_nflverse_backfill_executor` | PASS |
| `unittest discover tests` | PASS |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Service Readback

Production was untouched.

| Service | Revision | Traffic | Image | Relevant Flag State |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100 percent | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | all production risk flags false; Trade Analyzer score false; Trade History compat false; Data Ops trigger and local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100 percent | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score flags true; Trade History compat true; Data Ops trigger and local subprocess flags false |

## Warnings

- `ff_playerids` skipped 9641 rows with missing `nflverse_player_id` and deduped 45 source rows before merge. The final natural key check on `nflverse_player_id, platform, platform_player_id` had zero duplicates.
- `weekly` skipped 42 rows with missing `player_id`. The loader warning says these should be treated as non-player or aggregate rows unless a safe source key is proven.
- BigQuery emitted a pandas-gbq future warning during DataFrame loads. The write completed successfully.
- `raw_nflverse` season/week coverage validation is informational and now reflects 2014-2017 raw coverage.
- Static/global families were already current, so `teams`, `players`, and `ff_playerids` had zero net new merged rows.

## Blockers

None for raw 2016-2017 coverage.

Downstream staging, advanced metrics, and Pigskin packet refresh remain intentionally not run in this phase.

## Recommended Next Phase

Run an authorized, bounded Phase 29.21 staging materialization for 2016-2017, or use a one-season 2016 staging pass first if the owner wants the same conservative cadence used for the 2014 and 2015 canaries.
