# Phase 29.17 - Authorized 2015 Base Advanced Metrics Materialization

Date: 2026-06-29

Final decision: 2015 ADVANCED METRICS MATERIALIZED WITH WARNINGS

## Scope

Authorized materialization of 2015 base advanced metrics from the 2015 nflverse staging layer.

Target season range:

- `season_start=2015`
- `season_end=2015`

Metric version:

- `nflverse_adv_metrics_v0_2015_001`

Write targets:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

No raw backfill, staging materialization, Pigskin packet refresh, direct current-view write, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, ranking build, Pigskin prompt, LLM-backed action, scrape, Firebase artifact, or commit occurred.

## Authorization Gate State

All gates were unset before the live write.

| Gate | Before | During live write | After |
| --- | --- | --- | --- |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset | `true` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset | unset | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset | unset | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset | unset | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset | unset | unset |

The advanced-metrics write gate was set only inside the same PowerShell `try/finally` wrapper around the one live advanced-metrics command.

## Git State

Latest commit before the phase:

`4805610 Build nflverse Pigskin canary pipeline`

Worktree:

- Existing untracked historical validation backlog remained untracked.
- Phase 29 follow-up reports remained untracked.
- No files were staged.
- No commit was created.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_advanced_metrics.py src\nflverse_staging.py src\nflverse_backfill.py src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_advanced_metrics` | 12 tests passed |
| `python -m unittest tests.test_nflverse_staging` | 11 tests passed |
| `python -m unittest discover tests` | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

PowerShell displayed `NativeCommandError` wrappers for stderr logging during some Python test commands, but the process exit codes were 0 and the test summaries were PASS.

## Staging Source Precheck

2015 staging source rows were present before advanced-metrics materialization.

| Staging Table | 2015 Rows | Missing Freshness | Missing Flags |
| --- | ---: | ---: | ---: |
| `stg_player_identity` | 30,201 | 0 | 0 |
| `stg_game_context` | 267 | 0 | 0 |
| `stg_player_week_stats` | 17,592 | 0 | 0 |
| `stg_team_week_stats` | 534 | 0 | 0 |
| `stg_play_player_events` | 118,069 | 0 | 0 |
| `stg_participation_context` | 23,842 | 0 | 0 |

## Feature Pre-Write State

Before the write, the target feature tables contained only 2014 rows.

| Target Table | Total Rows Before | 2015 Rows Before | Season Range Before |
| --- | ---: | ---: | --- |
| `player_week_advanced_metrics` | 17,601 | 0 | 2014 to 2014 |
| `team_week_context_metrics` | 534 | 0 | 2014 to 2014 |
| `qb_week_environment_metrics` | 643 | 0 | 2014 to 2014 |

## Dry-Run Plan

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2015 --season-end 2015 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2015_001
```

Result:

- Exit code: 0
- `dry_run=True`
- `wrote=False`
- `metric_version=nflverse_adv_metrics_v0_2015_001`
- `season_start=2015`
- `season_end=2015`

| Target | Planned Rows | Source Rows | Duplicate Rows | Readiness |
| --- | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 17,592 | 17,592 | 0 | Ready with warnings |
| `team_week_context_metrics` | 534 | 534 | 0 | Ready with warnings |
| `qb_week_environment_metrics` | 618 | 20,432 | 0 | Ready with warnings |

Dry-run warning classes:

- `player_week_advanced_metrics`: route metrics, pressure metrics, yards before/after contact, alignment, red-zone usage, high-value touches, touchdown rates, and reception-flag-dependent metrics remain blocked in v0.
- `team_week_context_metrics`: seconds per play, pass rate over expected, pass/rush EPA split, and red-zone rates remain null pending source-field review.
- `qb_week_environment_metrics`: sacks, scrambles, designed rushes, sack rate, scramble rate, and pass-rate-over-expected context remain unavailable in v0.

The dry-run confirmed feature SQL uses staging tables, not legacy/raw tables. Pigskin packet refresh remained out of scope.

## Live Write

Command:

