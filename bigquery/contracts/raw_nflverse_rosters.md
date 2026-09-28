# raw_nflverse_rosters Contract

## Purpose

Raw seasonal roster landing table from `nflreadpy.load_rosters`.

## Grain

One roster row per player, season, and team.

## Natural Key

`season`, `player_id`, `gsis_id`, `team`, plus `row_hash`.

## Required Source Columns

Known critical columns include nflverse player ID, GSIS ID, player name, team, position, status, jersey, age, and roster metadata where present.

## Passthrough Policy

Typed identity fields are required. Extra roster attributes can remain passthrough only if documented.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `player_id`, `gsis_id`, `team`, `position`.

## Refresh Strategy

Season-level refresh after final roster publication, plus bounded current-season updates.

## Replacement Note

Replaces the seasonal roster role currently overloaded into `player_rosters`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
