# Phase 29.47 Advanced Metrics 2025 Report

Final decision: **2025 ADVANCED METRICS MATERIALIZED WITH WARNINGS**

## Scope

Owner correction accepted: season 2025 was treated as a completed historical season for this task.

This phase wrote only 2025 rows to the three base advanced metrics targets:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Metric version: `nflverse_adv_metrics_v0_2025_001`.

No raw nflverse backfill, staging materialization, Pigskin packet refresh, current-view write, deployment, feature flag change, Cloud Run Job, Scheduler job, LLM call, Pigskin prompt, scrape, Firebase artifact, or commit was run.

All BigQuery checks used neutral aliases. No query in this phase used `rows` as a BigQuery table alias.

## Authorization Gate

Pre-run gates were all empty or unset:

| Gate | State |
|---|---|
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Live write authorization was set only inside the same PowerShell process:

```powershell
try {
  $env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2025 --season-end 2025 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2025_001
} finally {
  Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Post-wrapper checks confirmed `ALLOW_ADVANCED_METRICS_MATERIALIZATION` was removed. All other write, deploy, packet, and local subprocess gates remained unset.

## Git State

Latest commit at start: `3c83af6 Expand nflverse Pigskin packets through 2024`.

No files were staged. The working tree still contained the known untracked historical validation backlog plus the Phase 29.45 and Phase 29.46 owner-review reports. No commit was created.

## Baseline Checks

All baseline checks passed before the write:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_advanced_metrics.py` | pass |
| `py_compile src\nflverse_staging.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_advanced_metrics` | pass, 12 tests |
| `unittest tests.test_nflverse_staging` | pass, 11 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Staging Source Precheck

Read-only checks confirmed 2025 source coverage existed in the staging layer.

| Table | Total rows | 2025 rows | 2026+ rows | Season range | 2025 week range |
|---|---:|---:|---:|---|---|
| `stg_player_identity` | 526,550 | 46,831 | 0 | 2014-2025 | 1-22 |
| `stg_game_context` | 3,295 | 285 | 0 | 2014-2025 | 1-22 |
| `stg_player_week_stats` | 217,230 | 19,399 | 0 | 2014-2025 | 1-22 |
| `stg_team_week_stats` | 6,590 | 570 | 0 | 2014-2025 | 1-22 |
| `stg_play_player_events` | 1,407,632 | 116,369 | 0 | 2014-2025 | 1-22 |
| `stg_participation_context` | 300,812 | 26,612 | 0 | 2014-2025 | 1-22 |

## Feature Pre-Write State

The target feature tables had no 2025 rows before materialization.

| Table | Total before | 2025 rows before | 2026+ rows before | Season range before |
|---|---:|---:|---:|---|
| `player_week_advanced_metrics` | 197,831 | 0 | 0 | 2014-2024 |
| `team_week_context_metrics` | 6,020 | 0 | 0 | 2014-2024 |
| `qb_week_environment_metrics` | 7,350 | 0 | 0 | 2014-2024 |

Pre-write derived view counts:

