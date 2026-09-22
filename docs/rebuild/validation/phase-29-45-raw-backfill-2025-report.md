# Phase 29.45 Raw Backfill 2025 Report

Final decision: **2025 RAW BACKFILL READY WITH WARNINGS**

## Scope

Owner correction accepted: the Phase 29.44 current-season lane recommendation is superseded for this task. Season 2025 was treated as a completed historical season and continued through the Phase 29 completed-season historical lane.

This phase wrote only the 2025 `core_historical` raw nflverse slice into `raw_nflverse_*` tables. It did not run staging materialization, advanced metrics materialization, Pigskin packet refresh, deployment, rankings, Cloud Run Jobs, Scheduler jobs, LLM actions, Pigskin prompts, or feature flag changes.

## Authorization Gate

Pre-run gates were all empty or unset:

| Gate | State |
|---|---|
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Live write gate was set only inside the same-session wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"
  .\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2025 --season-end 2025 --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

Post-wrapper checks confirmed the gate was removed. Staging, advanced metrics, Pigskin packet, weekly refresh, production deploy, and local subprocess gates remained unset.

## Git State

Latest commit at start: `3c83af6 Expand nflverse Pigskin packets through 2024`.

No files were staged. The working tree still contains the known untracked historical validation backlog and owner-review reports, including:

- `docs/rebuild/validation/phase-29-43-2024-expansion-commit-report.md`
- `docs/rebuild/validation/phase-29-44-2025-current-season-lane-decision-report.md`

No tracked Phase 29 package files were modified unexpectedly before the write.

## Baseline Checks

All baseline checks passed before the write:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_backfill_plan` | pass, 15 tests |
| `unittest tests.test_nflverse_backfill_executor` | pass, 18 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Plan-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2025 --season-end 2025
```

Result: pass, no writes.

Selected source families:

`schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`

Planner mode: `historical_backfill`.

Warnings were expected:

- Planner only. No nflverse loaders called and no BigQuery rows written.
- Raw `raw_nflverse_*` tables are not Pigskin/UI-safe surfaces.
- Season-level loaders perform week filtering only after extraction in future merge planning.
- Snap share is available from snap counts. Route share still needs a true route source.

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2025 --season-end 2025 --dry-run
```

Result: pass, `dry_run=true`, `wrote=false`.

No BigQuery rows were written. The dry-run selected the same nine `core_historical` source families and targeted only season 2025.

## Prepare-Only Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2025 --season-end 2025 --prepare-only --skip-source-family-on-error
```

Result: pass, `prepare_only=true`, `wrote=false`.

Source refresh ID: `nflverse_core_historical_2025_2025_20260630T175805Z`

| Source family | Fetched | Prepared | Skipped | Warning count |
|---|---:|---:|---:|---:|
| `schedules` | 285 | 285 | 0 | 0 |
| `teams` | 36 | 36 | 0 | 0 |
| `players` | 25,033 | 25,033 | 0 | 0 |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 2 |
| `rosters` | 3,137 | 3,134 | 3 | 1 |
| `rosters_weekly` | 46,849 | 46,831 | 18 | 1 |
| `weekly` | 19,421 | 19,399 | 22 | 2 |
| `pbp` | 48,771 | 48,771 | 0 | 0 |
| `snap_counts` | 26,612 | 26,612 | 0 | 0 |

No critical family prepared 0 rows. Counts are consistent with the 17-game era and postseason-inclusive Week 22 coverage.

Skipped-row warnings:

- `ff_playerids`: skipped 9,641 rows with missing `nflverse_player_id`; deduped 45 source rows on natural key.
- `rosters`: skipped 3 rows with missing `player_id`.
- `rosters_weekly`: skipped 18 rows with missing `player_id`.
- `weekly`: skipped 22 rows with missing `player_id`; treated as non-player or aggregate rows unless a safe source key is proven.

## Pre-Write Raw State

Read-only counts confirmed every season-grained 2025 target was empty before the write.

| Table | Total before | 2025 rows before | 2026+ rows before | Season range before | Week range before |
|---|---:|---:|---:|---|---|
| `raw_nflverse_schedules` | 3,010 | 0 | 0 | 2014-2024 | 1-22 |
| `raw_nflverse_rosters` | 32,202 | 0 | 0 | 2014-2024 | n/a |
| `raw_nflverse_rosters_weekly` | 479,719 | 0 | 0 | 2014-2024 | 1-22 |
| `raw_nflverse_weekly` | 197,831 | 0 | 0 | 2014-2024 | 1-22 |
| `raw_nflverse_pbp` | 531,234 | 0 | 0 | 2014-2024 | 1-22 |
| `raw_nflverse_snap_counts` | 274,200 | 0 | 0 | 2014-2024 | 1-22 |

Static/global tables before write:

| Table | Total before |
|---|---:|
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

