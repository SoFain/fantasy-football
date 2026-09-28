# Phase 29.50 2025 Expansion Commit Report

Final decision: **2025 NFLVERSE PIGSKIN EXPANSION COMMITTED WITH WARNINGS**

## Commit

Created commit:

- `acdb92c Expand nflverse Pigskin packets through 2025`

Latest committed checkpoint before this package:

- `3c83af6 Expand nflverse Pigskin packets through 2024`

The commit included only the approved 2025 evidence package files.

## Files Committed

- `docs/rebuild/validation/phase-29-45-raw-backfill-2025-report.md`
- `docs/rebuild/validation/phase-29-46-staging-materialization-2025-report.md`
- `docs/rebuild/validation/phase-29-47-advanced-metrics-2025-report.md`
- `docs/rebuild/validation/phase-29-48-pigskin-packet-dry-run-2025-report.md`
- `docs/rebuild/validation/phase-29-49-pigskin-packets-2025-report.md`
- `docs/rebuild/validation/phase-29-50-2025-expansion-release-package.md`

Staged review before commit:

- `git diff --cached --name-only`: only the six approved files above.
- `git diff --cached --stat`: 6 files changed, 2,033 insertions.
- `git diff --cached --check`: pass.
- Forbidden staged path scan: no forbidden staged paths detected.

## Files Excluded

Explicitly excluded:

- `docs/rebuild/validation/phase-29-44-2025-current-season-lane-decision-report.md`
- unrelated historical Phase 17-28 backlog
- unrelated Phase 29 reports outside the 2025 package
- source files
- logs
- caches
- local output folders
- temporary JSON
- deployment artifacts
- browser evidence
- secrets or environment files

Post-commit status:

- no staged files
- 98 untracked files remain, consistent with historical validation backlog and owner-review artifacts

## Owner Correction

The Phase 29.44 current-season lane recommendation is superseded for this task. The committed package treats 2025 as a completed historical season for this project and continues the completed-season historical lane.

No current-season lane was created, used, or committed.

## Gate State

All checked authorization gates were empty or unset:

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

## Checks Run

Local checks passed:

- `scripts/check_deployment_safety.py`: pass
- `py_compile src\nflverse_pigskin_packets.py`: pass
- `py_compile src\nflverse_advanced_metrics.py`: pass
- `py_compile src\nflverse_staging.py`: pass
- `py_compile src\nflverse_backfill.py`: pass
- `py_compile src\nflverse_backfill_plan.py`: pass
- `compileall -q src scripts`: pass
- `unittest tests.test_nflverse_pigskin_packets`: pass, 15 tests
- `unittest tests.test_nflverse_advanced_metrics`: pass, 12 tests
- `unittest tests.test_nflverse_staging`: pass, 11 tests
- `unittest tests.test_nflverse_backfill_executor`: pass, 18 tests
- `unittest tests.test_nflverse_backfill_plan`: pass, 15 tests
- `unittest discover tests`: pass, 487 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: catalog discovered through validation 200

## Validation Results

Read-only validation patterns passed:

- `raw_nflverse`: 3 passed, 0 failed, informational coverage review warning
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed, existing informational model-version warning

## Warehouse Read-Only State

Packet state:

- `pigskin_player_context_packet_current`: 4,084 total rows
- `compat_pigskin_player_context_current`: 4,084 total rows
- 2025 packet rows: 510
- target packet-version rows: 510
- 2026+ packet rows: 0
- 2025 duplicate packet grain groups: 0
- missing 2025 packet JSON: 0
- missing 2025 packet text: 0
- missing 2025 source freshness: 0
- missing 2025 blocked metric flags: 0
- 2025 Week 22 packet rows: 17

Packet row counts by season:

| Season | Packet rows |
| --- | ---: |
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
| 2025 | 510 |

Advanced metrics 2025:

- `player_week_advanced_metrics`: 19,399
- `team_week_context_metrics`: 570
- `qb_week_environment_metrics`: 692
- 2026+ feature rows: 0

Staging 2025:

- `stg_player_identity`: 46,831
- `stg_game_context`: 285
- `stg_player_week_stats`: 19,399
- `stg_team_week_stats`: 570
- `stg_play_player_events`: 116,369
- `stg_participation_context`: 26,612
- 2026+ staging rows: 0

Raw 2025:

- `raw_nflverse_schedules`: 285
- `raw_nflverse_rosters`: 3,134
- `raw_nflverse_rosters_weekly`: 46,831
- `raw_nflverse_weekly`: 19,399
- `raw_nflverse_pbp`: 48,771
- `raw_nflverse_snap_counts`: 26,612
- 2026+ raw rows: 0

No BigQuery rows were written in this phase.

## Service Untouched Confirmation

Read-only Cloud Run describes confirmed no deployment occurred in this phase.

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- traffic: `nfl-studio-dashboard-00077-2jp=100`
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- traffic: `nfl-studio-dashboard-staging-00029-jtb=100`
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- staging Trade Analyzer score/history flags remain true from prior staging QA

## Remaining Warnings

- 2025 includes Week 22 historical/postseason packet rows. They must not be presented as current-season content.
- 22 packet rows carry expected packet warnings.
- Known abbreviated display-name collisions remain, including `T.Hill`.
- `stg_participation_context` has 80 documented 2025 identity gaps from PFR-based snap-count matching.
- `raw_nflverse` validation retains the informational 2014-2025 coverage-review warning.
- `trade_pick_scores` validation retains the existing informational model-version warning.
- The historical validation backlog remains untracked by owner decision.

## Recommended Next Phase

Recommended next phase:

- Phase 30.1: post-expansion Pigskin integration/readiness review.
- Or an owner-approved release review for how the completed 2014-2025 packet warehouse should be exposed to Pigskin.
