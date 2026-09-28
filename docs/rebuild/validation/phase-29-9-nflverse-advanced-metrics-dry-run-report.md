# Phase 29.9 nflverse Advanced Metrics Dry-Run Report

Final decision: **NFLVERSE ADVANCED METRICS DRY RUN READY WITH WARNINGS**

## Scope

Phase 29.9 added a dry-run-only advanced metrics planner for the materialized 2014 nflverse staging layer.

No BigQuery rows were written. No feature marts, Pigskin packets, raw backfill, staging materialization, rankings, deployments, feature flags, Cloud Run Jobs, Scheduler jobs, LLM actions, scraping, or Firebase artifacts were touched.

## Authorization Gate State

Before and after this phase, all checked gates were empty or unset:

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

The future write gate is documented as `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true`, but `--write` still fails closed in Phase 29.9 even if that gate is set. A separate authorized Phase 29.10 is required before any feature-mart write.

## Git State

Latest commit before this phase:

```text
a73656c Document draft pick score release package
```

No files were staged. The worktree still contains the Phase 29 untracked warehouse files and historical validation backlog. Existing tracked modifications remain:

- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/table-classification.md`

Files changed by this phase:

- `src/nflverse_advanced_metrics.py`
- `tests/test_nflverse_advanced_metrics.py`
- `docs/rebuild/validation/phase-29-9-nflverse-advanced-metrics-dry-run-report.md`

## Baseline Checks

Initial baseline passed:

- `scripts/check_deployment_safety.py`
- `py_compile` for `src\nflverse_staging.py`, `src\nflverse_backfill.py`, `src\nflverse_backfill_plan.py`
- `compileall -q src scripts`
- `tests.test_nflverse_staging`
- `tests.test_nflverse_backfill_executor`
- `tests.test_nflverse_backfill_plan`
- `tests.test_nflverse_historical_contracts`
- `tests.test_pigskin_advanced_metrics_contracts`
- `unittest discover tests`
- migrations list: no pending migrations
- validation dry-run: pass, discovered validations through `200_no_pressure_metrics_without_source.sql`

## Module Behavior

Created `src.nflverse_advanced_metrics` with:

- dry-run SQL generation;
- read-only diagnostics;
- source dependency summaries;
- source-field audit output;
- `--dry-run`, `--plan-only`, `--target`, `--all-targets`, bounded season/week options, project/dataset options, `--output-json`, and `--strict`;
- default target set of the three base feature marts;
- current rolling placeholder targets for later;
- fail-closed `--write` behavior.

Default base targets:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

`--all-targets` also includes:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`

## Source Dependencies

Base feature SQL reads only staging tables:

- `stg_player_week_stats`
- `stg_play_player_events`
- `stg_team_week_stats`
- `stg_participation_context`
- `stg_player_identity`
- `stg_game_context`

Base feature SQL does not read:

- `raw_nflverse_*`
- `play_by_play`
- `weekly_metrics`
- feature marts
- Pigskin packet tables

The source-field audit includes read-only `raw_nflverse_pbp.raw_payload_json` checks only to document field availability and mapping risk. Those raw audit checks are not part of the feature-mart SELECTs.

## Source-Field Audit

