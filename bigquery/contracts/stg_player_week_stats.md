# stg_player_week_stats Contract

## Purpose

Canonical weekly player stat staging table for player-level advanced metrics.

## Source Raw Tables

`raw_nflverse_weekly`, `stg_player_identity`, rosters, and scoring profile context when needed downstream.

## Grain

One player, season, week, team, and scoring context row where scoring context is materialized downstream.

## Required Fields

`season`, `week`, `player_id_internal`, `nflverse_player_id`, `gsis_id`, `player_name`, `position`, `team`, `opponent_team`, `targets`, `carries`, `air_yards`, `receiving_yards`, `rushing_yards`, `passing_yards`, fantasy scoring inputs, `source_freshness_json`, `missing_data_flags`, `source_refresh_id`, `created_at`.

## Validation Expectations

Unique player-week-team grain, no impossible negative counting stats, and identity coverage warnings separated from hard failures.

## Safety Boundary

Internal staging only. Not direct UI or Pigskin context.
