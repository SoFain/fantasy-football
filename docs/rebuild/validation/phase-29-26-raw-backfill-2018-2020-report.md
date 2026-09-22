# Phase 29.26 Raw nflverse Backfill 2018-2020 Report

Date: 2026-06-30

Final decision: **2018-2020 RAW BACKFILL READY WITH WARNINGS**

## Scope

Phase 29.26 ran the authorized historical raw nflverse backfill for seasons 2018 through 2020 only.

Live write scope:

- Preset: `core_historical`
- Seasons: 2018-2020
- Families: `schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`
- Target: `raw_nflverse_*` tables only

No staging materialization, advanced metrics materialization, Pigskin packet refresh, ranking build, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, or Firebase artifact occurred.

## Authorization Gate State

Before the write, all checked gates were unset:

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

The live write used the required same-session wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"
  echo "ALLOW_NFLVERSE_HISTORICAL_BACKFILL=$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL"
  .\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2018 --season-end 2020 --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

After the write, these gates were confirmed unset:

| Gate | State |
| --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Git State

Latest commit at start:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

No files were staged at the start. The existing historical validation backlog remained untracked.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest discover tests` | PASS, 487 tests |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, validation catalog discovered through 200 |

## Plan-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2018 --season-end 2020
```

Result:

- `dry_run: True`
- Mode: `historical_backfill`
- Project/dataset: `fantasy-football-498121.fantasy_football_brain`
- Season range: `2018-2020`
- Selected families: `schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`
- No loaders called.
- No BigQuery rows written.

Known planner warnings:

- Season-level loaders are not week-bounded extraction paths.
- Raw `raw_nflverse_*` tables are not Pigskin/UI-safe surfaces.
- Snap share is valid from snap counts; route share still needs a true route source.

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2018 --season-end 2020 --dry-run
```

Result:

- `wrote: false`
- Selected source families matched `core_historical`.
- No BigQuery rows written.

## Prepare-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2018 --season-end 2020 --prepare-only --skip-source-family-on-error
```

Result:

- `wrote: false`
- `prepare_only: true`
- Source refresh ID: `nflverse_core_historical_2018_2020_20260630T042354Z`
- All critical families prepared nonzero rows.
- No source family failed.

| Family | Fetched | Prepared | Skipped | Warnings |
| --- | ---: | ---: | ---: | --- |
| `schedules` | 803 | 803 | 0 | none |
| `teams` | 36 | 36 | 0 | none |
| `players` | 25,033 | 25,033 | 0 | none |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 9,641 missing `nflverse_player_id`; 45 deduped source rows |
| `rosters` | 9,324 | 9,321 | 3 | 3 missing `player_id` |
| `rosters_weekly` | 148,000 | 147,954 | 46 | 46 missing `player_id` |
| `weekly` | 52,378 | 52,315 | 63 | 63 missing `player_id`, treated as non-player or aggregate rows |
| `pbp` | 142,074 | 142,074 | 0 | none |
| `snap_counts` | 72,738 | 72,738 | 0 | none |

Skipped-row behavior matched accepted patterns from earlier expansion phases.

## Pre-Write Raw State

Before the live write, season-grained 2018-2020 raw targets were empty:

| Table | 2018-2020 rows |
| --- | ---: |
| `raw_nflverse_schedules` | 0 |
| `raw_nflverse_rosters` | 0 |
| `raw_nflverse_rosters_weekly` | 0 |
| `raw_nflverse_weekly` | 0 |
| `raw_nflverse_pbp` | 0 |
| `raw_nflverse_snap_counts` | 0 |

Static/global raw tables before write:

| Table | Rows |
| --- | ---: |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

