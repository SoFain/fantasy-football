# Phase 29.28: 2018-2020 Base Advanced Metrics Materialization

Date: 2026-06-30

Final decision: **2018-2020 ADVANCED METRICS MATERIALIZED WITH WARNINGS**

## Scope

Materialized only the 2018-2020 base advanced metrics from the 2018-2020 nflverse staging layer into:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

No raw backfill, staging materialization rerun, Pigskin packet refresh, deployment, feature flag change, Cloud Run Job trigger, Scheduler change, Pigskin prompt, LLM action, scraping, or Firebase artifact creation occurred.

Metric version:

```text
nflverse_adv_metrics_v0_2018_2020_001
```

## Authorization Gate

Initial gate state was empty or unset for:

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

The live write used the required same-session wrapper:

```powershell
try {
  $env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2018 --season-end 2020 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2018_2020_001
} finally {
  Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Post-write gate state was empty or unset for all checked gates.

## Git State

Latest commit at start/end of phase:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

No files were staged. The known untracked historical validation backlog remains. This report is the only new Phase 29.28 artifact from this phase.

## Baseline Checks

All baseline checks passed before materialization:

- `scripts/check_deployment_safety.py`: PASS
- `py_compile src\nflverse_advanced_metrics.py`: PASS
- `py_compile src\nflverse_staging.py`: PASS
- `py_compile src\nflverse_backfill.py`: PASS
- `py_compile src\nflverse_backfill_plan.py`: PASS
- `compileall -q src scripts`: PASS
- `unittest tests.test_nflverse_advanced_metrics`: PASS, 12 tests
- `unittest tests.test_nflverse_staging`: PASS, 11 tests
- `unittest discover tests`: PASS, 487 tests
- `scripts/run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: PASS, catalog discovered through validation 200

## Staging Source Precheck

2018-2020 staging rows existed and matched Phase 29.27:

| Table | 2018 | 2019 | 2020 | Total | Week Range |
|---|---:|---:|---:|---:|---|
| `stg_player_identity` | 52,200 | 51,630 | 44,124 | 147,954 | 1-21 |
| `stg_game_context` | 267 | 267 | 269 | 803 | 1-21 |
| `stg_player_week_stats` | 17,393 | 17,341 | 17,581 | 52,315 | 1-21 |
| `stg_team_week_stats` | 534 | 534 | 538 | 1,606 | 1-21 |
| `stg_play_player_events` | 114,473 | 114,616 | 116,621 | 345,710 | 1-21 |
| `stg_participation_context` | 23,877 | 23,862 | 24,999 | 72,738 | 1-21 |

## Feature Pre-Write State

Before the write, the 2018-2020 bounded feature rows were empty:

| Feature Table | Total Before | 2018-2020 Rows Before |
|---|---:|---:|
| `player_week_advanced_metrics` | 70,180 | 0 |
| `team_week_context_metrics` | 2,136 | 0 |
| `qb_week_environment_metrics` | 2,525 | 0 |

Derived/current and packet objects before the write:

- `player_recent_advanced_metrics_current`: 3,128
- `player_role_usage_metrics_current`: 3,128
- `pigskin_player_context_packet_current`: 1,587
- `compat_pigskin_player_context_current`: 1,587

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2018 --season-end 2020 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2018_2020_001
```

Dry-run result: no writes.

| Target | Planned Rows | Source Rows | Duplicate Keys | Readiness |
|---|---:|---:|---:|---|
| `player_week_advanced_metrics` | 52,315 | 52,315 | 0 | ready with warnings |
| `team_week_context_metrics` | 1,606 | 1,606 | 0 | ready with warnings |
| `qb_week_environment_metrics` | 1,988 | 60,167 passer event rows | 0 | ready with warnings |

Dry-run diagnostics:

- `player_week_advanced_metrics`: 1,090 missing identity warning rows, 36,339 null WOPR rows, 36,339 null air-yards-share rows, 36,694 null EPA-per-opportunity rows, 1,234 null snap-share rows.
- `team_week_context_metrics`: 64 missing game-context warning rows, 1,606 null `seconds_per_play`, 1,606 null `pass_rate_over_expected`, 1,606 blocked red-zone metric rows.
- `qb_week_environment_metrics`: 185 missing QB identity warning rows, 46 null CPOE rows, 1,988 sack-field unavailable rows, 1,988 scramble-field unavailable rows.

Blocked metrics remained blocked in the plan:

- Player route, first-read, pressure, contact-yard, alignment, red-zone, high-value-touch, touchdown-rate, and reception-dependent metrics.
- Team seconds-per-play, pass-rate-over-expected, pass/rush EPA split, and red-zone rates.
- QB sacks, scrambles, designed rushes, sack rate, scramble rate, and pass-rate-over-expected context.

The CLI emitted stale generic warning text referencing earlier Phase 29.9/29.10 authorization language, but the executed command and wrapper matched Phase 29.28.

## Live Advanced Metrics Write

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2018 --season-end 2020 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2018_2020_001
```

