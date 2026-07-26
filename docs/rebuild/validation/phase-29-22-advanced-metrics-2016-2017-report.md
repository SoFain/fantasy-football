# Phase 29.22 Advanced Metrics 2016-2017 Report

Date: 2026-06-29

Final decision: **2016-2017 ADVANCED METRICS MATERIALIZED WITH WARNINGS**

## Scope

Authorized base advanced metrics materialization for nflverse seasons 2016 and 2017.

Written objects were limited to:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

No raw backfill, staging materialization, Pigskin packet refresh, ranking build, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, LLM call, Pigskin prompt, scrape, Firebase artifact, or commit occurred.

Metric version:

`nflverse_adv_metrics_v0_2016_2017_001`

Latest commit before and after this phase:

`67f37e7 Expand nflverse Pigskin pipeline to 2015`

## Authorization Gates

Initial gate state:

| Gate | State |
| --- | --- |
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

Write authorization was set only inside the same PowerShell wrapper around the one live advanced metrics command:

```powershell
try {
  $env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"
  echo "ALLOW_ADVANCED_METRICS_MATERIALIZATION=$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION"
  .\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2016 --season-end 2017 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2016_2017_001
} finally {
  Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Final gate state:

| Gate | State |
| --- | --- |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Git State

`git status --short --untracked-files=all` showed the existing untracked historical validation backlog plus current Phase 29 reports. No files were staged.

No tracked source diff existed before this report was created.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_advanced_metrics.py` | PASS |
| `py_compile src\nflverse_staging.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_advanced_metrics` | PASS |
| `unittest tests.test_nflverse_staging` | PASS |
| `unittest discover tests` | PASS |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Staging Source Precheck

2016-2017 staging rows were present before advanced metrics materialization.

| Staging Table | Total Rows | 2016 Rows | 2017 Rows | Bounded Rows |
| --- | ---: | ---: | ---: | ---: |
| `stg_player_identity` | 146737 | 35020 | 51321 | 86341 |
| `stg_game_context` | 1068 | 267 | 267 | 534 |
| `stg_player_week_stats` | 70180 | 17531 | 17456 | 34987 |
| `stg_team_week_stats` | 2136 | 534 | 534 | 1068 |
| `stg_play_player_events` | 466660 | 117281 | 114910 | 232191 |
| `stg_participation_context` | 95458 | 23890 | 23862 | 47752 |

## Feature Pre-Write State

All 2016 and 2017 base advanced metric target counts were zero before this phase.

| Feature Table | Total Rows Before | 2016 Rows Before | 2017 Rows Before | Season Range Before |
| --- | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 35193 | 0 | 0 | 2014-2015 |
| `team_week_context_metrics` | 1068 | 0 | 0 | 2014-2015 |
| `qb_week_environment_metrics` | 1261 | 0 | 0 | 2014-2015 |

## Dry Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2016 --season-end 2017 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2016_2017_001 --output-json %TEMP%\phase29_22_adv_dry_run.json
```

Dry-run exit code: 0

| Target | Readiness | Source Rows | Planned Rows | Duplicate Grain Count | Context Or Identity Gap | Null Or Blocked Counts | Warnings |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `player_week_advanced_metrics` | ready with warnings | 34987 | 34987 | 0 | 1619 | 34987 red-zone/high-value metric rows blocked | route metrics and red-zone/high-value-touch metrics blocked in v0 |
| `team_week_context_metrics` | ready with warnings | 1068 | 1068 | 0 | 94 missing game context joins | 1068 null pace, 1068 null pass-rate-over-expected, 1068 red-zone metrics blocked | pace, PROE, pass/rush EPA split, and red-zone rates remain null pending source review |
| `qb_week_environment_metrics` | ready with warnings | 40016 passer event rows | 1264 | 0 | 66 missing QB identity joins | 1264 unavailable sacks, 1264 unavailable scrambles | sack, scramble, designed-rush, and PROE fields unavailable in v0 |

Dry-run warnings:

- Feature SQL for base targets uses staging tables, not legacy or raw source tables.
- Pigskin packet refresh remains out of scope.
- CLI copy still says Phase 29.9/29.10 in warning strings. This is stale command text, not a data blocker.

## Live Advanced Metrics Write

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2016 --season-end 2017 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2016_2017_001
```

Write exit code: 0

| Target | Write SQL Kind | DML Affected Rows | Bounded Rows After | Duplicate Grain Count After | Metric Version Count | Feature Run ID Count | Missing Flags Rows | Missing Source Freshness Rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `player_week_advanced_metrics` | MERGE | 34987 | 34987 | 0 | 1 | 2 | 0 | 0 |
| `team_week_context_metrics` | MERGE | 1068 | 1068 | 0 | 1 | 2 | 0 | 0 |
| `qb_week_environment_metrics` | MERGE | 1264 | 1264 | 0 | 1 | 2 | 0 | 0 |

The command emitted CLI text saying `phase: 29.10` and a warning saying Phase 29.10 writes were authorized. This appears to be stale CLI copy. The executed command and report scope were Phase 29.22 scoped: `--season-start 2016 --season-end 2017` with only the three base metric targets.

