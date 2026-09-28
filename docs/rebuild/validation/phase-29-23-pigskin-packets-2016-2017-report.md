# Phase 29.23 - 2016-2017 Pigskin Packet Refresh

Final decision: **2016-2017 PIGSKIN PACKETS MATERIALIZED WITH WARNINGS**

## Scope

This phase refreshed only `pigskin_player_context_packet_current` for 2016 and 2017 from the already materialized nflverse advanced metrics lane.

No raw backfill, staging materialization, advanced metrics materialization, ranking build, deploy, scheduler change, Cloud Run Job trigger, Pigskin prompt, LLM action, scrape, external fetch, Firebase artifact, or commit was run.

## Authorization

Required write gate: `ALLOW_PIGSKIN_PACKET_REFRESH=true`.

Initial process gate check:

- `ALLOW_PIGSKIN_PACKET_REFRESH`: unset
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`: unset
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`: unset
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`: unset
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`: unset
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`: unset
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`: unset
- `ALLOW_TRADE_SCORE_MATERIALIZATION`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset

The packet gate was set only inside the write process:

```powershell
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"
  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2016 --season-end 2017 --write --strict --packet-version nflverse_pigskin_packet_v0_2016_2017_001 --source-metric-version nflverse_adv_metrics_v0_2016_2017_001 --output-json $env:TEMP\phase29_23_packet_write.json
} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

Post-write gate check confirmed `ALLOW_PIGSKIN_PACKET_REFRESH` was unset again. No other authorization gates were set.

## Baseline Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_pigskin_packets.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_pigskin_packets`: 11 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`: 12 tests passed
- `.\venv\Scripts\python.exe -m unittest discover tests`: 483 tests passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovery passed

Note: the first PowerShell wrapper misclassified unittest output because unittest progress is written to stderr. The tests were rerun through `cmd /c`; all exit codes were 0.

## Source State Before Write

`player_week_advanced_metrics`:

- total rows: 70,180
- 2016 rows: 17,531
- 2017 rows: 17,456
- target metric-version rows for 2016-2017: 34,987
- 2016-2017 week range: 1-21

`team_week_context_metrics`:

- total rows: 2,136
- 2016 rows: 534
- 2017 rows: 534
- target metric-version rows for 2016-2017: 1,068
- 2016-2017 week range: 1-21

`qb_week_environment_metrics`:

- total rows: 2,525
- 2016 rows: 636
- 2017 rows: 628
- target metric-version rows for 2016-2017: 1,264
- 2016-2017 week range: 1-21

Current feature views:

- `player_recent_advanced_metrics_current`: 3,128 total rows, with 457 rows for 2016 and 1,874 for 2017
- `player_role_usage_metrics_current`: 3,128 total rows, with 457 rows for 2016 and 1,874 for 2017

Packet tables before write:

- `pigskin_player_context_packet_current`: 980 total rows, 482 for 2014, 498 for 2015, 0 for 2016, 0 for 2017
- `compat_pigskin_player_context_current`: 980 total rows, 482 for 2014, 498 for 2015, 0 for 2016, 0 for 2017
- target packet version rows before write: 0

## Dry-Run Results

Command shape:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2016 --season-end 2017 --dry-run --strict --packet-version nflverse_pigskin_packet_v0_2016_2017_001 --source-metric-version nflverse_adv_metrics_v0_2016_2017_001 --limit 25 --output-json <temp-json>
```

All-position dry-run:

- candidate count: 607
- QB: 87
- RB: 165
- WR: 230
- TE: 125
- missing source freshness rows: 0
- missing flags rows: 0
- missing identity rows: 0
- missing identity flag rows: 23
- null CPOE rows: 52
- null EPA/opportunity rows: 19
- null snap share rows: 26
- sample-size warning rows: 19

Position dry-runs:

| Position | Candidate count | Missing identity flag rows | Sample-size warning rows | Null CPOE rows | Null snap-share rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| QB | 87 | 4 | 19 | 6 | 4 |
| RB | 165 | 7 | 0 | 43 | 8 |
| WR | 230 | 9 | 0 | 2 | 10 |
| TE | 125 | 3 | 0 | 1 | 4 |

