# backtest_result_player_week Contract

Migration: [bigquery/migrations/0020__create_backtest_framework.sql](../migrations/0020__create_backtest_framework.sql)

Helper: [src/backtesting.py](../../src/backtesting.py)

## Purpose

Player-week projection evaluation against realized fantasy points.

## Grain

One row per:

- `backtest_run_id`
- `model_run_id`
- player key
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `projection_horizon`

## Required Fields

- `backtest_run_id`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `projection_horizon`
- `projected_points`
- `actual_points`
- error metrics
- rank metrics
- boom and bust flags
- `created_at`

## Inputs

Allowed inputs:

- `projections_player_weekly`
- `projection_rankings_current` when needed by future versions
- `analytics_player_fantasy_points_by_profile`

This table must not be built from raw `weekly_metrics`, `play_by_play`, NGS, FTN, snap, injury, or raw Sleeper tables.

## Notes

`result_json` and `missing_data_flags` are JSON-encoded strings in v1 so Python inserts remain simple.
