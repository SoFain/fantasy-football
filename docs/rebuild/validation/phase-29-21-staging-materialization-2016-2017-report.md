# Phase 29.21 Staging Materialization 2016-2017 Report

Date: 2026-06-29

Final decision: **2016-2017 STAGING MATERIALIZED WITH WARNINGS**

## Scope

Authorized staging-only materialization for nflverse seasons 2016 and 2017.

Written objects were limited to:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

No raw backfill, advanced metrics materialization, Pigskin packet refresh, ranking build, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, LLM call, Pigskin prompt, scrape, Firebase artifact, or commit occurred.

Latest commit before and after this phase:

`67f37e7 Expand nflverse Pigskin pipeline to 2015`

## Authorization Gates

Initial gate state:

| Gate | State |
| --- | --- |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Write authorization was set only inside the same PowerShell wrapper around the one live staging command:

```powershell
try {
  $env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION = "true"
  echo "ALLOW_NFLVERSE_STAGING_MATERIALIZATION=$env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION"
  .\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2016 --season-end 2017 --all-targets --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Final gate state:

| Gate | State |
| --- | --- |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Git State

`git status --short --untracked-files=all` showed only the existing untracked historical validation backlog plus current phase reports. No files were staged.

No tracked source diff existed before this report was created.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_staging.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_staging` | PASS |
| `unittest tests.test_nflverse_backfill_executor` | PASS |
| `unittest discover tests` | PASS |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Raw Source Precheck

2016-2017 raw rows were present before staging materialization.

| Raw Table | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `raw_nflverse_schedules` | 1068 | 267 | 267 |
| `raw_nflverse_rosters` | 10484 | 3061 | 3082 |
| `raw_nflverse_rosters_weekly` | 146737 | 35020 | 51321 |
| `raw_nflverse_weekly` | 70180 | 17531 | 17456 |
| `raw_nflverse_pbp` | 190647 | 47651 | 47245 |
| `raw_nflverse_snap_counts` | 95458 | 23890 | 23862 |

Static/global raw tables:

| Raw Table | Rows |
| --- | ---: |
| `raw_nflverse_players` | 25033 |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_ff_playerids` | 69060 |

## Staging Pre-Write State

All 2016 and 2017 staging target counts were zero before this phase.

| Staging Table | Total Rows Before | 2016 Rows Before | 2017 Rows Before | Season Range Before |
| --- | ---: | ---: | ---: | --- |
| `stg_player_identity` | 60396 | 0 | 0 | 2014-2015 |
| `stg_game_context` | 534 | 0 | 0 | 2014-2015 |
| `stg_player_week_stats` | 35193 | 0 | 0 | 2014-2015 |
| `stg_team_week_stats` | 1068 | 0 | 0 | 2014-2015 |
| `stg_play_player_events` | 234469 | 0 | 0 | 2014-2015 |
| `stg_participation_context` | 47706 | 0 | 0 | 2014-2015 |

## Dry Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2016 --season-end 2017 --dry-run --all-targets --strict --output-json %TEMP%\phase29_21_staging_dry_run.json
```

Dry-run exit code: 0

| Target | Readiness | Source Rows | Planned Rows | Duplicate Grain Count | Identity Gap Count | Warnings |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `stg_player_identity` | ready with warnings | n/a | 86341 | 0 | n/a | no name-only identity joins |
| `stg_game_context` | ready | 534 | 534 | 0 | n/a | none |
| `stg_player_week_stats` | ready with warnings | 34987 | 34987 | 0 | 1619 | legacy `weekly_metrics` is not used |
| `stg_team_week_stats` | ready with warnings | 94896 | 1068 | 0 | n/a | `pass_rate_over_expected` remains null until a model source exists |
| `stg_play_player_events` | ready with warnings | 94896 | 232191 | 0 | 6615 | route metrics are not created |
| `stg_participation_context` | ready with warnings | 47752 | 47752 | 0 | 9 | PFR identifiers are used where GSIS is unavailable; route metrics remain blocked |

Dry-run route guard:

| Metric | Value |
| --- | ---: |
| `stg_participation_context.route_share_non_null_rows` | 0 |
| `stg_participation_context.true_route_source_rows` | 0 |

Dry-run warnings:

- Default mode is read-only.
- Raw `raw_nflverse_*` tables remain internal and are not Pigskin or UI surfaces.