Dry-run warnings were expected:

- packet writes are limited to `pigskin_player_context_packet_current`
- packet SQL reads current/base feature marts only, not raw or legacy source tables
- the CLI still prints a stale phase label in warning text

## Write Result

Write command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2016 --season-end 2017 --write --strict --packet-version nflverse_pigskin_packet_v0_2016_2017_001 --source-metric-version nflverse_adv_metrics_v0_2016_2017_001 --output-json $env:TEMP\phase29_23_packet_write.json
```

Result:

- exit code: 0
- target: `pigskin_player_context_packet_current`
- write SQL kind: `MERGE`
- DML affected rows: 607
- bounded row count: 607
- min source season: 2016
- max source season: 2017
- week range: 1-21
- packet version count: 1
- source metric version count: 1
- duplicate packet grain count: 0
- missing packet text count: 0
- missing packet JSON count: 0
- missing source freshness count: 0
- missing blocked-metric flag count: 0
- rows with packet warnings: 49

## Post-Write Counts

`pigskin_player_context_packet_current`:

- total rows: 1,587
- 2014 rows: 482
- 2015 rows: 498
- 2016 rows: 128
- 2017 rows: 479
- target packet version rows: 607
- missing packet text: 0
- missing packet JSON: 0
- missing source freshness: 0
- missing flags: 0

`compat_pigskin_player_context_current`:

- total rows: 1,587
- 2014 rows: 482
- 2015 rows: 498
- 2016 rows: 128
- 2017 rows: 479
- target packet version rows: 607
- missing packet text: 0
- missing packet JSON: 0
- missing source freshness: 0
- missing flags: 0

Packet version distribution:

| Packet version | Rows | Season range | Week range |
| --- | ---: | --- | --- |
| `nflverse_pigskin_packet_v0_2014_001` | 482 | 2014-2014 | 1-21 |
| `nflverse_pigskin_packet_v0_2015_001` | 498 | 2015-2015 | 1-21 |
| `nflverse_pigskin_packet_v0_2016_2017_001` | 607 | 2016-2017 | 1-21 |

2016-2017 packet rows by position:

| Season | QB | RB | WR | TE | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2016 | 14 | 40 | 50 | 24 | 128 |
| 2017 | 73 | 125 | 180 | 101 | 479 |

Duplicate packet grain:

- duplicate packet grain count: 0
- max rows per grain: 1

Compatibility view dependency check:

- `compat_pigskin_player_context_current` reads from `pigskin_player_context_packet_current`
- blocked dependency hits: none for `raw_nflverse_`, `play_by_play`, `weekly_metrics`, or `player_rosters`

## Packet Warning Review

Warning counts for the 607 refreshed rows:

- packet-warning rows: 49
- sample-size warning text rows: 19
- missing-snap-share warning rows: 26
- missing-identity warning text rows: 0
- blocked-metric flags rows: 607

Blocked metric flags are expected. The packet lane explicitly marks unavailable route share, yards per route run, targets per route run, first-read share, red-zone usage, high-value touches, touchdown-rate splits, true pressure, contact yards, and alignment metrics rather than inventing them.

## Named Player Spot Checks

The nflverse packet display names use abbreviated names, so exact full-name lookup returned no rows. Abbreviated-name spot checks found packets for 11 of the 12 requested examples.

| Requested name | Abbrev checked | Result |
| --- | --- | --- |
| Aaron Rodgers | `A.Rodgers` | found, QB GB, 2017 week 15 |
| Tom Brady | `T.Brady` | found, QB NE, 2017 week 21 |
| Matt Ryan | `M.Ryan` | found, QB ATL, 2017 week 19, sample-size warning |
| Cam Newton | `C.Newton` | found, QB CAR, 2017 week 18 |
| Ezekiel Elliott | `E.Elliott` | found, RB DAL, 2017 week 17 |
| Le'Veon Bell | `L.Bell` | found, RB PIT, 2017 week 19 |
| David Johnson | `D.Johnson` | found, TE PIT, 2016 week 20 |
| Antonio Brown | `A.Brown` | found, WR PIT, 2017 week 19 |
| Julio Jones | `J.Jones` | not found in refreshed packet rows |
| DeAndre Hopkins | `D.Hopkins` | found, WR HOU, 2017 week 16 |
| Travis Kelce | `T.Kelce` | found, TE KC, 2017 week 18 |
| Rob Gronkowski | `R.Gronkowski` | found, TE NE, 2017 week 21 |

Identity/display-name warnings:

- `Julio Jones` did not resolve under `J.Jones` in the packet output.
- `David Johnson` resolved to a Pittsburgh TE row under `D.Johnson`, not the expected Arizona RB context.
- These are source identity/display issues, not packet write failures. The generated rows still preserve player IDs, team, position, source freshness, missing-data flags, and blocked-metric flags.

## Non-Target State

Raw/staging/feature counts were read back after the packet write. The packet phase did not run raw backfill, staging materialization, or advanced metric materialization.

Selected non-target counts:

- `raw_nflverse_pbp`: 190,647 total rows, 47,651 for 2016, 47,245 for 2017
- `raw_nflverse_weekly`: 70,180 total rows, 17,531 for 2016, 17,456 for 2017
- `raw_nflverse_rosters`: 10,484 total rows, 3,061 for 2016, 3,082 for 2017
- `raw_nflverse_rosters_weekly`: 146,737 total rows, 35,020 for 2016, 51,321 for 2017
- `raw_nflverse_schedules`: 1,068 total rows, 267 for 2016, 267 for 2017
- `raw_nflverse_snap_counts`: 95,458 total rows, 23,890 for 2016, 23,862 for 2017
- `player_week_advanced_metrics`: 70,180 total rows, 17,531 for 2016, 17,456 for 2017
- `team_week_context_metrics`: 2,136 total rows, 534 for 2016, 534 for 2017
- `qb_week_environment_metrics`: 2,525 total rows, 636 for 2016, 628 for 2017
- `player_recent_advanced_metrics_current`: 3,128 total rows
- `player_role_usage_metrics_current`: 3,128 total rows

## Validations

Validation commands:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern raw_nflverse
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern stg_
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern advanced_metrics
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_pigskin
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_pick_scores
```

