# Phase 29.27: 2018-2020 nflverse Staging Materialization

Date: 2026-06-30

Final decision: **2018-2020 STAGING MATERIALIZED WITH WARNINGS**

## Scope

Materialized only the 2018-2020 nflverse staging layer into:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

No raw backfill, advanced metrics materialization, Pigskin packet refresh, deployment, feature flag change, Cloud Run Job trigger, Scheduler change, LLM action, scraping, or Firebase artifact creation occurred.

## Authorization Gate

Initial gate state was empty or unset for:

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

The live write used the required same-session wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2018 --season-end 2020 --all-targets --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Post-write gate state was empty or unset for all checked gates.

## Git State

Latest commit at start/end of phase:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

No files were staged. The worktree still contains the known untracked historical validation backlog and owner-review artifacts. This report is the only new Phase 29.27 artifact from this phase.

## Baseline Checks

All baseline checks passed:

- `scripts/check_deployment_safety.py`: PASS
- `py_compile src\nflverse_staging.py`: PASS
- `py_compile src\nflverse_backfill.py`: PASS
- `py_compile src\nflverse_backfill_plan.py`: PASS
- `compileall -q src scripts`: PASS
- `unittest tests.test_nflverse_staging`: PASS, 11 tests
- `unittest tests.test_nflverse_backfill_executor`: PASS, 18 tests
- `unittest discover tests`: PASS, 487 tests
- `scripts/run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: PASS, catalog discovered through validation 200

## Raw Source Precheck

2018-2020 raw source rows existed before staging materialization:

| Table | 2018 | 2019 | 2020 | Week Range |
|---|---:|---:|---:|---|
| `raw_nflverse_schedules` | 267 | 267 | 269 | 1-21 |
| `raw_nflverse_rosters` | 3,141 | 3,113 | 3,067 | n/a |
| `raw_nflverse_rosters_weekly` | 52,200 | 51,630 | 44,124 | 1-21 |
| `raw_nflverse_weekly` | 17,393 | 17,341 | 17,581 | 1-21 |
| `raw_nflverse_pbp` | 47,109 | 47,260 | 47,705 | 1-21 |
| `raw_nflverse_snap_counts` | 23,877 | 23,862 | 24,999 | 1-21 |

Static/global raw tables:

- `raw_nflverse_teams`: 36
- `raw_nflverse_players`: 25,033
- `raw_nflverse_ff_playerids`: 69,060

## Staging Pre-Write State

All six target staging tables had zero 2018, 2019, and 2020 rows before the first write.

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2018 --season-end 2020 --dry-run --all-targets --strict
```

Dry-run result: no writes.

| Target | Planned Rows | Source Rows | Duplicate Keys | Readiness | Warning Summary |
|---|---:|---:|---:|---|---|
| `stg_player_identity` | 147,954 | n/a | 0 | ready with warnings | No name-only identity joins are used. |
| `stg_game_context` | 803 | 803 | 0 | ready | None |
| `stg_player_week_stats` | 52,315 | 52,315 | 0 | ready with warnings | Legacy `weekly_metrics` is not used. |
| `stg_team_week_stats` | 1,606 | 142,074 | 0 | ready with warnings | `pass_rate_over_expected` remains null until a model source exists. |
| `stg_play_player_events` | 345,710 | 142,074 | 0 | ready with warnings | Route metrics are not created in play-player events. |
| `stg_participation_context` | 72,738 | 72,738 | 0 | ready with warnings | `route_share` stays null and `has_true_route_source` stays false. |

Dry-run identity-gap counters were:

- `stg_player_week_stats`: 1,090
- `stg_play_player_events`: 4,033
- `stg_participation_context`: 248

Those dry-run counters are retained as planning warnings. The materialized staging rows use internal identity fallbacks and post-write required identity checks showed zero missing `player_id_internal` rows.

