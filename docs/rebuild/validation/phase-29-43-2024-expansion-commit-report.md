# Phase 29.43 - 2024 nflverse Pigskin Expansion Commit Report

Date: 2026-06-30

Final decision: 2024 NFLVERSE PIGSKIN EXPANSION COMMITTED WITH WARNINGS

## Commit

Commit hash:
- `3c83af6 Expand nflverse Pigskin packets through 2024`

Previous checkpoint:
- `e56afa3 Expand nflverse Pigskin packets through 2023`

Committed files:
- `docs/rebuild/validation/phase-29-38-raw-backfill-2024-report.md`
- `docs/rebuild/validation/phase-29-39-staging-materialization-2024-report.md`
- `docs/rebuild/validation/phase-29-40-advanced-metrics-2024-report.md`
- `docs/rebuild/validation/phase-29-41-pigskin-packet-dry-run-2024-report.md`
- `docs/rebuild/validation/phase-29-42-pigskin-packets-2024-report.md`
- `docs/rebuild/validation/phase-29-43-2024-expansion-release-package.md`

Commit summary:
- 6 files changed
- 1,816 insertions
- No source files committed
- No generated output, logs, caches, browser evidence, env files, secrets, temporary JSON, or deployment artifacts committed

## Files Excluded

Excluded from the commit:
- Historical Phase 17 through Phase 28 validation backlog
- Superseded or non-package Phase 29 evidence
- `output/`
- `output/playwright/`
- local browser evidence
- temporary JSON files
- logs and caches
- `.env` and `.env.*`
- secret JSON files
- deployment artifacts

Post-commit untracked count before this report was created: 96. Those files remained intentionally untracked owner-review backlog files.

## Gate State

Confirmed unset before packaging and after the Phase 29.42 write:
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

No authorization gate was set in this packaging phase.

## Test Results

Pre-commit checks passed:
- `scripts/check_deployment_safety.py`
- `py_compile` for `src/nflverse_pigskin_packets.py`
- `py_compile` for `src/nflverse_advanced_metrics.py`
- `py_compile` for `src/nflverse_staging.py`
- `py_compile` for `src/nflverse_backfill.py`
- `py_compile` for `src/nflverse_backfill_plan.py`
- `compileall -q src scripts`
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `tests.test_nflverse_staging`: 11 tests passed
- `tests.test_nflverse_backfill_executor`: 18 tests passed
- `tests.test_nflverse_backfill_plan`: 15 tests passed
- `unittest discover tests`: 487 tests passed

Migration and validation discovery:
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: validation catalog discovered through `200`

## Validation Results

Read-only validation patterns:
- `raw_nflverse`: 3 passed, 0 failed, one informational coverage warning
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed, one informational model-version coverage warning

## Warehouse State

Read-only packet confirmation:
- `pigskin_player_context_packet_current`: 3,574 total rows
- `compat_pigskin_player_context_current`: 3,574 total rows
- 2024 packet rows: 492
- Target packet version `nflverse_pigskin_packet_v0_2024_001`: 492 rows
- 2025/future packet rows: 0
- 2024 duplicate packet grain count: 0
- 2024 missing packet JSON: 0
- 2024 missing packet text: 0
- 2024 missing source freshness: 0
- 2024 missing blocked metric flags: 0

Packet rows by season:

| Season | Rows |
|---:|---:|
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |
| 2018 | 111 |
| 2019 | 113 |
| 2020 | 525 |
| 2021 | 107 |
| 2022 | 131 |
| 2023 | 508 |
| 2024 | 492 |

2024 raw rows:
- `raw_nflverse_schedules`: 285
- `raw_nflverse_rosters`: 3,215
- `raw_nflverse_rosters_weekly`: 46,572
- `raw_nflverse_weekly`: 18,959
- `raw_nflverse_pbp`: 49,492
- `raw_nflverse_snap_counts`: 26,615

2024 staging rows:
- `stg_player_identity`: 46,572
- `stg_game_context`: 285
- `stg_player_week_stats`: 18,959
- `stg_team_week_stats`: 570
- `stg_play_player_events`: 118,037
- `stg_participation_context`: 26,615

2024 advanced metrics rows:
- `player_week_advanced_metrics`: 18,959
- `team_week_context_metrics`: 570
- `qb_week_environment_metrics`: 707

2025/future raw, staging, advanced metrics, and packet counts were 0 in the requested confirmation.

## Service State

Production readback:
- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Risk flags false
- Trade Analyzer score flags false
- Data Ops Cloud Run trigger flags false
- Data Ops local subprocess flags false

Staging readback:
- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Job trigger flags false
- Local subprocess flags false

No deployment occurred.

## Remaining Warnings

- Historical untracked validation backlog remains intentionally excluded from this package.
- `raw_nflverse` validation includes an informational coverage review warning.
- `trade_pick_scores` validation includes an informational model-version coverage warning.
- 2024 packets include postseason Week 22 historical rows. Do not present them as current-season content.
- Display-name ambiguity remains explicit and requires disambiguation for exact player targeting.
- Blocked metrics remain disclosed, not inferred.

## Recommended Next Phase

Phase 29.44: decide whether 2025/current-season work belongs in Phase 29 or should start a separate current-season lane.