| Object | Row count |
|---|---:|
| `player_recent_advanced_metrics_current` | 5,883 |
| `player_role_usage_metrics_current` | 5,883 |
| `pigskin_player_context_packet_current` | 3,574 |
| `compat_pigskin_player_context_current` | 3,574 |

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2025 --season-end 2025 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2025_001
```

Result: pass, `dry_run=True`, `wrote=False`, 3 target summaries.

| Target | Planned rows | Source rows | Duplicate groups | Status |
|---|---:|---:|---:|---|
| `player_week_advanced_metrics` | 19,399 | 19,399 | 0 | ready with warnings |
| `team_week_context_metrics` | 570 | 570 | 0 | ready with warnings |
| `qb_week_environment_metrics` | 692 | 19,819 passer events | 0 | ready with warnings |

Dry-run warnings were expected for v0:

- Route metrics and red-zone or high-value-touch metrics remain blocked in `player_week_advanced_metrics`.
- `seconds_per_play`, `pass_rate_over_expected`, pass/rush EPA split, and red-zone rates remain null in `team_week_context_metrics` pending source-field review.
- Sack, scramble, designed-rush, and pass-rate-over-expected context fields remain unavailable in `qb_week_environment_metrics`.
- Feature SQL for base targets uses staging tables, not legacy or raw source tables.
- Pigskin packet refresh remained out of scope.

## Live Write Result

The live write command completed with exit code 0 and `wrote=True`.

| Target | Merge affected rows | Post-write bounded rows | Duplicate groups | Metric versions | Feature run IDs | Season | Weeks |
|---|---:|---:|---:|---:|---:|---|---|
| `player_week_advanced_metrics` | 19,399 | 19,399 | 0 | 1 | 1 | 2025 | 1-22 |
| `team_week_context_metrics` | 570 | 570 | 0 | 1 | 1 | 2025 | 1-22 |
| `qb_week_environment_metrics` | 692 | 692 | 0 | 1 | 1 | 2025 | 1-22 |

All three targets used MERGE. No 2014 backfill rows or 2026+ rows were written by this phase.

## Post-Write Feature Verification

| Table | Total rows after | 2025 rows after | 2026+ rows after | Season range | 2025 week range |
|---|---:|---:|---:|---|---|
| `player_week_advanced_metrics` | 217,230 | 19,399 | 0 | 2014-2025 | 1-22 |
| `team_week_context_metrics` | 6,590 | 570 | 0 | 2014-2025 | 1-22 |
| `qb_week_environment_metrics` | 8,042 | 692 | 0 | 2014-2025 | 1-22 |

2025 quality checks:

| Table | Duplicate groups | Missing freshness | Missing flags | Invalid range rows | Blocked metrics non-null |
|---|---:|---:|---:|---:|---:|
| `player_week_advanced_metrics` | 0 | 0 | 0 | 0 | 0 |
| `team_week_context_metrics` | 0 | 0 | 0 | 0 | 0 |
| `qb_week_environment_metrics` | 0 | 0 | 0 | 0 | 0 |

Metric version distribution:

| Table | Metric version | 2025 rows |
|---|---|---:|
| `player_week_advanced_metrics` | `nflverse_adv_metrics_v0_2025_001` | 19,399 |
| `team_week_context_metrics` | `nflverse_adv_metrics_v0_2025_001` | 570 |
| `qb_week_environment_metrics` | `nflverse_adv_metrics_v0_2025_001` | 692 |

## Metric Sanity Results

`player_week_advanced_metrics` 2025 null and denominator checks:

| Check | Count |
|---|---:|
| `target_share` null rows | 0 |
| `air_yards_share` null rows | 13,764 |
| `wopr` null rows | 13,764 |
| `epa_per_opportunity` null rows | 13,858 |
| `success_rate` null rows | 13,764 |
| `cpoe` null rows | 14,216 |
| `snap_share` null rows | 47 |
| zero opportunity denominator rows | 13,858 |

Top WOPR examples were plausible for high-volume receiving weeks: `J.Smith-Njigba`, `D.London`, `P.Nacua`, `J.Chase`, and `D.Smith`. Top weighted-opportunity examples included `J.Chase`, `C.McCaffrey`, and `P.Nacua`.

EPA per opportunity remains volatile at small sample sizes. Even with an opportunity floor of 5, top rows included quarterback weeks such as `T.Lawrence` week 15, `B.Mayfield` week 5, and `M.Trubisky` week 18. This is not a blocking data-integrity issue, but it should be handled carefully in any user-facing ranking.

`team_week_context_metrics` 2025 checks:

| Check | Result |
|---|---:|
| Row count | 570 |
| `neutral_pass_rate` min | 0 |
| `neutral_pass_rate` avg | 0.4262 |
| `neutral_pass_rate` max | 1 |
| `opponent_epa_allowed` min | -0.5131 |
| `opponent_epa_allowed` avg | 0.0106 |
| `opponent_epa_allowed` max | 0.4486 |
| `pass_rate_over_expected` null rows | 570 |

Top and bottom EPA/success-rate examples were plausible. `DET` week 10 and `NE` week 17 appeared near the top by team EPA per play; `CIN` week 3 and `MIN` week 13 appeared near the bottom.

`qb_week_environment_metrics` 2025 checks:

| Check | Result |
|---|---:|
| Row count | 692 |
| `cpoe` coverage rows | 677 |
| `deep_attempt_rate` min | 0 |
| `deep_attempt_rate` avg | 0.1022 |
| `deep_attempt_rate` max | 1 |
| `sacks` null rows | 692 |
| `scrambles` null rows | 692 |
| `pass_rate_over_expected_context` null rows | 692 |

Top and bottom EPA examples were plausible for quarterback-week volatility. Missing sack, scramble, and PROE context fields remain expected v0 limitations.

## Blocked Metric Confirmation

Blocked or unavailable v0 metrics remained null:

- Red-zone and high-value-touch player metrics remained blocked.
- Team PROE and red-zone rates remained null.
- QB sack, scramble, designed-rush, and PROE context remained null.

No blocked metric unexpectedly materialized non-null values.

## Derived Current-View Behavior

No direct write targeted current or Pigskin packet objects.

Derived current views updated because the base advanced metrics now include 2025:

| Object | Pre-write rows | Post-write rows | Behavior |
|---|---:|---:|---|
| `player_recent_advanced_metrics_current` | 5,883 | 6,269 | derived from base metrics |
| `player_role_usage_metrics_current` | 5,883 | 6,269 | derived from base metrics |
| `pigskin_player_context_packet_current` | 3,574 | 3,574 | unchanged |
| `compat_pigskin_player_context_current` | 3,574 | 3,574 | unchanged |

This is acceptable for the base metrics phase. Pigskin packet refresh remains a separate authorized phase.

## 2025 And Week 22 Behavior

All three targets covered 2025 weeks 1 through 22 after materialization:

- `player_week_advanced_metrics`: 19,399 rows.
- `team_week_context_metrics`: 570 rows.
- `qb_week_environment_metrics`: 692 rows.

Week 22 rows came from the completed-season historical lane, not a current-season scrape or weekly refresh.

## 2026+ Separation

No 2026+ rows were present in the staging precheck and no 2026+ rows were written to the feature targets.

## Non-Target Object Verification

Raw tables remained at the Phase 29.45 counts:

| Table | Total rows | 2025 rows | 2026+ rows |
|---|---:|---:|---:|
| `raw_nflverse_schedules` | 3,295 | 285 | 0 |
| `raw_nflverse_rosters` | 35,336 | 3,134 | 0 |
| `raw_nflverse_rosters_weekly` | 526,550 | 46,831 | 0 |
| `raw_nflverse_weekly` | 217,230 | 19,399 | 0 |
| `raw_nflverse_pbp` | 580,005 | 48,771 | 0 |
| `raw_nflverse_snap_counts` | 300,812 | 26,612 | 0 |

Staging tables remained at the Phase 29.46 counts.

Score lanes were unchanged:

| Object | Row count |
|---|---:|
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validation Results

Post-write validation patterns all passed:

| Pattern | Result |
|---|---|
| `raw_nflverse` | pass, 3 passed, 0 failed, informational coverage warning |
| `stg_` | pass, 7 passed, 0 failed |
| `advanced_metrics` | pass, 4 passed, 0 failed |
| `compat_pigskin` | pass, 2 passed, 0 failed |
| `trade_player_scores` | pass, 12 passed, 0 failed |
| `trade_pick_scores` | pass, 17 passed, 0 failed, existing informational model-version warning |

## Final Local Checks

All final local checks passed after materialization:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_advanced_metrics.py` | pass |
| `py_compile src\nflverse_staging.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_advanced_metrics` | pass, 12 tests |
| `unittest tests.test_nflverse_staging` | pass, 11 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Deployment And Flag State

Production was inspected read-only:

| Field | Value |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flags remained false:

- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Staging was inspected read-only:

| Field | Value |
|---|---|
| Service | `nfl-studio-dashboard-staging` |
| Revision | `nfl-studio-dashboard-staging-00029-jtb` |
| Traffic | `nfl-studio-dashboard-staging-00029-jtb:100` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

No production or staging deploy was run.

## Remaining Warnings

- v0 route, red-zone, high-value-touch, team PROE, QB sack, QB scramble, designed-rush, and QB context PROE fields remain unavailable or intentionally blocked.
- `player_recent_advanced_metrics_current` and `player_role_usage_metrics_current` are derived views, so their counts changed when the base 2025 metrics were written. Pigskin packet tables did not refresh.
- `trade_pick_scores` validation retains the existing informational model-version warning.
- The repository still contains known untracked historical validation backlog and owner-review reports.

## Recommended Next Phase

Run the separate 2025 Pigskin current-view and packet dry-run phase, then perform a gated Pigskin packet refresh only if that dry-run is clean. Do not present 2025 advanced metrics through Pigskin as refreshed packet content until the packet phase runs.