## Live Staging Write

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2016 --season-end 2017 --all-targets --write --strict
```

Write exit code: 0

| Target | Write SQL Kind | DML Affected Rows | Bounded Rows After | Duplicate Grain Count After | Missing Flags Rows | Missing Source Freshness Rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `stg_player_identity` | MERGE | 86341 | 86341 | 0 | 0 | 0 |
| `stg_game_context` | MERGE | 534 | 534 | 0 | 0 | 0 |
| `stg_player_week_stats` | MERGE | 34987 | 34987 | 0 | 0 | 0 |
| `stg_team_week_stats` | MERGE | 1068 | 1068 | 0 | 0 | 0 |
| `stg_play_player_events` | MERGE | 232191 | 232191 | 0 | 0 | 0 |
| `stg_participation_context` | MERGE | 47752 | 47752 | 0 | 0 | 0 |

The command emitted CLI text saying `phase: 29.8` and a warning mentioning Phase 29.8 authorization. This appears to be stale CLI copy. The command boundaries and arguments were Phase 29.21 scoped: `--season-start 2016 --season-end 2017 --all-targets --write --strict`.

## Post-Write Staging Verification

| Staging Table | Total Rows | 2016 Rows | 2017 Rows | Season Range | Week Range | Duplicate Key Groups | Missing Required Key Rows | Missing Source Freshness | Missing Flags |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `stg_player_identity` | 146737 | 35020 | 51321 | 2014-2017 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_game_context` | 1068 | 267 | 267 | 2014-2017 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_player_week_stats` | 70180 | 17531 | 17456 | 2014-2017 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_team_week_stats` | 2136 | 534 | 534 | 2014-2017 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_play_player_events` | 466660 | 117281 | 114910 | 2014-2017 | 1-21 | 0 | 0 | 0 | 0 |
| `stg_participation_context` | 95458 | 23890 | 23862 | 2014-2017 | 1-21 | 0 | 0 | 0 | 0 |

Identity and route guard summary for the bounded 2016-2017 rows:

| Target | Identity Gap Count | Other Guard |
| --- | ---: | --- |
| `stg_player_identity` | n/a | 8 rows missing `position`; no rows below 0.95 confidence |
| `stg_player_week_stats` | 1619 | position and team populated |
| `stg_play_player_events` | 6615 | 231643 rows with `epa`; 231643 rows with `success` |
| `stg_participation_context` | 9 | `route_share` non-null rows: 0; `has_true_route_source` true rows: 0 |
| `stg_team_week_stats` | n/a | `pass_rate_over_expected` non-null rows: 0 |

Route metrics remain blocked:

- `route_share` remains null.
- `has_true_route_source` remains false.
- No true route source was introduced.

## Non-Target Object Verification

Raw row counts were unchanged after the staging write.

| Raw Table | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `raw_nflverse_schedules` | 1068 | 267 | 267 |
| `raw_nflverse_rosters` | 10484 | 3061 | 3082 |
| `raw_nflverse_rosters_weekly` | 146737 | 35020 | 51321 |
| `raw_nflverse_weekly` | 70180 | 17531 | 17456 |
| `raw_nflverse_pbp` | 190647 | 47651 | 47245 |
| `raw_nflverse_snap_counts` | 95458 | 23890 | 23862 |

Static/global raw rows were unchanged:

| Raw Table | Rows |
| --- | ---: |
| `raw_nflverse_players` | 25033 |
| `raw_nflverse_ff_playerids` | 69060 |
| `raw_nflverse_teams` | 36 |

Advanced metrics and Pigskin packet objects were not written:

| Object | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 35193 | 0 | 0 |
| `team_week_context_metrics` | 1068 | 0 | 0 |
| `qb_week_environment_metrics` | 1261 | 0 | 0 |
| `player_recent_advanced_metrics_current` | 2309 | 0 | 0 |
| `player_role_usage_metrics_current` | 2309 | 0 | 0 |
| `pigskin_player_context_packet_current` | 980 | 0 | 0 |
| `compat_pigskin_player_context_current` | 980 | 0 | 0 |

Score lanes were unchanged:

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
| `181_raw_nflverse_season_week_coverage.sql` | Informational review query now sees raw coverage through 2017. |
| `178_trade_pick_scores_model_version_coverage.sql` | Informational model-version coverage query returned existing `trade_pick_score_v0_2026_001` rows. |

No validation command failed.

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_staging.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_staging` | PASS |
| `unittest tests.test_nflverse_backfill_executor` | PASS |
| `unittest discover tests` | PASS |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Service Readback

No deployment occurred.

| Service | Revision | Traffic | Image | Relevant Flag State |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100 percent | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | all production risk flags false; Trade Analyzer score false; Trade History compat false; Data Ops trigger and local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100 percent | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score flags true; Trade History compat true; Data Ops trigger and local subprocess flags false |

## Warnings

- Identity gaps are quantified and not hidden: 1619 in `stg_player_week_stats`, 6615 in `stg_play_player_events`, and 9 in `stg_participation_context` for 2016-2017.
- `stg_player_identity` has 8 rows missing `position` in the 2016-2017 slice.
- `pass_rate_over_expected` remains null because no model source exists.
- `route_share` remains null and `has_true_route_source` remains false by design.
- CLI output still labels this staging write path as `phase: 29.8` and says Phase 29.8 writes were authorized. The command and report scope are Phase 29.21.
- Raw `raw_nflverse_*` tables remain internal and not Pigskin or UI-safe surfaces.

## Blockers

None for 2016-2017 staging materialization.

Advanced metrics and Pigskin packet refresh remain intentionally not run in this phase.

## Recommended Next Phase

Run an authorized Phase 29.22 bounded advanced metrics materialization for 2016-2017, followed by a separate Pigskin current packet refresh only after metric validations pass.
