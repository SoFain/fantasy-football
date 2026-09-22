# Phase 29.11 Pigskin Current Packet Dry-Run Report

Final decision: **PIGSKIN CURRENT PACKET DRY RUN READY WITH WARNINGS**

Date: 2026-06-29

## Scope

This was a read-only current-view QA and packet dry-run phase. No BigQuery rows were written. No Pigskin packets were written. No feature marts were written. No raw backfill, staging materialization, deployment, feature-flag change, Cloud Run Job trigger, Scheduler job, scrape, Firebase artifact, Pigskin prompt, LLM-backed action, or ranking build occurred.

## Authorization Gate State

Before work, the following gates were empty or unset:

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

No gate was set during this phase.

`--write` was smoke-tested and failed closed with exit code `2`:

```text
Pigskin packet writes are not implemented in Phase 29.11. A separate authorized Phase 29.12 with ALLOW_PIGSKIN_PACKET_REFRESH=true is required.
```

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

No files were staged. Existing Phase 29 files and the historical validation backlog remain untracked or modified for later release packaging.

Files changed in this phase:

- `src/nflverse_pigskin_packets.py`
- `tests/test_nflverse_pigskin_packets.py`
- `docs/rebuild/validation/phase-29-11-pigskin-current-packet-dry-run-report.md`

## Baseline Checks

Baseline checks before packet implementation passed:

- `scripts/check_deployment_safety.py`
- py_compile for `src\nflverse_advanced_metrics.py`
- py_compile for `src\nflverse_staging.py`
- py_compile for `src\nflverse_backfill.py`
- py_compile for `src\nflverse_backfill_plan.py`
- py_compile for `src\pigskin_context_tools.py`
- py_compile for `src\llm_context_packets.py`
- `compileall -q src scripts`
- `tests.test_nflverse_advanced_metrics`
- `tests.test_nflverse_staging`
- `tests.test_pigskin_advanced_metrics_contracts`
- full `unittest discover tests`
- migrations list pending: no pending migrations
- validation dry-run: discovered through validation `200`

## Current-View Behavior

Read-only diagnostics for the current advanced-metric views:

| View | Rows | Season range | Week range | Duplicate grain rows | Missing identity rows | Missing freshness rows | Missing flags rows |
|---|---:|---|---|---:|---:|---:|---:|
| `player_recent_advanced_metrics_current` | 1,854 | 2014 to 2014 | 1 to 21 | 0 | 0 | 0 | 0 |
| `player_role_usage_metrics_current` | 1,854 | 2014 to 2014 | 1 to 21 | 0 | 0 | 0 | 0 |

The current views are derived views over base feature rows. Their nonzero count is expected after Phase 29.10. They were not directly written.

Position distribution is broad and includes non-fantasy positions:

- WR: 206
- RB: 142
- TE: 123
- QB: 74
- DB: 149
- DE: 149
- LB: 118
- several offensive-line, defensive, kicking, punting, and long-snapper rows

Fantasy QB/RB/WR/TE rows: 545. Non-fantasy rows: 1,309.

View null examples from `player_role_usage_metrics_current`:

- WR: 206 rows, 27 null WOPR, 27 null air-yards share, 51 null snap share.
- RB: 142 rows, 16 null WOPR, 16 null air-yards share, 39 null snap share.
- TE: 123 rows, 19 null WOPR, 19 null air-yards share, 32 null snap share.
- QB: 74 rows, 1 null WOPR, 1 null air-yards share, 21 null snap share.
- Defensive and special-teams positions are mostly null for WOPR and air-yards share, which is expected but not useful for the first Pigskin packet class.

## Candidate Player Universe Decision

Initial packet universe:

- QB/RB/WR/TE only.
- Require at least one offensive opportunity or QB sample:
  - `targets > 0`
  - `carries > 0`
  - `weighted_opportunity > 0`
  - `dropbacks > 0`
  - `pass_attempts > 0`

Reason: the current views contain many defensive, offensive-line, kicking, punting, and long-snapper rows. Those rows are valid warehouse outputs but poor first-pass Pigskin evidence packets because opportunity and air-yards fields are mostly null.

Default candidate count from the implemented packet SQL: 482.

By position:

| Position | Candidates | Null WOPR | Null air-yards share | Null snap share | Null EPA/opportunity | Null success rate | Null CPOE | Sample-size warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QB | 73 | 0 | 0 | 21 | 16 | 0 | 2 | 16 |
| RB | 126 | 0 | 0 | 32 | 0 | 0 | 32 | 0 |
| WR | 179 | 0 | 0 | 45 | 0 | 0 | 1 | 0 |
| TE | 104 | 0 | 0 | 26 | 1 | 0 | 0 | 1 |

## Packet Module Behavior

Created `src/nflverse_pigskin_packets.py`.

CLI:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --limit 25
```

Supported options:

- `--dry-run`
- `--plan-only`
- `--season-start`
- `--season-end`
- `--as-of-week`
- repeated `--position` for QB/RB/WR/TE
- `--player-name`
- `--limit`
- `--project`
- `--dataset`
- `--output-json`
- `--strict`

Write behavior:

- Default mode is no-write safe.
- `--write` always fails closed in Phase 29.11.
- Future gate is `ALLOW_PIGSKIN_PACKET_REFRESH`, but even if set, this phase still rejects writes and points to a separate authorized Phase 29.12.

## Packet SQL and Source Dependencies

Packet SQL reads only:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Packet SQL does not read:

- `raw_nflverse_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`
- LLM outputs

The SQL contains no write tokens: no `INSERT`, `MERGE`, `DELETE`, `TRUNCATE`, or `UPDATE`.

## Packet JSON Structure

Dry-run packet previews contain these sections:

- `identity`
- `usage_summary`
- `receiving_air_yards`
- `efficiency_summary`
- `qb_context`
- `team_context`
- `blocked_metrics`
- `source_freshness`
- `warnings`

Blocked metrics preserved in each packet:

- route share
- yards per route run
- targets per route run
- first-read share
- red-zone usage
- high-value touches
- touchdown rates
- reception-flag-dependent metrics
- true pressure
- contact yards
- alignment

Packet text is compact evidence text, not an article.

## Packet Dry-Run Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position QB --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position RB --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position WR --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position TE --limit 25
```

