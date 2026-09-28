# Phase 29.34 - 2021-2023 Base Advanced Metrics Materialization

Date: 2026-06-30

## Final Decision

2021-2023 ADVANCED METRICS MATERIALIZED WITH WARNINGS

The bounded 2021-2023 base advanced metrics materialization completed for the three authorized feature tables:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

No raw backfill, staging materialization, Pigskin packet refresh, deployment, feature-flag change, Cloud Run Job trigger, Scheduler job, scraping, LLM call, ranking build, or commit occurred.

## Authorization Gate State

Before materialization, these gates were empty or unset:

- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

During the live write, only `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true` was set inside the same-session wrapper:

```powershell
try {
$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"

echo "ALLOW_ADVANCED_METRICS_MATERIALIZATION=$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION"

.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2021 --season-end 2023 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2021_2023_001

} finally {
Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

After materialization, the gate was removed. The checked authorization gates were empty or unset.

## Git State

- Latest commit: `db8f279 Expand nflverse Pigskin packets through 2020`
- No staged files before this phase.
- No tracked source diffs before this phase.
- Historical validation backlog remained untracked.

## Baseline Checks

Passed before write:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- `tests.test_nflverse_advanced_metrics`: 12 tests passed.
- `tests.test_nflverse_staging`: 11 tests passed.
- Full unit discovery: 487 tests passed.
- No pending migrations.
- Validation catalog discovered through `200_no_pressure_metrics_without_source.sql`.

## Staging Source Precheck

2021-2023 staging source rows were present before the feature write:

| Table | 2021 | 2022 | 2023 | Total | Week range |
| --- | ---: | ---: | ---: | ---: | --- |
| `stg_player_identity` | 46,670 | 46,136 | 45,650 | 138,456 | 1-22 |
| `stg_game_context` | 285 | 284 | 285 | 854 | 1-22 |
| `stg_player_week_stats` | 18,947 | 18,809 | 18,621 | 56,377 | 1-22 |
| `stg_team_week_stats` | 570 | 568 | 570 | 1,708 | 1-22 |
| `stg_play_player_events` | 121,589 | 119,216 | 120,051 | 360,856 | 1-22 |
| `stg_participation_context` | 26,468 | 26,381 | 26,540 | 79,389 | 1-22 |

## Feature Pre-Write State

2021-2023 feature rows before materialization:

| Table | 2021-2023 rows | Total rows before | Existing season range |
| --- | ---: | ---: | --- |
| `player_week_advanced_metrics` | 0 | 122,495 | 2014-2020 |
| `team_week_context_metrics` | 0 | 3,742 | 2014-2020 |
| `qb_week_environment_metrics` | 0 | 4,513 | 2014-2020 |

Derived and packet objects before write:

- `player_recent_advanced_metrics_current`: 4,344 rows
- `player_role_usage_metrics_current`: 4,344 rows
- `pigskin_player_context_packet_current`: 2,336 rows
- `compat_pigskin_player_context_current`: 2,336 rows

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2021 --season-end 2023 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2021_2023_001
```

Result: exit 0, `wrote=false`.

| Target | Planned rows | Source rows | Duplicate keys | Readiness | Main warning |
| --- | ---: | ---: | ---: | --- | --- |
| `player_week_advanced_metrics` | 56,377 | 56,377 | 0 | ready with warnings | Route, red-zone, high-value touch, touchdown, and reception-dependent metrics remain blocked. |
| `team_week_context_metrics` | 1,708 | 1,708 | 0 | ready with warnings | Pace, pass-rate-over-expected, pass/rush EPA splits, and red-zone rates remain null pending source-field review. |
| `qb_week_environment_metrics` | 2,130 | 62,341 passer event rows | 0 | ready with warnings | Sack, scramble, designed-rush, and pass-rate-over-expected fields are unavailable in v0. |

Notable dry-run diagnostics:

- Player metrics: `target_share_null_count=0`, `air_yards_share_null_count=39,416`, `wopr_null_count=39,416`, `epa_per_opportunity_null_count=39,727`, `snap_share_null_count=63`.
- Team metrics: `epa_coverage_count=1,708`, `success_coverage_count=1,708`, `null_pass_rate_over_expected_count=1,708`.
- QB metrics: `cpoe_coverage_count=2,078`, `epa_coverage_count=2,130`, `missing_qb_identity_count=179`.

