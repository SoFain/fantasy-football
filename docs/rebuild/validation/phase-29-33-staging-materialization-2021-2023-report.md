# Phase 29.33 - 2021-2023 nflverse Staging Materialization

Date: 2026-06-30

## Final Decision

2021-2023 STAGING MATERIALIZED WITH WARNINGS

The bounded 2021-2023 nflverse staging materialization completed successfully for all six staging targets. The write gate was set only inside the same PowerShell command session and was removed immediately afterward. No raw backfill, advanced metrics materialization, Pigskin packet refresh, deployment, Cloud Run Job trigger, Scheduler job, LLM action, scraping, ranking refresh, or commit occurred.

## Authorization Gate State

Before materialization, these gates were empty or unset:

- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

During the live write, only `ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true` was set, inside this wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION = "true"

  echo "ALLOW_NFLVERSE_STAGING_MATERIALIZATION=$env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION"

  .\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2021 --season-end 2023 --all-targets --write --strict

} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

After materialization, the gate was removed and the checked authorization gates were empty or unset.

## Git State

- Latest commit before this phase: `db8f279 Expand nflverse Pigskin packets through 2020`
- No staged files before the phase.
- No tracked diffs before the phase.
- Historical validation backlog remained untracked.

## Baseline Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_executor`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- `tests.test_nflverse_staging`: 11 tests passed.
- `tests.test_nflverse_backfill_executor`: 18 tests passed.
- Full unit discovery: 487 tests passed.
- No pending migrations.
- Validation catalog discovered through `200_no_pressure_metrics_without_source.sql`.

## Raw Source Precheck

Read-only source coverage confirmed for 2021-2023:

| Source table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `raw_nflverse_schedules` | 285 | 284 | 285 | 1-22 |
| `raw_nflverse_rosters` | 2,960 | 3,133 | 3,089 | season table |
| `raw_nflverse_rosters_weekly` | 46,670 | 46,136 | 45,650 | 1-22 |
| `raw_nflverse_weekly` | 18,947 | 18,809 | 18,621 | 1-22 |
| `raw_nflverse_pbp` | 49,922 | 49,434 | 49,665 | 1-22 |
| `raw_nflverse_snap_counts` | 26,468 | 26,381 | 26,540 | 1-22 |

Static raw tables:

- `raw_nflverse_teams`: 36 rows
- `raw_nflverse_players`: 25,033 rows
- `raw_nflverse_ff_playerids`: 69,060 rows

## Staging Pre-Write State

Read-only pre-write checks found no 2021-2023 rows in the six target staging tables:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2021 --season-end 2023 --dry-run --all-targets --strict
```

Result: exit 0, `wrote=false`.

| Target | Dry-run status | Planned rows | Duplicate groups | Notes |
| --- | --- | ---: | ---: | --- |
| `stg_player_identity` | ready with warnings | 138,456 | 0 | No name-only identity joins are used. |
| `stg_game_context` | ready | 854 | 0 | 17-game era schedule weeks covered. |
| `stg_player_week_stats` | ready with warnings | 56,377 | 0 | Legacy `weekly_metrics` is not used. |
| `stg_team_week_stats` | ready with warnings | 1,708 | 0 | `pass_rate_over_expected` remains null until a model source exists. |
| `stg_play_player_events` | ready with warnings | 360,856 | 0 | Route metrics are not created. |
| `stg_participation_context` | ready with warnings | 79,389 | 0 | 153 missing identity matches from PFR snap-count identity gaps; route source remains blocked. |

## Live Staging Write

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2021 --season-end 2023 --all-targets --write --strict
```

Result: exit 0, `wrote=true`.

| Target | MERGE affected rows | Bounded rows written | Duplicate groups | Rows outside 2021-2023 written |
| --- | ---: | ---: | ---: | ---: |
| `stg_player_identity` | 138,456 | 138,456 | 0 | 0 |
| `stg_game_context` | 854 | 854 | 0 | 0 |
| `stg_player_week_stats` | 56,377 | 56,377 | 0 | 0 |
| `stg_team_week_stats` | 1,708 | 1,708 | 0 | 0 |
| `stg_play_player_events` | 360,856 | 360,856 | 0 | 0 |
| `stg_participation_context` | 79,389 | 79,389 | 0 | 0 |

The CLI output still uses stale internal wording that references Phase 29.8. The executed command, gate, and target window were Phase 29.33 and bounded to 2021-2023.

## Post-Write Staging Verification

Read-only post-write checks used the grains declared in `src\nflverse_staging.py`:

