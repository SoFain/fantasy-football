# Phase 29.7: nflverse Staging Dry-Run Report

Date: 2026-06-29

## Final Decision

**NFLVERSE STAGING DRY RUN READY WITH WARNINGS**

The first canonical 2014 nflverse staging layer is ready for a separate, bounded, authorized staging materialization phase. This phase did not write BigQuery rows.

Main warnings:

- `stg_player_week_stats`, `stg_play_player_events`, and `stg_participation_context` have quantified identity-match gaps.
- 2014 snap counts use PFR IDs. The dry-run joins those cautiously through PFR values stored in raw payloads.
- `route_share` remains null and `has_true_route_source` remains false.
- red-zone, inside-10, inside-5, reception, and touchdown event counts are currently 0 from the raw smoke schema or raw payload fields available in this slice.

## Authorization Gate State

No authorization gates were set.

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
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |

Write attempt smoke:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --write
```

Result:

- exit code: 2
- message: `staging writes are not implemented in Phase 29.7. ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true is reserved for a separate authorized Phase 29.8.`

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

Phase 29 source and warehouse scaffold remains uncommitted and untracked. Existing modified tracked files remain:

- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/table-classification.md`

New files from this phase:

- `src/nflverse_staging.py`
- `tests/test_nflverse_staging.py`
- `docs/rebuild/validation/phase-29-7-nflverse-staging-dry-run-report.md`

No files were staged or committed.

## Baseline Checks

Before implementation:

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

## Staging Module Behavior

Created `src/nflverse_staging.py`.

CLI supports:

- `--dry-run`
- `--plan-only`
- `--target`
- `--all-targets`
- `--season-start`
- `--season-end`
- `--week-start`
- `--week-end`
- `--project`
- `--dataset`
- `--output-json`
- `--strict`
- `--write`, which fails closed in Phase 29.7

Default behavior:

- no writes
- all six staging targets selected when no target is supplied
- read-only diagnostics run against BigQuery
- JSON summary includes generated SQL, row counts, duplicate checks, warnings, and write-readiness recommendation

Future gate name:

- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`

The gate is documented only. It does not authorize writes in Phase 29.7.

## SQL and Source Design Summary

| Target | Sources | Grain | Write Readiness |
| --- | --- | --- | --- |
| `stg_player_identity` | `raw_nflverse_players`, `raw_nflverse_ff_playerids`, `raw_nflverse_rosters_weekly` | `player_id_internal`, `season`, `week`, `team` | ready with warnings |
| `stg_game_context` | `raw_nflverse_schedules` | `season`, `week`, `game_id` | ready |
| `stg_player_week_stats` | `raw_nflverse_weekly`, identity dry-run CTE, `raw_nflverse_rosters_weekly` | `season`, `week`, `player_id_internal`, `team` | ready with warnings |
| `stg_team_week_stats` | `raw_nflverse_pbp`, schedule context | `season`, `week`, `team` | ready with warnings |
| `stg_play_player_events` | `raw_nflverse_pbp`, identity dry-run CTE | `season`, `week`, `game_id`, `play_id`, `event_type`, `player_id_internal`, `team` | ready with warnings |
| `stg_participation_context` | `raw_nflverse_snap_counts`, identity dry-run CTE | `season`, `week`, `game_id`, `player_id_internal`, `team` | ready with warnings |

Safety checks in generated SQL:

- no `play_by_play`
- no `weekly_metrics`
- no legacy `player_rosters`
- no feature marts
- no `INSERT`, `MERGE`, or `DELETE`
- no Pigskin packet source
- no name-only player identity joins

## Dry-Run Commands

All targets:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --all-targets
```