```powershell
try {
  $env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2015 --season-end 2015 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2015_001
} finally {
  Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Result:

- Exit code: 0
- `dry_run=False`
- `wrote=True`
- `metric_version=nflverse_adv_metrics_v0_2015_001`
- `season_start=2015`
- `season_end=2015`

| Target | Written Rows | Source Rows | Duplicate Rows | Readiness |
| --- | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 17,592 | 17,592 | 0 | Ready with warnings |
| `team_week_context_metrics` | 534 | 534 | 0 | Ready with warnings |
| `qb_week_environment_metrics` | 618 | 20,432 | 0 | Ready with warnings |

The authorization gate was removed immediately after the command.

## Post-Write Feature Verification

| Target Table | Total Rows After | 2015 Rows After | 2015 Week Range | Duplicate Key Groups | Metric Versions | Feature Run IDs |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 35,193 | 17,592 | 1 to 21 | 0 | 1 | 1 |
| `team_week_context_metrics` | 1,068 | 534 | 1 to 21 | 0 | 1 | 1 |
| `qb_week_environment_metrics` | 1,261 | 618 | 1 to 21 | 0 | 1 | 1 |

Metadata checks:

| Target Table | Missing Freshness | Missing Flags | Missing `created_at` | Invalid Metric Ranges |
| --- | ---: | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 0 | 0 | 0 | 0 |
| `team_week_context_metrics` | 0 | 0 | 0 | 0 |
| `qb_week_environment_metrics` | 0 | 0 | 0 | 0 |

Blocked metrics remained blocked:

- `player_week_advanced_metrics`: high-value touch blocked fields had 0 non-null rows.
- `team_week_context_metrics`: red-zone rates and pass/rush EPA split blocked fields had 0 non-null rows.
- `qb_week_environment_metrics`: blocked QB sack/scramble fields had 0 non-null rows.

## Raw and Staging Tables Unchanged

Raw source counts after the phase:

| Raw Table | Total Rows | 2015 Rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 534 | 267 |
| `raw_nflverse_rosters` | 4,341 | 2,189 |
| `raw_nflverse_rosters_weekly` | 60,396 | 30,201 |
| `raw_nflverse_weekly` | 35,193 | 17,592 |
| `raw_nflverse_pbp` | 95,751 | 48,122 |
| `raw_nflverse_snap_counts` | 47,706 | 23,842 |

Staging counts after the phase:

| Staging Table | Total Rows | 2015 Rows |
| --- | ---: | ---: |
| `stg_player_identity` | 60,396 | 30,201 |
| `stg_game_context` | 534 | 267 |
| `stg_player_week_stats` | 35,193 | 17,592 |
| `stg_team_week_stats` | 1,068 | 534 |
| `stg_play_player_events` | 234,469 | 118,069 |
| `stg_participation_context` | 47,706 | 23,842 |

No raw backfill or staging materialization command was run in this phase.

## Non-Target Objects

No direct write was made to Pigskin packets, Trade Analyzer scores, or draft-pick scores.

| Object | Row Count After | Note |
| --- | ---: | --- |
| `pigskin_player_context_packet_current` | 482 | Unchanged packet surface |
| `compat_pigskin_player_context_current` | 482 | Unchanged compatibility packet surface |
| `trade_player_scores` | 154 | Non-target |
| `trade_player_scores_current` | 77 | Non-target |
| `compat_trade_player_scores_current` | 77 | Non-target |
| `trade_pick_scores` | 64 | Non-target |
| `trade_pick_scores_current` | 64 | Non-target |
| `compat_trade_pick_scores_current` | 64 | Non-target |
| `player_recent_advanced_metrics_current` | 2,309 | Derived current view now reflects 2014 and 2015 base metrics |
| `player_role_usage_metrics_current` | 2,309 | Derived current view now reflects 2014 and 2015 base metrics |

The two current advanced-metrics views changed by derivation only. They were not direct write targets.

## Metric Sanity Review

Player examples:

| Metric | Example Rows |
| --- | --- |
| Top WOPR | `S.Watkins BUF W9 wopr=1.700 targets=8 target_share=0.667 air_yards_share=1.000`; `D.Walker TEN W17 wopr=1.266`; `J.Jones ATL W3 wopr=1.260` |
| Top target share | `S.Watkins BUF W9 target_share=0.667`; `D.Walker TEN W17 target_share=0.560`; `J.Jones ATL W3 target_share=0.556` |
| Top weighted opportunity | `A.Brown PIT W9 weighted_opportunity=59.5`; `D.Hopkins HOU W4 weighted_opportunity=55.0`; `D.Adams GB W10 weighted_opportunity=52.5` |
| Top EPA per opportunity | `R.Wilson SEA W15 epa_per_opportunity=4.019`; `B.Hoyer HOU W6 epa_per_opportunity=3.809`; `R.Wilson SEA W13 epa_per_opportunity=3.327` |

Skill-position WOPR null review:

| Position | Rows | Null WOPR | Null Rate |
| --- | ---: | ---: | ---: |
| WR | 2,304 | 256 | 0.111 |
| RB | 1,552 | 146 | 0.094 |
| TE | 1,157 | 109 | 0.094 |
| QB | 630 | 12 | 0.019 |
| FB | 206 | 62 | 0.301 |

Snap-share coverage:

| Position | Rows | Snap-Share Rows | Coverage Rate |
| --- | ---: | ---: | ---: |
| WR | 2,304 | 1,785 | 0.775 |
| RB | 1,552 | 1,198 | 0.772 |
| TE | 1,157 | 896 | 0.774 |
| QB | 630 | 491 | 0.779 |
| FB | 206 | 163 | 0.791 |

Denominator and missing-data flags:

- `null_target_share=0`
- `null_air_yards_share=12282`
- `null_opportunity_share=0`
- `rows_with_denominator_missing_sample_flags=17592`

Team context examples:

| Metric | Example Rows |
| --- | --- |
| Top team EPA/play | `PIT W2 epa=0.412 success=0.493 plays=70`; `NE W3 epa=0.367 success=0.589 plays=96`; `KC W8 epa=0.336 success=0.531 plays=81` |
| Bottom team EPA/play | `JAX W17 epa=-0.435 success=0.347`; `SF W3 epa=-0.433 success=0.388`; `IND W14 epa=-0.357 success=0.323` |
| Top success rate | `DET W15 success=0.671`; `NE W3 success=0.589`; `NYG W8 success=0.589` |
| Bottom success rate | `HOU W18 success=0.237`; `MIA W13 success=0.262`; `CHI W3 success=0.284` |

Team distributions:

- `neutral_pass_rate`: min 0.000, avg 0.441, max 0.722
- `opponent_epa_allowed`: min -0.435, avg -0.017, max 0.412
- `pass_rate_over_expected`: 534 null rows, expected v0 blocked metric

QB environment examples:

| Metric | Example Rows |
| --- | --- |
| Top EPA/dropback | `M.Mariota TEN W1 epa_per_dropback=1.126 cpoe=21.861`; `L.Jones PIT W6 epa_per_dropback=0.927`; `T.Bridgewater MIN W15 epa_per_dropback=0.911` |
| Bottom EPA/dropback | `P.Manning DEN W10 epa_per_dropback=-1.170 cpoe=-32.209`; `C.Kaepernick SF W3 epa_per_dropback=-1.139`; `T.Romo DAL W12 epa_per_dropback=-0.982` |

QB coverage:

- Rows: 618
- `cpoe` rows: 613
- `deep_attempt_rate` rows: 618
- `deep_attempt_rate`: min 0.000, avg 0.118, max 1.000
- `sacks`, `scrambles`, `sack_rate`, and `scramble_rate`: 618 null rows each, expected v0 blocked metrics

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Informational warning: raw nflverse now spans 2014 and 2015. |
| `stg_` | 7 passed, 0 failed |
| `advanced_metrics` | 4 passed, 0 failed |
| `compat_pigskin` | 2 passed, 0 failed |
| `trade_player_scores` | 12 passed, 0 failed |
| `trade_pick_scores` | 17 passed, 0 failed. Informational warning: `trade_pick_score_v0_2026_001` has 64 prior rows. |

## Deployment and Flag State

Production remained untouched:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Production risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging remained untouched:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Expected staging-only flags remained true: `USE_COMPAT_TRADE_PLAYER_HISTORY`, `USE_TRADE_ANALYZER_SCORE_V0`, `USE_COMPAT_TRADE_PLAYER_SCORE`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

## Warnings

- Several advanced metrics remain intentionally blocked in v0 until source-field review, including route metrics, pressure/sack/scramble metrics, pass rate over expected, and red-zone/high-value-touch metrics.
- `player_recent_advanced_metrics_current` and `player_role_usage_metrics_current` changed by derivation because they read the base metrics tables. They were not directly written.
- Raw nflverse validations now show a 2014-2015 warehouse span. This is expected after the 2015 canary expansion.
- Draft-pick score validations still report the prior 64-row `trade_pick_score_v0_2026_001` informational review warning.

## Recommended Next Phase

Phase 29.18 should run a strict, 2015-only Pigskin packet refresh dry-run first, then materialize only if explicitly authorized with `ALLOW_PIGSKIN_PACKET_REFRESH=true` in a same-process `try/finally` wrapper.

Do not rerun raw backfill, staging materialization, or base advanced-metrics materialization unless a separate phase explicitly authorizes it.
