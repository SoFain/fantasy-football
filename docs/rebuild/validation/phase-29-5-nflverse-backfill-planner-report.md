# Phase 29.5 nflverse Backfill Planner Report

Date: 2026-06-29

Final decision: NFLVERSE BACKFILL PLANNER READY WITH WARNINGS

## Scope

Phase 29.5 added a dry-run-only planner for the Phase 29 nflverse historical warehouse.

No nflverse data was fetched. No nflreadpy loader was called. No local data file was written. No BigQuery row was written. No table was created. No migration was applied. No backfill, weekly refresh, advanced-metric materialization, Pigskin packet refresh, deploy, feature flag change, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scraping, ranking build, or Firebase artifact occurred.

## Authorization Gate State

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

No gate was set in this phase.

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

No files were staged.

Existing uncommitted state before Phase 29.5 remained present:

- modified `docs/rebuild/compatibility-contracts.md`;
- modified `docs/rebuild/table-classification.md`;
- untracked Phase 29.3 migration, contracts, views, validations, docs, and tests;
- untracked Phase 29.1 through 29.4 reports;
- historical Phase 17 through Phase 28 validation backlog.

After Phase 29.5, the worktree also includes the new planner module, planner tests, planner doc, and this report.

## Files Created or Changed

Phase 29.5 created:

- `src/nflverse_backfill_plan.py`
- `tests/test_nflverse_backfill_plan.py`
- `docs/rebuild/nflverse-backfill-planner.md`
- `docs/rebuild/validation/phase-29-5-nflverse-backfill-planner-report.md`

No commit was created.

## Source-Family Registry Summary

The planner registry covers all required Phase 29 source families:

| Source family | Loader metadata | Raw target |
| --- | --- | --- |
| `pbp` | `nflreadpy.load_pbp` | `raw_nflverse_pbp` |
| `weekly` | `nflreadpy.load_player_stats` | `raw_nflverse_weekly` |
| `rosters` | `nflreadpy.load_rosters` | `raw_nflverse_rosters` |
| `rosters_weekly` | `nflreadpy.load_rosters_weekly` | `raw_nflverse_rosters_weekly` |
| `players` | `nflreadpy.load_players` | `raw_nflverse_players` |
| `ff_playerids` | `nflreadpy.load_ff_playerids` | `raw_nflverse_ff_playerids` |
| `schedules` | `nflreadpy.load_schedules` | `raw_nflverse_schedules` |
| `teams` | `nflreadpy.load_teams` | `raw_nflverse_teams` |
| `team_stats` | `nflreadpy.load_team_stats` | `raw_nflverse_team_stats` |
| `injuries` | `nflreadpy.load_injuries` | `raw_nflverse_injuries` |
| `depth_charts` | `nflreadpy.load_depth_charts` | `raw_nflverse_depth_charts` |
| `snap_counts` | `nflreadpy.load_snap_counts` | `raw_nflverse_snap_counts` |
| `participation` | `nflreadpy.load_participation` | `raw_nflverse_participation` |
| `ngs_passing` | `nflreadpy.load_nextgen_stats:passing` | `raw_nflverse_ngs_passing` |
| `ngs_rushing` | `nflreadpy.load_nextgen_stats:rushing` | `raw_nflverse_ngs_rushing` |
| `ngs_receiving` | `nflreadpy.load_nextgen_stats:receiving` | `raw_nflverse_ngs_receiving` |
| `ftn_charting` | `nflreadpy.load_ftn_charting` | `raw_nflverse_ftn_charting` |
| `draft_picks` | `nflreadpy.load_draft_picks` | `raw_nflverse_draft_picks` |

Each source family records:

- source type;
- recommended first backfill season;
- limited range warnings where applicable;
- week-filter support;
- natural key fields;
- partition and clustering fields;
- required metadata fields;
- downstream staging tables;
- post-load validation patterns;
- future authorization gate;
- safety warnings.

The loader values are strings only. The module does not import `nflreadpy`.

## CLI Behavior