## Live Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2025 --season-end 2025 --write --strict
```

Result: pass, exit 0, `wrote=true`.

Source refresh ID: `nflverse_core_historical_2025_2025_20260630T180037Z`

| Source family | Fetched | Prepared | Skipped | Written or merged | Target rows after | Duplicate keys after |
|---|---:|---:|---:|---:|---:|---:|
| `schedules` | 285 | 285 | 0 | 285 | 3,295 | 0 |
| `teams` | 36 | 36 | 0 | 0 | 36 | 0 |
| `players` | 25,033 | 25,033 | 0 | 0 | 25,033 | 0 |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 0 | 69,060 | 0 |
| `rosters` | 3,137 | 3,134 | 3 | 3,134 | 35,336 | 0 |
| `rosters_weekly` | 46,849 | 46,831 | 18 | 46,831 | 526,550 | 0 |
| `weekly` | 19,421 | 19,399 | 22 | 19,399 | 217,230 | 0 |
| `pbp` | 48,771 | 48,771 | 0 | 48,771 | 580,005 | 0 |
| `snap_counts` | 26,612 | 26,612 | 0 | 26,612 | 300,812 | 0 |

The command emitted a non-blocking `pandas_gbq` future warning from BigQuery DataFrame loading. The write still exited 0 and all post-write validations passed.

## Post-Write Raw Verification

| Table | Total after | 2025 rows | 2026+ rows | Season range | Week range | 2025 metadata count | 2025 duplicate groups |
|---|---:|---:|---:|---|---|---:|---:|
| `raw_nflverse_schedules` | 3,295 | 285 | 0 | 2014-2025 | 1-22 | 285 | 0 |
| `raw_nflverse_rosters` | 35,336 | 3,134 | 0 | 2014-2025 | n/a | 3,134 | 0 |
| `raw_nflverse_rosters_weekly` | 526,550 | 46,831 | 0 | 2014-2025 | 1-22 | 46,831 | 0 |
| `raw_nflverse_weekly` | 217,230 | 19,399 | 0 | 2014-2025 | 1-22 | 19,399 | 0 |
| `raw_nflverse_pbp` | 580,005 | 48,771 | 0 | 2014-2025 | 1-22 | 48,771 | 0 |
| `raw_nflverse_snap_counts` | 300,812 | 26,612 | 0 | 2014-2025 | 1-22 | 26,612 | 0 |

For every 2025 row above, `source_refresh_id`, `loaded_at`, and `row_hash` were non-null. Source loader distribution matched the expected single loader per family, and source version was `0.1.5`.

Static/global table behavior:

| Table | Total after | Metadata populated | Duplicate groups |
|---|---:|---:|---:|
| `raw_nflverse_teams` | 36 | 36 | 0 |
| `raw_nflverse_players` | 25,033 | 25,033 | 0 |
| `raw_nflverse_ff_playerids` | 69,060 | 69,060 | 0 |

Static/global tables were idempotent. No new rows were merged into those tables.

## Non-Target Object Verification

Counts remained aligned with the Phase 29.44 baseline. No 2025 rows were introduced into staging or advanced metric tables.

| Object | Total after | 2025 rows | 2026+ rows |
|---|---:|---:|---:|
| `stg_player_identity` | 479,719 | 0 | 0 |
| `stg_game_context` | 3,010 | 0 | 0 |
| `stg_player_week_stats` | 197,831 | 0 | 0 |
| `stg_team_week_stats` | 6,020 | 0 | 0 |
| `stg_play_player_events` | 1,291,263 | 0 | 0 |
| `stg_participation_context` | 274,200 | 0 | 0 |
| `player_week_advanced_metrics` | 197,831 | 0 | 0 |
| `team_week_context_metrics` | 6,020 | 0 | 0 |
| `qb_week_environment_metrics` | 7,350 | 0 | 0 |
| `pigskin_player_context_packet_current` | 3,574 | n/a | n/a |
| `compat_pigskin_player_context_current` | 3,574 | n/a | n/a |
| `trade_player_scores` | 154 | 154 | 0 |
| `trade_player_scores_current` | 77 | 77 | 0 |
| `compat_trade_player_scores_current` | 77 | 77 | 0 |
| `trade_pick_scores` | 64 | n/a | n/a |
| `trade_pick_scores_current` | 64 | n/a | n/a |
| `compat_trade_pick_scores_current` | 64 | n/a | n/a |

Trade pick score rows remained unchanged at 64 total rows. Their pick-year distribution remained outside the nflverse raw backfill lane: 52 for 2026, 4 for 2027, 4 for 2028, and 4 for 2029.

## Validation Results

| Pattern | Result |
|---|---|
| `raw_nflverse` | 3 passed, 0 failed. Coverage review warning returned 2014-2025 rows. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Existing model-version coverage review warning only. |

## Final Local Checks

All final checks passed after the raw write:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_backfill_plan` | pass, 15 tests |
| `unittest tests.test_nflverse_backfill_executor` | pass, 18 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Staging and Production Untouched

Read-only Cloud Run describes confirmed no deployment occurred.

| Service | Revision | Traffic | Image digest | Relevant flag state |
|---|---|---|---|---|
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100 percent to `00077-2jp` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | all production risk flags false, score flags false, Trade History compat false, Data Ops trigger/local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100 percent to `00029-jtb` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score/history flags true as before, Data Ops trigger/local subprocess flags false |

## Remaining Warnings

- `ff_playerids` retains expected skipped rows for missing `nflverse_player_id` and expected source dedupe.
- `weekly`, `rosters`, and `rosters_weekly` retain expected missing `player_id` skipped-row warnings.
- 2025 includes Week 22 coverage, consistent with postseason-inclusive historical source behavior.
- `raw_nflverse` validation includes an informational coverage review row now spanning 2014-2025.
- `trade_pick_scores` validation includes the existing informational model-version coverage warning.
- BigQuery DataFrame loading emitted a future warning that `pandas-gbq>=0.26.1` will be required in the future.
- The backfill JSON reported `gate_removed=false` before the outer PowerShell `finally` ran. The shell-level post-wrapper check confirmed the environment variable was removed.

## Recommended Next Phase

Proceed to a separate authorized 2025 nflverse staging materialization phase using only the already-written 2025 raw rows. Keep it separate from advanced metrics and Pigskin packet refresh. Do not run a current-season lane for this task.