| Field | Layer | Rows | Non-null | True | v0 status |
|---|---|---:|---:|---:|---|
| `raw_nflverse_pbp.raw_payload_json.complete_pass` | raw audit only | 47,629 | 46,150 | 0 | blocked until staging mapping review |
| `raw_nflverse_pbp.raw_payload_json.pass_touchdown` | raw audit only | 47,629 | 46,150 | 0 | blocked until staging mapping review |
| `raw_nflverse_pbp.raw_payload_json.rush_touchdown` | raw audit only | 47,629 | 46,150 | 0 | blocked until staging mapping review |
| `raw_nflverse_pbp.raw_payload_json.touchdown` | raw audit only | 47,629 | 46,150 | 0 | blocked until staging mapping review |
| `stg_play_player_events.air_yards` | staging | 116,400 | 74,131 | n/a | safe |
| `stg_play_player_events.cpoe` | staging | 116,400 | 73,596 | n/a | safe with nulls |
| `stg_play_player_events.epa` | staging | 116,400 | 116,125 | n/a | safe |
| `stg_play_player_events.inside_10_flag` | staging | 116,400 | 0 | 0 | blocked |
| `stg_play_player_events.inside_5_flag` | staging | 116,400 | 0 | 0 | blocked |
| `stg_play_player_events.pass_attempt` | staging | 116,400 | 115,533 | 76,678 | safe |
| `stg_play_player_events.reception` | staging | 116,400 | 79,512 | 0 | blocked |
| `stg_play_player_events.red_zone_flag` | staging | 116,400 | 0 | 0 | blocked |
| `stg_play_player_events.rush_attempt` | staging | 116,400 | 115,533 | 27,734 | safe |
| `stg_play_player_events.success` | staging | 116,400 | 116,125 | n/a | safe |
| `stg_play_player_events.target` | staging | 116,400 | 116,400 | 36,884 | safe |
| `stg_play_player_events.touchdown` | staging | 116,400 | 0 | 0 | blocked |
| `stg_play_player_events.yardline_100` | staging | 116,400 | 115,557 | n/a | diagnostic only |
| `stg_play_player_events.yards_gained` | staging | 116,400 | 115,462 | n/a | safe |

Decision:

- Keep target, pass/rush attempt, air yards, yards gained, EPA, success, CPOE, and yardline diagnostics available for v0 dry-run use.
- Block red-zone, inside-10, inside-5, touchdown, and reception-flag-dependent metrics until source-field mapping is fixed and reviewed.
- Keep route metrics blocked. `route_share` remains unavailable from Phase 29.8.

## Metric Availability Matrix

| Metric | Status | Source |
|---|---|---|
| `target_share` | safe | `stg_player_week_stats.targets / stg_team_week_stats.team_targets` |
| `air_yards_share` | safe with null flags | `stg_player_week_stats.air_yards`, fallback to `stg_play_player_events` target air yards |
| `wopr` | safe with null flags | `1.5 * target_share + 0.7 * air_yards_share` |
| `snap_share` | safe with identity warnings | `stg_participation_context.offense_pct` |
| `epa_per_opportunity` | safe with denominator flags | `stg_play_player_events.epa` |
| `cpoe` | safe with nulls | `stg_play_player_events.cpoe` |
| `route_share` | blocked | no true route source |
| `red_zone_touches` | blocked | `stg_play_player_events.red_zone_flag` unavailable |
| `touchdown_rates` | blocked | `stg_play_player_events.touchdown` unavailable |
| reception-flag-dependent metrics | blocked | `stg_play_player_events.reception` true count is 0 |

## Per-Target Design Summary

### `player_week_advanced_metrics`

Sources:

- `stg_player_week_stats`
- `stg_play_player_events`
- `stg_team_week_stats`
- `stg_participation_context`
- `stg_player_identity`

Implemented dry-run formulas:

- `opportunities = carries + targets`
- `weighted_opportunity = carries + 2.5 * targets`
- `target_share = targets / team_targets`
- `air_yards_share = player_air_yards / team_air_yards`
- `wopr = 1.5 * target_share + 0.7 * air_yards_share`
- `adot = player_air_yards / targets`
- `racr = receiving_yards / player_air_yards`
- `carry_share = carries / team_rush_attempts`
- `opportunity_share = opportunities / (team_targets + team_rush_attempts)`
- `epa_total = summed player event EPA`
- `epa_per_opportunity = epa_total / opportunities`
- `success_rate = successful eligible player events / eligible player events`
- `cpoe = average event CPOE where present`
- `explosive_rush_rate = explosive rush events / rush events`
- `explosive_reception_rate = explosive receiver events / receiver events`
- `snap_share = max offense_pct from participation context`

Player-week air yards were empty in `stg_player_week_stats`, so the dry-run uses staging-only target-event air yards from `stg_play_player_events` as a fallback. Missing air-yards rows are still flagged.

Blocked fields are set null and flagged:

- red-zone targets/carries/touches
- inside-10 carries
- inside-5 carries
- high-value touches
- route-derived metrics
- injury/depth context

Dry-run diagnostics:

