# raw_nflverse_teams Contract

## Purpose

Raw team metadata table from `nflreadpy.load_teams`.

## Grain

One team row per source team abbreviation and source version.

## Natural Key

Team abbreviation plus `source_version`, with `row_hash`.

## Required Source Columns

Known critical columns include team abbreviation, full name, conference, division, colors, logos, and aliases where present.

## Passthrough Policy

Typed identity and alias fields are required. Presentation fields remain source metadata and are not direct Pigskin context.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

No season partition required. Cluster by team abbreviation.

## Refresh Strategy

Full snapshot merge.

## Replacement Note

Supersedes the raw/source role currently served by `team_descriptions`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
