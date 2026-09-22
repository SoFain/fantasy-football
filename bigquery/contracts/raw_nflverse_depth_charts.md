# raw_nflverse_depth_charts Contract

## Purpose

Raw depth chart source from `nflreadpy.load_depth_charts`.

## Grain

One player/team/position/depth row per source snapshot.

## Natural Key

`season`, `team`, `gsis_id`, `position`, `depth_rank`, snapshot date where available, plus `row_hash`.

## Required Source Columns

Known critical columns include season, team, player ID, player name, position, depth rank, formation/position group, and snapshot date or week if present.

## Passthrough Policy

Depth chart fields are source status, not final role claims. Downstream marts must flag stale or missing depth context.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by team, player ID, position.

## Refresh Strategy

Season snapshot backfill and current-season refresh after source updates.

## Replacement Note

Supersedes the raw/source role currently served by `depth_charts`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