## Post-Write Feature Verification

| Feature Table | Total Rows | 2016 Rows | 2017 Rows | Week Range | Metric Versions | Feature Run IDs | Duplicate Key Groups | Invalid Metric Range Count |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 70180 | 17531 | 17456 | 1-21 | `nflverse_adv_metrics_v0_2016_2017_001` | 2 | 0 | 0 |
| `team_week_context_metrics` | 2136 | 534 | 534 | 1-21 | `nflverse_adv_metrics_v0_2016_2017_001` | 2 | 0 | 0 |
| `qb_week_environment_metrics` | 2525 | 636 | 628 | 1-21 | `nflverse_adv_metrics_v0_2016_2017_001` | 2 | 0 | 0 |

Metadata and flags:

| Feature Table | Missing Source Freshness | Missing Flags | Context Or Identity Gap |
| --- | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 0 | 0 | 1619 missing identity matches |
| `team_week_context_metrics` | 0 | 0 | 94 missing game context joins |
| `qb_week_environment_metrics` | 0 | 0 | 66 missing QB identity joins |

Blocked and null metric checks:

| Feature Table | Check | Count |
| --- | --- | ---: |
| `player_week_advanced_metrics` | `target_share` null | 0 |
| `player_week_advanced_metrics` | `air_yards_share` null | 24404 |
| `player_week_advanced_metrics` | `wopr` null | 24404 |
| `player_week_advanced_metrics` | `epa_per_opportunity` null | 24646 |
| `player_week_advanced_metrics` | `success_rate` null | 24404 |
| `player_week_advanced_metrics` | `cpoe` null | 25158 |
| `player_week_advanced_metrics` | `snap_share` null | 1625 |
| `player_week_advanced_metrics` | blocked red-zone/high-value metrics non-null | 0 |
| `team_week_context_metrics` | `team_success_rate` null | 0 |
| `team_week_context_metrics` | blocked pace, PROE, pass/rush EPA split, red-zone metrics non-null | 0 |
| `qb_week_environment_metrics` | `cpoe` null | 11 |
| `qb_week_environment_metrics` | blocked sack, scramble, designed-rush, sack-rate, scramble-rate, PROE-context metrics non-null | 0 |

## Metric Sanity

Full top-25 sanity query results were saved during execution to `%TEMP%\phase29_22_metric_sanity.json`. Key excerpts:

Top WOPR examples:

| Season | Week | Player | Position | Team | WOPR | Target Share | Air Yards Share |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: |
| 2016 | 17 | R.Matthews | WR | TEN | 1.2943 | 0.5200 | 0.7347 |
| 2017 | 15 | D.Hopkins | WR | HOU | 1.2580 | 0.4483 | 0.8365 |
| 2017 | 2 | D.Hopkins | WR | HOU | 1.2510 | 0.5417 | 0.6264 |
| 2016 | 10 | D.Hopkins | WR | HOU | 1.2500 | 0.4815 | 0.7540 |
| 2017 | 3 | A.Green | WR | CIN | 1.2479 | 0.5000 | 0.7113 |

Player null and denominator summary:

| Metric | Count |
| --- | ---: |
| zero team target denominators | 0 |
| zero team air-yard denominators | 0 |
| zero team opportunity denominators | 0 |
| zero player opportunity denominators | 24646 |
| zero player target denominators | 26358 |
| missing participation context | 1625 |

Team context sanity:

| Metric | Value |
| --- | ---: |
| min team success rate | 0.2344 |
| avg team success rate | 0.4233 |
| max team success rate | 0.6145 |
| min neutral pass rate | 0.0000 |
| avg neutral pass rate | 0.4377 |
| max neutral pass rate | 0.8182 |
| null pass-rate-over-expected rows | 1068 |

Top and bottom team EPA examples:

| Direction | Season | Week | Team | Opponent | EPA Per Play | Success Rate |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| top | 2017 | 2 | LV | NYJ | 0.3998 | 0.5333 |
| top | 2016 | 3 | ATL | NO | 0.3844 | 0.5570 |
| bottom | 2016 | 17 | LA | ARI | -0.5526 | 0.3049 |
| bottom | 2017 | 15 | SEA | LA | -0.5079 | 0.2632 |

QB environment sanity:

| Metric | Value |
| --- | ---: |
| QB rows | 1264 |
| CPOE rows | 1253 |
| deep attempt rate rows | 1264 |
| null sacks | 1264 |
| null scrambles | 1264 |
| min deep attempt rate | 0.0000 |
| avg deep attempt rate | 0.1239 |
| max deep attempt rate | 1.0000 |

Top and bottom QB EPA examples with minimum 20 dropbacks:

| Direction | Season | Week | QB | Team | EPA Per Dropback | Dropbacks | CPOE |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| top | 2017 | 9 | J.Goff | LA | 1.1376 | 22 | 1.4100 |
| top | 2017 | 9 | M.Stafford | DET | 0.9867 | 34 | 14.7240 |
| bottom | 2017 | 1 | S.Tolzien | IND | -1.2583 | 22 | -10.3960 |
| bottom | 2017 | 3 | J.Flacco | BAL | -0.9520 | 20 | -19.6755 |