Preferred command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2014 --season-end 2025
```

Supported options:

- `--plan-only`
- `--source-family`
- `--all-source-families`
- `--preset`
- `--season-start`
- `--season-end`
- `--week-start`
- `--week-end`
- `--mode historical_backfill|weekly_refresh`
- `--project`
- `--dataset`
- `--output-json`
- `--strict`
- `--skip-bigquery-inspection`

Safety behavior:

- `--plan-only` is required by the CLI in Phase 29.5.
- If invoked without `--plan-only`, the CLI exits with status `2`.
- The fail-closed message names the future required gate and states live execution is not implemented in Phase 29.5.
- `weekly_refresh` mode requires one explicit season plus `--week-start` and `--week-end`.
- Season-level loaders warn that future weekly refresh must load season data and merge only impacted weeks.

## Presets

`core_historical`:

- `schedules`
- `teams`
- `players`
- `ff_playerids`
- `rosters`
- `rosters_weekly`
- `weekly`
- `pbp`
- `snap_counts`

`role_context`:

- `injuries`
- `depth_charts`
- `participation`
- `snap_counts`

`tier2_enrichment`:

- `ngs_passing`
- `ngs_rushing`
- `ngs_receiving`
- `ftn_charting`
- `team_stats`
- `draft_picks`

`all`:

- every registered source family.

## Dry-Run Example Results

All planner examples produced dry-run plans and wrote no data.

| Command | Status | Notes |
| --- | ---: | --- |
| `--plan-only --preset core_historical --season-start 2014 --season-end 2025` | 0 | Planned Tier 1 source families. BigQuery inspection showed target raw tables exist with 0 rows. |
| `--plan-only --preset role_context --season-start 2014 --season-end 2025` | 0 | Included route-source warning for participation and snap-count route-share boundary. |
| `--plan-only --preset tier2_enrichment --season-start 2014 --season-end 2025` | 0 | Included NGS 2016+ and FTN 2022+ limited-range warnings. |
| `--plan-only --preset core_historical --mode weekly_refresh --season-start 2026 --season-end 2026 --week-start 1 --week-end 1` | 0 | Planned week 1 and warned that season-level loaders require future impacted-week merge logic. |

Example observed output for weekly refresh included:

```text
target_weeks: [1]
week_filter_behavior: season-level loader, impacted-week merge required later
future_authorization_gate: ALLOW_NFLVERSE_WEEKLY_REFRESH
```

## Fail-Closed Smoke Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --preset core_historical --season-start 2014 --season-end 2025 --mode historical_backfill
```

Result:

- exit status: `2`;
- no writes;
- no BigQuery mutation;
- no loader call.

Message:

```text
Live execution is not implemented in Phase 29.5. Future execution would require ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true and a separate authorized phase.
```

## BigQuery Inspection Behavior

The planner performs optional read-only BigQuery inspection:

- target table existence;
- table metadata row count;
- season coverage query for season-partitioned tables;
- min/max/distinct week coverage when a `week` column exists;
- capped season coverage rows.

If inspection is unavailable, the planner continues with warnings. `--skip-bigquery-inspection` is available for offline runs.

No raw rows are previewed.

## Tests Added

New test file:

`tests/test_nflverse_backfill_plan.py`

Coverage:

- registry contains all required source families;
- target raw tables, loader names, natural keys, and metadata fields are present;
- no `nflreadpy` import or loader call happens during registry import;
- plan output is dry-run;
- historical plans include target seasons;
- weekly refresh requires week bounds;
- non-plan CLI execution fails closed;
- future gates are documented but not set;
- PBP, weekly, and schedules mappings are correct;
- NGS and FTN limited-range warnings are present;
- participation warns about true route source;
- fake read-only inspector is used without writes;
- no legacy tables are write targets;
- no BigQuery write/create helpers or Cloud Run job calls are present.

## Check Results

All required checks passed.

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m py_compile app.py` | PASS |
| `python -m py_compile src\extract.py` | PASS |
| `python -m py_compile src\pipeline.py` | PASS |
| `python -m py_compile src\load.py` | PASS |
| `python -m py_compile src\transform.py` | PASS |
| `python -m py_compile src\pigskin_context_tools.py` | PASS |
| `python -m py_compile src\llm_context_packets.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `python -m unittest tests.test_nflverse_historical_contracts` | PASS |
| `python -m unittest tests.test_pigskin_advanced_metrics_contracts` | PASS |
| `python -m unittest discover tests` | PASS |
| `scripts/run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS WITH EMPTY-STATE WARNING, 3 passed, 0 failed |
| `stg_` | PASS, 7 passed, 0 failed |
| `advanced_metrics` | PASS, 4 passed, 0 failed |
| `compat_pigskin` | PASS, 2 passed, 0 failed |

The `raw_nflverse` warning is expected:

```text
181_raw_nflverse_season_week_coverage.sql returned review rows because the raw tables exist with 0 rows.
```

## Zero-Row and No-Ingestion Confirmation

Read-only row-count verification covered 31 Phase 29 objects:

- 18 `raw_nflverse_*` tables;
- 6 `stg_*` staging tables;
- 4 base feature or packet tables;
- 3 current or compatibility views.

Result:

```text
total_objects=31
nonzero_objects=0
```

The new warehouse remains empty. No backfill or refresh ran.

## Staging and Production Untouched

Read-only Cloud Run describe confirmed no deployment happened in this phase.

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

- The new Phase 29 warehouse tables are intentionally empty.
- `raw_nflverse` coverage validation reports the empty-state warning until a future authorized backfill writes rows.
- Phase 29.1 through Phase 29.5 evidence and the Phase 29.3 scaffold remain uncommitted.
- Historical Phase 17 through Phase 28 validation backlog remains untracked owner-review material.
- Live backfill, weekly refresh, staging materialization, and Pigskin packet refresh are not implemented in this phase.

## Recommended Next Phase

Phase 29.6 should implement an authorized, bounded, idempotent historical backfill write path only after operator approval.

Recommended guardrails for that phase:

- require `ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true`;
- start with `core_historical` only;
- use explicit season bounds;
- keep raw/source tables out of Pigskin and UI;
- write source metadata and row hashes;
- use idempotent merge or replacement-by-run strategy;
- run `raw_nflverse`, `stg_`, `advanced_metrics`, and `compat_pigskin` validations after writes;
- keep weekly refresh, advanced metric materialization, and Pigskin packet refresh as separate gates.