## Live Advanced Metrics Write

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2021 --season-end 2023 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2021_2023_001
```

The Python command printed `wrote=true` and returned MERGE results for all three targets. My outer PowerShell logging wrapper had an invalid trailing `2>&1 | Tee-Object` placement after the `try/finally` block, which produced a non-mutating shell wrapper error after the MERGE output printed. The write was not rerun. Post-write read-only verification below confirms the warehouse state.

| Target | MERGE affected rows | Bounded rows | Duplicate keys | Feature run IDs | Week range |
| --- | ---: | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 56,377 | 56,377 | 0 | 3 | 1-22 |
| `team_week_context_metrics` | 1,708 | 1,708 | 0 | 3 | 1-22 |
| `qb_week_environment_metrics` | 2,130 | 2,130 | 0 | 3 | 1-22 |

All three write results used `MERGE`.

## Post-Write Feature Verification

| Target | 2021 | 2022 | 2023 | Total after | Duplicate groups | Missing freshness | Missing flags | Invalid ranges |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 18,947 | 18,809 | 18,621 | 178,872 | 0 | 0 | 0 | 0 |
| `team_week_context_metrics` | 570 | 568 | 570 | 5,450 | 0 | 0 | 0 | 0 |
| `qb_week_environment_metrics` | 718 | 694 | 718 | 6,643 | 0 | 0 | 0 | 0 |

Metric version distribution:

- `player_week_advanced_metrics`: `nflverse_adv_metrics_v0_2021_2023_001`, 56,377 rows, 3 feature run IDs.
- `team_week_context_metrics`: `nflverse_adv_metrics_v0_2021_2023_001`, 1,708 rows, 3 feature run IDs.
- `qb_week_environment_metrics`: `nflverse_adv_metrics_v0_2021_2023_001`, 2,130 rows, 3 feature run IDs.

## Metric Sanity Results

Player metric sanity:

- Top WOPR examples: D.Adams LV 2023 week 10 at 1.4018, D.Adams GB 2021 week 3 at 1.3713, T.Lockett SEA 2021 week 8 at 1.3649, A.Brown TEN 2021 week 16 at 1.3475, G.Wilson NYJ 2022 week 18 at 1.2844.
- Top weighted opportunity examples: N.Harris PIT 2021 week 3 at 61.5, Breece Hall NYJ 2023 week 16 at 60.0, A.Ekeler LAC 2022 week 6 at 54.0, D.Adams LV 2023 week 17 at 52.5, P.Nacua LA 2023 week 2 at 52.0.
- Null WOPR is concentrated in non-skill positions, as expected. Among top row-count positions: WR 854 of 7,682 null WOPR rows, RB 459 of 4,792, TE 389 of 3,787, QB 1 of 2,034.

Team metric sanity:

- Top team EPA per play examples: BUF 2021 week 19 at 0.5297, MIA 2023 week 3 at 0.4726, DAL 2021 week 18 at 0.4399, SF 2023 week 13 at 0.4283, NE 2021 week 10 at 0.4118.
- Bottom team EPA per play examples: HOU 2021 week 4 at -0.6429, NE 2023 week 5 at -0.6237, ARI 2023 week 9 at -0.5443, IND 2022 week 9 at -0.5408, HOU 2021 week 13 at -0.5251.
- Neutral pass rate distribution: min 0.0, average 0.4365, max 1.0.
- `pass_rate_over_expected` is null for all 1,708 rows, as designed.

QB metric sanity:

- Top EPA/dropback examples with at least 10 dropbacks: L.Jackson BAL 2023 week 17 at 1.3180, J.Love GB 2023 week 19 at 1.1400, B.Purdy SF 2023 week 4 at 1.0384, T.Tagovailoa MIA 2023 week 3 at 1.0143, J.Brissett WAS 2023 week 15 at 0.9428.
- Bottom EPA/dropback examples with at least 10 dropbacks: M.Glennon NYG 2021 week 17 at -2.3710, P.Walker CAR 2022 week 9 at -1.3387, C.Tune ARI 2023 week 9 at -1.2137, D.Mills HOU 2021 week 4 at -1.1806, J.Hall MIN 2023 week 17 at -1.1532.
- QB rows: 2,130. CPOE non-null rows: 2,078. Sack and scramble fields are null for all 2,130 rows because those fields are blocked in v0.

## Blocked Metric Confirmation

Blocked or unavailable metrics remained null:

- Player red-zone/high-value fields: 0 non-null blocked rows.
- Team blocked fields: 0 non-null rows for `pass_epa_per_play`, `rush_epa_per_play`, `red_zone_pass_rate`, and `red_zone_rush_rate`.
- QB blocked fields: 0 non-null rows for `sacks`, `scrambles`, `designed_rushes`, `sack_rate`, `scramble_rate`, and `pass_rate_over_expected_context`.
- Route metrics remain blocked. No route share was inferred from snap-count data.

## Derived Current-View Behavior

No current view was written directly. The two current views changed as a derived consequence of the new base metric rows:

- `player_recent_advanced_metrics_current`: 4,344 before, 5,497 after.
- `player_role_usage_metrics_current`: 4,344 before, 5,497 after.

Pigskin packet tables stayed unchanged:

- `pigskin_player_context_packet_current`: 2,336 rows.
- `compat_pigskin_player_context_current`: 2,336 rows.

## 17-Game Era and Week 22 Behavior

The 2021-2023 feature layer is postseason-inclusive through week 22. All three base feature targets have `min_week=1` and `max_week=22`. This mirrors the source staging layer and does not mean Pigskin packets were refreshed or current-facing content was changed.

## Non-Target Object Verification

Raw source counts remained aligned with Phase 29.32:

| Raw table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `raw_nflverse_schedules` | 285 | 284 | 285 | 1-22 |
| `raw_nflverse_rosters_weekly` | 46,670 | 46,136 | 45,650 | 1-22 |
| `raw_nflverse_weekly` | 18,947 | 18,809 | 18,621 | 1-22 |
| `raw_nflverse_pbp` | 49,922 | 49,434 | 49,665 | 1-22 |
| `raw_nflverse_snap_counts` | 26,468 | 26,381 | 26,540 | 1-22 |

Staging counts remained aligned with Phase 29.33:

- `stg_player_week_stats`: 56,377 bounded rows.
- `stg_team_week_stats`: 1,708 bounded rows.
- `stg_play_player_events`: 360,856 bounded rows.
- `stg_participation_context`: 79,389 bounded rows.

Score lanes were unchanged:

- `trade_player_scores`: 154 rows.
- `trade_pick_scores`: 64 rows.

## Validation Results

Passed:

- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern stg_`: 7 passed, 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern advanced_metrics`: 4 passed, 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_pigskin`: 2 passed, 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores`: 12 passed, 0 failed.

Passed with informational warnings:

- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern raw_nflverse`: 3 passed, 0 failed. Validation `181_raw_nflverse_season_week_coverage.sql` returned informational 2014-2023 coverage rows.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_pick_scores`: 17 passed, 0 failed. Validation `178_trade_pick_scores_model_version_coverage.sql` returned the expected informational model-version row.

## Final Local Checks

Passed after materialization:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- `tests.test_nflverse_advanced_metrics`: 12 tests passed.
- `tests.test_nflverse_staging`: 11 tests passed.
- Full unit discovery: 487 tests passed.
- No pending migrations.

## Production and Staging Untouched

Read-only Cloud Run describe after materialization:

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false
- Existing staging-only Trade History and score UI flags remain enabled from prior QA.

## Remaining Warnings

- The advanced metrics CLI still uses stale internal Phase 29.9 or Phase 29.10 wording. The executed command, gate, metric version, and season window are authoritative for Phase 29.34.
- The live write produced a PowerShell logging-wrapper error after the Python MERGE output due an invalid trailing redirection placement. The gate was removed, the write was not rerun, and read-only verification confirms the materialized state.
- 2021-2023 rows are postseason-inclusive through week 22.
- `stg_participation_context` still carries known PFR identity gaps from snap-count coverage.
- Route, red-zone, pressure, first-read, contact-yard, alignment, touchdown, reception-dependent, sack, scramble, designed-rush, and pass-rate-over-expected metrics remain blocked or null unless true source fields are proven.
- Raw nflverse tables remain internal only and are not Pigskin or UI-safe surfaces.

## Recommended Next Phase

Proceed to a separate Phase 29.35 for 2021-2023 Pigskin current-view and packet dry-run planning. Do not refresh Pigskin packets until that phase proves the 2021-2023 feature rows are safe for packet selection and display.
