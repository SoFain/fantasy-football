# Phase 29.15 - Authorized 2015 Raw nflverse Backfill

Date: 2026-06-29

Final decision: 2015 RAW BACKFILL READY WITH WARNINGS

## Scope

Authorized raw backfill for season 2015 only.

Preset: `core_historical`

Target tables: `raw_nflverse_*` only

No staging materialization, advanced metric materialization, Pigskin packet refresh, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, ranking build, Pigskin prompt, LLM-backed action, scrape, Firebase artifact, or commit occurred.

The only live write was the authorized 2015 raw nflverse backfill command.

## Authorization Gate State

Before the write, all relevant gates were unset:

| Gate | Before | During live write | After |
| --- | --- | --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset | `true` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset | unset | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset | unset | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset | unset | unset |

The write gate was set only inside the requested PowerShell `try/finally` wrapper and removed immediately afterward.

## Git State

Latest commit before the phase:

`4805610 Build nflverse Pigskin canary pipeline`

Worktree:

- Existing untracked historical validation backlog remained untracked.
- `docs/rebuild/validation/phase-29-14-historical-expansion-planner-report.md` was untracked from the prior planner phase.
- No files were staged before the phase.
- No commit was created.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_backfill_plan` | 15 tests passed |
| `python -m unittest tests.test_nflverse_backfill_executor` | 18 tests passed |
| `python -m unittest discover tests` | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

PowerShell displayed `NativeCommandError` wrappers for stderr logging during some Python test commands, but the process exit codes were 0 and the test summaries were PASS.

## Plan-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2015 --season-end 2015
```

Result:

- Exit code 0.
- No loaders called.
- No BigQuery rows written.
- Selected source families matched `core_historical`:
  - `schedules`
  - `teams`
  - `players`
  - `ff_playerids`
  - `rosters`
  - `rosters_weekly`
  - `weekly`
  - `pbp`
  - `snap_counts`

Planner warnings preserved:

- Raw `raw_nflverse_*` tables are not Pigskin or UI-safe surfaces.
- Schedules include week, but loader is season-level.
- Roster-weekly, weekly, and pbp week planning is post-load filtering, not week-bounded extraction.
- Snap share is valid from snap counts. Route share still needs a true route source.

## Executor Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2015 --season-end 2015 --dry-run
```

Result:

- Exit code 0.
- `dry_run=True`
- `wrote=False`
- No loader writes.
- No BigQuery rows written.

## Prepare-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2015 --season-end 2015 --prepare-only --skip-source-family-on-error
```

Result:

- Exit code 0.
- `prepare_only=True`
- `wrote=False`
- Critical families prepared nonzero rows.

| Source Family | Fetched | Prepared | Skipped | Target Table | Warnings |
| --- | ---: | ---: | ---: | --- | --- |
| `schedules` | 267 | 267 | 0 | `raw_nflverse_schedules` | none |
| `teams` | 36 | 36 | 0 | `raw_nflverse_teams` | none |
| `players` | 25,033 | 25,033 | 0 | `raw_nflverse_players` | none |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | `raw_nflverse_ff_playerids` | 9,641 rows missing `nflverse_player_id`; 45 source rows deduped on natural key |
| `rosters` | 2,190 | 2,189 | 1 | `raw_nflverse_rosters` | 1 row missing `player_id` |
| `rosters_weekly` | 32,098 | 30,201 | 1,897 | `raw_nflverse_rosters_weekly` | 1 row missing `player_id`; 1,896 source rows deduped on natural key |
| `weekly` | 17,613 | 17,592 | 21 | `raw_nflverse_weekly` | 21 rows missing `player_id`; treated as non-player or aggregate rows until a safe source key is proven |
| `pbp` | 48,122 | 48,122 | 0 | `raw_nflverse_pbp` | none |
| `snap_counts` | 23,842 | 23,842 | 0 | `raw_nflverse_snap_counts` | none |

No critical family prepared 0 rows.

## Pre-Write Raw State

Before the live write, all 2015 season-grained raw targets had 0 rows.

| Table | Total Rows Before | 2015 Rows Before | Duplicate 2015 Key Groups |
| --- | ---: | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 0 | 0 |
| `raw_nflverse_rosters` | 2,152 | 0 | 0 |
| `raw_nflverse_rosters_weekly` | 30,195 | 0 | 0 |
| `raw_nflverse_weekly` | 17,601 | 0 | 0 |
| `raw_nflverse_pbp` | 47,629 | 0 | 0 |
| `raw_nflverse_snap_counts` | 23,864 | 0 | 0 |

Static/global tables were already populated from the 2014 canary and had clean metadata plus 0 duplicate key groups:

| Table | Total Rows Before | Duplicate Key Groups |
| --- | ---: | ---: |
| `raw_nflverse_teams` | 36 | 0 |
| `raw_nflverse_players` | 25,033 | 0 |
| `raw_nflverse_ff_playerids` | 69,060 | 0 |

## Live Write Command

Command wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"

  echo "ALLOW_NFLVERSE_HISTORICAL_BACKFILL=$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL"

  .\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2015 --season-end 2015 --write --strict

} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

Result:

- Exit code 0.
- `dry_run=false`
- `wrote=true`
- `strict=true`
- `source_refresh_id=nflverse_core_historical_2015_2015_20260629T192750Z`
- Elapsed time: 214.115 seconds.
- Source families attempted: 9.
- Source families succeeded: 9.
- Source families failed: 0.

Warnings:

- BigQuery Python helper emitted a `FutureWarning` that future DataFrame loads will require `pandas-gbq>=0.26.1`. The warning did not block the write.
- `ff_playerids`, `rosters`, `rosters_weekly`, and `weekly` preserved the expected skipped-row warnings from prepare-only.

