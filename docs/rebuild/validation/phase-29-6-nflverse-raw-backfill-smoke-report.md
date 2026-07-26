# Phase 29.6 nflverse Raw Backfill Smoke Report

Date: 2026-06-29

Final decision: NFLVERSE RAW BACKFILL SMOKE READY WITH WARNINGS

## Scope

Phase 29.6 implemented the gated raw nflverse backfill executor and ran one authorized 2014 `core_historical` smoke backfill.

The live write scope was limited to new `raw_nflverse_*` tables. No legacy source tables, staging tables, feature marts, Pigskin packet tables, score tables, deployments, feature flags, Cloud Run Jobs, Scheduler jobs, LLM-backed actions, Pigskin prompts, scraping, rankings, or Firebase artifacts were touched.

## Authorization Gate State

### Before

All checked gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

### During

`ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true` was set only inside the same PowerShell `try/finally` wrapper that ran the single live smoke command.

No other gate was set.

### After

The wrapper removed `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`.

Post-smoke checks confirmed these were unset:

- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

No files were staged or committed.

Relevant Phase 29 uncommitted files include:

- modified `docs/rebuild/compatibility-contracts.md`
- modified `docs/rebuild/table-classification.md`
- untracked `bigquery/migrations/0027__nflverse_historical_feature_warehouse.sql`
- untracked Phase 29 reports
- untracked `src/nflverse_backfill_plan.py`
- untracked `src/nflverse_backfill.py`
- untracked Phase 29 tests

The historical validation backlog remains untracked owner-review material.

## Files Created or Changed

Phase 29.6 created:

- `src/nflverse_backfill.py`
- `tests/test_nflverse_backfill_executor.py`
- `docs/rebuild/validation/phase-29-6-nflverse-raw-backfill-smoke-report.md`

Phase 29.6 also exercised the already-created planner:

- `src/nflverse_backfill_plan.py`

## Executor Behavior

The new executor provides:

- CLI entry point: `python -m src.nflverse_backfill`
- dry-run behavior that does not import or call `nflreadpy`
- `--write` gate enforcement through `ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true`
- source-family selection through the Phase 29.5 planner registry
- loader dispatch only inside the live execution path
- schema alignment against existing target raw table schemas
- conservative type coercion
- extra source-column dropping
- missing target-column null filling
- metadata injection
- deterministic `row_hash`
- temporary-table load followed by BigQuery `MERGE`
- null-safe natural-key merge conditions
- source-key dedupe before merge
- temp table cleanup
- per-family write summaries

Write mode fails closed before loader calls if the gate is missing. The error includes:

```text
ALLOW_NFLVERSE_HISTORICAL_BACKFILL must be true for live historical backfill writes
```

The executor does not target legacy tables, staging tables, feature marts, Pigskin packets, trade score tables, Cloud Run Jobs, or Scheduler jobs.

## Source Families Attempted

Authorized preset: `core_historical`

Season range: `2014` to `2014`

Attempted:

- `schedules`
- `teams`
- `players`
- `ff_playerids`
- `rosters`
- `rosters_weekly`
- `weekly`
- `pbp`
- `snap_counts`

Critical families:

- `schedules`
- `teams`
- `players`
- `weekly`
- `pbp`

## Dry-Run Planner Output Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2014 --season-end 2014
```

Result:

- status `0`;
- target tables existed;
- target row counts were `0` before smoke;
- all target seasons were `[2014]`;
- no nflverse data fetched;
- no BigQuery rows written.

## Executor Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2014 --season-end 2014 --dry-run
```

Result:

- status `0`;
- `wrote=false`;
- `dry_run=true`;
- source families listed;
- no `nflreadpy` loader called;
- no BigQuery rows written.

## Pre-Smoke Row Counts

Target raw tables before the live smoke:

