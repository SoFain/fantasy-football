# Phase 29.6B: nflverse Optional Raw Repair Smoke Report

Date: 2026-06-29

## Final Decision

**NFLVERSE OPTIONAL RAW REPAIR SMOKE READY WITH WARNINGS**

The authorized bounded repair smoke wrote only the four approved optional 2014 raw nflverse source families:

- `raw_nflverse_ff_playerids`
- `raw_nflverse_rosters`
- `raw_nflverse_rosters_weekly`
- `raw_nflverse_snap_counts`

No core raw families were rewritten. No legacy tables, staging tables, feature marts, Pigskin packet objects, score lanes, Cloud Run services, Scheduler jobs, or feature flags were touched.

## Authorization Gate State

Before the write, all relevant gates were unset:

| Gate | Before | During repair smoke | After |
| --- | --- | --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset | `true` inside the same PowerShell wrapper | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset | unset | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset | unset | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset | unset | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset | unset | unset |

The executor JSON reports `gate_removed=false` because the Python process exits before the PowerShell `finally` block runs. The follow-up shell check confirmed the environment variable was removed.

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

Phase 29 working tree state remains uncommitted and untracked, including the Phase 29 contracts, migration, validations, planner, executor, tests, and reports. No files were staged or committed in this phase.

Existing modified tracked docs:

- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/table-classification.md`

Relevant untracked Phase 29 files include:

- `src/nflverse_backfill.py`
- `src/nflverse_backfill_plan.py`
- `tests/test_nflverse_backfill_executor.py`
- `tests/test_nflverse_backfill_plan.py`
- `tests/test_nflverse_historical_contracts.py`
- `tests/test_pigskin_advanced_metrics_contracts.py`
- `docs/rebuild/validation/phase-29-6a-nflverse-optional-schema-mapping-report.md`
- this report

Historical validation backlog files remain untracked.

## Baseline Checks

Before the live repair smoke:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_historical_contracts` | PASS, 5 tests |
| `unittest tests.test_pigskin_advanced_metrics_contracts` | PASS, 4 tests |
| `unittest discover tests` | PASS, 449 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | PASS, 200 validations discovered |

## Dry-Run Planner

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --source-family ff_playerids --source-family rosters --source-family rosters_weekly --source-family snap_counts --season-start 2014 --season-end 2014
```

Result:

- `dry_run: True`
- selected families: `ff_playerids`, `rosters`, `rosters_weekly`, `snap_counts`
- target tables: the four approved `raw_nflverse_*` optional targets
- no nflverse loaders called
- no BigQuery rows written

Planner warnings were expected:

- raw `raw_nflverse_*` tables are not Pigskin or UI safe surfaces
- `rosters_weekly` is a season-level loader with week rows
- `snap_counts` can support snap share, but route share still needs a true route source

## Executor Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --source-family ff_playerids --source-family rosters --source-family rosters_weekly --source-family snap_counts --season-start 2014 --season-end 2014 --dry-run
```

Result:

- `dry_run=true`
- `wrote=false`
- source families attempted: `ff_playerids`, `rosters`, `rosters_weekly`, `snap_counts`
- no BigQuery rows written

## Prepare-Only Proof

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --source-family ff_playerids --source-family rosters --source-family rosters_weekly --source-family snap_counts --season-start 2014 --season-end 2014 --prepare-only
```

Result:

| Family | Fetched | Prepared | Skipped | Warning Summary |
| --- | ---: | ---: | ---: | --- |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | 9,641 rows missing `nflverse_player_id`; 45 duplicate natural-key rows deduped. |
| `rosters` | 2,153 | 2,152 | 1 | 1 row missing `player_id`. |
| `rosters_weekly` | 31,964 | 30,195 | 1,769 | 1 row missing `player_id`; 1,768 duplicate natural-key rows deduped. |
| `snap_counts` | 23,864 | 23,864 | 0 | None. |

No family prepared 0 rows.

## Pre-Repair Row Counts

Before the authorized write:

| Table | Total Rows | 2014 Rows |
| --- | ---: | ---: |
| `raw_nflverse_ff_playerids` | 0 | 0 |
| `raw_nflverse_rosters` | 0 | 0 |
| `raw_nflverse_rosters_weekly` | 0 | 0 |
| `raw_nflverse_snap_counts` | 0 | 0 |
| `raw_nflverse_schedules` | 267 | 267 |
| `raw_nflverse_teams` | 36 | 0, static table |
| `raw_nflverse_players` | 25,033 | 0, static table |
| `raw_nflverse_weekly` | 17,601 | 17,601 |
| `raw_nflverse_pbp` | 47,629 | 47,629 |

Phase 29 staging tables, feature marts, Pigskin packet objects, and compatibility Pigskin views were all 0 rows.

## Live Repair Command

Command:

```powershell
try {
$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"

echo "ALLOW_NFLVERSE_HISTORICAL_BACKFILL=$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL"

.\venv\Scripts\python.exe -m src.nflverse_backfill --source-family ff_playerids --source-family rosters --source-family rosters_weekly --source-family snap_counts --season-start 2014 --season-end 2014 --write --strict

} finally {
Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
}
```

Result:

- `wrote=true`
- `dry_run=false`
- elapsed seconds: `79.801`
- `source_refresh_id`: `nflverse_source_family_2014_2014_20260629T151833Z`
- succeeded families: `ff_playerids`, `rosters`, `rosters_weekly`, `snap_counts`
- failed families: none
- critical failures: none

Live write summary:

| Family | Fetched | Prepared | Written or Merged | Target Rows After | Duplicate Key Groups After |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ff_playerids` | 12,465 | 69,060 | 69,060 | 69,060 | 0 |
| `rosters` | 2,153 | 2,152 | 2,152 | 2,152 | 0 |
| `rosters_weekly` | 31,964 | 30,195 | 30,195 | 30,195 | 0 |
| `snap_counts` | 23,864 | 23,864 | 23,864 | 23,864 | 0 |