## Live Write Result

| Source Family | Fetched | Prepared | Skipped | Written or Merged | Target Rows After | Duplicate Keys After |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `schedules` | 267 | 267 | 0 | 267 | 534 | 0 |
| `teams` | 36 | 36 | 0 | 0 | 36 | 0 |
| `players` | 25,033 | 25,033 | 0 | 0 | 25,033 | 0 |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 0 | 69,060 | 0 |
| `rosters` | 2,190 | 2,189 | 1 | 2,189 | 4,341 | 0 |
| `rosters_weekly` | 32,098 | 30,201 | 1,897 | 30,201 | 60,396 | 0 |
| `weekly` | 17,613 | 17,592 | 21 | 17,592 | 35,193 | 0 |
| `pbp` | 48,122 | 48,122 | 0 | 48,122 | 95,751 | 0 |
| `snap_counts` | 23,842 | 23,842 | 0 | 23,842 | 47,706 | 0 |

Static/global behavior:

- `raw_nflverse_teams` remained 36 rows.
- `raw_nflverse_players` remained 25,033 rows.
- `raw_nflverse_ff_playerids` remained 69,060 rows.
- Static/global duplicates remained 0.

## Post-Write Raw Verification

All 2015 rows had non-null `source_refresh_id`, `loaded_at`, and `row_hash`.

| Table | Total Rows After | 2015 Rows | Season Range | Week Range 2015 | Metadata Non-Null 2015 | Duplicate 2015 Key Groups | Source Loader |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| `raw_nflverse_schedules` | 534 | 267 | 2014-2015 | 1-21 | 267 | 0 | `nflreadpy.load_schedules` |
| `raw_nflverse_rosters` | 4,341 | 2,189 | 2014-2015 | n/a | 2,189 | 0 | `nflreadpy.load_rosters` |
| `raw_nflverse_rosters_weekly` | 60,396 | 30,201 | 2014-2015 | 1-21 | 30,201 | 0 | `nflreadpy.load_rosters_weekly` |
| `raw_nflverse_weekly` | 35,193 | 17,592 | 2014-2015 | 1-21 | 17,592 | 0 | `nflreadpy.load_player_stats` |
| `raw_nflverse_pbp` | 95,751 | 48,122 | 2014-2015 | 1-21 | 48,122 | 0 | `nflreadpy.load_pbp` |
| `raw_nflverse_snap_counts` | 47,706 | 23,842 | 2014-2015 | 1-21 | 23,842 | 0 | `nflreadpy.load_snap_counts` |

Source version for all loaded 2015 rows:

`0.1.5`

## Non-Target Object Verification

No staging, advanced metrics, Pigskin packet, or score-lane object changed.

| Object | Pre-Write Rows | Post-Write Rows |
| --- | ---: | ---: |
| `stg_game_context` | 267 | 267 |
| `stg_participation_context` | 23,864 | 23,864 |
| `stg_play_player_events` | 116,400 | 116,400 |
| `stg_player_identity` | 30,195 | 30,195 |
| `stg_player_week_stats` | 17,601 | 17,601 |
| `stg_team_week_stats` | 534 | 534 |
| `player_week_advanced_metrics` | 17,601 | 17,601 |
| `team_week_context_metrics` | 534 | 534 |
| `qb_week_environment_metrics` | 643 | 643 |
| `player_recent_advanced_metrics_current` | 1,854 | 1,854 |
| `player_role_usage_metrics_current` | 1,854 | 1,854 |
| `pigskin_player_context_packet_current` | 482 | 482 |
| `compat_pigskin_player_context_current` | 482 | 482 |
| `trade_player_scores` | 154 | 154 |
| `trade_player_scores_current` | 77 | 77 |
| `compat_trade_player_scores_current` | 77 | 77 |
| `trade_pick_scores` | 64 | 64 |
| `trade_pick_scores_current` | 64 | 64 |
| `compat_trade_pick_scores_current` | 64 | 64 |

## Validation Results After Write

| Validation Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Coverage review warning now reports `raw_nflverse_pbp` with 95,751 rows, min season 2014, max season 2015, 42 season-week combinations. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Informational warning still reports model `trade_pick_score_v0_2026_001` with 64 rows. |

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_backfill_plan` | 15 tests passed |
| `python -m unittest tests.test_nflverse_backfill_executor` | 18 tests passed |
| `python -m unittest discover tests` | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

## Production and Staging State

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

- `raw_nflverse_rosters_weekly` for 2015 skipped 1,897 source rows, mostly from natural-key dedupe. The write result has 0 duplicate key groups after merge.
- `raw_nflverse_weekly` skipped 21 rows missing `player_id`. These remain treated as non-player or aggregate rows until a safe key is proven.
- `raw_nflverse_ff_playerids` is global/static. It prepared 69,060 rows but merged 0 new rows because the 2014 canary already loaded the same key set.
- The BigQuery Python helper warned that future DataFrame loads will require `pandas-gbq>=0.26.1`.
- Raw tables are not Pigskin or UI-safe surfaces. Staging and compatibility layers must remain the only Pigskin path.

## Recommended Next Phase

Recommended Phase 29.16:

Dry-run and then, only if explicitly authorized, materialize 2015 staging transforms from the newly written 2015 raw tables.

Suggested guardrails:

- Use `season_start=2015` and `season_end=2015` only.
- Run staging dry-run first.
- Require `ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true` only inside the live staging command wrapper.
- Do not run advanced metrics or Pigskin packet refresh in the same phase.
- Validate `stg_` after staging materialization.

2016 or later raw backfill should wait until the 2015 staging results prove identity and row-grain behavior are clean.
