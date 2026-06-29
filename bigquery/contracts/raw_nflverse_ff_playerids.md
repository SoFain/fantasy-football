# raw_nflverse_ff_playerids Contract

## Purpose

Raw fantasy-platform identity bridge from `nflreadpy.load_ff_playerids`.

## Grain

One player-platform identity mapping row.

## Natural Key

Source player ID, platform ID, platform name, plus `row_hash`.

## Required Source Columns

Known critical columns include nflverse player ID, GSIS ID, Sleeper ID, fantasy platform IDs, player name, and platform-specific aliases where present.

## Passthrough Policy

Typed ID fields are preferred. New platform columns may be passthrough until promoted.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

No season partition required. Cluster by nflverse, GSIS, Sleeper, and fantasy IDs.

## Refresh Strategy

Full snapshot merge before identity mart rebuilds.

## Replacement Note

Adds a missing identity source needed by `stg_player_identity`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
