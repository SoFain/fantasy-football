# raw_nflverse_players Contract

## Purpose

Raw static player dimension from `nflreadpy.load_players`.

## Grain

One source player identity row.

## Natural Key

Strongest available player ID, with `row_hash` for drift tracking.

## Required Source Columns

Known critical columns include nflverse player ID, GSIS ID, fantasy IDs where available, player name, normalized name, position, latest team, birthdate, and physical/profile fields where present.

## Passthrough Policy

Typed identity fields are required. Do not expose raw profile attributes to Pigskin directly.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

No season partition required. Cluster by player IDs and normalized name.

## Refresh Strategy

Full snapshot merge in a future authorized phase.

## Replacement Note

Replaces the current pattern that replicates static player data into `player_rosters`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