- `stg_player_identity`: `player_id_internal`, `season`, `week`, `team`
- `stg_game_context`: `season`, `week`, `game_id`
- `stg_player_week_stats`: `season`, `week`, `player_id_internal`, `team`
- `stg_team_week_stats`: `season`, `week`, `team`
- `stg_play_player_events`: `season`, `week`, `game_id`, `play_id`, `event_type`, `player_id_internal`, `team`
- `stg_participation_context`: `season`, `week`, `game_id`, `player_id_internal`, `team`

| Target | 2021 rows | 2022 rows | 2023 rows | Week range | Duplicate groups | Missing freshness | Missing flags | Required field nulls |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| `stg_player_identity` | 46,670 | 46,136 | 45,650 | 1-22 | 0 | 0 | 0 | 0 |
| `stg_game_context` | 285 | 284 | 285 | 1-22 | 0 | 0 | 0 | 0 |
| `stg_player_week_stats` | 18,947 | 18,809 | 18,621 | 1-22 | 0 | 0 | 0 | 0 |
| `stg_team_week_stats` | 570 | 568 | 570 | 1-22 | 0 | 0 | 0 | 0 |
| `stg_play_player_events` | 121,589 | 119,216 | 120,051 | 1-22 | 0 | 0 | 0 | 0 |
| `stg_participation_context` | 26,468 | 26,381 | 26,540 | 1-22 | 0 | 0 | 0 | 0 |

## Identity Gap Summary

- `stg_player_identity`: 0 missing identity matches, 0 ambiguous identity rows.
- `stg_player_week_stats`: 0 missing identity matches, 0 ambiguous identity rows.
- `stg_play_player_events`: 0 missing identity matches, 0 ambiguous identity rows.
- `stg_participation_context`: 153 missing identity matches, 0 ambiguous identity rows.

The remaining participation gap is limited to snap-count/PFR identity coverage and is carried in `missing_data_flags`.

## Route-Share Blocked Confirmation

`stg_participation_context` route-source checks:

- `route_share_non_null`: 0
- `true_route_source_rows`: 0

No route participation metric was inferred without a route source.

## 17-Game Era Behavior

The 2021-2023 staging layer uses nflverse week range 1-22. Schedule row counts are 285, 284, and 285 respectively. This reflects postseason-inclusive source coverage and does not imply current-week presentation in Pigskin.

## Non-Target Object Verification

Read-only counts after staging materialization:

| Object | Row count |
| --- | ---: |
| `player_week_advanced_metrics` | 122,495 |
| `team_week_context_metrics` | 3,742 |
| `qb_week_environment_metrics` | 4,513 |
| `pigskin_player_context_packet_current` | 2,336 |
| `compat_pigskin_player_context_current` | 2,336 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

No advanced metrics, Pigskin packet, player score, or pick score write was run in this phase.

## Validation Results

Passed:

- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern stg_`: 7 passed, 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern advanced_metrics`: 4 passed, 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_pigskin`: 2 passed, 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores`: 12 passed, 0 failed.

Passed with informational warnings:

- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern raw_nflverse`: 3 passed, 0 failed. Validation `181_raw_nflverse_season_week_coverage.sql` returned informational coverage rows showing raw nflverse tables now span 2014-2023.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_pick_scores`: 17 passed, 0 failed. Validation `178_trade_pick_scores_model_version_coverage.sql` returned the expected informational model-version coverage row.

## Final Local Checks

Passed after the live write:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_executor`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- `tests.test_nflverse_staging`: 11 tests passed.
- `tests.test_nflverse_backfill_executor`: 18 tests passed.
- Full unit discovery: 487 tests passed.
- No pending migrations.

## Production and Staging Untouched

Read-only Cloud Run describe after the write:

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false
- Existing staging-only Trade History and score UI flags remain enabled from prior QA.

## Remaining Warnings

- The staging CLI output still contains stale Phase 29.8 wording. The command and gate were correct for Phase 29.33.
- `stg_participation_context` has 153 known missing identity matches from PFR snap-count identity coverage.
- Route share remains unavailable: `route_share` is null and `has_true_route_source` is false for the 2021-2023 participation rows.
- Raw nflverse tables are internal warehouse sources only. They remain unsafe for direct Pigskin or UI exposure.
- The 2021-2023 source range is postseason-inclusive through week 22.

## Recommended Next Phase

Proceed to a separate Phase 29.34 for bounded 2021-2023 base advanced metrics materialization. That phase should dry-run first, require its own explicit materialization gate, and keep Pigskin packet refresh separate.