| Table | Total rows | 2014 rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 0 | 0 |
| `raw_nflverse_teams` | 0 | n/a |
| `raw_nflverse_players` | 0 | n/a |
| `raw_nflverse_ff_playerids` | 0 | n/a |
| `raw_nflverse_rosters` | 0 | 0 |
| `raw_nflverse_rosters_weekly` | 0 | 0 |
| `raw_nflverse_weekly` | 0 | 0 |
| `raw_nflverse_pbp` | 0 | 0 |
| `raw_nflverse_snap_counts` | 0 | 0 |

Because the target tables were empty, the authorized smoke proceeded.

## Live Smoke Command

Command wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"

  echo "ALLOW_NFLVERSE_HISTORICAL_BACKFILL=$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL"

  .\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2014 --season-end 2014 --write --strict

} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

Result:

- command status: `0`;
- source refresh ID: `nflverse_core_historical_2014_2014_20260629T124110Z`;
- elapsed time: `148.932` seconds;
- critical failures: none;
- source families failed: none.

Runtime warning:

```text
FutureWarning: Loading pandas DataFrame into BigQuery will require pandas-gbq package version 0.26.1 or greater in the future.
```

This warning did not block the smoke. It should be handled as dependency cleanup before broad backfill.

## Live Smoke Result

| Source family | Fetched | Prepared | Skipped | Merged or inserted | Target rows after | Duplicate key groups | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `schedules` | 267 | 267 | 0 | 267 | 267 | 0 | succeeded |
| `teams` | 36 | 36 | 0 | 36 | 36 | 0 | succeeded |
| `players` | 25,033 | 25,033 | 0 | 25,033 | 25,033 | 0 | succeeded |
| `ff_playerids` | 12,465 | 0 | 12,465 | 0 | 0 | 0 | warning |
| `rosters` | 2,153 | 0 | 2,153 | 0 | 0 | 0 | warning |
| `rosters_weekly` | 31,964 | 0 | 31,964 | 0 | 0 | 0 | warning |
| `weekly` | 17,622 | 17,601 | 21 | 17,601 | 17,601 | 0 | succeeded with minor warning |
| `pbp` | 47,629 | 47,629 | 0 | 47,629 | 47,629 | 0 | succeeded |
| `snap_counts` | 23,864 | 0 | 23,864 | 0 | 0 | 0 | warning |

The optional zero-prepared families fetched rows but skipped them because their current natural-key mappings did not resolve from the live source schema. This did not corrupt partial state, but it must be fixed before broad historical backfill.

## Post-Smoke Raw Verification

| Source family | Table | Total rows | 2014 rows | Season range | Week range | Metadata rows | Row-hash rows | Duplicate key groups | Loader |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| `schedules` | `raw_nflverse_schedules` | 267 | 267 | 2014-2014 | 1-21 | 267 | 267 | 0 | `nflreadpy.load_schedules` |
| `teams` | `raw_nflverse_teams` | 36 | n/a | n/a | n/a | 36 | 36 | 0 | `nflreadpy.load_teams` |
| `players` | `raw_nflverse_players` | 25,033 | n/a | n/a | n/a | 25,033 | 25,033 | 0 | `nflreadpy.load_players` |
| `ff_playerids` | `raw_nflverse_ff_playerids` | 0 | n/a | n/a | n/a | 0 | 0 | 0 | n/a |
| `rosters` | `raw_nflverse_rosters` | 0 | 0 | n/a | n/a | 0 | 0 | 0 | n/a |
| `rosters_weekly` | `raw_nflverse_rosters_weekly` | 0 | 0 | n/a | n/a | 0 | 0 | 0 | n/a |
| `weekly` | `raw_nflverse_weekly` | 17,601 | 17,601 | 2014-2014 | 1-21 | 17,601 | 17,601 | 0 | `nflreadpy.load_player_stats` |
| `pbp` | `raw_nflverse_pbp` | 47,629 | 47,629 | 2014-2014 | 1-21 | 47,629 | 47,629 | 0 | `nflreadpy.load_pbp` |
| `snap_counts` | `raw_nflverse_snap_counts` | 0 | 0 | n/a | n/a | 0 | 0 | 0 | n/a |

Metadata verification:

- `source_refresh_id` populated for all written rows;
- `loaded_at` populated for all written rows;
- `row_hash` populated for all written rows;
- `source_version` populated for all written rows.

