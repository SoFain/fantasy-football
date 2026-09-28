# raw_nflverse_injuries Contract

## Purpose

Raw injury report source from `nflreadpy.load_injuries`.

## Grain

One report row per player/team/report date or season/week status.

## Natural Key

`season`, `week`, `team`, `gsis_id`, report fields hash, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, team, player ID, player name, position, report status, practice status, game status, and injury notes where present.

## Passthrough Policy

Text injury notes must stay source-labeled and not be promoted to final claims without downstream validation.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `team`, `gsis_id`.

## Refresh Strategy

Current impacted-week refresh and historical season batches.

## Replacement Note

Supersedes the raw/source role currently served by `injury_reports`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
