# stg_team_week_stats Contract

## Purpose

Canonical team-week context staging table for pace, tendency, and opponent context metrics.

## Source Raw Tables

`raw_nflverse_pbp`, `raw_nflverse_team_stats`, and `stg_game_context`.

## Grain

One team, season, and week row.

## Required Fields

`season`, `week`, `team`, `opponent_team`, `plays`, `pass_attempts`, `rush_attempts`, `team_targets`, `team_air_yards`, `epa_total`, `epa_per_play`, `success_rate`, `neutral_pass_rate`, `pass_rate_over_expected`, `red_zone_pass_rate`, `red_zone_rush_rate`, opponent defensive EPA fields where appropriate, `source_freshness_json`, `missing_data_flags`, `source_refresh_id`, `created_at`.

## Validation Expectations

Unique team-week grain, rate fields between 0 and 1 where applicable, denominator-zero flags, and opponent coverage.

## Safety Boundary

Internal staging only. Not direct UI or Pigskin context.