| Metric | Value |
|---|---:|
| planned rows | 17,601 |
| source rows | 17,601 |
| duplicate grain rows | 0 |
| missing identity rows | 3,818 |
| missing team context rows | 0 |
| zero team targets denominator | 0 |
| null target share rows | 0 |
| null air-yards share rows | 12,267 |
| null WOPR rows | 12,267 |
| null snap share rows | 3,882 |

### `team_week_context_metrics`

Sources:

- `stg_team_week_stats`
- `stg_game_context`

Implemented dry-run fields:

- plays
- pass attempts
- rush attempts
- neutral pass rate
- team EPA per play
- team success rate
- opponent EPA allowed
- opponent pass EPA allowed
- opponent rush EPA allowed
- game environment JSON

Blocked or null fields:

- seconds per play, because clock-derived pace is not modeled yet
- pass rate over expected, because no model/source field exists
- pass/rush EPA split, because the staging team table does not carry a safe split
- red-zone pass/rush rates, because red-zone source-field review is blocked

Dry-run diagnostics:

| Metric | Value |
|---|---:|
| planned rows | 534 |
| source rows | 534 |
| duplicate grain rows | 0 |
| missing game context rows | 0 |
| null pace rows | 534 |
| null pass-rate-over-expected rows | 534 |
| EPA coverage rows | 534 |
| success coverage rows | 534 |

### `qb_week_environment_metrics`

Sources:

- `stg_play_player_events`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_player_identity`

Implemented dry-run fields:

- dropbacks
- pass attempts
- passing EPA
- EPA per dropback
- CPOE
- aDOT
- deep attempt rate

Blocked or null fields:

- sacks
- scrambles
- designed rushes
- sack rate
- scramble rate
- pass-rate-over-expected context

Dry-run diagnostics:

| Metric | Value |
|---|---:|
| planned QB rows | 643 |
| source passer-event rows | 19,973 |
| duplicate grain rows | 0 |
| missing QB identity rows | 41 |
| CPOE coverage rows | 637 |
| EPA coverage rows | 643 |

## Current Rolling Placeholder Plan

`player_recent_advanced_metrics_current` and `player_role_usage_metrics_current` are placeholders only in Phase 29.9.

They require base `player_week_advanced_metrics` rows first and are not ready to write. Planned rolling windows:

- season to date
- last 3
- last 5
- last 8

Dry-run state:

| Target | Planned rows | Source rows | Readiness |
|---|---:|---:|---|
| `player_recent_advanced_metrics_current` | 0 | 0 | blocked |
| `player_role_usage_metrics_current` | 0 | 0 | blocked |

## Dry-Run Commands

All commands completed with `dry_run=true` and `wrote=false`.

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2014 --season-end 2014 --dry-run --all-targets
```

All-target summary:

| Target | Planned rows | Source rows | Duplicate grains | Readiness |
|---|---:|---:|---:|---|
| `player_week_advanced_metrics` | 17,601 | 17,601 | 0 | ready with warnings |
| `team_week_context_metrics` | 534 | 534 | 0 | ready with warnings |
| `qb_week_environment_metrics` | 643 | 19,973 | 0 | ready with warnings |
| `player_recent_advanced_metrics_current` | 0 | 0 | 0 | blocked |
| `player_role_usage_metrics_current` | 0 | 0 | 0 | blocked |

Individual target dry-runs also completed:

- `player_week_advanced_metrics`: 17,601 planned, ready with warnings
- `team_week_context_metrics`: 534 planned, ready with warnings
- `qb_week_environment_metrics`: 643 planned, ready with warnings
- `player_recent_advanced_metrics_current`: 0 planned, blocked until base rows exist
- `player_role_usage_metrics_current`: 0 planned, blocked until base rows exist

## Warehouse Unchanged Confirmation

Raw counts remained unchanged:

| Table | Rows |
|---|---:|
| `raw_nflverse_schedules` | 267 |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |
| `raw_nflverse_rosters` | 2,152 |
| `raw_nflverse_rosters_weekly` | 30,195 |
| `raw_nflverse_weekly` | 17,601 |
| `raw_nflverse_pbp` | 47,629 |
| `raw_nflverse_snap_counts` | 23,864 |

Staging counts remained unchanged:

