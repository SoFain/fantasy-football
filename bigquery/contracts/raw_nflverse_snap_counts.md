# raw_nflverse_snap_counts Contract

## Purpose

Raw snap count source from `nflreadpy.load_snap_counts`.

## Grain

One player, team, game/week snap row.

## Natural Key

`season`, `week`, `game_id`, player ID or name/team fallback, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, game ID, player ID, player name, team, position, offensive snaps, offensive percentage, defensive snaps, and special-teams snaps.

## Passthrough Policy

Typed snap counts are required. Missing player IDs must be flagged in staging identity.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, player ID, team, position.

## Refresh Strategy

Impacted-week refresh after games are final. Historical backfill by season.

## Replacement Note

Supersedes the raw/source role currently served by `weekly_snap_counts`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
