# raw_nflverse_weekly Contract

## Purpose

Raw nflverse weekly player stats landing table from `nflreadpy.load_player_stats(summary_level='week')`.

## Grain

One player, season, week, and team row.

## Natural Key

`season`, `week`, `player_id`, `team`, `position`, plus `row_hash`.

## Required Source Columns

Known critical columns include player ID, player name, recent team, opponent team, position, passing stats, rushing stats, receiving stats, targets, carries, air yards, and fantasy scoring inputs.

## Passthrough Policy

Keep stable metric fields typed. Preserve unstable extras only through documented passthrough JSON after schema inspection.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `player_id`, `team`, `position`.

## Refresh Strategy

Historical backfill uses season batches. Weekly refresh is current-season impacted-week only.

## Replacement Note

Supersedes the raw/source role currently served by `weekly_metrics`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