The command ran once inside the temporary `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true` wrapper.

Live write result:

| Target | DML Affected Rows | Post-Write Rows | Duplicate Keys | Feature Run IDs | Metric Versions | SQL Kind | Season Range | Week Range |
|---|---:|---:|---:|---:|---:|---|---|---|
| `player_week_advanced_metrics` | 52,315 | 52,315 | 0 | 3 | 1 | MERGE | 2018-2020 | 1-21 |
| `team_week_context_metrics` | 1,606 | 1,606 | 0 | 3 | 1 | MERGE | 2018-2020 | 1-21 |
| `qb_week_environment_metrics` | 1,988 | 1,988 | 0 | 3 | 1 | MERGE | 2018-2020 | 1-21 |

No 2014 rows were touched by the bounded write.

## Post-Write Feature Verification

| Target | 2018 | 2019 | 2020 | Total 2018-2020 | Duplicate Keys | Missing Freshness | Missing Flags | Invalid Range Rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `player_week_advanced_metrics` | 17,393 | 17,341 | 17,581 | 52,315 | 0 | 0 | 0 | 0 |
| `team_week_context_metrics` | 534 | 534 | 538 | 1,606 | 0 | 0 | 0 | 0 |
| `qb_week_environment_metrics` | 653 | 653 | 682 | 1,988 | 0 | 0 | 0 | 0 |

Metric version distribution:

- `player_week_advanced_metrics`: 52,315 rows for `nflverse_adv_metrics_v0_2018_2020_001`, 3 feature run IDs.
- `team_week_context_metrics`: 1,606 rows for `nflverse_adv_metrics_v0_2018_2020_001`, 3 feature run IDs.
- `qb_week_environment_metrics`: 1,988 rows for `nflverse_adv_metrics_v0_2018_2020_001`, 3 feature run IDs.

Null and blocked metric counts:

| Metric Area | Count |
|---|---:|
| Player null `target_share` | 0 |
| Player null `air_yards_share` | 36,339 |
| Player null `wopr` | 36,339 |
| Player null `epa_per_opportunity` | 36,694 |
| Player null `success_rate` | 36,339 |
| Player null `cpoe` | 37,521 |
| Player null `snap_share` | 1,234 |
| Player blocked high-value/red-zone non-null rows | 0 |
| Team null `seconds_per_play` | 1,606 |
| Team null `pass_rate_over_expected` | 1,606 |
| Team null `team_epa_per_play` | 0 |
| Team null `team_success_rate` | 0 |
| Team blocked split/red-zone non-null rows | 0 |
| QB null `cpoe` | 46 |
| QB null `epa_per_dropback` | 0 |
| QB null `deep_attempt_rate` | 0 |
| QB blocked sack/scramble/context non-null rows | 0 |

Unsafe metrics remained null or blocked as expected.

## Metric Sanity Review

Player sanity checks:

- Top WOPR rows are plausible high-volume receiving weeks: Michael Thomas 2020 Week 11, Julio Jones 2019 Week 15, Julio Jones 2018 Week 1, DK Metcalf 2020 Week 12, Kenny Golladay 2018 Week 11.
- Top target-share rows are plausible high-target weeks: DeAndre Hopkins, Michael Thomas, Kenny Golladay, George Kittle, Julio Jones.
- Top weighted-opportunity rows are plausible high-workload RB weeks: Alvin Kamara 2018 Week 3, Ezekiel Elliott 2018 Week 14, Dalvin Cook 2020 Week 13, Leonard Fournette 2019 Week 12, Austin Ekeler 2020 Week 12.
- Top EPA-per-opportunity rows with at least 20 opportunities include Tyler Lockett 2020 Week 7, Aaron Jones 2019 Week 8, Kareem Hunt 2018 Week 4, Tyreek Hill 2019 Week 10, Julio Jones 2019 Week 15.
- Null WOPR is concentrated in defensive, special teams, line, and non-receiving positions. WR/RB/TE still retain broad coverage.

Team sanity checks:

- Top team EPA-per-play rows include 2019 BAL over MIA, 2019 LAC over JAX, 2018 CHI over TB, 2020 TEN over DET, and 2019 GB over LV.
- Bottom team EPA-per-play rows include 2019 MIA vs NE, 2020 LAC vs NE, 2018 ARI vs DEN, 2020 LV vs ATL, and 2019 NYG vs NE.
- Neutral pass rate distribution: min 0.000, average 0.442, max 1.000.
- Opponent EPA allowed distribution: min -0.591, average -0.004, max 0.518.
- `pass_rate_over_expected` remains null for all 1,606 team-week rows by design.

