# projections_player_dynasty Contract

Migration: [bigquery/migrations/0018__create_projection_outputs.sql](../migrations/0018__create_projection_outputs.sql)

Helper: [src/projection_engine.py](../../src/projection_engine.py)

## Purpose

Versioned deterministic dynasty player value projections.

## Grain

One row per player, as-of season, as-of week, scoring profile, league type, roster format, and `model_run_id`.

## Required Fields

- `model_run_id`
- `as_of_season`
- `as_of_week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `projection_horizon`
- `year_1_value`
- `year_2_value`
- `year_3_value`
- `total_dynasty_value`
- `confidence_score`
- `risk_score`
- `rank_source`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

## Inputs

Allowed curated inputs:

- `compat_trade_player_history`
- `compat_player_profiles_current`
- `compat_trade_assets_current`
- `fraud_watch_packets`
- `sleeper_breakout_packets`
- `model_runs`
- `source_freshness_snapshots`

## Baseline Formula

The baseline blends:

- weekly and ROS value placeholders
- age curve by position
- position lifecycle adjustment
- rookie or prospect adjustment
- contract or team stability placeholder
- market value context when available
- Pigskin tier context when available

The config version is `baseline_dynasty_v1`.

## Limitations

Dynasty values are first-generation placeholders. They must be backtested and calibrated before being treated as public ranks.