Results:

- `raw_nflverse`: 3 passed, 0 failed, 1 informational coverage warning
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed, 1 informational model-version warning

Validation warnings:

- `181_raw_nflverse_season_week_coverage.sql` returned informational raw season-week coverage rows.
- `178_trade_pick_scores_model_version_coverage.sql` returned the existing `trade_pick_score_v0_2026_001` model-version coverage row.

## Service State

Production was read-only described after the packet write:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- production score flags: false
- production Trade History compatibility: false
- production Data Ops Cloud Run trigger flags: false
- production Data Ops local subprocess flags: false

Staging was read-only described:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- staging score flags: true
- staging Trade History compatibility: true
- staging Data Ops Cloud Run trigger flags: false
- staging Data Ops local subprocess flags: false

No deployment was run.

## Final Checks

Final checks passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile app.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_pigskin_packets.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_pigskin_packets`: 11 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`: 12 tests passed
- `.\venv\Scripts\python.exe -m unittest discover tests`: 483 tests passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

## Warnings

- Packet warning rows exist by design: 49 refreshed rows carry packet warnings.
- Every refreshed packet carries blocked-metric flags. This is expected and safer than fabricating unsupported metrics.
- Full-name spot checks do not match the packet display-name format because current packets use abbreviated names.
- `Julio Jones` did not appear under `J.Jones`.
- `David Johnson` resolves to `D.Johnson`, TE, PIT, 2016 week 20 in this packet slice.
- The packet CLI warning text still references Phase 29.12 even though this run is Phase 29.23.
- Validation warnings were informational only.

## Recommended Next Phase

- Review the abbreviated-name/display-name behavior before broader Pigskin UI exposure.
- Decide whether the `Julio Jones` and `David Johnson` identity-display cases need a source identity correction before expanding the packet lane beyond canary years.
- If accepted, continue historical expansion with the next bounded season window, keeping raw, staging, advanced metrics, and packet refreshes in separate authorized phases.
