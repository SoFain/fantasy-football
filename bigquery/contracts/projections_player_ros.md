# projections_player_ros Contract

Migration: [bigquery/migrations/0018__create_projection_outputs.sql](../migrations/0018__create_projection_outputs.sql)

Helper: [src/projection_engine.py](../../src/projection_engine.py)

## Purpose

Versioned deterministic rest-of-season player projections.

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
- `remaining_games`
- `projected_points_total`
- `projected_points_per_game`
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

The baseline starts with the weekly projection, then applies:

- remaining games placeholder
- role stability
- trend
- position risk
- scoring profile context
- roster format context
- league type context

The config version is `baseline_ros_v1`.

## Limitations

Remaining games are a placeholder until schedule and injury availability marts are promoted. This is not ML and not LLM output.
