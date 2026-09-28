# Phase 29.16 - Authorized 2015 nflverse Staging Materialization

Date: 2026-06-29

Final decision: 2015 STAGING MATERIALIZED WITH WARNINGS

## Scope

Authorized materialization of 2015 rows into the six canonical `stg_*` nflverse staging tables.

Target season range:

- `season_start=2015`
- `season_end=2015`

Target tables:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

No raw backfill, advanced metric materialization, Pigskin packet refresh, direct current-view write, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, ranking build, Pigskin prompt, LLM-backed action, scrape, Firebase artifact, or commit occurred.

## Authorization Gate State

All gates were unset before the live write.

| Gate | Before | During live write | After |
| --- | --- | --- | --- |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset | `true` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset | unset | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset | unset | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset | unset | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset | unset | unset |

The staging write gate was set only inside the same PowerShell `try/finally` wrapper around the one live staging command.

## Git State

Latest commit before the phase:

`4805610 Build nflverse Pigskin canary pipeline`

Worktree:

- Existing untracked historical validation backlog remained untracked.
- Phase 29.13, Phase 29.14, and Phase 29.15 reports remained untracked.
- No files were staged.
- No commit was created.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_staging.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_staging` | 11 tests passed |
| `python -m unittest tests.test_nflverse_backfill_executor` | 18 tests passed |
| `python -m unittest discover tests` | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

PowerShell displayed `NativeCommandError` wrappers for stderr logging during some Python test commands, but the process exit codes were 0 and the test summaries were PASS.

## Raw Source Precheck

2015 raw source rows were present before staging materialization.

| Raw Table | 2015 Rows | `source_refresh_id` Non-Null | `loaded_at` Non-Null | `row_hash` Non-Null |
| --- | ---: | ---: | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 267 | 267 | 267 |
| `raw_nflverse_rosters` | 2,189 | 2,189 | 2,189 | 2,189 |
| `raw_nflverse_rosters_weekly` | 30,201 | 30,201 | 30,201 | 30,201 |
| `raw_nflverse_weekly` | 17,592 | 17,592 | 17,592 | 17,592 |
| `raw_nflverse_pbp` | 48,122 | 48,122 | 48,122 | 48,122 |
| `raw_nflverse_snap_counts` | 23,842 | 23,842 | 23,842 | 23,842 |

Static/global raw tables:

| Raw Table | Total Rows |
| --- | ---: |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

## Staging Pre-Write State

Before the live staging write, all 2015 staging targets had 0 rows.

| Staging Table | 2015 Rows Before |
| --- | ---: |
| `stg_player_identity` | 0 |
| `stg_game_context` | 0 |
| `stg_player_week_stats` | 0 |
| `stg_team_week_stats` | 0 |
| `stg_play_player_events` | 0 |
| `stg_participation_context` | 0 |

## Strict Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2015 --season-end 2015 --dry-run --all-targets --strict
```

Result:

- Exit code 0.
- `dry_run=True`
- `wrote=False`
- No target was blocked.

| Target | Planned Rows | Source Rows | Duplicate Grain Count | Readiness | Warnings |
| --- | ---: | ---: | ---: | --- | --- |
| `stg_player_identity` | 30,201 | n/a | 0 | ready with warnings | No name-only identity joins are used. |
| `stg_game_context` | 267 | 267 | 0 | ready | none |
| `stg_player_week_stats` | 17,592 | 17,592 | 0 | ready with warnings | Legacy `weekly_metrics` is not used. |
| `stg_team_week_stats` | 534 | 48,122 | 0 | ready with warnings | `pass_rate_over_expected` remains null until a model source exists. |
| `stg_play_player_events` | 118,069 | 48,122 | 0 | ready with warnings | Route metrics are not created in play-player events. |
| `stg_participation_context` | 23,842 | 23,842 | 0 | ready with warnings | `snap_counts` uses PFR IDs for 2014; `route_share` stays null and `has_true_route_source` stays false. |

Global dry-run warnings:

- Default mode is read-only. Staging writes require an authorized gate.
- Raw `raw_nflverse_*` tables remain internal and are not Pigskin or UI surfaces.

## Live Staging Write Command

Command wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION = "true"

  echo "ALLOW_NFLVERSE_STAGING_MATERIALIZATION=$env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION"

  .\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2015 --season-end 2015 --all-targets --write --strict

} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Result:

- Exit code 0.
- `dry_run=False`
- `wrote=True`
- `season_start=2015`
- `season_end=2015`
- Target summaries matched the strict dry-run plan.
- No raw backfill rerun occurred.
- No advanced metric or Pigskin packet materialization followed.

Live write warnings:

