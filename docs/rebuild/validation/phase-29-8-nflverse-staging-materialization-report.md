# Phase 29.8 nflverse Staging Materialization Report

Final decision: **NFLVERSE STAGING MATERIALIZED WITH WARNINGS**

## Scope

Phase 29.8 wrote only 2014 rows to the six canonical nflverse staging tables:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

No raw nflverse backfill was rerun. No feature marts, advanced metrics, Pigskin packets, rankings, Cloud Run Jobs, deployments, feature flags, LLM actions, scraping, or Firebase artifacts were touched.

## Authorization Gate State

Before write, all checked gates were empty or unset:

- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

The live write used the required same-session wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --all-targets --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

After write, all checked gates were again empty or unset:

- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Git State

Latest commit before this phase:

```text
a73656c Document draft pick score release package
```

No files were staged. The worktree still contains Phase 29 untracked source, contract, migration, validation, and report files plus the historical validation backlog. Existing tracked modifications remain:

- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/table-classification.md`

Files changed by this phase:

- `src/nflverse_staging.py`
- `tests/test_nflverse_staging.py`
- `docs/rebuild/validation/phase-29-8-nflverse-staging-materialization-report.md`

## Baseline Checks

Initial baseline passed:

- `scripts/check_deployment_safety.py`: pass
- `py_compile` for `src\nflverse_staging.py`, `src\nflverse_backfill.py`, `src\nflverse_backfill_plan.py`: pass
- `compileall -q src scripts`: pass
- focused nflverse and Pigskin contract tests: pass
- `unittest discover tests`: pass
- migrations list: no pending migrations
- validation dry-run: pass, discovered validations through `200_no_pressure_metrics_without_source.sql`

## Raw Source Precheck

Raw source row counts before the staging write matched the expected smoke state:

| Table | Total rows | 2014 rows | Season range |
|---|---:|---:|---|
| `raw_nflverse_schedules` | 267 | 267 | 2014 to 2014 |
| `raw_nflverse_teams` | 36 | static | static |
| `raw_nflverse_players` | 25,033 | static | static |
| `raw_nflverse_ff_playerids` | 69,060 | static | static |
| `raw_nflverse_rosters` | 2,152 | 2,152 | 2014 to 2014 |
| `raw_nflverse_rosters_weekly` | 30,195 | 30,195 | 2014 to 2014 |
| `raw_nflverse_weekly` | 17,601 | 17,601 | 2014 to 2014 |
| `raw_nflverse_pbp` | 47,629 | 47,629 | 2014 to 2014 |
| `raw_nflverse_snap_counts` | 23,864 | 23,864 | 2014 to 2014 |

## Staging Pre-Write Counts

All six staging targets were empty before the first materialization:

| Table | Total rows | 2014 rows |
|---|---:|---:|
| `stg_player_identity` | 0 | 0 |
| `stg_game_context` | 0 | 0 |
| `stg_player_week_stats` | 0 | 0 |
| `stg_team_week_stats` | 0 | 0 |
| `stg_play_player_events` | 0 | 0 |
| `stg_participation_context` | 0 | 0 |

## Final Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --all-targets
```

Result:

| Target | Planned rows | Source rows | Duplicate grains | Readiness |
|---|---:|---:|---:|---|
| `stg_player_identity` | 30,195 | not reported by diagnostic | 0 | ready with warnings |
| `stg_game_context` | 267 | 267 | 0 | ready |
| `stg_player_week_stats` | 17,601 | 17,601 | 0 | ready with warnings |
| `stg_team_week_stats` | 534 | 47,629 | 0 | ready with warnings |
| `stg_play_player_events` | 116,400 | 47,629 | 0 | ready with warnings |
| `stg_participation_context` | 23,864 | 23,864 | 0 | ready with warnings |

No writes occurred during dry-run.

## Write Mode Implementation

`src.nflverse_staging` now supports a gated Phase 29.8 write path:

- `--write` requires `ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true`.
- Unrelated gates do not authorize staging writes.
- The write path only accepts registered `stg_*` targets.
- Source plans are checked for `raw_nflverse_*` sources only.
- Legacy tables such as `play_by_play`, `weekly_metrics`, and `player_rosters` are blocked from staging source SQL.
- Feature marts and Pigskin packet tables are blocked from staging source SQL.
- Writes use BigQuery `MERGE`.
- No full-table `WRITE_TRUNCATE`, `TRUNCATE`, or unbounded replacement is used.
- Grains use null-safe equality, so repeated writes remain idempotent if nullable keys appear.

Tests added or updated in `tests/test_nflverse_staging.py` cover:

- fail-closed `--write` when the staging gate is unset;
- unrelated gates do not authorize staging writes;
- authorized writes use `MERGE` for staging targets;
- merge SQL uses null-safe contract grains;
- merge SQL does not reference score or feature marts.

