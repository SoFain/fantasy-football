# Phase 29.32: 2021-2023 Raw nflverse Backfill

Date: 2026-06-30

Final decision: **2021-2023 RAW BACKFILL READY WITH WARNINGS**

## Scope

Phase 29.32 ran the authorized historical raw nflverse backfill for seasons 2021 through 2023 only.

Live write scope:

- Preset: `core_historical`
- Seasons: `2021-2023`
- Target family: `raw_nflverse_*` tables only
- Source families: `schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`

No staging materialization, advanced metrics materialization, Pigskin packet refresh, packet-display repair, ranking build, staging deployment, production deployment, feature-flag change, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, or Firebase artifact creation occurred.

## Authorization Gate State

Before the phase, all checked gates were empty or unset:

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

During the single live raw backfill command, only this gate was set inside the same PowerShell wrapper:

```powershell
ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true
```

After the `finally` block, these gates were checked and were empty or unset:

- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Git State

Latest commit at start:

```text
db8f279 Expand nflverse Pigskin packets through 2020
```

No files were staged. There were no tracked source diffs. Existing untracked files were historical validation backlog and owner-review reports, including `phase-29-31-2018-2020-expansion-commit-report.md`.

No commit was created in this phase.

## Baseline Checks

Pre-write checks:

- `scripts/check_deployment_safety.py`: pass
- `py_compile src\nflverse_backfill_plan.py`: pass
- `py_compile src\nflverse_backfill.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_nflverse_backfill_plan`: pass, 15 tests
- `tests.test_nflverse_backfill_executor`: pass, 18 tests
- `unittest discover tests`: pass, 487 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through 200

## Plan-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2021 --season-end 2023
```

Result:

- No writes.
- No loaders called.
- Selected families matched `core_historical`.
- Target seasons were `[2021, 2022, 2023]`.
- Existing target tables were present.
- Raw tables remained marked as not Pigskin/UI-safe surfaces.
- Season-level loader warnings were preserved for `weekly`, `pbp`, and `snap_counts`.

Output captured at:

```text
%TEMP%\phase29_32_plan_only.txt
```

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2021 --season-end 2023 --dry-run
```

Result:

- No BigQuery rows written.
- Selected source families matched `core_historical`.
- Target seasons were `[2021, 2022, 2023]`.
- Future authorization gate remained `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`.
- Raw `raw_nflverse_*` tables remained explicitly non-Pigskin/UI-safe.

Output captured at:

```text
%TEMP%\phase29_32_dry_run.txt
```