All commands completed successfully and wrote no rows.

Examples from all-position dry-run:

- `C.Newton`, QB, CAR, week 19, no packet warnings.
- `G.Smith`, QB, NYJ, week 17, no packet warnings.
- `M.Sanchez`, QB, PHI, week 17, no packet warnings.

Position examples:

- QB: `C.Newton`, `G.Smith`, `M.Sanchez`.
- RB: `M.Forte`, `S.Vereen`, `C.Anderson`; `S.Vereen` has missing snap share.
- WR: `O.Beckham`, `A.Johnson`, `E.Sanders`; `A.Johnson` has missing snap share.
- TE: `M.Bennett`, `O.Daniels`, `D.Walker`; `O.Daniels` has missing snap share.

## Named-Player Packet Examples

Read-only dry-run lookups:

| Requested player | Found row | Packet usefulness |
|---|---|---|
| Aaron Rodgers | `A.Rodgers`, QB, GB, week 20 | Useful, no packet warnings |
| DeMarco Murray | `D.Murray`, RB, DAL, week 19 | Useful, no packet warnings |
| Antonio Brown | `A.Brown`, WR, PIT, week 18 | Useful, no packet warnings |
| Rob Gronkowski | `R.Gronkowski`, TE, NE, week 21 | Useful, warning: missing snap share |
| Odell Beckham Jr. | `O.Beckham`, WR, NYG, week 17 | Useful, no packet warnings |
| DeAndre Hopkins | `D.Hopkins`, WR, HOU, week 17 | Useful, warning: missing snap share |

The player-name filter supports common full names by matching nflverse initial-plus-last-name forms such as `A.Rodgers` and `D.Murray`.

## Tests Added

Created `tests/test_nflverse_pigskin_packets.py`.

Coverage includes:

- CLI defaults to no write.
- `--write` fails closed.
- `ALLOW_PIGSKIN_PACKET_REFRESH=true` is not sufficient in Phase 29.11.
- Packet SQL reads only safe current/base feature objects.
- Packet SQL does not read raw nflverse or legacy source tables.
- Packet SQL does not read or write Pigskin packet tables in dry-run.
- QB/RB/WR/TE opportunity universe filter exists.
- Packet JSON includes required sections.
- Blocked metric list is included.
- Missing WOPR/air-yards warnings are preserved.
- Named-player filter handles initial-last-name variants.

## Warehouse Unchanged Confirmation

Post-dry-run row counts:

| Object | Rows |
|---|---:|
| `player_week_advanced_metrics` | 17,601 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 643 |
| `player_recent_advanced_metrics_current` | 1,854 |
| `player_role_usage_metrics_current` | 1,854 |
| `pigskin_player_context_packet_current` | 0 |
| `compat_pigskin_player_context_current` | 0 |
| `stg_player_identity` | 30,195 |
| `stg_game_context` | 267 |
| `stg_player_week_stats` | 17,601 |
| `stg_team_week_stats` | 534 |
| `stg_play_player_events` | 116,400 |
| `stg_participation_context` | 23,864 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

Raw nflverse counts remained unchanged, including:

- `raw_nflverse_pbp`: 47,629
- `raw_nflverse_weekly`: 17,601
- `raw_nflverse_rosters_weekly`: 30,195
- `raw_nflverse_snap_counts`: 23,864

## Validation Results

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern raw_nflverse
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern stg_
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern advanced_metrics
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_pigskin
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_pick_scores
```

Results:

- `raw_nflverse`: 3 passed, 0 failed. Informational coverage warning returned 3 rows.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Informational model-version coverage warning returned 1 row.

## Final Local Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_pigskin_packets.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_nflverse_pigskin_packets
.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics
.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging
.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_executor
.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_plan
.\venv\Scripts\python.exe -m unittest tests.test_nflverse_historical_contracts
.\venv\Scripts\python.exe -m unittest tests.test_pigskin_advanced_metrics_contracts
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Safety checker passed.
- Targeted py_compile passed.
- `compileall -q src scripts` passed.
- New packet tests passed: 8 tests.
- Focused nflverse tests passed.
- Full test suite passed: 480 tests.
- Migrations: no pending migrations.
- Validation dry-run passed and discovered through validation `200`.

## Staging And Production Untouched

Read-only Cloud Run describe results:

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Staging Trade History compatibility: true
- Staging Trade Analyzer score flags: true
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false

No deployment occurred.

## Remaining Warnings

- The packet universe should stay QB/RB/WR/TE for the first Pigskin integration. Current views include many valid but not useful non-fantasy rows.
- Current views are derived and return rows automatically. This is acceptable for dry-run, but future packet materialization should explicitly filter the packet universe.
- Snap share is still missing for some useful players.
- QB sack and scramble fields remain unavailable in v0.
- Red-zone, route, first-read, true pressure, contact-yard, touchdown, reception-dependent, and alignment metrics remain blocked.
- Pigskin packet table remains empty until a separate authorized materialization phase.

## Recommended Next Phase

Phase 29.12 should be a separate authorized packet materialization phase, still bounded to 2014 and still defaulting to QB/RB/WR/TE with the opportunity filter. It should write only `pigskin_player_context_packet_current` after a dry-run and should keep `compat_pigskin_player_context_current` as a view over that packet table.

