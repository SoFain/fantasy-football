# Phase 29.31: 2018-2020 nflverse Pigskin Expansion Release Package

Date: 2026-06-30

Final package status: **READY TO COMMIT WITH WARNINGS**

## Scope

Phase 29.31 packages the completed 2018-2020 nflverse Pigskin expansion checkpoint before the 2021-plus expansion begins.

This phase performed source-control and evidence packaging only. No BigQuery writes, raw backfills, staging materializations, advanced metrics materializations, Pigskin packet refreshes, packet-display repairs, deployments, feature-flag changes, Cloud Run Job triggers, Scheduler jobs, LLM actions, Pigskin prompts, scraping, rankings builds, or Firebase artifact creation occurred.

Latest committed checkpoint before this package:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

## Authorization Gate State

All checked authorization gates were empty or unset at the start of packaging:

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

## Final Expansion State

Committed source state before this package already included the nflverse Pigskin pipeline through 2017. The 2018-2020 warehouse checkpoint now exists as live warehouse state and release evidence:

- Raw nflverse source rows exist for 2018-2020.
- Staging rows exist for 2018-2020.
- Base advanced metrics exist for 2018-2020.
- Pigskin packet rows exist for 2018-2020.
- `pigskin_player_context_packet_current` now covers 2014-2020.
- `compat_pigskin_player_context_current` mirrors the same packet coverage.
- Production and staging Cloud Run services were read-only checked and untouched by this phase.

2018-2020 packet version:

```text
nflverse_pigskin_packet_v0_2018_2020_001
```

2018-2020 source metric version:

```text
nflverse_adv_metrics_v0_2018_2020_001
```

## Raw 2018-2020 Row Counts

Read-only warehouse confirmation:

| Table | 2018 | 2019 | 2020 |
| --- | ---: | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 267 | 269 |
| `raw_nflverse_rosters` | 3,141 | 3,113 | 3,067 |
| `raw_nflverse_rosters_weekly` | 52,200 | 51,630 | 44,124 |
| `raw_nflverse_weekly` | 17,393 | 17,341 | 17,581 |
| `raw_nflverse_pbp` | 47,109 | 47,260 | 47,705 |
| `raw_nflverse_snap_counts` | 23,877 | 23,862 | 24,999 |

## Staging 2018-2020 Row Counts

Read-only warehouse confirmation:

| Table | 2018 | 2019 | 2020 |
| --- | ---: | ---: | ---: |
| `stg_player_identity` | 52,200 | 51,630 | 44,124 |
| `stg_game_context` | 267 | 267 | 269 |
| `stg_player_week_stats` | 17,393 | 17,341 | 17,581 |
| `stg_team_week_stats` | 534 | 534 | 538 |
| `stg_play_player_events` | 114,473 | 114,616 | 116,621 |
| `stg_participation_context` | 23,877 | 23,862 | 24,999 |

## Advanced Metrics 2018-2020 Row Counts

Read-only warehouse confirmation:

| Table | 2018 | 2019 | 2020 |
| --- | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 17,393 | 17,341 | 17,581 |
| `team_week_context_metrics` | 534 | 534 | 538 |
| `qb_week_environment_metrics` | 653 | 653 | 682 |

## Pigskin Packet Row Counts

Read-only warehouse confirmation:

| Object | Total | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 2,336 | 482 | 498 | 128 | 479 | 111 | 113 | 525 |
| `compat_pigskin_player_context_current` | 2,336 | 482 | 498 | 128 | 479 | 111 | 113 | 525 |

Packet version distribution in `pigskin_player_context_packet_current`:

| Packet version | Rows |
| --- | ---: |
| `nflverse_pigskin_packet_v0_2014_001` | 482 |
| `nflverse_pigskin_packet_v0_2015_001` | 498 |
| `nflverse_pigskin_packet_v0_2016_2017_001` | 607 |
| `nflverse_pigskin_packet_v0_2018_2020_001` | 749 |

2018-2020 duplicate packet grain count:

```text
0
```

## Warnings Preserved

2020-heavy candidate warning:

- The 2018-2020 packet candidate set is weighted toward 2020 because current derived feature views expose more 2020 fantasy-position rows than 2018 or 2019.
- Packet distribution is 2018: 111, 2019: 113, 2020: 525.
- This is historical expansion evidence, not current-season content.

Display-name ambiguity warning:

- Abbreviated display names can collide.
- `Josh Allen` and `Tyreek Hill` were intentionally fail-safe ambiguous by full-name lookup.
- Disambiguated lookups with team and position returned the expected candidates.
- Packet consumers should keep using player ID, team, or position where display-name collisions are possible.

Blocked metrics summary:

- Route-derived fields remain blocked because no true route source exists.
- Team `pass_rate_over_expected`, seconds-per-play, pass/rush EPA splits, and red-zone rates remain intentionally blocked or null.
- QB sack and scramble split fields remain intentionally blocked or null.
- Player route, first-read, pressure, contact-yard, alignment, red-zone usage, high-value-touch, touchdown-rate, and reception-dependent metrics remain blocked unless supported by real source data.
- Phase 29.30 packet diagnostics showed missing source freshness rows `0`, missing flags rows `0`, missing blocked metric flag rows `0`, and duplicate packet grain count `0`.

Known informational validation warnings:

- `raw_nflverse` validation 181 is informational and reports 2014-2020 coverage.
- `trade_pick_scores` validation 178 is informational for model-version coverage.
- Phase 29.30 confirmed 22 sample-size warning rows in the final all-position packet dry-run. The older Phase 29.29 dry-run report recorded 47 sample-size warning rows before the final Phase 29.30 rerun.

## Reports Intended For Commit

Approved package files:

- `docs/rebuild/validation/phase-29-26-raw-backfill-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-27-staging-materialization-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-28-advanced-metrics-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-29-pigskin-packet-dry-run-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-30-pigskin-packets-2018-2020-report.md`
- `docs/rebuild/validation/phase-29-31-2018-2020-expansion-release-package.md`

## Files Intentionally Excluded

Excluded from this package:

- Historical Phase 17-28 validation backlog.
- Earlier Phase 29 checkpoint reports not listed above.
- Generated browser evidence.
- `output/` and `output/playwright/`.
- Logs, caches, `.env` files, secret JSON files, Codex caches, temporary files, and deployment artifacts.

## Final Checks

Local checks run before staging package files:

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

Read-only validation patterns:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS, 3 passed, 0 failed. Informational coverage warning returned 3 review rows. |
| `stg_` | PASS, 7 passed, 0 failed. |
| `advanced_metrics` | PASS, 4 passed, 0 failed. |
| `compat_pigskin` | PASS, 2 passed, 0 failed. |
| `trade_player_scores` | PASS, 12 passed, 0 failed. |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Informational model-version warning returned 1 review row. |

## Service State

Read-only Cloud Run state:

| Service | Revision | Traffic | Image | Relevant flags |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | `100%` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | Data Ops trigger flags false, local subprocess flags false, Trade Analyzer score flags false, Trade History compatibility false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | `100%` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | Data Ops trigger flags false, local subprocess flags false, staging score and trade-history flags still enabled from prior staging QA |

No deployment occurred.

## Next Recommended Expansion Phase

Phase 29.32: authorized 2021-2023 raw backfill, with special attention to the 17-game schedule era and any source-shape differences introduced after 2020.
