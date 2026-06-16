# projections_player_weekly Contract

Migration: [bigquery/migrations/0018__create_projection_outputs.sql](../migrations/0018__create_projection_outputs.sql)

Helper: [src/projection_engine.py](../../src/projection_engine.py)

## Purpose

Versioned deterministic weekly player projections. This is the first durable projection output layer for future rankings, trade reviews, viewer-team advice, and show packets.

## Grain

One row per player, season, week, scoring profile, league type, roster format, and `model_run_id`.

## Required Fields

- `model_run_id`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `projection_horizon`
- `projected_points_mean`
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

No raw weekly, play, NGS, FTN, snap, injury, or raw Sleeper source tables should be queried by the output runner.

## Baseline Formula

The baseline blends:

- recent profile-aware fantasy points
- current profile fantasy points
- Pigskin projection context
- role score
- trend score
- fraud penalty
- breakout lift
- scoring profile factor
- roster format QB factor

The config version is `baseline_weekly_v1`.

## Limitations

This is not ML and not LLM output. It must be backtested before public confidence claims.
