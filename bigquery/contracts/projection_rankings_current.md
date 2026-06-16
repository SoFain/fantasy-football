# projection_rankings_current Contract

Migration: [bigquery/migrations/0018__create_projection_outputs.sql](../migrations/0018__create_projection_outputs.sql)

Helper: [src/projection_engine.py](../../src/projection_engine.py)

## Purpose

Current rank view over projection outputs by horizon, scoring profile, league type, roster format, and `model_run_id`.

## Grain

One row per projected player, projection horizon, scoring profile, league type, roster format, and `model_run_id`.

## Required Fields

- `model_run_id`
- `projection_horizon`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `rank_overall`
- `rank_position`
- `tier`
- `projected_points_or_value`
- `confidence_score`
- `risk_score`
- `rank_source`
- `created_at`

## Ranking Rules

Rows are sorted by projected points or value descending, then assigned:

- `rank_overall`
- `rank_position`
- a simple tier label by position rank and horizon

## Limitations

This table should not replace Pigskin rankings UI until the product explicitly chooses to wire it. It is projection ranking output, not the LLM ranking voice.
