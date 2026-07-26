# Phase 29.37 - 2021-2023 Expansion Commit Report

Final decision: **2021-2023 NFLVERSE PIGSKIN EXPANSION COMMITTED WITH WARNINGS**

Phase 29.37 packaged and committed the 2021-2023 nflverse Pigskin expansion checkpoint evidence. This was a source-control and evidence packaging phase only.

No BigQuery rows were written. No raw backfill, staging materialization, advanced metric materialization, Pigskin packet materialization, packet-display repair, ranking build, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, Pigskin prompt, LLM action, scrape, fetch, or Firebase artifact occurred.

## Commit

- Commit hash: `e56afa3`
- Commit subject: `Expand nflverse Pigskin packets through 2023`
- Previous checkpoint: `db8f279 Expand nflverse Pigskin packets through 2020`

## Files Committed

The commit contains only the approved 2021-2023 expansion package files:

- `docs/rebuild/validation/phase-29-32-raw-backfill-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-33-staging-materialization-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-34-advanced-metrics-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-35-pigskin-packet-dry-run-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-36-pigskin-packets-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-37-2021-2023-expansion-release-package.md`

Staged diff before commit:

- 6 files changed.
- 1,785 insertions.
- `git diff --cached --check` passed.
- Git emitted CRLF normalization warnings for the markdown files, with no whitespace errors.

## Files Excluded

Excluded from the commit:

- Historical Phase 17 through Phase 28 validation backlog.
- Earlier Phase 29 checkpoint reports outside the approved 2021-2023 package.
- `output/`, `output/playwright/`, browser evidence, screenshots, temp JSON, logs, caches, `.env`, `.env.*`, secret JSON, Codex cache folders, deployment artifacts, and local runtime files.
- Source files, since no source change was part of this packaging phase.

Remaining untracked files are historical validation backlog reports and owner-review artifacts.

## Gate State

Before packaging, all checked gates were empty or unset:

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

No authorization gate was set during this phase.

## Test And Check Results

All requested checks passed before staging:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_pigskin_packets.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_pigskin_packets`: 15 tests passed.
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`: 12 tests passed.
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`: 11 tests passed.
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_executor`: 18 tests passed.
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_backfill_plan`: 15 tests passed.
- `.\venv\Scripts\python.exe -m unittest discover tests`: 487 tests passed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: validation catalog discovered through `200_no_pressure_metrics_without_source.sql`.

PowerShell wrapped unittest progress emitted on stderr as `NativeCommandError` text, but every test command exited 0 and reported `OK`.

## Warehouse Read-Only State

Read-only warehouse confirmation matched the expected checkpoint:

- `pigskin_player_context_packet_current`: 3,082 rows.
- `compat_pigskin_player_context_current`: 3,082 rows.
- Target packet version `nflverse_pigskin_packet_v0_2021_2023_001`: 746 rows.
- Week 22 packet rows: 21.
- Duplicate packet grain count for 2021-2023: 0.

Packet row counts:

| Season | Rows |
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

2021-2023 raw, staging, and advanced metric counts matched the package report.

## Validation Results

Read-only validation patterns passed:

- `raw_nflverse`: 3 passed, 0 failed. Informational 2014-2023 coverage warning remains.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Informational `trade_pick_score_v0_2026_001` model-version coverage warning remains.

## Service Untouched Confirmation

Read-only Cloud Run describe confirmed no deployment occurred:

| Service | Revision | Traffic | Image | Relevant flags |
| --- | --- | ---: | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | Trade History false, score flags false, Data Ops job trigger flags false, local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | Trade History compat true, score flags true, Data Ops job trigger flags false, local subprocess flags false |

## Remaining Warnings

- 2021-2023 packets are historical and postseason-inclusive through Week 22. They must not be presented as current-season content.
- Display-name collisions remain real and require team, position, or player ID disambiguation.
- Route metrics, pressure/sack/scramble metrics, pass rate over expected, red-zone usage, high-value touches, true pressure, contact yards, and alignment remain blocked or unavailable by design.
- The historical validation backlog remains untracked unless the owner later asks to archive or commit it.
- This commit report was created after the package commit and is intentionally uncommitted.

## Recommended Next Phase

Proceed to **Phase 29.38 - decide whether to run 2024-only raw backfill**.

Keep 2024 separate from the 2025/current-season lane and require a fresh authorization gate before any write.