## Prepare-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2021 --season-end 2023 --prepare-only --skip-source-family-on-error
```

Result:

- Exit code: `0`
- `prepare_only`: `true`
- `wrote`: `false`
- Source refresh ID: `nflverse_core_historical_2021_2023_20260630T135819Z`
- Critical failures: none
- All critical families prepared nonzero rows.

| Family | Fetched | Prepared | Skipped | Warnings |
| --- | ---: | ---: | ---: | --- |
| `schedules` | 854 | 854 | 0 | none |
| `teams` | 36 | 36 | 0 | none |
| `players` | 25,033 | 25,033 | 0 | none |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 9,641 missing `nflverse_player_id`; 45 deduped source rows |
| `rosters` | 9,185 | 9,182 | 3 | 3 missing `player_id` |
| `rosters_weekly` | 138,514 | 138,456 | 58 | 58 missing `player_id` |
| `weekly` | 56,443 | 56,377 | 66 | 66 missing `player_id`; treated as non-player or aggregate rows unless a safe source key is proven |
| `pbp` | 149,021 | 149,021 | 0 | none |
| `snap_counts` | 79,389 | 79,389 | 0 | none |

Compared with the 2018-2020 backfill, skipped-row behavior was slightly higher for `weekly` and `rosters_weekly`, but remained bounded and explainable. No critical family prepared 0 rows.

Output captured at:

```text
%TEMP%\phase29_32_prepare_only.txt
```

## Pre-Write Raw State

Season-grained raw targets had zero 2021-2023 rows before the live write:

| Table | 2021-2023 rows before |
| --- | ---: |
| `raw_nflverse_schedules` | 0 |
| `raw_nflverse_rosters` | 0 |
| `raw_nflverse_rosters_weekly` | 0 |
| `raw_nflverse_weekly` | 0 |
| `raw_nflverse_pbp` | 0 |
| `raw_nflverse_snap_counts` | 0 |

Static/global raw tables before the write:

| Table | Rows |
| --- | ---: |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

Because no 2021-2023 season-grained rows existed, the phase proceeded with the single authorized write.

## Live Write Command

The live write ran once inside the required same-session wrapper:

```powershell
try {
$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"

echo "ALLOW_NFLVERSE_HISTORICAL_BACKFILL=$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL"

.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2021 --season-end 2023 --write --strict

} finally {
Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

Output captured at:

```text
%TEMP%\phase29_32_raw_backfill_write.txt
```

## Live Write Result

Result:

- Exit code: `0`
- `wrote`: `true`
- Elapsed seconds: `335.317`
- Gate used: `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- Source refresh ID: `nflverse_core_historical_2021_2023_20260630T140142Z`
- Critical failures: none
- Failed source families: none
- Skipped source families: none

| Family | Fetched | Prepared | Skipped | Written or merged | Target total after | Duplicate keys after | Warnings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `schedules` | 854 | 854 | 0 | 854 | 2,725 | 0 | none |
| `teams` | 36 | 36 | 0 | 0 | 36 | 0 | none |
| `players` | 25,033 | 25,033 | 0 | 0 | 25,033 | 0 | none |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 0 | 69,060 | 0 | 9,641 missing `nflverse_player_id`; 45 deduped source rows |
| `rosters` | 9,185 | 9,182 | 3 | 9,182 | 28,987 | 0 | 3 missing `player_id` |
| `rosters_weekly` | 138,514 | 138,456 | 58 | 138,456 | 433,147 | 0 | 58 missing `player_id` |
| `weekly` | 56,443 | 56,377 | 66 | 56,377 | 178,872 | 0 | 66 missing `player_id`; treated as aggregate/non-player rows |
| `pbp` | 149,021 | 149,021 | 0 | 149,021 | 481,742 | 0 | none |
| `snap_counts` | 79,389 | 79,389 | 0 | 79,389 | 247,585 | 0 | none |

Runtime warning:

- BigQuery pandas helper emitted a future warning that `pandas-gbq>=0.26.1` will be required for future DataFrame loads. This did not fail the backfill.

## Post-Write Raw Verification

All 2021-2023 season-grained rows had populated `source_refresh_id`, `loaded_at`, and `row_hash`.

| Table | 2021 rows | 2022 rows | 2023 rows | Week range | Metadata populated | Duplicate keys |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| `raw_nflverse_schedules` | 285 | 284 | 285 | 1-22 | yes | 0 |
| `raw_nflverse_rosters` | 2,960 | 3,133 | 3,089 | n/a | yes | 0 |
| `raw_nflverse_rosters_weekly` | 46,670 | 46,136 | 45,650 | 1-22 | yes | 0 |
| `raw_nflverse_weekly` | 18,947 | 18,809 | 18,621 | 1-22 | yes | 0 |
| `raw_nflverse_pbp` | 49,922 | 49,434 | 49,665 | 1-22 | yes | 0 |
| `raw_nflverse_snap_counts` | 26,468 | 26,381 | 26,540 | 1-22 | yes | 0 |

Source loader and version distribution for 2021-2023 rows:

| Table | Loader | Source version | Rows |
| --- | --- | --- | ---: |
| `raw_nflverse_schedules` | `nflreadpy.load_schedules` | `0.1.5` | 854 |
| `raw_nflverse_rosters` | `nflreadpy.load_rosters` | `0.1.5` | 9,182 |
| `raw_nflverse_rosters_weekly` | `nflreadpy.load_rosters_weekly` | `0.1.5` | 138,456 |
| `raw_nflverse_weekly` | `nflreadpy.load_player_stats` | `0.1.5` | 56,377 |
| `raw_nflverse_pbp` | `nflreadpy.load_pbp` | `0.1.5` | 149,021 |
| `raw_nflverse_snap_counts` | `nflreadpy.load_snap_counts` | `0.1.5` | 79,389 |

Source refresh distribution:

| Source refresh ID | Rows |
| --- | ---: |
| `nflverse_core_historical_2021_2023_20260630T140142Z` | 433,279 |

Static/global table behavior:

| Table | Rows after write | Duplicate keys |
| --- | ---: | ---: |
| `raw_nflverse_teams` | 36 | 0 |
| `raw_nflverse_players` | 25,033 | 0 |
| `raw_nflverse_ff_playerids` | 69,060 | 0 |

Static/global tables remained idempotent.

## 17-Game Schedule Era Behavior

The 2021-2023 backfill reflects the 17-game schedule era:

- `raw_nflverse_schedules` has 285 rows for 2021, 284 for 2022, and 285 for 2023.
- Week coverage extends from 1 through 22 for schedule, weekly, PBP, roster-weekly, and snap-count rows.
- PBP volume increased relative to 2018-2020 and remained bounded by season.
- No 2024 or later rows were written.

## Non-Target Object Verification

Non-target counts remained unchanged from the 2014-2020 checkpoint:

| Object | Rows |
| --- | ---: |
| `stg_player_identity` | 294,691 |
| `stg_game_context` | 1,871 |
| `stg_player_week_stats` | 122,495 |
| `stg_team_week_stats` | 3,742 |
| `stg_play_player_events` | 812,370 |
| `stg_participation_context` | 168,196 |
| `player_week_advanced_metrics` | 122,495 |
| `team_week_context_metrics` | 3,742 |
| `qb_week_environment_metrics` | 4,513 |
| `player_recent_advanced_metrics_current` | 4,344 |
| `player_role_usage_metrics_current` | 4,344 |
| `pigskin_player_context_packet_current` | 2,336 |
| `compat_pigskin_player_context_current` | 2,336 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

No staging, advanced metrics, Pigskin packet, or score-lane table was written.

## Validation Results

Read-only validation patterns after the raw write:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS, 3 passed, 0 failed. Validation 181 returned informational 2014-2023 coverage rows. First row: `raw_nflverse_pbp`, 481,742 rows, min season 2014, max season 2023, season-week count 213. |
| `stg_` | PASS, 7 passed, 0 failed. |
| `advanced_metrics` | PASS, 4 passed, 0 failed. |
| `compat_pigskin` | PASS, 2 passed, 0 failed. |
| `trade_player_scores` | PASS, 12 passed, 0 failed. |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Validation 178 remains informational for `trade_pick_score_v0_2026_001`, 64 rows. |

## Final Local Checks

Post-write checks:

- `scripts/check_deployment_safety.py`: pass
- `py_compile src\nflverse_backfill_plan.py`: pass
- `py_compile src\nflverse_backfill.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_nflverse_backfill_plan`: pass, 15 tests
- `tests.test_nflverse_backfill_executor`: pass, 18 tests
- `unittest discover tests`: pass, 487 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through 200

## Staging and Production Untouched

Read-only Cloud Run state:

| Service | Revision | Traffic | Image | Relevant flags |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | `100%` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | Data Ops trigger flags false, local subprocess flags false, Trade Analyzer score flags false, Trade History compatibility false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | `100%` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | Data Ops trigger flags false, local subprocess flags false, staging score and trade-history flags remained enabled from prior staging QA |

No deployment occurred.

## Remaining Warnings

- This phase wrote raw source rows only. Raw `raw_nflverse_*` tables remain blocked from Pigskin/UI-safe surfaces.
- 2021-2023 schedule counts reflect the 17-game era and differ from 2014-2020 season shapes.
- `ff_playerids` skipped missing `nflverse_player_id` rows and deduped 45 source rows before merge.
- `weekly`, `rosters`, and `rosters_weekly` skipped missing-player rows, matching the known source behavior.
- `snap_counts` continues to use PFR identifiers where GSIS is unavailable.
- BigQuery DataFrame loads emitted a future `pandas-gbq` dependency warning.
- `raw_nflverse` validation 181 and `trade_pick_scores` validation 178 remain informational review warnings.
- Phase 29.31 commit evidence remains untracked, along with historical validation backlog.

## Recommended Next Phase

Phase 29.33: authorized 2021-2023 nflverse staging materialization, with a dry-run first and explicit confirmation that no raw backfill, advanced metrics materialization, or Pigskin packet refresh runs in the same phase.
