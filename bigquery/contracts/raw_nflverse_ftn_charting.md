# raw_nflverse_ftn_charting Contract

## Purpose

Raw FTN charting source from `nflreadpy.load_ftn_charting`.

## Grain

Expected play or charting event row. Exact key must be verified by schema inspection.

## Natural Key

`season`, `week`, game/play identifiers where present, source charting key, plus `row_hash`.

## Required Source Columns

Known critical columns include season, week, game ID, play ID where present, charting flags, QB-fault or pressure-adjacent fields where present, and screen or receiver context fields where present.

## Passthrough Policy

Do not label true pressure, route, first-read, alignment, or contact-yard metrics unless a true source field exists. A true pressure source must be explicitly identified before any pressure metric is promoted.

## Load Metadata

`source_system`, `source_loader`, `source_version`, `source_season`, `source_week`, `source_refresh_id`, `loaded_at`, `loaded_by`, `row_hash`.

## Partitioning and Clustering

Partition by `season`. Cluster by `week`, game ID, play ID.

## Refresh Strategy

Schema inspection first, then season-batched backfill.

## Replacement Note

Supersedes the raw/source role currently served by `ftn_charting`.

## Safety

This raw table is not Pigskin safe and is not UI safe.
