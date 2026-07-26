# raw_nflverse_ngs_rushing Contract

## Purpose

Raw NGS rushing context from `nflreadpy.load_nextgen_stats(stat_type='rushing')`.

## Grain

One rusher, season, week, and team row.

## Natural Key

`season`, `week`, `player_gsis_id`, `team`, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, player GSIS ID, player name, team, attempts, expected yards, rushing yards over expected, stacked-box rate, and speed/context metrics where present.

## Passthrough Policy

Typed stable NGS fields are preferred. Do not infer missing contact-yards metrics from unrelated fields.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `player_gsis_id`, `team`.

## Refresh Strategy

Season backfill and current impacted-week refresh.

## Replacement Note

Supersedes the raw/source role currently served by `ngs_rushing`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
