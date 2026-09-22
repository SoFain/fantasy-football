# Phase 29.4 nflverse Warehouse Migration Apply Report

Date: 2026-06-29

Final decision: NFLVERSE WAREHOUSE MIGRATION APPLIED WITH WARNINGS

## Scope

Phase 29.4 applied only migration `0027__nflverse_historical_feature_warehouse.sql` and verified the new nflverse historical warehouse objects in an empty state.

No nflverse ingestion, historical backfill, weekly refresh, advanced metric materialization, Pigskin packet refresh, deploy, feature flag change, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scraping, external fetch, ranking build, or Firebase artifact occurred.

Only migration DDL and migration ledger metadata were written.

## Authorization Gate State

### Before Apply

All checked gates were unset:

- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_PROJECTION_CONTEXT_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

### During Apply

`ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY=true` was set only inside the same PowerShell `try` block that ran the migration apply command.

### After Apply

The `finally` block removed `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`.

Post-apply gates checked as unset:

- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Git State

Latest commit:

`a73656c Document draft pick score release package`

Recent commits include:

- `a73656c Document draft pick score release package`
- `6e4b565 Draft pick score lane and staging UI`
- `6158549 Document Trade Score v1 Track A closeout`
- `3268a5a Document Trade Score v1 UI polish package`
- `9ec04f3 Polish Trade Score v1 staging UI`
- `aa543d0 Document Phase 26 evidence commit`
- `251fd18 Document Phase 25 production closeout`
- `b3b0ec1 Document Data Ops hardening production rollout`
- `22e3256 Gate Data Ops local subprocess controls`
- `63149aa Clean up production warning noise`

No files were staged.

Phase 29.1, Phase 29.2, and Phase 29.3 reports remain untracked owner-review artifacts. The Phase 29.3 scaffold files also remain untracked or modified, as expected because this phase did not commit.

## Preflight Results

Passed:

- `scripts/check_deployment_safety.py`
- `python -m py_compile app.py src\extract.py src\pipeline.py src\load.py src\transform.py src\pigskin_context_tools.py src\llm_context_packets.py`
- `python -m compileall -q src scripts`
- `python -m unittest tests.test_nflverse_historical_contracts`
- `python -m unittest tests.test_pigskin_advanced_metrics_contracts`
- `python -m unittest discover tests`: 416 tests passed
- `scripts/run_bigquery_migrations.py --dry-run`
- `scripts/run_bigquery_validations.py --dry-run`: 200 validation files discovered

## Pending Migration State Before Apply

`scripts/run_bigquery_migrations.py --list-pending` showed exactly one pending migration:

`0027: nflverse historical feature warehouse`

No other pending migration was present.

## Migration Safety Review

Reviewed migration:

`bigquery/migrations/0027__nflverse_historical_feature_warehouse.sql`

Confirmed:

- additive only;
- creates raw nflverse tables with `CREATE TABLE IF NOT EXISTS`;
- creates canonical staging tables with `CREATE TABLE IF NOT EXISTS`;
- creates feature and packet tables with `CREATE TABLE IF NOT EXISTS`;
- creates current and compatibility views with `CREATE OR REPLACE VIEW`;
- no `DROP`;
- no `DELETE`;
- no `TRUNCATE`;
- no `INSERT`;
- no `MERGE`;
- no destructive `ALTER TABLE`;
- no `trade_player_scores` mutation;
- no `trade_pick_scores` mutation;
- no Scheduler job creation;
- no Cloud Run Job trigger;
- no backfill rows;
- compatibility view reads `pigskin_player_context_packet_current`, not raw/source tables.

## Migration Apply Command and Result

Command pattern used:

```powershell
try {
  $env:ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY = "true"
  echo "ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY=$env:ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY"
  .\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --apply
  $status = $LASTEXITCODE
  if ($status -ne 0) { exit $status }
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY -ErrorAction SilentlyContinue
}
```

Result:

- pending migration before apply: `0027`;
- migration applied: `0027`;
- runner output: `Applied 1 migration(s).`;
- gate removed afterward.