## Live Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2018 --season-end 2020 --write --strict
```

Result:

- `wrote: true`
- Source refresh ID: `nflverse_core_historical_2018_2020_20260630T042853Z`
- Elapsed seconds: `498.243`
- Critical failures: none
- Failed families: none
- Succeeded families: all nine selected families

| Family | Fetched | Prepared | Skipped | Written or merged | Duplicate keys after |
| --- | ---: | ---: | ---: | ---: | ---: |
| `schedules` | 803 | 803 | 0 | 803 | 0 |
| `teams` | 36 | 36 | 0 | 0 | 0 |
| `players` | 25,033 | 25,033 | 0 | 0 | 0 |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 0 | 0 |
| `rosters` | 9,324 | 9,321 | 3 | 9,321 | 0 |
| `rosters_weekly` | 148,000 | 147,954 | 46 | 147,954 | 0 |
| `weekly` | 52,378 | 52,315 | 63 | 52,315 | 0 |
| `pbp` | 142,074 | 142,074 | 0 | 142,074 | 0 |
| `snap_counts` | 72,738 | 72,738 | 0 | 72,738 | 0 |

Runtime warning:

- BigQuery pandas helper emitted a future warning that `pandas-gbq>=0.26.1` will be required for future DataFrame loads. This did not fail the backfill.

## Post-Write Raw Verification

All metadata fields were populated for 2018-2020 rows in season-grained targets:

- `source_refresh_id`
- `loaded_at`
- `row_hash`

All checked duplicate natural key counts were `0`.

| Table | Total rows | 2018 rows | 2019 rows | 2020 rows | Week range | Duplicate keys |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `raw_nflverse_schedules` | 1,871 | 267 | 267 | 269 | 1-21 | 0 |
| `raw_nflverse_rosters` | 19,805 | 3,141 | 3,113 | 3,067 | n/a | 0 |
| `raw_nflverse_rosters_weekly` | 294,691 | 52,200 | 51,630 | 44,124 | 1-21 | 0 |
| `raw_nflverse_weekly` | 122,495 | 17,393 | 17,341 | 17,581 | 1-21 | 0 |
| `raw_nflverse_pbp` | 332,721 | 47,109 | 47,260 | 47,705 | 1-21 | 0 |
| `raw_nflverse_snap_counts` | 168,196 | 23,877 | 23,862 | 24,999 | 1-21 | 0 |

Source loader distribution for 2018-2020 rows:

| Table | Loader | Rows |
| --- | --- | ---: |
| `raw_nflverse_schedules` | `nflreadpy.load_schedules` | 803 |
| `raw_nflverse_rosters` | `nflreadpy.load_rosters` | 9,321 |
| `raw_nflverse_rosters_weekly` | `nflreadpy.load_rosters_weekly` | 147,954 |
| `raw_nflverse_weekly` | `nflreadpy.load_player_stats` | 52,315 |
| `raw_nflverse_pbp` | `nflreadpy.load_pbp` | 142,074 |
| `raw_nflverse_snap_counts` | `nflreadpy.load_snap_counts` | 72,738 |

Source version distribution:

- All 2018-2020 season-grained rows used `source_version = 0.1.5`.

## Static and Global Table Behavior

Static/global tables remained idempotent:

| Table | Rows after write | Duplicate keys | Metadata populated |
| --- | ---: | ---: | --- |
| `raw_nflverse_teams` | 36 | 0 | yes |
| `raw_nflverse_players` | 25,033 | 0 | yes |
| `raw_nflverse_ff_playerids` | 69,060 | 0 | yes |

No static/global table grew during this phase.

## 2020-Specific Source Behavior

2020 loaded successfully for all season-grained target families. Differences to note:

- `raw_nflverse_schedules` has 269 rows for 2020, compared with 267 in 2018 and 2019.
- `raw_nflverse_rosters_weekly` has 44,124 rows for 2020, lower than 2018 and 2019.
- `raw_nflverse_weekly`, `raw_nflverse_pbp`, and `raw_nflverse_snap_counts` all loaded nonzero 2020 rows with week range 1-21 and complete metadata.

These are documented season-context differences, not blockers.

## Non-Target Object Verification

The following counts matched the pre-write baseline exactly:

| Object | Rows |
| --- | ---: |
| `stg_player_identity` | 146,737 |
| `stg_game_context` | 1,068 |
| `stg_player_week_stats` | 70,180 |
| `stg_team_week_stats` | 2,136 |
| `stg_play_player_events` | 466,660 |
| `stg_participation_context` | 95,458 |
| `player_week_advanced_metrics` | 70,180 |
| `team_week_context_metrics` | 2,136 |
| `qb_week_environment_metrics` | 2,525 |
| `player_recent_advanced_metrics_current` | 3,128 |
| `pigskin_player_context_packet_current` | 1,587 |
| `compat_pigskin_player_context_current` | 1,587 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

No staging, metrics, packet, compatibility view, or score-lane write occurred.

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS, 3 passed, 0 failed. Informational coverage warning now reports 2014-2020 coverage. |
| `stg_` | PASS, 7 passed, 0 failed |
| `advanced_metrics` | PASS, 4 passed, 0 failed |
| `compat_pigskin` | PASS, 2 passed, 0 failed |
| `trade_player_scores` | PASS, 12 passed, 0 failed |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Informational model-version warning remains. |

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest discover tests` | PASS, 487 tests |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, validation catalog discovered through 200 |

## Staging and Production Untouched

Read-only Cloud Run describes confirmed no deployment occurred.

| Service | Revision | Traffic | Image digest | Flag state |
| --- | --- | ---: | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | production risk flags false, score flags false, Trade History compatibility false, Data Ops job/local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score and Trade History flags remain true as previously configured, Data Ops job/local subprocess flags false |

## Remaining Warnings

- `ff_playerids`, `teams`, and `players` are static/global tables and remained idempotent.
- `ff_playerids` skipped missing `nflverse_player_id` rows and deduped 45 source rows before merge.
- `weekly` skipped 63 missing-player rows, treated as non-player or aggregate rows.
- `rosters` skipped 3 rows with missing `player_id`.
- `rosters_weekly` skipped 46 rows with missing `player_id`.
- `snap_counts` uses PFR identifiers where GSIS is unavailable.
- Raw nflverse validation has an informational coverage row.
- Trade pick score validation has an informational model-version coverage row.
- BigQuery DataFrame loads emitted a future `pandas-gbq` dependency warning.

## Recommended Next Phase

Phase 29.27: authorized 2018-2020 staging materialization, with a dry-run/plan first and explicit confirmation that no advanced metrics or Pigskin packet refresh runs in the same phase.