No formula tuning was performed.

## Blocked Metric Confirmation

Blocked metrics remained null or unavailable by design:

- Player route and alignment fields: `route_share`, route-derived rates, first-read share, pressure-to-sack, contact-yard splits, slot/wide/inline alignment.
- Player red-zone and high-value fields: red-zone targets/carries/touches, inside-10/inside-5 carries, high-value touches, touchdown-rate and reception-flag-dependent metrics.
- Team context blocked fields: seconds per play, pass-rate-over-expected, pass/rush EPA split, red-zone pass/rush rates.
- QB environment blocked fields: sacks, scrambles, designed rushes, sack rate, scramble rate, pass-rate-over-expected context.

## Derived Current-View Behavior

No direct write was made to current views. They changed because they derive from base metric tables.

| Current View | Total Rows | As-Of 2016 Rows | As-Of 2017 Rows | As-Of Season Range |
| --- | ---: | ---: | ---: | --- |
| `player_recent_advanced_metrics_current` | 3128 | 457 | 1874 | 2014-2017 |
| `player_role_usage_metrics_current` | 3128 | 457 | 1874 | 2014-2017 |

## Non-Target Object Verification

Raw row counts were unchanged after advanced metrics materialization.

| Raw Table | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `raw_nflverse_schedules` | 1068 | 267 | 267 |
| `raw_nflverse_rosters` | 10484 | 3061 | 3082 |
| `raw_nflverse_rosters_weekly` | 146737 | 35020 | 51321 |
| `raw_nflverse_weekly` | 70180 | 17531 | 17456 |
| `raw_nflverse_pbp` | 190647 | 47651 | 47245 |
| `raw_nflverse_snap_counts` | 95458 | 23890 | 23862 |

Staging table counts were unchanged after advanced metrics materialization.

| Staging Table | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `stg_player_identity` | 146737 | 35020 | 51321 |
| `stg_game_context` | 1068 | 267 | 267 |
| `stg_player_week_stats` | 70180 | 17531 | 17456 |
| `stg_team_week_stats` | 2136 | 534 | 534 |
| `stg_play_player_events` | 466660 | 117281 | 114910 |
| `stg_participation_context` | 95458 | 23890 | 23862 |

Pigskin packets were not refreshed:

| Object | Total Rows | 2016 Rows | 2017 Rows |
| --- | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 980 | 0 | 0 |
| `compat_pigskin_player_context_current` | 980 | 0 | 0 |

Score lanes were unchanged:

| Object | Rows |
| --- | ---: |
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validations

| Command | Result |
| --- | --- |
| `run_bigquery_validations.py --run --pattern raw_nflverse` | PASS with review warning |
| `run_bigquery_validations.py --run --pattern stg_` | PASS |
| `run_bigquery_validations.py --run --pattern advanced_metrics` | PASS |
| `run_bigquery_validations.py --run --pattern compat_pigskin` | PASS |
| `run_bigquery_validations.py --run --pattern trade_player_scores` | PASS |
| `run_bigquery_validations.py --run --pattern trade_pick_scores` | PASS with informational warning |

Validation warnings:

| Validation | Warning |
| --- | --- |
| `181_raw_nflverse_season_week_coverage.sql` | Informational review query sees raw coverage through 2017. |
| `178_trade_pick_scores_model_version_coverage.sql` | Informational model-version coverage query returned existing `trade_pick_score_v0_2026_001` rows. |

No validation command failed.

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_advanced_metrics.py` | PASS |
| `py_compile src\nflverse_staging.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_advanced_metrics` | PASS |
| `unittest tests.test_nflverse_staging` | PASS |
| `unittest discover tests` | PASS |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, 200 validation files discovered |

## Service Readback

No deployment occurred.

| Service | Revision | Traffic | Image | Relevant Flag State |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100 percent | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | all production risk flags false; Trade Analyzer score false; Trade History compat false; Data Ops trigger and local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100 percent | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score flags true; Trade History compat true; Data Ops trigger and local subprocess flags false |

## Warnings

- Identity or context gaps remain quantified: 1619 player rows with missing identity matches, 94 team rows with missing game context joins, and 66 QB rows with missing QB identity joins.
- Large null counts for WOPR, air-yards share, EPA per opportunity, CPOE, and snap share are denominator or source-driven and surfaced through `missing_data_flags`.
- Blocked route, red-zone, pressure, contact-yard, alignment, sack, scramble, designed-rush, and pass-rate-over-expected metrics remained null.
- Current metric views changed because they derive from the base metric tables. They were not directly written.
- CLI output still labels this write path as `phase: 29.10` and mentions Phase 29.10 authorization. The command and report scope are Phase 29.22.
- Raw `raw_nflverse_*` tables remain internal and not Pigskin or UI-safe surfaces.

## Blockers

None for 2016-2017 base advanced metric materialization.

Pigskin packet refresh remains intentionally not run in this phase.

## Recommended Next Phase

Run an authorized, separate Phase 29.23 Pigskin packet refresh for 2016-2017 only after reviewing the current-view changes and accepting the documented v0 metric nulls and identity gaps.
