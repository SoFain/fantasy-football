# Phase 29.25 2016-2017 Packet Identity Commit Report

Date: 2026-06-29

Final decision: **2016-2017 NFLVERSE PIGSKIN EXPANSION COMMITTED WITH WARNINGS**

## Commit

Commit created:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

Previous checkpoint:

```text
67f37e7 Expand nflverse Pigskin pipeline to 2015
```

## Files Committed

| File | Purpose |
| --- | --- |
| `src/nflverse_pigskin_packets.py` | Added safer packet player lookup, first-two-letter abbreviation variants, `--team`, `--player-id`, lookup diagnostics, ambiguity warnings, no-match warnings, and generic warning text. |
| `tests/test_nflverse_pigskin_packets.py` | Added regression tests for abbreviation lookup, disambiguation filters, ambiguity warnings, and stale warning text removal. |
| `docs/rebuild/validation/phase-29-20-raw-backfill-2016-2017-report.md` | 2016-2017 raw nflverse backfill evidence. |
| `docs/rebuild/validation/phase-29-21-staging-materialization-2016-2017-report.md` | 2016-2017 staging materialization evidence. |
| `docs/rebuild/validation/phase-29-22-advanced-metrics-2016-2017-report.md` | 2016-2017 base advanced metrics materialization evidence. |
| `docs/rebuild/validation/phase-29-23-pigskin-packets-2016-2017-report.md` | 2016-2017 Pigskin packet refresh evidence. |
| `docs/rebuild/validation/phase-29-24-pigskin-packet-identity-display-qa-report.md` | Packet identity/display-name QA and lookup fix evidence. |
| `docs/rebuild/validation/phase-29-25-2016-2017-packet-identity-release-package.md` | Package summary for the 2016-2017 packet expansion and identity lookup fix. |

## Files Excluded

The commit intentionally excluded:

- Phase 17 through Phase 28 historical validation backlog reports.
- Phase 29 reports outside the approved 2016-2017 packet/identity package.
- `output/`, Playwright/browser evidence, local QA JSON, proxy files, logs, caches, `.env` files, secret JSON files, Codex caches, deployment artifacts.

## Gate State

All checked gates were unset:

| Gate | State |
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

## Test and Check Results

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_pigskin_packets.py` | PASS |
| `py_compile src\nflverse_advanced_metrics.py` | PASS |
| `py_compile src\nflverse_staging.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_pigskin_packets` | PASS, 15 tests |
| `unittest tests.test_nflverse_advanced_metrics` | PASS, 12 tests |
| `unittest tests.test_nflverse_staging` | PASS, 11 tests |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest discover tests` | PASS, 487 tests |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, validation catalog discovered through 200 |

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS, 3 passed, 0 failed. Informational coverage warning returned 3 rows. |
| `stg_` | PASS, 7 passed, 0 failed |
| `advanced_metrics` | PASS, 4 passed, 0 failed |
| `compat_pigskin` | PASS, 2 passed, 0 failed |
| `trade_player_scores` | PASS, 12 passed, 0 failed |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Informational model-version warning returned 1 row. |

## Warehouse Read-Only State

Phase 29.25 did not write BigQuery rows.

Packet totals:

| Object | Row count |
| --- | ---: |
| `pigskin_player_context_packet_current` | 1,587 |
| `compat_pigskin_player_context_current` | 1,587 |

Packet rows by season:

| Season | Rows |
| --- | ---: |
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |

Duplicate packet grain count for 2016-2017: `0`.

Key 2016-2017 row-count confirmations:

| Layer | Object | 2016 rows | 2017 rows |
| --- | --- | ---: | ---: |
| Raw | `raw_nflverse_pbp` | 47,651 | 47,245 |
| Raw | `raw_nflverse_weekly` | 17,531 | 17,456 |
| Raw | `raw_nflverse_snap_counts` | 23,890 | 23,862 |
| Staging | `stg_player_identity` | 35,020 | 51,321 |
| Staging | `stg_player_week_stats` | 17,531 | 17,456 |
| Staging | `stg_play_player_events` | 117,281 | 114,910 |
| Advanced metrics | `player_week_advanced_metrics` | 17,531 | 17,456 |
| Advanced metrics | `team_week_context_metrics` | 534 | 534 |
| Advanced metrics | `qb_week_environment_metrics` | 636 | 628 |

## Service Untouched Confirmation

Read-only Cloud Run describes were run. No deploy occurred.

| Service | Revision | Traffic | Image digest | Flag state |
| --- | --- | ---: | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | production risk flags false, score flags false, Trade History compatibility false, Data Ops job/local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score and Trade History flags remain true as previously configured, Data Ops job/local subprocess flags false |

## Remaining Warnings

- Existing packet rows still use abbreviated source display names such as `Ju.Jones` and `Da.Johnson`; the committed code fixes lookup and diagnostics, not stored packet display values.
- `David Johnson` should be disambiguated with `--team`, `--position`, or `--player-id` when auditing abbreviated packet names.
- Raw nflverse validation includes an informational coverage warning.
- Trade pick score validation includes an informational model-version coverage warning.
- Historical validation backlog reports remain untracked for owner review.

## Recommended Next Phase

Phase 29.26: authorized 2018-2020 raw backfill, or 2018-only if the owner wants a more conservative cadence.

