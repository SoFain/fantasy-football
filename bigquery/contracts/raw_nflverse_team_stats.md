# raw_nflverse_team_stats Contract

## Purpose

Raw weekly team stats from `nflreadpy.load_team_stats(summary_level='week')` when available.

## Grain

One team, season, and week row.

## Natural Key

`season`, `week`, `team`, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, team, plays, passing attempts, rushing attempts, yards, touchdowns, turnovers, and EPA-like fields where source support exists.

## Passthrough Policy

Typed team fields should be modeled only after source inspection. Unknown extras can be held in passthrough JSON.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `team`.

## Refresh Strategy

Historical season batches and current impacted-week refresh.

## Replacement Note

Adds canonical team-week input instead of deriving all team context from play-level source rows.

## Safety

This raw table is not Pigskin safe and is not UI safe.