## Pending Migration State After Apply

`scripts/run_bigquery_migrations.py --list-pending` returned:

`No pending migrations.`

## Raw Object Verification

All 18 raw objects exist and have 0 rows.

| Object | Type | Fields | Rows | Partitioning | Clustering |
| --- | --- | ---: | ---: | --- | --- |
| `raw_nflverse_pbp` | BASE TABLE | 31 | 0 | range:season | week, game_id, posteam, defteam |
| `raw_nflverse_weekly` | BASE TABLE | 27 | 0 | range:season | week, player_id, team, position |
| `raw_nflverse_rosters` | BASE TABLE | 17 | 0 | range:season | player_id, gsis_id, team, position |
| `raw_nflverse_rosters_weekly` | BASE TABLE | 18 | 0 | range:season | week, player_id, team, position |
| `raw_nflverse_players` | BASE TABLE | 18 | 0 | none | nflverse_player_id, gsis_id, sleeper_player_id, normalized_player_name |
| `raw_nflverse_ff_playerids` | BASE TABLE | 17 | 0 | none | nflverse_player_id, gsis_id, sleeper_player_id, platform_player_id |
| `raw_nflverse_schedules` | BASE TABLE | 23 | 0 | range:season | week, game_id, home_team, away_team |
| `raw_nflverse_teams` | BASE TABLE | 15 | 0 | none | team |
| `raw_nflverse_team_stats` | BASE TABLE | 19 | 0 | range:season | week, team |
| `raw_nflverse_injuries` | BASE TABLE | 20 | 0 | range:season | week, team, gsis_id |
| `raw_nflverse_depth_charts` | BASE TABLE | 18 | 0 | range:season | team, gsis_id, position |
| `raw_nflverse_snap_counts` | BASE TABLE | 22 | 0 | range:season | week, player_id, team, position |
| `raw_nflverse_participation` | BASE TABLE | 18 | 0 | range:season | week, game_id, player_id, team |
| `raw_nflverse_ngs_passing` | BASE TABLE | 19 | 0 | range:season | week, player_gsis_id, team |
| `raw_nflverse_ngs_rushing` | BASE TABLE | 19 | 0 | range:season | week, player_gsis_id, team |
| `raw_nflverse_ngs_receiving` | BASE TABLE | 19 | 0 | range:season | week, player_gsis_id, team |
| `raw_nflverse_ftn_charting` | BASE TABLE | 17 | 0 | range:season | week, game_id, play_id |
| `raw_nflverse_draft_picks` | BASE TABLE | 18 | 0 | range:season | player_id, team, position |

## Staging Object Verification

All 6 staging objects exist and have 0 rows.

| Object | Type | Fields | Rows | Partitioning | Clustering |
| --- | --- | ---: | ---: | --- | --- |
| `stg_player_identity` | BASE TABLE | 17 | 0 | range:season | week, player_id_internal, team, position |
| `stg_game_context` | BASE TABLE | 17 | 0 | range:season | week, game_id, home_team, away_team |
| `stg_player_week_stats` | BASE TABLE | 23 | 0 | range:season | week, player_id_internal, team, position |
| `stg_team_week_stats` | BASE TABLE | 23 | 0 | range:season | week, team, opponent_team |
| `stg_play_player_events` | BASE TABLE | 32 | 0 | range:season | week, game_id, player_id_internal, event_type |
| `stg_participation_context` | BASE TABLE | 18 | 0 | range:season | week, game_id, player_id_internal, team |

## Feature and Packet Object Verification

Base feature and packet tables exist and have 0 rows.

| Object | Type | Fields | Rows | Partitioning | Clustering |
| --- | --- | ---: | ---: | --- | --- |
| `player_week_advanced_metrics` | BASE TABLE | 41 | 0 | range:season | week, player_id_internal, scoring_profile_id, position |
| `team_week_context_metrics` | BASE TABLE | 24 | 0 | range:season | week, team, opponent_team |
| `qb_week_environment_metrics` | BASE TABLE | 24 | 0 | range:season | week, qb_player_id_internal, team |
| `pigskin_player_context_packet_current` | BASE TABLE | 24 | 0 | range:as_of_season | as_of_week, player_id_internal, scoring_profile_id, position |

