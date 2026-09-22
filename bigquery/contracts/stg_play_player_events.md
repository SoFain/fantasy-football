# stg_play_player_events Contract

## Purpose

Normalized play-player event staging table for passer, rusher, receiver, target, touchdown, and team event metrics.

## Source Raw Tables

`raw_nflverse_pbp`, `stg_player_identity`, and `stg_game_context`.

## Grain

One normalized player event per play, event type, player, and team.

## Required Fields

`season`, `week`, `game_id`, `play_id`, `event_type`, `player_id_internal`, `nflverse_player_id`, `gsis_id`, `team`, `opponent_team`, `posteam`, `defteam`, `yardline_100`, `game_seconds_remaining`, `score_differential`, `epa`, `success`, `cpoe`, `air_yards`, `yards_gained`, `pass_attempt`, `rush_attempt`, `target`, `reception`, `touchdown`, `red_zone_flag`, `inside_10_flag`, `inside_5_flag`, `source_freshness_json`, `missing_data_flags`, `source_refresh_id`, `created_at`.

## Validation Expectations

Unique normalized event grain and no player event rows without event type. Boolean indicators should stay boolean or 0/1.

## Safety Boundary

Internal staging only. Not direct UI or Pigskin context.
