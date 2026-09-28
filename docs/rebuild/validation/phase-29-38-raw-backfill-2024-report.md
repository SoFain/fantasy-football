# Phase 29.38 - 2024 Raw nflverse Backfill

Date: 2026-06-30

Final decision: **2024 RAW BACKFILL READY WITH WARNINGS**

## Scope

Authorized operation was limited to:

- `preset=core_historical`
- `season_start=2024`
- `season_end=2024`
- raw nflverse tables only: `raw_nflverse_*`

No staging materialization, advanced metric materialization, Pigskin packet refresh, deployment, feature-flag change, Cloud Run Job trigger, Scheduler job, current-season lane, LLM action, Pigskin prompt, or Firebase artifact was run.

## Authorization Gate State

Before write, all checked gates were empty or unset:

- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

The live write used the required same-session wrapper:

```powershell
try {
$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"

echo "ALLOW_NFLVERSE_HISTORICAL_BACKFILL=$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL"

.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2024 --season-end 2024 --write --strict

} finally {
Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

After the wrapper, `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` and adjacent write/deploy gates were empty or unset. The executor JSON reported `gate_removed=false` before the outer PowerShell `finally` completed; the independent post-wrapper environment check confirmed the gate was removed.

## Git State

Latest commit before work:

- `e56afa3 Expand nflverse Pigskin packets through 2023`

No files were staged. The worktree had the known untracked historical validation-report backlog.

## Baseline Checks

All baseline checks passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_plan`: 15 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_executor`: 18 tests passed
- `.\venv\Scripts\python.exe -m unittest discover tests`: 487 tests passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: validation catalog discovered through `200`

## Plan-Only and Dry-Run

Plan-only command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2024 --season-end 2024
```

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2024 --season-end 2024 --dry-run
```

Selected source families matched `core_historical`:

- `schedules`
- `teams`
- `players`
- `ff_playerids`
- `rosters`
- `rosters_weekly`
- `weekly`
- `pbp`
- `snap_counts`

Target season was only `2024`. Plan-only and dry-run wrote no BigQuery rows.

## Prepare-Only Summary

Prepare-only command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2024 --season-end 2024 --prepare-only --skip-source-family-on-error
```

Source refresh ID:

- `nflverse_core_historical_2024_2024_20260630T155910Z`

| Source family | Fetched | Prepared | Skipped | Warning summary |
| --- | ---: | ---: | ---: | --- |
| `schedules` | 285 | 285 | 0 | none |
| `teams` | 36 | 36 | 0 | none |
| `players` | 25,033 | 25,033 | 0 | none |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 9,641 missing `nflverse_player_id`; 45 deduped source rows |
| `rosters` | 3,216 | 3,215 | 1 | 1 missing `player_id` |
| `rosters_weekly` | 46,579 | 46,572 | 7 | 7 missing `player_id` |
| `weekly` | 18,981 | 18,959 | 22 | 22 missing `player_id`; treated as non-player or aggregate rows unless a safe source key is proven |
| `pbp` | 49,492 | 49,492 | 0 | none |
| `snap_counts` | 26,615 | 26,615 | 0 | none |

Critical families prepared nonzero rows. No critical family blocked the write.

## Pre-Write Raw State

Before the write, the season-grained raw targets had `0` rows for 2024:

| Table | Total rows before | 2024 rows before |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 2,725 | 0 |
| `raw_nflverse_rosters` | 28,987 | 0 |
| `raw_nflverse_rosters_weekly` | 433,147 | 0 |
| `raw_nflverse_weekly` | 178,872 | 0 |
| `raw_nflverse_pbp` | 481,742 | 0 |
| `raw_nflverse_snap_counts` | 247,585 | 0 |

Static/global raw tables matched the expected idempotent baseline:

- `raw_nflverse_teams`: 36
- `raw_nflverse_players`: 25,033
- `raw_nflverse_ff_playerids`: 69,060

## Live Write Result

