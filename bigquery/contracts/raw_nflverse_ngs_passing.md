# raw_nflverse_ngs_passing Contract

## Purpose

Raw NGS passing context from `nflreadpy.load_nextgen_stats(stat_type='passing')`.

## Grain

One quarterback, season, week, and team row.

## Natural Key

`season`, `week`, `player_gsis_id`, `team`, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, player GSIS ID, player name, team, attempts, expected completion, completion percentage over expected, air-yards fields, time to throw, and related NGS passing metrics where present.

## Passthrough Policy

Stable NGS fields should be typed. Missing or renamed fields must be flagged instead of silently inferred.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `player_gsis_id`, `team`.

## Refresh Strategy

Season backfill and current impacted-week refresh.

## Replacement Note

Supersedes the raw/source role currently served by `ngs_passing`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
