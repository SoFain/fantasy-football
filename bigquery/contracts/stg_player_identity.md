# stg_player_identity Contract

## Purpose

Canonical player identity staging table for nflverse historical feature work.

## Source Raw Tables

`raw_nflverse_players`, `raw_nflverse_ff_playerids`, `raw_nflverse_rosters`, and `raw_nflverse_rosters_weekly`.

## Grain

One player identity row per player, season, week where weekly identity is available. Static-only rows may use null week and must be flagged.

## Identity Keys

`player_id_internal`, `nflverse_player_id`, `gsis_id`, `sleeper_player_id`, `fantasy_player_id`.

## Season and Team Keys

`season`, `week`, `team`, `position`.

## Required Fields

`player_id_internal`, `nflverse_player_id`, `gsis_id`, `sleeper_player_id`, `fantasy_player_id`, `player_name`, `normalized_player_name`, `position`, `team`, `season`, `week`, `identity_confidence`, `identity_source_json`, `source_freshness_json`, `missing_data_flags`, `source_refresh_id`, `created_at`.

## Validation Expectations

Unique active identity rows per player/team/week, no high-confidence name-only joins, and all missing IDs explicitly flagged.

## Safety Boundary

Internal canonical staging only. Not direct UI or Pigskin context.