Current and compatibility views exist and return 0 rows.

| Object | Type | Fields | Rows |
| --- | --- | ---: | ---: |
| `player_recent_advanced_metrics_current` | VIEW | 20 | 0 |
| `player_role_usage_metrics_current` | VIEW | 27 | 0 |
| `compat_pigskin_player_context_current` | VIEW | 16 | 0 |

## Compatibility View Dependency Verification

Validation `198_compat_pigskin_context_no_raw_dependencies.sql` passed with:

`raw_source_dependency_count = 0`

The compatibility view does not read raw/source tables.

## Validation Results

Phase 29 validation patterns:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Expected empty-state review warning for season/week coverage. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `pigskin_context` | 2 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `route_metrics` | 1 passed, 0 failed. |
| `pressure_metrics` | 1 passed, 0 failed. |
| `player_identity_coverage` | Phase 29 identity coverage returned an expected empty-state review row. Existing claim identity coverage also returned its preexisting informational warning. |
| `rolling_window` | 1 passed, 0 failed, expected empty-state review row. |
| `source_freshness_present` | 1 passed, 0 failed. |
| `missing_flags_present` | 1 passed, 0 failed. |

Expected warnings:

- `181_raw_nflverse_season_week_coverage.sql`: empty raw tables return no season/week coverage yet.
- `189_player_identity_coverage.sql`: empty staging table returns `player_week_rows = 0`.
- `194_rolling_window_consistency.sql`: empty current view returns `current_player_rows = 0`.

## Existing Score-Lane Validation Results

| Pattern | Result |
| --- | --- |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. One informational model-version coverage row remains expected. |
| `compat_trade_player_scores` | 2 passed, 0 failed. |
| `compat_trade_pick_scores` | 2 passed, 0 failed. |

No player-score or draft-pick-score contamination was detected.

## Zero-Row and No-Ingestion Confirmation

All new raw nflverse tables have 0 rows.

All new staging tables have 0 rows.

All new feature and packet base tables have 0 rows.

All new current and compatibility views return 0 rows.

No nflverse loader was run. No backfill command was run. No weekly refresh command was run.

Legacy source snapshot after migration:

| Object | Rows |
| --- | ---: |
| `play_by_play` | 48,771 |
| `weekly_metrics` | 19,421 |
| `analytics_player_weekly_truth` | 18,539 |
| `analytics_fraud_watch` | 1,218 |

Migration `0027` does not reference or mutate these legacy source tables.

## Staging and Production Untouched

Production service:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: `nfl-studio-dashboard-00077-2jp:100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_TRADE_PICK_SCORE_V0`: unset
- `USE_COMPAT_TRADE_PICK_SCORE`: unset
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Staging service:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- traffic: `nfl-studio-dashboard-staging-00029-jtb:100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops trigger flags remain false.
- local subprocess flags remain false.

No staging or production deployment occurred.

## Remaining Warnings

- Phase 29.1, Phase 29.2, and Phase 29.3 reports remain untracked owner-review artifacts.
- Phase 29.3 scaffold files remain uncommitted.
- New objects are empty by design. Coverage validations will stay informational until a separate authorized backfill phase writes source rows.
- `player_identity_coverage` pattern also ran an older claim validation and reported a preexisting claim identity warning. It is unrelated to the nflverse migration.
- Route share, first-read share, true pressure, alignment splits, and contact yards remain blocked until true source columns are inspected and contracted.

## Recommended Next Phase

Phase 29.5 should design and implement a dry-run-only nflverse historical backfill planner. It should not write data.

Future live backfill should require:

- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true`;
- explicit season ranges;
- explicit source-family selection;
- no `WRITE_TRUNCATE` unless a separate destructive-refresh gate exists;
- dry-run plan output before any write;
- row-count and duplicate checks after each source family.

## Final Decision

NFLVERSE WAREHOUSE MIGRATION APPLIED WITH WARNINGS