- Phase 29.8 staging writes were authorized by `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`.
- Raw `raw_nflverse_*` tables remain internal and are not Pigskin or UI surfaces.
- Target-level dry-run warnings remained unchanged.

## Post-Write Staging Verification

| Staging Table | Total Rows | 2015 Rows | Season Range | Week Range 2015 | Duplicate 2015 Grain Groups | Null Grain Fields 2015 | Missing Freshness | Missing Flags |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `stg_player_identity` | 60,396 | 30,201 | 2014-2015 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_game_context` | 534 | 267 | 2014-2015 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_player_week_stats` | 35,193 | 17,592 | 2014-2015 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_team_week_stats` | 1,068 | 534 | 2014-2015 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_play_player_events` | 234,469 | 118,069 | 2014-2015 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_participation_context` | 47,706 | 23,842 | 2014-2015 | 1-21 | 0 | 0 | 0 | 0 |

All 2015 staging rows had non-null:

- `source_freshness_json`
- `missing_data_flags`
- `source_refresh_id`
- `created_at`

## Identity Gap Summary

| Table | Missing `player_id_internal` 2015 | Missing `nflverse_player_id` 2015 |
| --- | ---: | ---: |
| `stg_player_identity` | 0 | 0 |
| `stg_player_week_stats` | 0 | 3,821 |
| `stg_play_player_events` | 0 | 61,778 |
| `stg_participation_context` | 0 | n/a |

Interpretation:

- Canonical internal player IDs are present for all 2015 player-grained staging rows.
- `nflverse_player_id` gaps remain visible in downstream staging rows and should be handled as known identity-context gaps, not hidden.

## Route-Share Block Confirmation

For `stg_participation_context` 2015:

- `route_share IS NOT NULL`: 0 rows
- `has_true_route_source = TRUE`: 0 rows

This matches the accepted rule that route metrics must remain blocked until a true route source is proven.

## Non-Target Object Verification

Raw nflverse counts stayed unchanged from Phase 29.15 post-write:

| Raw Table | Total Rows | 2015 Rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 534 | 267 |
| `raw_nflverse_rosters` | 4,341 | 2,189 |
| `raw_nflverse_rosters_weekly` | 60,396 | 30,201 |
| `raw_nflverse_weekly` | 35,193 | 17,592 |
| `raw_nflverse_pbp` | 95,751 | 48,122 |
| `raw_nflverse_snap_counts` | 47,706 | 23,842 |

Static/global raw counts:

| Raw Table | Total Rows |
| --- | ---: |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

Advanced metrics, Pigskin packets, and score lanes were unchanged:

| Object | Rows |
| --- | ---: |
| `player_week_advanced_metrics` | 17,601 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 643 |
| `player_recent_advanced_metrics_current` | 1,854 |
| `player_role_usage_metrics_current` | 1,854 |
| `pigskin_player_context_packet_current` | 482 |
| `compat_pigskin_player_context_current` | 482 |
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validation Results After Staging Materialization

| Validation Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Coverage review warning reports 2014-2015 raw coverage. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Informational warning still reports model `trade_pick_score_v0_2026_001` with 64 rows. |

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_staging.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_staging` | 11 tests passed |
| `python -m unittest tests.test_nflverse_backfill_executor` | 18 tests passed |
| `python -m unittest discover tests` | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

## Production and Staging Service State

Production service:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp=100%`
- Production risk flags false.
- Trade Analyzer score flags false.
- Trade History compatibility false.
- Data Ops Cloud Run trigger flags false.
- Data Ops local subprocess flags false.

Staging service:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: `nfl-studio-dashboard-staging-00029-jtb=100%`
- Existing staging score flags remain true from prior staging work.
- No staging deployment or flag mutation occurred in this phase.

## Remaining Warnings

- `nflverse_player_id` remains null for 3,821 rows in `stg_player_week_stats` and 61,778 rows in `stg_play_player_events`.
- `snap_counts` uses PFR identifiers where GSIS is unavailable.
- `route_share` remains null and `has_true_route_source` remains false by design.
- `pass_rate_over_expected` remains null until a model source exists.
- Raw tables remain internal only and are not Pigskin or UI-safe surfaces.

## Recommended Next Phase

Recommended Phase 29.17:

Dry-run and then, only if explicitly authorized, materialize 2015 base advanced metrics from the 2015 staging layer.

Suggested guardrails:

- Use `season_start=2015` and `season_end=2015` only.
- Dry-run first with target summaries.
- Require `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true` only inside the live command wrapper.
- Do not refresh Pigskin packets in the same phase.
- Run `advanced_metrics`, `stg_`, and `compat_pigskin` validations after materialization.
- Keep route and pressure metrics blocked unless true source columns are present.
