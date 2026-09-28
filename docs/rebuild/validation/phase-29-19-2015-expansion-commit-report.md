# Phase 29.19 - 2015 nflverse Pigskin Expansion Commit Report

Date: 2026-06-29

Final decision: 2015 NFLVERSE PIGSKIN EXPANSION COMMITTED WITH WARNINGS

## Commit

Commit created:

`67f37e7 Expand nflverse Pigskin pipeline to 2015`

Base checkpoint before commit:

`4805610 Build nflverse Pigskin canary pipeline`

No deployment, rollback, feature flag change, BigQuery write, materialization, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scrape, Firebase artifact, or ranking build occurred in this packaging phase.

## Files Committed

Committed files:

- `src/nflverse_pigskin_packets.py`
- `tests/test_nflverse_pigskin_packets.py`
- `docs/rebuild/validation/phase-29-14-historical-expansion-planner-report.md`
- `docs/rebuild/validation/phase-29-15-raw-backfill-2015-report.md`
- `docs/rebuild/validation/phase-29-16-staging-materialization-2015-report.md`
- `docs/rebuild/validation/phase-29-17-advanced-metrics-2015-report.md`
- `docs/rebuild/validation/phase-29-18-pigskin-packets-2015-report.md`
- `docs/rebuild/validation/phase-29-19-2015-expansion-release-package.md`

Commit scope:

- Added 2015 expansion evidence from planner through Pigskin packet materialization.
- Fixed Pigskin packet text season labeling to use dynamic `as_of_season`.
- Preserved blocked metric handling.
- Documented no production deployment.

## Files Excluded

Excluded from the commit:

- Historical Phase 17 through Phase 28 validation backlog.
- Phase 29 reports outside the approved 2015 checkpoint package.
- Local browser evidence.
- `output/`.
- Logs.
- Caches.
- Env files.
- Secret JSON files.
- Deployment artifacts.

Remaining untracked files are historical validation reports and owner-review artifacts.

## Authorization Gate State

All checked gates were unset after the commit:

| Gate | Final State |
| --- | --- |
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

## Checks Run

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_pigskin_packets.py` | PASS |
| `python -m py_compile src\nflverse_advanced_metrics.py` | PASS |
| `python -m py_compile src\nflverse_staging.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_pigskin_packets` | 11 tests passed |
| `python -m unittest tests.test_nflverse_advanced_metrics` | 12 tests passed |
| `python -m unittest tests.test_nflverse_staging` | 11 tests passed |
| `python -m unittest tests.test_nflverse_backfill_executor` | 18 tests passed |
| `python -m unittest tests.test_nflverse_backfill_plan` | 15 tests passed |
| `python -m unittest discover tests` | 483 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

PowerShell displayed `NativeCommandError` wrappers for stderr logging during some Python test commands, but process exit codes were 0 and test summaries were PASS.

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Informational 2014-2015 coverage warning remained. |
| `stg_` | 7 passed, 0 failed |
| `advanced_metrics` | 4 passed, 0 failed |
| `compat_pigskin` | 2 passed, 0 failed |
| `trade_player_scores` | 12 passed, 0 failed |
| `trade_pick_scores` | 17 passed, 0 failed. Existing `trade_pick_score_v0_2026_001` 64-row review warning remained. |

## Warehouse Read-Only State

Raw 2015 rows:

| Table | 2015 Rows |
| --- | ---: |
| `raw_nflverse_schedules` | 267 |
| `raw_nflverse_rosters` | 2,189 |
| `raw_nflverse_rosters_weekly` | 30,201 |
| `raw_nflverse_weekly` | 17,592 |
| `raw_nflverse_pbp` | 48,122 |
| `raw_nflverse_snap_counts` | 23,842 |

Staging 2015 rows:

| Table | 2015 Rows |
| --- | ---: |
| `stg_player_identity` | 30,201 |
| `stg_game_context` | 267 |
| `stg_player_week_stats` | 17,592 |
| `stg_team_week_stats` | 534 |
| `stg_play_player_events` | 118,069 |
| `stg_participation_context` | 23,842 |

Advanced metrics 2015 rows:

| Table | 2015 Rows |
| --- | ---: |
| `player_week_advanced_metrics` | 17,592 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 618 |

Packet rows:

| Object | Total Rows | 2014 Rows | 2015 Rows |
| --- | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 980 | 482 | 498 |
| `compat_pigskin_player_context_current` | 980 | 482 | 498 |

2015 duplicate packet grain count: 0.

## Service State

Production remained untouched:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false

Staging remained untouched:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- Staging-only score and Trade History flags remained true.

## Remaining Warnings

- Route metrics remain blocked.
- Pressure, sack, and scramble metrics remain blocked.
- Pass rate over expected remains null.
- Red-zone and high-value-touch metrics remain blocked.
- Raw nflverse validation retains the expected 2014-2015 coverage review warning.
- Trade pick score validation retains the existing 64-row model-version review warning.
- The historical validation backlog remains untracked by owner decision.

## Recommended Next Phase

Phase 29.20 should run an authorized 2016-2017 raw backfill planner/write gate, or 2016-only if the owner wants to keep the conservative one-season cadence.

Do not rerun the 2015 raw, staging, advanced-metrics, or Pigskin packet materialization steps unless a separate phase explicitly requests a bounded idempotency check.
