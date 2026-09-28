# Phase 29.10 NFLVerse Base Advanced Metrics Materialization Report

Final decision: **NFLVERSE BASE ADVANCED METRICS MATERIALIZED WITH WARNINGS**

Date: 2026-06-29

## Scope

This phase materialized only the bounded 2014 base advanced-metrics feature marts:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

No raw backfill was run. No staging materialization was rerun. No current rolling target was directly written. No Pigskin packet table was written. No deployment, feature-flag change, Cloud Run Job trigger, Scheduler job, scrape, Firebase artifact, Pigskin prompt, or LLM-backed action occurred.

## Authorization Gate

Before write, the following gates were empty or unset:

- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

During write, `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true` was set only inside the PowerShell `try/finally` wrapper. The gate was removed afterward. Post-write verification showed all checked gates empty or unset.

## Git State

Latest commit at phase start:

```text
a73656c Document draft pick score release package
```

Recent history included:

```text
a73656c Document draft pick score release package
6e4b565 Draft pick score lane and staging UI
6158549 Document Trade Score v1 Track A closeout
3268a5a Document Trade Score v1 UI polish package
9ec04f3 Polish Trade Score v1 staging UI
aa543d0 Document Phase 26 evidence commit
251fd18 Document Phase 25 production closeout
b3b0ec1 Document Data Ops hardening production rollout
22e3256 Gate Data Ops local subprocess controls
63149aa Clean up production warning noise
```

No files were staged. Existing Phase 29 source, test, contract, validation, and report files remain untracked or modified for later release packaging.

Files changed during this phase:

- `src/nflverse_advanced_metrics.py`
- `tests/test_nflverse_advanced_metrics.py`
- `docs/rebuild/validation/phase-29-10-nflverse-base-advanced-metrics-materialization-report.md`

## Staging Source Precheck

Read-only staging source counts before the feature write:

| Table | Rows | 2014 rows | Week range |
|---|---:|---:|---|
| `stg_player_identity` | 30,195 | 30,195 | 1 to 21 |
| `stg_game_context` | 267 | 267 | 1 to 21 |
| `stg_player_week_stats` | 17,601 | 17,601 | 1 to 21 |
| `stg_team_week_stats` | 534 | 534 | 1 to 21 |
| `stg_play_player_events` | 116,400 | 116,400 | 1 to 21 |
| `stg_participation_context` | 23,864 | 23,864 | 1 to 21 |

These matched the expected Phase 29 staging source state.

## Feature Target Pre-Write Counts

Read-only target counts before the first write:

| Object | Pre-write rows |
|---|---:|
| `player_week_advanced_metrics` | 0 |
| `team_week_context_metrics` | 0 |
| `qb_week_environment_metrics` | 0 |
| `player_recent_advanced_metrics_current` | 0 |
| `player_role_usage_metrics_current` | 0 |
| `pigskin_player_context_packet_current` | 0 |
| `compat_pigskin_player_context_current` | 0 |

## Final Dry-Run Summary