QB sanity checks:

- Top EPA-per-dropback rows with at least 20 dropbacks include Lamar Jackson 2019 Week 1, Philip Rivers 2019 Week 14, Ben Roethlisberger 2018 Week 10, Lamar Jackson 2019 Week 12, and Ryan Fitzpatrick 2018 Week 1.
- Bottom EPA-per-dropback rows include Ryan Fitzpatrick 2019 Week 2, Brandon Allen 2020 Week 17, Nathan Peterman 2018 Week 1, Sam Darnold 2019 Week 7, and Luke Falk 2019 Week 5.
- CPOE coverage: 1,942 of 1,988 QB-week rows.
- Deep attempt rate distribution: min 0.000, average 0.119, max 1.000.
- Sack and scramble fields remain null for all 1,988 QB-week rows.

No formula tuning was performed.

## Non-Target Verification

Raw nflverse counts remained unchanged:

| Object | Count |
|---|---:|
| `raw_nflverse_schedules` | 1,871 |
| `raw_nflverse_rosters` | 19,805 |
| `raw_nflverse_rosters_weekly` | 294,691 |
| `raw_nflverse_weekly` | 122,495 |
| `raw_nflverse_pbp` | 332,721 |
| `raw_nflverse_snap_counts` | 168,196 |

Staging counts remained unchanged from the expanded 2014-2020 staging state:

| Object | Count |
|---|---:|
| `stg_player_identity` | 294,691 |
| `stg_game_context` | 1,871 |
| `stg_player_week_stats` | 122,495 |
| `stg_team_week_stats` | 3,742 |
| `stg_play_player_events` | 812,370 |
| `stg_participation_context` | 168,196 |

Pigskin packets and score lanes remained unchanged:

| Object | Count |
|---|---:|
| `pigskin_player_context_packet_current` | 1,587 |
| `compat_pigskin_player_context_current` | 1,587 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

Derived current views changed because they read from base metrics:

| View | Before | After | Direct Write |
|---|---:|---:|---|
| `player_recent_advanced_metrics_current` | 3,128 | 4,344 | No |
| `player_role_usage_metrics_current` | 3,128 | 4,344 | No |

## Validation Results

Post-write validation commands:

| Pattern | Result |
|---|---|
| `raw_nflverse` | PASS, 3 passed, 0 failed. Validation 181 returned informational coverage review rows for 2014-2020. |
| `stg_` | PASS, 7 passed, 0 failed. |
| `advanced_metrics` | PASS, 4 passed, 0 failed. |
| `compat_pigskin` | PASS, 2 passed, 0 failed. |
| `trade_player_scores` | PASS, 12 passed, 0 failed. |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Validation 178 returned the expected informational model-version coverage row. |

## Final Local Checks

Final checks after materialization:

- `scripts/check_deployment_safety.py`: PASS
- `py_compile src\nflverse_advanced_metrics.py`: PASS
- `py_compile src\nflverse_staging.py`: PASS
- `py_compile src\nflverse_backfill.py`: PASS
- `py_compile src\nflverse_backfill_plan.py`: PASS
- `compileall -q src scripts`: PASS
- `unittest tests.test_nflverse_advanced_metrics`: PASS, 12 tests
- `unittest tests.test_nflverse_staging`: PASS, 11 tests
- `unittest discover tests`: PASS, 487 tests
- `scripts/run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: PASS, catalog discovered through validation 200

## Service State

Read-only Cloud Run describe confirmed no deployment occurred.

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Production risk flags: false
- Trade History compatibility: false
- Trade Analyzer score flags: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

## Remaining Warnings

- 2020 source shape remains uneven: `stg_game_context` has 269 rows, while 2018 and 2019 have 267.
- 2020 `stg_player_identity` remains lower than 2018 and 2019, matching the lower 2020 `rosters_weekly` source count.
- Dry-run identity warning counters remain useful for follow-up even though duplicate and required metadata checks passed.
- `pass_rate_over_expected`, seconds-per-play, pass/rush split EPA, team red-zone rates, route metrics, high-value touches, touchdown-rate metrics, sacks, scrambles, and designed rush splits remain intentionally blocked or null.
- Current metric views now reflect 2018-2020 derived base metrics, but no direct current-view write occurred.
- Raw nflverse validation 181 remains informational for 2014-2020 coverage.
- Trade-pick validation 178 remains informational for model-version coverage.

## Recommended Next Phase

Proceed to a bounded 2018-2020 Pigskin current-view and packet dry-run only. Do not refresh Pigskin packets until the packet dry-run confirms the expanded 2018-2020 metrics select the intended player/context rows and preserve raw-source isolation.
