# raw_nflverse_draft_picks Contract

## Purpose

Raw NFL draft pick source from `nflreadpy.load_draft_picks`.

## Grain

One drafted player/pick row.

## Natural Key

Draft season, draft team, player ID or pick number, plus `row_hash`.

## Required Source Columns

Known critical columns include season, team, player ID, player name, position, draft round, pick number, college, and draft metadata where present.

## Passthrough Policy

College or rookie context remains source-labeled until a curated rookie mart exists. Do not blend this directly into player or pick scores.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by player ID, team, position.

## Refresh Strategy

Season-level backfill after each NFL draft.

## Replacement Note

Supersedes the raw/source role currently served by `draft_picks`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