## Post-Repair Raw Table Verification

| Table | Total Rows | 2014 Rows | Season Range | Week Range | Metadata Populated | Duplicate Key Groups |
| --- | ---: | ---: | --- | --- | --- | ---: |
| `raw_nflverse_ff_playerids` | 69,060 | 0, static snapshot | none | none | `source_refresh_id`, `loaded_at`, `row_hash`, `source_version`: 69,060 each | 0 |
| `raw_nflverse_rosters` | 2,152 | 2,152 | 2014 to 2014 | 1 to 21 | `source_refresh_id`, `loaded_at`, `row_hash`, `source_version`: 2,152 each | 0 |
| `raw_nflverse_rosters_weekly` | 30,195 | 30,195 | 2014 to 2014 | 1 to 21 | `source_refresh_id`, `loaded_at`, `row_hash`, `source_version`: 30,195 each | 0 |
| `raw_nflverse_snap_counts` | 23,864 | 23,864 | 2014 to 2014 | 1 to 21 | `source_refresh_id`, `loaded_at`, `row_hash`, `source_version`: 23,864 each | 0 |

Source loader distribution:

| Table | Source Loader | Rows |
| --- | --- | ---: |
| `raw_nflverse_ff_playerids` | `nflreadpy.load_ff_playerids` | 69,060 |
| `raw_nflverse_rosters` | `nflreadpy.load_rosters` | 2,152 |
| `raw_nflverse_rosters_weekly` | `nflreadpy.load_rosters_weekly` | 30,195 |
| `raw_nflverse_snap_counts` | `nflreadpy.load_snap_counts` | 23,864 |

Source version:

- all four repaired tables show `source_version=0.1.5`

## Non-Target Object Verification

Core raw tables remained unchanged:

| Table | Total Rows | 2014 Rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 267 |
| `raw_nflverse_teams` | 36 | 0, static table |
| `raw_nflverse_players` | 25,033 | 0, static table |
| `raw_nflverse_weekly` | 17,601 | 17,601 |
| `raw_nflverse_pbp` | 47,629 | 47,629 |

Phase 29 staging and feature objects remained empty:

- `stg_player_identity`: 0
- `stg_game_context`: 0
- `stg_player_week_stats`: 0
- `stg_team_week_stats`: 0
- `stg_play_player_events`: 0
- `stg_participation_context`: 0
- `player_week_advanced_metrics`: 0
- `team_week_context_metrics`: 0
- `qb_week_environment_metrics`: 0
- `pigskin_player_context_packet_current`: 0
- `compat_pigskin_player_context_current`: 0

Score lanes remained unchanged:

- `trade_player_scores`: 154 total, 0 rows for 2014.
- `trade_pick_scores`: 64 total.

Legacy source tables were read-only in this phase:

| Table | Total Rows | 2014 Rows |
| --- | ---: | ---: |
| `play_by_play` | 48,771 | 0 |
| `weekly_metrics` | 19,421 | 0 |
| `player_rosters` | 25,040 | 0 |
| `team_descriptions` | 36 | 0 |
| `ngs_passing` | 605 | 0 |
| `ngs_rushing` | 648 | 0 |
| `ngs_receiving` | 1,402 | 0 |
| `weekly_snap_counts` | 26,612 | 0 |
| `injury_reports` | 6,068 | 0 |
| `depth_charts` | 554,215 | 0 |

## Validation Results After Repair Smoke

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Known partial-coverage review warning remains. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Informational model-version coverage warning remains. |

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_historical_contracts` | PASS, 5 tests |
| `unittest tests.test_pigskin_advanced_metrics_contracts` | PASS, 4 tests |
| `unittest discover tests` | PASS, 449 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |

## Staging and Production Untouched

Read-only Cloud Run describe results:

| Service | Revision | Image | Traffic | Flag State |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | `00077-2jp:100` | Trade score false, trade history compat false, Cloud Run Job flags false, local subprocess flags false. |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | `00029-jtb:100` | Staging score and trade history flags remain true from prior QA; Cloud Run Job and local subprocess trigger flags false. |

No deployment occurred.

## Remaining Warnings

- `raw_nflverse` coverage still warns because this warehouse has only a bounded 2014 smoke, not a complete historical backfill.
- `trade_pick_scores` validation `178` remains an informational model-version coverage warning from prior authorized pick-score work.
- The live BigQuery dataframe load emitted a `pandas-gbq` future dependency warning. It did not block the load.
- `snap_counts` uses `pfr_player_id` as the raw player key because the nflverse 2014 snap-count source does not provide GSIS IDs in this loader output.

## Recommended Next Phase

Run a separate Phase 29.7 planning step before any staging or feature-mart materialization.

Recommended scope:

- verify whether `stg_player_identity` can safely bridge `raw_nflverse_ff_playerids`, `raw_nflverse_rosters`, and `raw_nflverse_snap_counts`
- plan staging materialization only, no Pigskin packets yet
- keep advanced metrics and Pigskin context marts blocked until staging row counts and identity coverage are proven