## Live Staging Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --all-targets --write --strict
```

Result:

| Target | Planned rows | DML affected rows | 2014 rows after | Duplicate grains after |
|---|---:|---:|---:|---:|
| `stg_player_identity` | 30,195 | 30,195 | 30,195 | 0 |
| `stg_game_context` | 267 | 267 | 267 | 0 |
| `stg_player_week_stats` | 17,601 | 17,601 | 17,601 | 0 |
| `stg_team_week_stats` | 534 | 534 | 534 | 0 |
| `stg_play_player_events` | 116,400 | 116,400 | 116,400 | 0 |
| `stg_participation_context` | 23,864 | 23,864 | 23,864 | 0 |

## Post-Write Staging Verification

| Target | Total rows | 2014 rows | Week range | Missing identity rows | Missing freshness rows | Missing flag rows | Duplicate grains | Route share non-null | True route source |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `stg_player_identity` | 30,195 | 30,195 | 1 to 21 | 0 | 0 | 0 | 0 | 0 | 0 |
| `stg_game_context` | 267 | 267 | 1 to 21 | 0 | 0 | 0 | 0 | 0 | 0 |
| `stg_player_week_stats` | 17,601 | 17,601 | 1 to 21 | 3,818 | 0 | 0 | 0 | 0 | 0 |
| `stg_team_week_stats` | 534 | 534 | 1 to 21 | 0 | 0 | 0 | 0 | 0 | 0 |
| `stg_play_player_events` | 116,400 | 116,400 | 1 to 21 | 14,991 | 0 | 0 | 0 | 0 | 0 |
| `stg_participation_context` | 23,864 | 23,864 | 1 to 21 | 3,818 | 0 | 0 | 0 | 0 | 0 |

Route-share status remains blocked as intended:

- `route_share` non-null rows: 0
- `has_true_route_source` true rows: 0

The identity gaps are preserved in `missing_data_flags`; they were not hidden or coerced away.

## Non-Target Object Verification

Raw nflverse source counts remained unchanged after the staging write:

| Table | Total rows | 2014 rows |
|---|---:|---:|
| `raw_nflverse_schedules` | 267 | 267 |
| `raw_nflverse_teams` | 36 | static |
| `raw_nflverse_players` | 25,033 | static |
| `raw_nflverse_ff_playerids` | 69,060 | static |
| `raw_nflverse_rosters` | 2,152 | 2,152 |
| `raw_nflverse_rosters_weekly` | 30,195 | 30,195 |
| `raw_nflverse_weekly` | 17,601 | 17,601 |
| `raw_nflverse_pbp` | 47,629 | 47,629 |
| `raw_nflverse_snap_counts` | 23,864 | 23,864 |

Feature and Pigskin objects remained empty:

| Object | Rows |
|---|---:|
| `player_week_advanced_metrics` | 0 |
| `team_week_context_metrics` | 0 |
| `qb_week_environment_metrics` | 0 |
| `pigskin_player_context_packet_current` | 0 |
| `compat_pigskin_player_context_current` | 0 |
| `player_recent_advanced_metrics_current` | 0 |
| `player_role_usage_metrics_current` | 0 |

Score lanes were not modified by this phase. Current row counts were recorded for separation:

| Object | Rows |
|---|---:|
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

Legacy source tables were not used by the write path. Current counts:

| Object | Rows |
|---|---:|
| `play_by_play` | 48,771 |
| `weekly_metrics` | 19,421 |
| `player_rosters` | 25,040 |
| `weekly_snap_counts` | 26,612 |

## Validation Results

Post-write validations:

- `--pattern raw_nflverse`: 3 passed, 0 failed. Informational warning from `181_raw_nflverse_season_week_coverage.sql` for 2014 smoke coverage review.
- `--pattern stg_`: 7 passed, 0 failed.
- `--pattern advanced_metrics`: 4 passed, 0 failed.
- `--pattern compat_pigskin`: 2 passed, 0 failed.
- `--pattern trade_player_scores`: 12 passed, 0 failed.
- `--pattern trade_pick_scores`: 17 passed, 0 failed. Informational warning from `178_trade_pick_scores_model_version_coverage.sql` for existing model version coverage.

## Final Local Checks

Final checks passed:

- `scripts/check_deployment_safety.py`
- `py_compile` for `src\nflverse_staging.py`, `src\nflverse_backfill.py`, `src\nflverse_backfill_plan.py`
- `compileall -q src scripts`
- `tests.test_nflverse_staging`
- `tests.test_nflverse_backfill_executor`
- `tests.test_nflverse_backfill_plan`
- `tests.test_nflverse_historical_contracts`
- `tests.test_pigskin_advanced_metrics_contracts`
- `unittest discover tests`
- migrations list: no pending migrations
- validation dry-run: pass, discovered validations through 200

## Staging and Production Untouched

Read-only Cloud Run describe confirmed no deployment occurred.

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops trigger flags false
- local subprocess flags false

## Remaining Warnings

- 2014 identity gaps remain:
  - `stg_player_week_stats`: 3,818 rows
  - `stg_play_player_events`: 14,991 rows
  - `stg_participation_context`: 3,818 rows
- 2014 snap counts use PFR IDs for matching.
- `route_share` remains null and `has_true_route_source` remains false because no true route source is loaded.
- Red-zone, inside-10, inside-5, reception, and touchdown event counts remain incomplete or zero and must not feed advanced metrics until source-field review is complete.
- The working tree remains intentionally dirty with Phase 29 files and historical validation backlog. No files were staged or committed.

## Recommended Next Phase

Proceed to a bounded Phase 29.9 feature-mart dry-run or transform design only after accepting the identity and route-source warnings. Do not materialize `player_week_advanced_metrics`, `team_week_context_metrics`, `qb_week_environment_metrics`, or Pigskin context until the staging warnings are either accepted for limited use or corrected.
