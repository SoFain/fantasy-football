# raw_nflverse_participation Contract

## Purpose

Raw participation source from `nflreadpy.load_participation`.

## Grain

To be finalized after schema inspection. Expected game, player, team, and participation context row.

## Natural Key

`season`, `week`, `game_id`, player/team participation key, plus `row_hash`.

## Required Source Columns

Known critical columns are intentionally conservative: season, week, game ID, player identity if present, team, participation fields, and source event metadata.

## Passthrough Policy

Do not label route share, route participation, alignment, or first-read data unless the source exposes true fields. Unknown participation columns remain source-labeled.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `game_id`, player/team identifiers.

## Refresh Strategy

Schema inspection first, then bounded season backfill.

## Replacement Note

Adds a missing source lane for future role and participation context.

## Safety

This raw table is not Pigskin safe and is not UI safe.