Live write command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2024 --season-end 2024 --write --strict
```

Result:

- Exit code: 0
- `wrote`: true
- Elapsed seconds: 211.608
- Source refresh ID: `nflverse_core_historical_2024_2024_20260630T160150Z`
- Failed source families: none
- Skipped source families: none

| Source family | Prepared | Written or merged | Target rows after | Duplicate keys after |
| --- | ---: | ---: | ---: | ---: |
| `schedules` | 285 | 285 | 3,010 | 0 |
| `teams` | 36 | 0 | 36 | 0 |
| `players` | 25,033 | 0 | 25,033 | 0 |
| `ff_playerids` | 69,060 | 0 | 69,060 | 0 |
| `rosters` | 3,215 | 3,215 | 32,202 | 0 |
| `rosters_weekly` | 46,572 | 46,572 | 479,719 | 0 |
| `weekly` | 18,959 | 18,959 | 197,831 | 0 |
| `pbp` | 49,492 | 49,492 | 531,234 | 0 |
| `snap_counts` | 26,615 | 26,615 | 274,200 | 0 |

Static/global tables were idempotent. They retained their previous row counts and did not insert duplicate rows.

## Post-Write Raw Verification

Read-only BigQuery checks used neutral aliases such as `row_count` and `scope_row_count`.

| Table | Total rows | 2024 rows | Full season range | 2024 week range | Metadata populated | Duplicate key groups | 2025+ rows |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: |
| `raw_nflverse_schedules` | 3,010 | 285 | 2014-2024 | 1-22 | 285/285 | 0 | 0 |
| `raw_nflverse_rosters` | 32,202 | 3,215 | 2014-2024 | n/a | 3,215/3,215 | 0 | 0 |
| `raw_nflverse_rosters_weekly` | 479,719 | 46,572 | 2014-2024 | 1-22 | 46,572/46,572 | 0 | 0 |
| `raw_nflverse_weekly` | 197,831 | 18,959 | 2014-2024 | 1-22 | 18,959/18,959 | 0 | 0 |
| `raw_nflverse_pbp` | 531,234 | 49,492 | 2014-2024 | 1-22 | 49,492/49,492 | 0 | 0 |
| `raw_nflverse_snap_counts` | 274,200 | 26,615 | 2014-2024 | 1-22 | 26,615/26,615 | 0 | 0 |
| `raw_nflverse_teams` | 36 | n/a | n/a | n/a | 36/36 | 0 | n/a |
| `raw_nflverse_players` | 25,033 | n/a | n/a | n/a | 25,033/25,033 | 0 | n/a |
| `raw_nflverse_ff_playerids` | 69,060 | n/a | n/a | n/a | 69,060/69,060 | 0 | n/a |

For each 2024-scoped raw table, `source_refresh_id`, `loaded_at`, and `row_hash` were fully populated. Source loader distribution and source version distribution were single-source per family, using `nflreadpy` version `0.1.5`.

## 2025 and Current-Season Separation

Season-grained raw tables reported `0` rows where `season >= 2025` after the write. No 2025/current-season lane was run.

## Non-Target Object Verification

Staging tables remained 2014-2023 only:

| Table | Row count | 2024 rows | Season range |
| --- | ---: | ---: | --- |
| `stg_player_identity` | 433,147 | 0 | 2014-2023 |
| `stg_game_context` | 2,725 | 0 | 2014-2023 |
| `stg_player_week_stats` | 178,872 | 0 | 2014-2023 |
| `stg_team_week_stats` | 5,450 | 0 | 2014-2023 |
| `stg_play_player_events` | 1,173,226 | 0 | 2014-2023 |
| `stg_participation_context` | 247,585 | 0 | 2014-2023 |

Advanced metrics and current views were unchanged:

| Object | Row count | 2024 rows |
| --- | ---: | ---: |
| `player_week_advanced_metrics` | 178,872 | 0 |
| `team_week_context_metrics` | 5,450 | 0 |
| `qb_week_environment_metrics` | 6,643 | 0 |
| `player_recent_advanced_metrics_current` | 5,497 | n/a |
| `player_role_usage_metrics_current` | 5,497 | n/a |

Pigskin packet counts remained unchanged:

- `pigskin_player_context_packet_current`: 3,082
- `compat_pigskin_player_context_current`: 3,082

Score lanes remained unchanged:

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
- `src\nflverse_backfill_plan.py` compiled
- `src\nflverse_backfill.py` compiled
- `src` and `scripts` compileall passed
- `tests.test_nflverse_backfill_plan`: 15 tests passed
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

- `ff_playerids` skipped 9,641 source rows with missing `nflverse_player_id` and deduped 45 source rows before merge.
- `rosters` skipped 1 row with missing `player_id`.
- `rosters_weekly` skipped 7 rows with missing `player_id`.
- `weekly` skipped 22 rows with missing `player_id`; these remain classified as non-player or aggregate rows unless a safe source key is proven.
- `raw_nflverse` season/week coverage validation is informational and now reflects 2014-2024 raw coverage.
- `trade_pick_scores` model-version coverage validation is informational and unrelated to this raw backfill.
- The live write emitted a local BigQuery client `pandas-gbq` future warning. It did not block the load.
- The local BigQuery REST fallback warning appeared on read-only checks where BigQuery Storage was unavailable in the active venv.

## Recommended Next Phase

Proceed to a separate Phase 29.39 for 2024 staging materialization planning and dry-run. Keep it bounded to 2024, do not run advanced metrics or packet refresh until staging verification passes, and keep using neutral BigQuery aliases such as `row_count` instead of `rows`.
