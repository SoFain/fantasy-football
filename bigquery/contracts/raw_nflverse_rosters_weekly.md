# raw_nflverse_rosters_weekly Contract

## Purpose

Raw weekly roster identity and status table from `nflreadpy.load_rosters_weekly`.

## Grain

One player, season, week, and team row.

## Natural Key

`season`, `week`, `player_id`, `gsis_id`, `team`, plus `row_hash`.

## Required Source Columns

Known critical columns include player IDs, name, team, position, status, week, and roster status fields.

## Passthrough Policy

Keep typed identity and status fields. Do not infer player identity from names alone without flags.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `player_id`, `team`, `position`.

## Refresh Strategy

Impacted-week refresh for active seasons. Historical backfill by bounded seasons.

## Replacement Note

Adds missing weekly roster state that legacy `player_rosters` does not safely provide.

## Safety

This raw table is not Pigskin safe and is not UI safe.
