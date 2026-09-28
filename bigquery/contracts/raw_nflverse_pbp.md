# raw_nflverse_pbp Contract

## Purpose

Raw nflverse play-by-play landing table from `nflreadpy.load_pbp`. It preserves source play facts for historical feature construction.

## Grain

One source play row per `season`, `game_id`, and `play_id`.

## Natural Key

`season`, `game_id`, `play_id`, plus `row_hash` for idempotent reload checks.

## Required Source Columns

Known critical columns include `season`, `week`, `game_id`, `play_id`, `posteam`, `defteam`, `play_type`, player ID columns, `epa`, `success`, `cpoe`, `air_yards`, `yards_gained`, field position, clock, score differential, and red-zone indicators where present.

## Passthrough Policy

Stable typed columns should be modeled first. Extra source columns may be retained later through `raw_payload_json` if schema drift requires it.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, `game_id`, `posteam`, `defteam`.

## Refresh Strategy

Historical backfill uses bounded season batches. Weekly refresh rewrites or merges only impacted current-season weeks in a future authorized phase.

## Replacement Note

Supersedes the raw/source role currently served by `play_by_play`.

## Safety

This raw table is not Pigskin safe and is not UI safe. Pigskin and Streamlit must use curated feature marts or compatibility views.