## Live Staging Write

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2018 --season-end 2020 --all-targets --write --strict
```

The command ran once inside the required temporary `ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true` wrapper.

Live write result:

| Target | DML Affected Rows | Post-Write Rows | Duplicate Keys | SQL Kind | Season Range | Metadata Missing |
|---|---:|---:|---:|---|---|---:|
| `stg_player_identity` | 147,954 | 147,954 | 0 | MERGE | 2018-2020 | 0 |
| `stg_game_context` | 803 | 803 | 0 | MERGE | 2018-2020 | 0 |
| `stg_player_week_stats` | 52,315 | 52,315 | 0 | MERGE | 2018-2020 | 0 |
| `stg_team_week_stats` | 1,606 | 1,606 | 0 | MERGE | 2018-2020 | 0 |
| `stg_play_player_events` | 345,710 | 345,710 | 0 | MERGE | 2018-2020 | 0 |
| `stg_participation_context` | 72,738 | 72,738 | 0 | MERGE | 2018-2020 | 0 |

No 2014 rows were touched by the bounded write.

## Post-Write Staging Verification

| Target | 2018 | 2019 | 2020 | Total | Week Range | Duplicate Keys | Missing Source Freshness | Missing Flags |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `stg_player_identity` | 52,200 | 51,630 | 44,124 | 147,954 | 1-21 | 0 | 0 | 0 |
| `stg_game_context` | 267 | 267 | 269 | 803 | 1-21 | 0 | 0 | 0 |
| `stg_player_week_stats` | 17,393 | 17,341 | 17,581 | 52,315 | 1-21 | 0 | 0 | 0 |
| `stg_team_week_stats` | 534 | 534 | 538 | 1,606 | 1-21 | 0 | 0 | 0 |
| `stg_play_player_events` | 114,473 | 114,616 | 116,621 | 345,710 | 1-21 | 0 | 0 | 0 |
| `stg_participation_context` | 23,877 | 23,862 | 24,999 | 72,738 | 1-21 | 0 | 0 | 0 |

Post-write required identity field checks:

- `stg_player_identity`: 0 missing `player_id_internal`
- `stg_player_week_stats`: 0 missing `player_id_internal`
- `stg_play_player_events`: 0 missing `player_id_internal`
- `stg_participation_context`: 0 missing `player_id_internal`

Route metrics remain blocked:

- `stg_participation_context.route_share IS NOT NULL`: 0 rows
- `stg_participation_context.has_true_route_source IS TRUE`: 0 rows

2020-specific behavior:

- `stg_game_context` has 269 2020 rows, matching the accepted 2020 schedule-source count.
- `stg_player_identity` has 44,124 2020 rows, matching the lower accepted 2020 `rosters_weekly` source count.
- No 2021 or later staging rows were written by this command.

## Non-Target Verification

Read-only counts after the write matched the pre-write baseline:

| Object | Count |
|---|---:|
| `raw_nflverse_schedules` | 1,871 |
| `raw_nflverse_rosters` | 19,805 |
| `raw_nflverse_rosters_weekly` | 294,691 |
| `raw_nflverse_weekly` | 122,495 |
| `raw_nflverse_pbp` | 332,721 |
| `raw_nflverse_snap_counts` | 168,196 |
| `player_week_advanced_metrics` | 70,180 |
| `team_week_context_metrics` | 2,136 |
| `qb_week_environment_metrics` | 2,525 |
| `player_recent_advanced_metrics_current` | 3,128 |
| `player_role_usage_metrics_current` | 3,128 |
| `pigskin_player_context_packet_current` | 1,587 |
| `compat_pigskin_player_context_current` | 1,587 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

This confirms no raw backfill rerun, no advanced metrics materialization, no Pigskin packet refresh, and no score-table write occurred during Phase 29.27.

## Validation Results

Post-write validation commands:

| Pattern | Result |
|---|---|
| `raw_nflverse` | PASS, 3 passed, 0 failed. Validation 181 returned informational coverage review rows for 2014-2020. |
| `stg_` | PASS, 7 passed, 0 failed. |
| `advanced_metrics` | PASS, 4 passed, 0 failed. |
| `compat_pigskin` | PASS, 2 passed, 0 failed. |
| `trade_player_scores` | PASS, 12 passed, 0 failed. |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Validation 178 returned the expected informational model-version coverage row. |

## Final Local Checks

Final checks after materialization:

- `scripts/check_deployment_safety.py`: PASS
- `py_compile src\nflverse_staging.py`: PASS
- `py_compile src\nflverse_backfill.py`: PASS
- `py_compile src\nflverse_backfill_plan.py`: PASS
- `compileall -q src scripts`: PASS
- `unittest tests.test_nflverse_staging`: PASS, 11 tests
- `unittest tests.test_nflverse_backfill_executor`: PASS, 18 tests
- `unittest discover tests`: PASS, 487 tests
- `scripts/run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: PASS, catalog discovered through validation 200

## Service State

Read-only Cloud Run describe confirmed no deployment occurred.

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`
- Production risk flags: false
- Trade History compatibility: false
- Trade Analyzer score flags: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

## Remaining Warnings

- 2020 source shape remains accepted but uneven: schedule rows are 269, while 2018 and 2019 are 267.
- 2020 `rosters_weekly` source coverage remains lower than 2018 and 2019.
- Dry-run identity-gap counters remain useful follow-up signals, even though post-write required `player_id_internal` checks passed.
- `pass_rate_over_expected` remains null for all 1,606 `stg_team_week_stats` rows until a real model source exists.
- Route metrics remain correctly unavailable: `route_share` is null and `has_true_route_source` is false for all 72,738 participation rows.
- Raw nflverse coverage validation 181 is informational and now reflects 2014-2020 coverage.
- Trade-pick validation 178 remains informational for model-version coverage.

## Recommended Next Phase

Proceed to bounded 2018-2020 base advanced metrics dry-run and then gated materialization only if explicitly authorized. Do not refresh Pigskin packets until advanced metrics checks pass for the expanded 2018-2020 staging layer.