Dry-run command shape:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2014 --season-end 2014 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2014_001
```

Dry-run result:

| Target | Planned rows | Source rows | Duplicate keys | Readiness |
|---|---:|---:|---:|---|
| `player_week_advanced_metrics` | 17,601 | 17,601 | 0 | ready with warnings |
| `team_week_context_metrics` | 534 | 534 | 0 | ready with warnings |
| `qb_week_environment_metrics` | 643 | 19,973 | 0 | ready with warnings |

Blocked metrics remained explicit: route, first-read, true pressure, contact-yard, alignment, red-zone, inside-10, inside-5, high-value-touch, touchdown-rate, reception-flag-dependent, sacks, scrambles, designed-rush, and pass-rate-over-expected metrics remain unavailable or null in v0.

## Write Mode Implementation

Implemented or confirmed:

- `--write` requires `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true`.
- Live writes support only base feature targets.
- Current rolling targets are rejected in live write mode.
- Feature SELECT SQL reads only Phase 29 staging tables.
- Feature SELECT SQL does not read legacy `play_by_play`, `weekly_metrics`, `player_rosters`, raw `raw_nflverse_*` tables, or Pigskin packet tables.
- Writes use bounded idempotent BigQuery `MERGE`.
- No full-table `WRITE_TRUNCATE`, `TRUNCATE`, raw backfill, staging rebuild, Pigskin refresh, or current target write was introduced.
- `metric_version`, `feature_run_id`, `source_freshness_json`, `missing_data_flags`, and `created_at` are preserved.

During validation, the first authorized bounded write exposed `invalid_metric_range_rows=574` in validation `192_advanced_metrics_range_sanity.sql`. The offending field was `air_yards_share`, which could go negative when raw air-yard values were negative. This was a real range-contract issue.

Fix applied:

- Clamp `air_yards_share` to `0.0` through `1.0`.
- Recompute WOPR from the same bounded `air_yards_share` expression.
- Add focused test coverage in `tests/test_nflverse_advanced_metrics.py`.

A second bounded authorized MERGE was run as failure recovery, as allowed by the phase instructions. It used the same 2014 season window, same three base targets, and same metric version.

## Live Write Command

```powershell
try {
$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"

echo "ALLOW_ADVANCED_METRICS_MATERIALIZATION=$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION"

.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2014 --season-end 2014 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2014_001

} finally {
Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

## Live Write Result

Final corrective write result:

| Target | DML affected rows | 2014 rows after | Duplicate keys after | Metric versions | Feature run IDs |
|---|---:|---:|---:|---:|---:|
| `player_week_advanced_metrics` | 17,601 | 17,601 | 0 | 1 | 1 |
| `team_week_context_metrics` | 534 | 534 | 0 | 1 | 1 |
| `qb_week_environment_metrics` | 643 | 643 | 0 | 1 | 1 |

All rows use `metric_version=nflverse_adv_metrics_v0_2014_001`.

## Post-Write Feature Verification

| Target | Total rows | 2014 rows | Week range | Duplicate grains | Missing source freshness | Missing flags |
|---|---:|---:|---|---:|---:|---:|
| `player_week_advanced_metrics` | 17,601 | 17,601 | 1 to 21 | 0 | 0 | 0 |
| `team_week_context_metrics` | 534 | 534 | 1 to 21 | 0 | 0 | 0 |
| `qb_week_environment_metrics` | 643 | 643 | 1 to 21 | 0 | 0 | 0 |

Player-week null and warning counts:

- `target_share` null rows: 0
- `air_yards_share` null rows: 12,267
- `WOPR` null rows: 12,267
- `epa_per_opportunity` null rows: 12,382
- `success_rate` null rows: 12,267
- `CPOE` null rows: 12,704
- `snap_share` null rows: 3,882
- blocked red-zone/high-value metric non-null rows: 0
- staging-inherited `missing_identity_match` flag rows: 3,818
- `air_yards_share` range after fix: min `0.0`, max `0.8785046728971962`

Team-week null and warning counts:

- `pass_rate_over_expected` null rows: 534
- `seconds_per_play` null rows: 534
- `team_epa_per_play` null rows: 0
- `team_success_rate` null rows: 0
- blocked metric non-null rows: 0
- missing game context flag rows: 88

QB-week null and warning counts:

- `epa_per_dropback` null rows: 0
- `CPOE` null rows: 6
- `deep_attempt_rate` null rows: 0
- `sacks` null rows: 643
- `scrambles` null rows: 643
- blocked metric non-null rows: 0
- `missing_qb_identity` flag rows: 41

## Metric Sanity Results

Player examples:

- Top WOPR: `D.Hopkins` HOU week 15 `1.2475`, `A.Johnson` HOU week 6 `1.2419`, `D.Bryant` DAL week 7 `1.2353`.
- Top target share: `D.Bryant` DAL week 7 `0.5652`, `D.Thomas` DEN week 15 `0.5238`, `A.Johnson` HOU week 6 `0.5217`.
- Top weighted opportunity: `D.Murray` DAL week 14 `57.0`, `O.Beckham` NYG week 17 `52.5`, `D.Murray` DAL week 5 `51.0`.
- Top EPA per opportunity with at least 5 opportunities: `A.Dalton` CIN week 11 `4.4876`, `A.Rodgers` GB week 14 `4.1276`, `P.Rivers` LAC week 6 `3.9227`.

Position null coverage:

- WR: 2,312 rows, 261 null WOPR, 261 null air-yards share, 528 null snap share.
- RB: 1,540 rows, 125 null WOPR, 125 null air-yards share, 353 null snap share.
- TE: 1,167 rows, 130 null WOPR, 130 null air-yards share, 253 null snap share.
- QB: 620 rows, 4 null WOPR, 4 null air-yards share, 131 null snap share.
- Defensive positions are mostly null for opportunity metrics, which is expected in v0 because offensive opportunity metrics are not meaningful for those rows.

Denominator flags:

- zero team targets: 0
- zero team air yards: 0
- zero team opportunities: 0
- zero player opportunities: 12,382
- missing player air-yards source: 12,267

Team examples:

- Top EPA/play: GB week 4 `0.3797`, BAL week 4 `0.3658`, BAL week 6 `0.3373`.
- Bottom EPA/play: TB week 3 `-0.4699`, LV week 13 `-0.4689`, TEN week 14 `-0.4285`.
- Neutral pass rate: min `0.0`, max `1.0`, average `0.4354`.
- Opponent EPA allowed: min `-0.4699`, max `0.3797`, average `-0.0223`.

QB examples:

- Top EPA/dropback with at least 20 dropbacks: `T.Romo` DAL week 16 `1.0395`, `J.Flacco` BAL week 6 `0.9812`, `G.Smith` NYJ week 17 `0.9720`.
- Bottom EPA/dropback with at least 20 dropbacks: `M.Vick` NYJ week 5 `-0.7896`, `J.Manziel` CLE week 15 `-0.7779`, `A.Davis` LA week 10 `-0.7079`.
- QB rows: 643.
- CPOE coverage: 637 rows.
- Deep attempt rate: min `0.0`, max `1.0`, average `0.1231`.
- Sack and scramble fields remain null for all 643 rows, as expected in v0.

## Non-Target Object Verification

Raw nflverse table counts were read-only inspected. No raw backfill was run. Current raw counts include:

- `raw_nflverse_pbp`: 47,629
- `raw_nflverse_weekly`: 17,601
- `raw_nflverse_rosters_weekly`: 30,195
- `raw_nflverse_snap_counts`: 23,864
- optional raw families with no 2014 rows remain at 0 where previously empty.

Staging counts remained at the precheck values listed above.

Non-target objects after the base write:

| Object | Object type | Rows after | Classification |
|---|---|---:|---|
| `player_recent_advanced_metrics_current` | VIEW | 1,854 | derived from base rows, not directly written |
| `player_role_usage_metrics_current` | VIEW | 1,854 | derived from base rows, not directly written |
| `pigskin_player_context_packet_current` | BASE TABLE | 0 | not written |
| `compat_pigskin_player_context_current` | VIEW | 0 | empty-state safe |
| `trade_player_scores` | BASE TABLE | 154 | existing score lane, not touched; 0 rows for 2014 |
| `trade_pick_scores` | BASE TABLE | 64 | existing pick-score lane, not touched |

Warning: the phase prompt expected the two current rolling objects to remain at 0 rows. They are views, not materialized write targets, and now return 1,854 derived rows because the base feature tables are populated. No DML was executed against them. Pigskin packet and compatibility context remain empty.

Legacy source table read-only counts:

- `play_by_play`: 48,771 rows, 0 rows for 2014.
- `weekly_metrics`: 19,421 rows, 0 rows for 2014.
- `player_rosters`: 25,040 rows, 0 rows for 2014.
- `weekly_snap_counts`: 26,612 rows, 0 rows for 2014.

## Validation Results

Post-materialization validation commands:

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

The initial `advanced_metrics` run failed validation `192_advanced_metrics_range_sanity.sql` with `invalid_metric_range_rows=574`. That was fixed by clamping `air_yards_share`, followed by the documented bounded corrective MERGE. Final `advanced_metrics` validation passed.

## Final Local Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py
.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py
.\venv\Scripts\python.exe -m compileall -q src scripts
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
- Focused nflverse and Pigskin contract tests passed.
- Full test suite passed: 472 tests.
- Migrations: no pending migrations.
- Validation dry-run passed and discovered through validation `200`.

## Deployment State

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

No deployment occurred in this phase.

## Remaining Warnings

- Current rolling advanced metric views now return 1,854 rows because they derive from newly populated base rows. They were not directly written.
- Identity warning flags remain inherited from staging: 3,818 player-week rows and 41 QB-week rows.
- `snap_share` remains null for 3,882 player-week rows.
- `WOPR` and `air_yards_share` remain null for 12,267 rows, mainly non-offensive or missing air-yard source rows.
- `seconds_per_play` and `pass_rate_over_expected` remain null for all 534 team-week rows.
- QB sack and scramble fields remain null for all 643 QB-week rows.
- Pigskin context packet remains empty and was not refreshed.

## Recommended Next Phase

1. Decide whether the current rolling advanced-metric views returning derived rows is acceptable before any Pigskin or UI exposure.
2. Run a dedicated current-view/Pigskin packet dry-run phase that remains read-only first.
3. Review identity warning flags and decide whether defensive/special-teams rows should stay in `player_week_advanced_metrics` or be filtered for offensive-only downstream consumers.
4. Keep expansion to additional seasons separate from this 2014 base write.

