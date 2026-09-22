# raw_nflverse_schedules Contract

## Purpose

Raw schedule and game environment seed from `nflreadpy.load_schedules`.

## Grain

One game row.

## Natural Key

`season`, `week`, `game_id`, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, game ID, game date, home team, away team, stadium, roof, surface, weather, total line, and spread line where present.

## Passthrough Policy

Typed game context fields are required. Sportsbook or weather extras may be added only after source inspection.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `game_id`, `home_team`, `away_team`.

## Refresh Strategy

Season backfill plus impacted-week current refresh.

## Replacement Note

Replaces game context inferred directly from `play_by_play`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
