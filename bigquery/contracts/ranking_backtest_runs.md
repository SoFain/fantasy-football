# ranking_backtest_runs Contract

Migration SQL: [bigquery/migrations/0028__ranking_formula_backtest_foundation.sql](../migrations/0028__ranking_formula_backtest_foundation.sql)

## Purpose

Stores deterministic ranking formula backtest run metadata.

## Grain

One row per `backtest_run_id`.

## Required Fields

- `backtest_run_id`
- `formula_version`
- `candidate_count`
- `season_start`
- `season_end`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `target_definition_json`
- `input_tables_json`
- `dry_run`
- `status`
- `created_at`

## Input Rules

Allowed inputs are curated feature marts and packet tables only:

- `player_week_advanced_metrics`
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `pigskin_player_context_packet_current`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`

Raw/source tables are not Pigskin-visible inputs.

## Write Rules

Live run rows require `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`. Dry-run mode must remain non-mutating.