Each target individually:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --target stg_player_identity
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --target stg_game_context
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --target stg_player_week_stats
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --target stg_team_week_stats
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --target stg_play_player_events
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2014 --season-end 2014 --dry-run --target stg_participation_context
```

## Per-Target Diagnostics

| Target | Planned Rows | Source Rows | Duplicate Key Groups | Missing Identity Rows | Readiness |
| --- | ---: | ---: | ---: | ---: | --- |
| `stg_player_identity` | 30,195 | source mix | 0 | 0 ambiguous identities | ready with warnings |
| `stg_game_context` | 267 | 267 | 0 | n/a | ready |
| `stg_player_week_stats` | 17,601 | 17,601 | 0 | 3,818 | ready with warnings |
| `stg_team_week_stats` | 534 | 47,629 plays | 0 | n/a | ready with warnings |
| `stg_play_player_events` | 116,400 | 47,629 plays | 0 | 14,991 | ready with warnings |
| `stg_participation_context` | 23,864 | 23,864 | 0 | 3,818 | ready with warnings |

### `stg_player_identity`

Diagnostics:

- planned rows: 30,195
- unique raw players: 25,033
- unique GSIS IDs: 25,033
- unique PFR IDs: 22,554
- unique Sleeper IDs: 6,147
- raw roster IDs: 2,053
- weekly roster IDs: 2,053
- missing position count: 0
- missing team count: 0
- high-confidence rows: 30,195
- lower-confidence rows: 0
- ambiguous identity count: 0
- duplicate key groups: 0

Design choice:

- identity rows come from weekly roster player IDs and are enriched from raw player and fantasy ID bridges
- name-only joins are not used

### `stg_game_context`

Diagnostics:

- planned rows: 267
- source rows: 267
- duplicate game keys: 0
- missing home or away team: 0
- missing game date: 0
- missing stadium: 0
- missing roof: 0
- missing surface: 0
- missing total line: 0
- missing spread line: 0

### `stg_player_week_stats`

Diagnostics:

- planned rows: 17,601
- source weekly rows: 17,601
- missing identity matches: 3,818
- duplicate player-week-team keys: 0
- missing team: 0
- missing position: 0
- fantasy/stat input rows: 17,601
- postseason or playoff week rows: 455

Boundary:

- uses `raw_nflverse_weekly`
- does not use legacy `weekly_metrics`

### `stg_team_week_stats`

Diagnostics:

- planned rows: 534
- source play rows: 47,629
- offense play count: 45,267
- pass attempts: 19,897
- rush attempts: 13,867
- team targets: 18,446
- team air yards: 156,322
- EPA total: -918.8756254369767
- average success rate: 0.432971254280069
- neutral script rows: 526
- red-zone rows: 0
- opponent defensive rows: 534
- duplicate team-week keys: 0

Warning:

- `pass_rate_over_expected` remains null until a model source exists

### `stg_play_player_events`

Diagnostics:

- planned rows: 116,400
- source play rows: 47,629
- duplicate event keys: 0
- missing identity matches: 14,991
- passer event rows: 19,973
- receiver event rows: 18,446
- rusher event rows: 14,272
- target event rows: 18,442
- reception event rows: 0
- touchdown event rows: 0
- EPA non-null rows: 116,125
- success non-null rows: 116,125
- red-zone event rows: 0
- inside-10 event rows: 0
- inside-5 event rows: 0

Warning:

- event expansion is viable, but touchdown, reception, and red-zone flags need source-field review before advanced metric materialization
- no route metrics are created here

### `stg_participation_context`

Diagnostics:

- planned rows: 23,864
- source snap rows: 23,864
- rows with PFR ID: 23,864
- rows matched by PFR ID: 20,046
- rows unmatched by PFR ID: 3,818
- missing identity matches: 3,818
- duplicate player-game keys: 0
- offense percentage rows: 23,864
- offense pct range: 0.0 to 1.0
- offense snaps range: 0.0 to 92.0
- route share non-null rows: 0
- true route source rows: 0

Route rule:

- `route_share` stays null
- `has_true_route_source` stays false
- snap share is not treated as route share

## Tests Added

Created `tests/test_nflverse_staging.py`.

Coverage:

- CLI defaults to no write
- `--write` fails closed
- future gate name does not authorize writes in Phase 29.7
- all six staging targets are registered
- generated SQL reads only `raw_nflverse_*` and approved identity CTE sources
- generated SQL does not read legacy source tables or feature marts
- generated SQL does not contain write operations
- participation keeps `route_share` null and `has_true_route_source` false
- snap participation uses PFR ID cautiously
- player identity does not force ambiguous name-only joins
- dry-run output contains row counts and warnings

## Warehouse Unchanged Confirmation

Raw source counts remained unchanged from Phase 29.6B:

| Table | Total Rows | 2014 Rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 267 |
| `raw_nflverse_teams` | 36 | 0, static table |
| `raw_nflverse_players` | 25,033 | 0, static table |
| `raw_nflverse_ff_playerids` | 69,060 | 0, static snapshot |
| `raw_nflverse_rosters` | 2,152 | 2,152 |
| `raw_nflverse_rosters_weekly` | 30,195 | 30,195 |
| `raw_nflverse_weekly` | 17,601 | 17,601 |
| `raw_nflverse_pbp` | 47,629 | 47,629 |
| `raw_nflverse_snap_counts` | 23,864 | 23,864 |

All staging and feature objects remained empty:

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

- `trade_player_scores`: 154 rows
- `trade_pick_scores`: 64 rows

Legacy source tables were read-only and unchanged.

## Validation Results

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
| `py_compile src\nflverse_staging.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_staging` | PASS, 9 tests |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_historical_contracts` | PASS, 5 tests |
| `unittest tests.test_pigskin_advanced_metrics_contracts` | PASS, 4 tests |
| `unittest discover tests` | PASS, 458 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | PASS, 200 validations discovered |

## Staging and Production Untouched

Read-only Cloud Run describe results:

| Service | Revision | Image | Traffic | Flag State |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | `00077-2jp:100` | Trade score false, trade history compat false, Cloud Run Job flags false, local subprocess flags false. |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | `00029-jtb:100` | Staging score and trade history flags remain true from prior QA; Cloud Run Job and local subprocess trigger flags false. |

No deployment occurred.

## Recommended Next Phase

Run Phase 29.8 only if staging materialization is explicitly authorized.

Recommended Phase 29.8 boundary:

- set `ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true` only inside a same-session wrapper
- write only the six 2014 `stg_*` tables
- do not build advanced metrics yet
- do not refresh Pigskin packets
- quantify the same identity gaps after write
- keep route metrics blocked until a true route source exists

