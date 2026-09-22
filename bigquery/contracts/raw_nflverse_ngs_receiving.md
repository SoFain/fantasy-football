# raw_nflverse_ngs_receiving Contract

## Purpose

Raw NGS receiving context from `nflreadpy.load_nextgen_stats(stat_type='receiving')`.

## Grain

One receiver, season, week, and team row.

## Natural Key

`season`, `week`, `player_gsis_id`, `team`, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, player GSIS ID, player name, team, targets, separation, intended air yards, expected YAC, and receiving efficiency fields where present.

## Passthrough Policy

Typed NGS fields are required for promoted metrics. Do not infer route share or first-read share from NGS receiving rows.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `player_gsis_id`, `team`.

## Refresh Strategy

Season backfill and current impacted-week refresh.

## Replacement Note

Supersedes the raw/source role currently served by `ngs_receiving`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
