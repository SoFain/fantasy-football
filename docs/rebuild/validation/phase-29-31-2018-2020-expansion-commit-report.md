# Phase 29.31: 2018-2020 nflverse Pigskin Expansion Commit Report

Date: 2026-06-30

Final decision: **2018-2020 NFLVERSE PIGSKIN EXPANSION COMMITTED WITH WARNINGS**

## Commit

Commit created:

```text
db8f279090d2 Expand nflverse Pigskin packets through 2020
```

The commit was created from branch `codex/phase-14-validation-footer`.

## Files Committed

The commit contains only the approved 2018-2020 expansion package reports:

- `docs/rebuild/validation/phase-29-26-raw-backfill-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-27-staging-materialization-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-28-advanced-metrics-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-29-pigskin-packet-dry-run-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-30-pigskin-packets-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-31-2018-2020-expansion-release-package.md`

Commit message:

```text
Expand nflverse Pigskin packets through 2020

Adds 2018-2020 raw, staging, advanced metrics, and Pigskin packet evidence reports.

Documents 2020 source-shape differences, blocked metrics, and display-name ambiguity warnings.

No production deployment.
```

## Files Excluded

Excluded from the commit:

- Historical Phase 17-28 validation backlog.
- Earlier Phase 29 checkpoint reports not in the approved 2018-2020 package.
- Generated browser evidence.
- `output/` and `output/playwright/`.
- Logs, caches, `.env` files, secret JSON files, Codex caches, temporary files, and deployment artifacts.

Post-commit status still contains 94 untracked files, all treated as historical validation backlog or owner-review artifacts for this phase.

## Gate State

All checked gates were empty or unset before packaging:

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

No authorization gate was set during this packaging or commit phase.

## Checks Run

Pre-stage checks:

- `scripts/check_deployment_safety.py`: pass
- `py_compile src\nflverse_pigskin_packets.py`: pass
- `py_compile src\nflverse_advanced_metrics.py`: pass
- `py_compile src\nflverse_staging.py`: pass
- `py_compile src\nflverse_backfill.py`: pass
- `py_compile src\nflverse_backfill_plan.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_nflverse_pigskin_packets`: pass, 15 tests
- `tests.test_nflverse_advanced_metrics`: pass, 12 tests
- `tests.test_nflverse_staging`: pass, 11 tests
- `tests.test_nflverse_backfill_executor`: pass, 18 tests
- `tests.test_nflverse_backfill_plan`: pass, 15 tests
- `unittest discover tests`: pass, 487 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through 200

Staged package checks:

- Expected staged file set matched exactly.
- `git diff --cached --check`: pass after removing trailing blank EOF lines from two staged reports.
- Secret and risky pattern scan: no secret-like content found. The only match was an exclusion sentence mentioning `.env` files and secret JSON files.

## Read-Only Warehouse State

Packet state:

- `pigskin_player_context_packet_current`: 2,336 rows.
- `compat_pigskin_player_context_current`: 2,336 rows.
- 2014: 482 rows.
- 2015: 498 rows.
- 2016: 128 rows.
- 2017: 479 rows.
- 2018: 111 rows.
- 2019: 113 rows.
- 2020: 525 rows.
- 2018-2020 packet version `nflverse_pigskin_packet_v0_2018_2020_001`: 749 rows.
- 2018-2020 duplicate packet grain count: 0.

Advanced metrics 2018-2020:

- `player_week_advanced_metrics`: 2018 17,393, 2019 17,341, 2020 17,581.
- `team_week_context_metrics`: 2018 534, 2019 534, 2020 538.
- `qb_week_environment_metrics`: 2018 653, 2019 653, 2020 682.

Staging and raw count details are documented in `phase-29-31-2018-2020-expansion-release-package.md`.

## Validation Results

Read-only validation patterns:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS, 3 passed, 0 failed. Informational coverage warning returned 3 review rows. |
| `stg_` | PASS, 7 passed, 0 failed. |
| `advanced_metrics` | PASS, 4 passed, 0 failed. |
| `compat_pigskin` | PASS, 2 passed, 0 failed. |
| `trade_player_scores` | PASS, 12 passed, 0 failed. |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Informational model-version warning returned 1 review row. |

## Service Untouched Confirmation

Read-only service state:

- Production service `nfl-studio-dashboard` remained on revision `nfl-studio-dashboard-00077-2jp`, 100 percent traffic.
- Production image remained `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`.
- Production Data Ops trigger flags, local subprocess flags, Trade Analyzer score flags, and Trade History compatibility remained false.
- Staging service `nfl-studio-dashboard-staging` remained on revision `nfl-studio-dashboard-staging-00029-jtb`, 100 percent traffic.
- No staging or production deployment occurred.

## Remaining Warnings

- This package is historical 2018-2020 expansion evidence, not current-season content.
- 2020 packet candidates dominate the 2018-2020 packet set: 525 of 749 rows.
- 2020 source shape differs from 2018 and 2019: schedules have 269 rows, while 2018 and 2019 have 267; roster-weekly coverage is lower in 2020.
- Display-name ambiguity remains intentional and fail-safe. `Josh Allen` and `Tyreek Hill` require disambiguation by team, position, or player ID.
- Route, pressure, red-zone, team tempo, team pass-rate-over-expected, QB sack, and QB scramble metrics remain blocked or null unless real sources are added.
- `raw_nflverse` validation 181 and `trade_pick_scores` validation 178 remain informational review warnings.
- Historical untracked validation backlog remains outside the commit.

## Recommended Next Phase

Phase 29.32: authorized 2021-2023 raw backfill, with special attention to the 17-game schedule era.
