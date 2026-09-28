# Phase 29.39 - 2024 nflverse Staging Materialization

Date: 2026-06-30

Final decision: **2024 STAGING MATERIALIZED WITH WARNINGS**

## Scope

Authorized operation was limited to:

- `season_start=2024`
- `season_end=2024`
- staging tables only
- six target tables:
  - `stg_player_identity`
  - `stg_game_context`
  - `stg_player_week_stats`
  - `stg_team_week_stats`
  - `stg_play_player_events`
  - `stg_participation_context`

No raw backfill, advanced metric materialization, Pigskin packet refresh, current-season lane, ranking build, deployment, feature-flag change, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, scrape, or Firebase artifact was run.

## Authorization Gate State

Before write, all checked gates were empty or unset:

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

echo "ALLOW_NFLVERSE_STAGING_MATERIALIZATION=$env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION"

.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2024 --season-end 2024 --all-targets --write --strict

} finally {
Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

After the wrapper, the staging gate and adjacent write/deploy gates were empty or unset.

## Git State

Latest commit before work:

- `e56afa3 Expand nflverse Pigskin packets through 2023`

No files were staged. The worktree had the known untracked historical validation-report backlog, including the Phase 29.38 report.

## Baseline Checks

All baseline checks passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`: 11 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_executor`: 18 tests passed
- `.\venv\Scripts\python.exe -m unittest discover tests`: 487 tests passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: validation catalog discovered through `200`

## Raw Source Precheck

Read-only 2024 raw checks matched Phase 29.38:

| Raw table | Total row count | 2024 row count | 2025+ row count | Week range |
| --- | ---: | ---: | ---: | --- |
| `raw_nflverse_schedules` | 3,010 | 285 | 0 | 1-22 |
| `raw_nflverse_rosters` | 32,202 | 3,215 | 0 | n/a |
| `raw_nflverse_rosters_weekly` | 479,719 | 46,572 | 0 | 1-22 |
| `raw_nflverse_weekly` | 197,831 | 18,959 | 0 | 1-22 |
| `raw_nflverse_pbp` | 531,234 | 49,492 | 0 | 1-22 |
| `raw_nflverse_snap_counts` | 274,200 | 26,615 | 0 | 1-22 |

Static/global tables remained idempotent:

- `raw_nflverse_teams`: 36
- `raw_nflverse_players`: 25,033
- `raw_nflverse_ff_playerids`: 69,060

## Staging Pre-Write State

Before the staging write, each target had `0` rows for 2024 and `0` rows for 2025 or later:

| Staging table | Total rows before | 2024 rows before | Season range before |
| --- | ---: | ---: | --- |
| `stg_player_identity` | 433,147 | 0 | 2014-2023 |
| `stg_game_context` | 2,725 | 0 | 2014-2023 |
| `stg_player_week_stats` | 178,872 | 0 | 2014-2023 |
| `stg_team_week_stats` | 5,450 | 0 | 2014-2023 |
| `stg_play_player_events` | 1,173,226 | 0 | 2014-2023 |
| `stg_participation_context` | 247,585 | 0 | 2014-2023 |

## Dry-Run Summary

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2024 --season-end 2024 --dry-run --all-targets --strict
```

Result:

- Exit code: 0
- `wrote`: false
- targets planned: 6
- no blocked target

| Target | Planned rows | Source rows | Duplicate keys | Readiness | Warning summary |
| --- | ---: | ---: | ---: | --- | --- |
| `stg_player_identity` | 46,572 | n/a | 0 | ready with warnings | no name-only joins |
| `stg_game_context` | 285 | 285 | 0 | ready | none |
| `stg_player_week_stats` | 18,959 | 18,959 | 0 | ready with warnings | legacy `weekly_metrics` not used |
| `stg_team_week_stats` | 570 | 49,492 | 0 | ready with warnings | `pass_rate_over_expected` remains null until a model source exists |
| `stg_play_player_events` | 118,037 | 49,492 | 0 | ready with warnings | route metrics are not created |
| `stg_participation_context` | 26,615 | 26,615 | 0 | ready with warnings | 65 unmatched PFR identity rows; route metrics blocked |

Dry-run diagnostics:

- `stg_player_week_stats` postseason rows: 849
- `stg_participation_context` missing identity count: 65
- `stg_participation_context` route_share non-null rows: 0
- `stg_participation_context` `has_true_route_source=true` rows: 0

## Live Staging Write Result

Live write command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2024 --season-end 2024 --all-targets --write --strict
```

Result:

- Exit code: 0
- `wrote`: true
- selected targets: exactly the six `stg_*` targets in scope
- write kind: `MERGE` for each target

| Target | Affected rows | Bounded 2024 rows after | Duplicate keys after | Missing source freshness | Missing flags |
| --- | ---: | ---: | ---: | ---: | ---: |
| `stg_player_identity` | 46,572 | 46,572 | 0 | 0 | 0 |
| `stg_game_context` | 285 | 285 | 0 | 0 | 0 |
| `stg_player_week_stats` | 18,959 | 18,959 | 0 | 0 | 0 |
| `stg_team_week_stats` | 570 | 570 | 0 | 0 | 0 |
| `stg_play_player_events` | 118,037 | 118,037 | 0 | 0 | 0 |
| `stg_participation_context` | 26,615 | 26,615 | 0 | 0 | 0 |

The staging command output labels the internal CLI phase as `29.8`; the command scope and target season were Phase 29.39 as requested.

## Post-Write Staging Verification

Read-only BigQuery checks used neutral aliases such as `row_count`, `scope_row_count`, and `staging_snapshot`.

| Staging table | Total row count | 2024 row count | 2025+ row count | Full season range | 2024 week range | Duplicate keys | Missing required fields | Missing identity |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `stg_player_identity` | 479,719 | 46,572 | 0 | 2014-2024 | 1-22 | 0 | 0 | 0 |
| `stg_game_context` | 3,010 | 285 | 0 | 2014-2024 | 1-22 | 0 | 0 | n/a |
| `stg_player_week_stats` | 197,831 | 18,959 | 0 | 2014-2024 | 1-22 | 0 | 0 | 0 |
| `stg_team_week_stats` | 6,020 | 570 | 0 | 2014-2024 | 1-22 | 0 | 0 | n/a |
| `stg_play_player_events` | 1,291,263 | 118,037 | 0 | 2014-2024 | 1-22 | 0 | 0 | 0 |
| `stg_participation_context` | 274,200 | 26,615 | 0 | 2014-2024 | 1-22 | 0 | 0 | 65 |

Source freshness and missing-data flag columns were present for the 2024 slice:

- `missing_source_freshness_count`: 0 for all six targets
- `missing_flags_count`: 0 for all six targets

## Identity Gap Summary

Identity gaps are quantified and not hidden:

- `stg_player_identity`: 0 missing identity rows
- `stg_player_week_stats`: 0 missing identity rows
- `stg_play_player_events`: 0 missing identity rows
- `stg_participation_context`: 65 missing identity rows

The participation gap is tied to the accepted snap-count behavior where PFR identifiers are used when GSIS is unavailable.

## Route-Share Blocked Confirmation

Route metrics stayed blocked:

- `stg_participation_context.route_share` non-null rows: 0
- `stg_participation_context.has_true_route_source=true` rows: 0

This matches the source limitation: there is no true route source in this staging pass.

## 2024 and Week 22 Behavior

All six staging targets now cover 2024, weeks 1-22 where week is applicable. This is expected for the 17-game schedule era and postseason-inclusive historical slice.

## 2025 and Current-Season Separation

All six staging targets reported `0` rows where `season >= 2025`. No current-season lane was run.

## Non-Target Object Verification

Raw nflverse counts remained unchanged from Phase 29.38:

- `raw_nflverse_schedules`: 3,010 total, 285 for 2024
- `raw_nflverse_rosters`: 32,202 total, 3,215 for 2024
- `raw_nflverse_rosters_weekly`: 479,719 total, 46,572 for 2024
- `raw_nflverse_weekly`: 197,831 total, 18,959 for 2024
- `raw_nflverse_pbp`: 531,234 total, 49,492 for 2024
- `raw_nflverse_snap_counts`: 274,200 total, 26,615 for 2024
- `raw_nflverse_teams`: 36
- `raw_nflverse_players`: 25,033
- `raw_nflverse_ff_playerids`: 69,060

Advanced metrics remained unchanged:

- `player_week_advanced_metrics`: 178,872
- `team_week_context_metrics`: 5,450
- `qb_week_environment_metrics`: 6,643

Current metric views remained unchanged:

- `player_recent_advanced_metrics_current`: 5,497
- `player_role_usage_metrics_current`: 5,497

Pigskin packets remained unchanged:

- `pigskin_player_context_packet_current`: 3,082
- `compat_pigskin_player_context_current`: 3,082

Trade score tables remained unchanged:

- `trade_player_scores`: 154
- `trade_player_scores_current`: 77
- `compat_trade_player_scores_current`: 77
- `trade_pick_scores`: 64
- `trade_pick_scores_current`: 64
- `compat_trade_pick_scores_current`: 64

## Validation Results

Post-write validation patterns:

- `raw_nflverse`: 3 passed, 0 failed; informational review warning from `181_raw_nflverse_season_week_coverage.sql`
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed; informational review warning from `178_trade_pick_scores_model_version_coverage.sql`

## Final Local Checks

All final checks passed:

- safety checker passed
- `src\nflverse_staging.py` compiled
- `src\nflverse_backfill.py` compiled
- `src\nflverse_backfill_plan.py` compiled
- `src` and `scripts` compileall passed
- `tests.test_nflverse_staging`: 11 tests passed
- `tests.test_nflverse_backfill_executor`: 18 tests passed
- `unittest discover tests`: 487 tests passed
- no pending migrations
- validation catalog discovered through `200`

## Staging and Production Untouched

Read-only Cloud Run describe confirmed no deployment in this phase.

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: `nfl-studio-dashboard-00077-2jp:100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- all production risk, score, Cloud Run Job trigger, and local subprocess flags: false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- traffic: `nfl-studio-dashboard-staging-00029-jtb:100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- staging-only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- staging-only score flags true
- Data Ops trigger and local subprocess flags false

## Warnings

- `stg_player_identity` uses no name-only joins by design.
- `stg_player_week_stats` does not use legacy `weekly_metrics`.
- `stg_team_week_stats.pass_rate_over_expected` remains null until a model source exists.
- `stg_play_player_events` does not create route metrics.
- `stg_participation_context` has 65 missing identity matches from snap-count PFR behavior.
- `route_share` remains null and `has_true_route_source` remains false, by design.
- `raw_nflverse` season/week coverage validation is informational and now reflects 2014-2024 raw coverage.
- `trade_pick_scores` model-version coverage validation is informational and unrelated to this staging materialization.
- The local BigQuery REST fallback warning appeared on read-only checks where BigQuery Storage was unavailable in the active venv.

## Recommended Next Phase

Proceed to a separate Phase 29.40 for 2024 base advanced metrics dry-run and, if authorized, bounded materialization. Do not refresh Pigskin packets until 2024 advanced metrics pass validation.
