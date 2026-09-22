# Phase 29.13 Pigskin Canary Release Commit Report

Date: 2026-06-29

Phase 29.13B reviewed this package after the commit was already present at HEAD. No second package commit was created because the reviewed Phase 29 package files were already committed in `480561014be3947834d1cd528dd551ff5e476e1f`, and no Phase 29 package files remained modified or staged.

Final decision: PIGSKIN NFLVERSE CANARY COMMITTED WITH WARNINGS

## Commit

- Commit: `480561014be3947834d1cd528dd551ff5e476e1f`
- Short hash: `4805610`
- Message: `Build nflverse Pigskin canary pipeline`
- Branch: `codex/phase-14-validation-footer`
- Phase 29.13B commit action: no-op, package already committed as latest HEAD

Commit body recorded:

- raw nflverse warehouse contracts and migration 0027;
- raw backfill planner/executor, staging transforms, advanced metrics, and Pigskin packet builders;
- 2014 canary materialized through the Pigskin packet table with unsafe metrics blocked or null;
- no production deployment.

## Files Committed

Summary:

- 89 files committed.
- 14,846 insertions.
- No generated output, logs, env files, caches, secret files, browser evidence, deployment artifacts, or historical Phase 17 through 28 backlog reports were committed.

Committed groups:

- Source modules:
  - `src/nflverse_backfill_plan.py`
  - `src/nflverse_backfill.py`
  - `src/nflverse_staging.py`
  - `src/nflverse_advanced_metrics.py`
  - `src/nflverse_pigskin_packets.py`
- Tests:
  - `tests/test_nflverse_backfill_plan.py`
  - `tests/test_nflverse_backfill_executor.py`
  - `tests/test_nflverse_staging.py`
  - `tests/test_nflverse_advanced_metrics.py`
  - `tests/test_nflverse_pigskin_packets.py`
  - `tests/test_nflverse_historical_contracts.py`
  - `tests/test_pigskin_advanced_metrics_contracts.py`
- Migration:
  - `bigquery/migrations/0027__nflverse_historical_feature_warehouse.sql`
- Contracts:
  - `raw_nflverse_*`
  - `stg_*`
  - advanced metric contracts
  - Pigskin packet and compat contracts
- Views:
  - `player_recent_advanced_metrics_current.sql`
  - `player_role_usage_metrics_current.sql`
  - `compat_pigskin_player_context_current.sql`
- Validations:
  - `179_raw_nflverse_tables_exist.sql` through `200_no_pressure_metrics_without_source.sql`
- Documentation:
  - `docs/rebuild/nflverse-backfill-planner.md`
  - `docs/rebuild/nflverse-historical-backfill-plan.md`
  - `docs/rebuild/pigskin-advanced-metrics-warehouse.md`
  - `docs/rebuild/compatibility-contracts.md`
  - `docs/rebuild/table-classification.md`
  - Phase 29 reports 29.1 through 29.12
  - `phase-29-13-pigskin-canary-release-package.md`

## Excluded Files

Remaining untracked file count after commit: 91.

The remaining files are historical validation backlog and owner-review evidence from Phases 17 through 28, including older production, staging, score, and release reports. They were intentionally left untracked because Phase 29.13 is scoped to the 2014 nflverse Pigskin canary package.

Excluded categories:

- historical Phase 17 through 28 validation reports;
- local/generated artifacts if present in the broader worktree;
- logs;
- env files;
- cache files;
- secret-looking files;
- browser evidence;
- deployment artifacts.

## Gate State

All checked authorization gates were empty or unset before packaging:

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

No gate was set during Phase 29.13.

## Checks Run

Phase 29.13 and Phase 29.13B checks:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile` for nflverse backfill, staging, advanced metrics, and packet modules | PASS |
| `compileall -q src scripts` | PASS |
| Targeted nflverse and Pigskin tests | 75 passed |
| Full test discovery | 482 passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | validation catalog discovers through 200 |

No materialization, ingestion, Cloud Run Job, deployment, scraping, LLM-backed action, Pigskin prompt, rankings build, Scheduler job, or Firebase action was run.

## Read-Only Warehouse State

Pigskin and advanced metric objects:

| Object | Rows |
| --- | ---: |
| `pigskin_player_context_packet_current` | 482 |
| `compat_pigskin_player_context_current` | 482 |
| `player_week_advanced_metrics` | 17,601 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 643 |
| `player_recent_advanced_metrics_current` | 1,854 |
| `player_role_usage_metrics_current` | 1,854 |

Staging objects:

| Object | Rows |
| --- | ---: |
| `stg_game_context` | 267 |
| `stg_participation_context` | 23,864 |
| `stg_play_player_events` | 116,400 |
| `stg_player_identity` | 30,195 |
| `stg_player_week_stats` | 17,601 |
| `stg_team_week_stats` | 534 |

Raw nflverse objects:

| Object | Rows |
| --- | ---: |
| `raw_nflverse_pbp` | 47,629 |
| `raw_nflverse_weekly` | 17,601 |
| `raw_nflverse_rosters` | 2,152 |
| `raw_nflverse_rosters_weekly` | 30,195 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |
| `raw_nflverse_schedules` | 267 |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_snap_counts` | 23,864 |
| `raw_nflverse_depth_charts` | 0 |
| `raw_nflverse_draft_picks` | 0 |
| `raw_nflverse_ftn_charting` | 0 |
| `raw_nflverse_injuries` | 0 |
| `raw_nflverse_ngs_passing` | 0 |
| `raw_nflverse_ngs_receiving` | 0 |
| `raw_nflverse_ngs_rushing` | 0 |
| `raw_nflverse_participation` | 0 |
| `raw_nflverse_team_stats` | 0 |

Zero-row optional raw families are preserved as explicit empty-state objects. They are not presented as available metric sources.

## Service State

Read-only Cloud Run describe confirmed services were untouched.

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp=100`

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: `nfl-studio-dashboard-staging-00029-jtb=100`

## Remaining Warnings

- This is a 2014 canary foundation, not a current-season content rollout.
- Some Pigskin packet rows carry expected missing-data warnings.
- Route share, yards per route run, first-read share, red-zone usage, true pressure, contact yards, and alignment metrics remain blocked or null until true sources are verified.
- Raw nflverse coverage validation is informational by design.
- Historical validation backlog from Phases 17 through 28 remains untracked for owner review.
- Git emitted LF-to-CRLF working-copy warnings while staging markdown and SQL files. The commit succeeded.

## Recommended Next Phase

Phase 29.14: authorized historical expansion planner for 2015 through 2025 batches.

Recommended constraints:

- planner-first;
- bounded season batches;
- explicit authorization gates for live backfill or materialization;
- no raw/source dependency in Pigskin-facing views;
- keep unsafe metrics blocked until source proof exists.