| Table | Rows |
|---|---:|
| `stg_player_identity` | 30,195 |
| `stg_game_context` | 267 |
| `stg_player_week_stats` | 17,601 |
| `stg_team_week_stats` | 534 |
| `stg_play_player_events` | 116,400 |
| `stg_participation_context` | 23,864 |

Feature and packet targets remain empty:

| Object | Rows |
|---|---:|
| `player_week_advanced_metrics` | 0 |
| `team_week_context_metrics` | 0 |
| `qb_week_environment_metrics` | 0 |
| `pigskin_player_context_packet_current` | 0 |
| `compat_pigskin_player_context_current` | 0 |
| `player_recent_advanced_metrics_current` | 0 |
| `player_role_usage_metrics_current` | 0 |

Score lanes were unchanged:

| Object | Rows |
|---|---:|
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

Legacy source counts were read only:

| Object | Rows |
|---|---:|
| `play_by_play` | 48,771 |
| `weekly_metrics` | 19,421 |
| `player_rosters` | 25,040 |
| `weekly_snap_counts` | 26,612 |

## Validation Results

Post-dry-run validations:

- `--pattern raw_nflverse`: 3 passed, 0 failed. Known informational warning from `181_raw_nflverse_season_week_coverage.sql`.
- `--pattern stg_`: 7 passed, 0 failed.
- `--pattern advanced_metrics`: 4 passed, 0 failed.
- `--pattern compat_pigskin`: 2 passed, 0 failed.
- `--pattern trade_player_scores`: 12 passed, 0 failed.
- `--pattern trade_pick_scores`: 17 passed, 0 failed. Known informational warning from `178_trade_pick_scores_model_version_coverage.sql`.

## Tests Added

Created `tests/test_nflverse_advanced_metrics.py`.

Coverage includes:

- CLI defaults to no write;
- `--write` fails closed;
- future gate is not sufficient in Phase 29.9;
- feature targets are registered;
- base generated SQL reads staging tables only;
- generated SQL avoids raw, legacy, feature, and Pigskin packet dependencies;
- generated SQL contains no writes;
- WOPR formula is present;
- denominator-zero handling is present;
- route/red-zone/high-value metrics remain blocked;
- pass-rate-over-expected remains null and flagged;
- dry-run output contains row counts and coverage warnings.

## Final Local Checks

Final checks passed:

- `scripts/check_deployment_safety.py`
- `py_compile` for `src\nflverse_advanced_metrics.py`, `src\nflverse_staging.py`, `src\nflverse_backfill.py`, `src\nflverse_backfill_plan.py`
- `compileall -q src scripts`
- `tests.test_nflverse_advanced_metrics`
- `tests.test_nflverse_staging`
- `tests.test_nflverse_backfill_executor`
- `tests.test_nflverse_backfill_plan`
- `tests.test_nflverse_historical_contracts`
- `tests.test_pigskin_advanced_metrics_contracts`
- `unittest discover tests`
- migrations list: no pending migrations
- validation dry-run: pass, discovered validations through 200

## Staging and Production Untouched

Read-only Cloud Run describe confirmed no deployment occurred.

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- image digest: `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- Data Ops trigger flags false
- local subprocess flags false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- image digest: `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops trigger flags false
- local subprocess flags false

## Remaining Warnings

- `player_week_advanced_metrics` still has 3,818 missing identity rows inherited from staging.
- `qb_week_environment_metrics` has 41 missing QB identity rows.
- `snap_share` is null for 3,882 player-week dry-run rows.
- `wopr` and `air_yards_share` are null for 12,267 player-week dry-run rows after using staging target-event air-yards fallback.
- `seconds_per_play` and `pass_rate_over_expected` are null for all 534 team-week rows.
- Red-zone, inside-10, inside-5, touchdown, and reception-flag-dependent metrics remain blocked.
- Current rolling targets are placeholders until base feature rows exist.

## Recommended Next Phase

Proceed to Phase 29.10 only as a bounded, explicitly authorized feature-mart materialization phase. Before write, decide whether to accept the partial WOPR/air-yards coverage and the identity gaps, or add a source-field repair phase for pass-completion, touchdown, red-zone, and inside-zone mapping first.
