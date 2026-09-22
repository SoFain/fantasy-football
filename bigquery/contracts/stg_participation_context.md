# stg_participation_context Contract

## Purpose

Canonical participation and snap context staging table.

## Source Raw Tables

`raw_nflverse_snap_counts`, `raw_nflverse_participation`, rosters, and identity staging.

## Grain

One player, season, week, game, and team participation row.

## Required Fields

`season`, `week`, `game_id`, `player_id_internal`, `player_name`, `position`, `team`, `offense_snaps`, `offense_pct`, `defense_snaps`, `st_snaps`, `participation_json`, `has_true_route_source`, `route_share`, `source_freshness_json`, `missing_data_flags`, `source_refresh_id`, `created_at`.

## Route Rule

`route_share` must stay null and flagged unless `has_true_route_source` is true. Snap share is not route share.

## Validation Expectations

Snap percentages must stay between 0 and 1 where populated. Route metrics must remain null without true route source.

## Safety Boundary

Internal staging only. Not direct UI or Pigskin context.