## Non-Target Object Verification

Legacy and score table counts matched the pre-smoke baseline:

| Table | Rows after smoke |
| --- | ---: |
| `play_by_play` | 48,771 |
| `weekly_metrics` | 19,421 |
| `player_rosters` | 25,040 |
| `team_descriptions` | 36 |
| `ngs_passing` | 605 |
| `ngs_rushing` | 648 |
| `ngs_receiving` | 1,402 |
| `weekly_snap_counts` | 26,612 |
| `injury_reports` | 6,068 |
| `depth_charts` | 554,215 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

Phase 29 staging, feature, packet, and compatibility objects remain empty:

| Object | Rows |
| --- | ---: |
| `stg_player_identity` | 0 |
| `stg_game_context` | 0 |
| `stg_player_week_stats` | 0 |
| `stg_team_week_stats` | 0 |
| `stg_play_player_events` | 0 |
| `stg_participation_context` | 0 |
| `player_week_advanced_metrics` | 0 |
| `team_week_context_metrics` | 0 |
| `qb_week_environment_metrics` | 0 |
| `pigskin_player_context_packet_current` | 0 |
| `player_recent_advanced_metrics_current` | 0 |
| `player_role_usage_metrics_current` | 0 |
| `compat_pigskin_player_context_current` | 0 |

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS WITH REVIEW WARNING, 3 passed, 0 failed |
| `stg_` | PASS, 7 passed, 0 failed |
| `advanced_metrics` | PASS, 4 passed, 0 failed |
| `compat_pigskin` | PASS, 2 passed, 0 failed |
| `trade_player_scores` | PASS, 12 passed, 0 failed |
| `trade_pick_scores` | PASS WITH REVIEW WARNING, 17 passed, 0 failed |

Warnings:

- `181_raw_nflverse_season_week_coverage.sql` returned review rows because raw tables now contain a partial 2014 smoke slice.
- `178_trade_pick_scores_model_version_coverage.sql` returned its expected informational model-version review row.

## Final Local Check Results

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_backfill_executor` | PASS, 12 tests |
| `python -m unittest tests.test_nflverse_backfill_plan` | PASS |
| `python -m unittest tests.test_nflverse_historical_contracts` | PASS |
| `python -m unittest tests.test_pigskin_advanced_metrics_contracts` | PASS |
| `python -m unittest discover tests` | PASS |
| `scripts/run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |

## Staging and Production Untouched

Read-only Cloud Run describe confirmed no deployment happened.

Production:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| `USE_TRADE_PICK_SCORE_V0` | unset |
| `USE_COMPAT_TRADE_PICK_SCORE` | unset |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

Staging:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard-staging` |
| Revision | `nfl-studio-dashboard-staging-00029-jtb` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |
| Traffic | `nfl-studio-dashboard-staging-00029-jtb:100` |
| Data Ops trigger flags | `false` |
| Local subprocess flags | `false` |

## Remaining Warnings

- Optional families `ff_playerids`, `rosters`, `rosters_weekly`, and `snap_counts` need source-schema mapping fixes before broad backfill.
- `weekly` skipped 21 rows with missing natural key values.
- The BigQuery pandas helper emitted a future `pandas-gbq` dependency warning.
- This phase wrote only raw tables. No staging or feature tables are ready yet.
- Raw/source tables remain unsafe for Pigskin and UI.
- Phase 29 files remain uncommitted.

## Recommended Next Phase

Phase 29.6A should inspect live source schemas for optional families without broad writes, then update mappings:

- `ff_playerids`: convert wide platform IDs into the contract shape or revise the raw contract.
- `rosters`: map source player identity fields to `player_id` and `gsis_id`.
- `rosters_weekly`: map weekly roster player identity fields and week fields.
- `snap_counts`: map source player ID fields and game/team fields.

After those fixes, run a bounded optional-family repair smoke or an idempotent rerun only with explicit authorization and clear duplicate checks. Keep staging, advanced metrics, and Pigskin packets separate.

