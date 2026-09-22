# stg_game_context Contract

## Purpose

Canonical game, team, schedule, and environment context for historical feature work.

## Source Raw Tables

`raw_nflverse_schedules`, `raw_nflverse_teams`, and game-level fields from `raw_nflverse_pbp`.

## Grain

One row per `season`, `week`, and `game_id`.

## Required Fields

`season`, `week`, `game_id`, `game_date`, `home_team`, `away_team`, `stadium`, `roof`, `surface`, `temp`, `wind`, `total_line`, `spread_line`, `source_freshness_json`, `missing_data_flags`, `source_refresh_id`, `created_at`.

## Validation Expectations

Unique game grain, non-null teams, schedule coverage matching source seasons and weeks, and stale environment fields flagged.

## Safety Boundary

Internal staging only. UI and Pigskin should read derived context packets or compatibility views.
