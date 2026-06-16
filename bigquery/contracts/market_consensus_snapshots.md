# market_consensus_snapshots Contract

Migration: [bigquery/migrations/0021__create_market_consensus_baselines.sql](../migrations/0021__create_market_consensus_baselines.sql)

Helper: [src/market_consensus.py](../../src/market_consensus.py)

## Purpose

Metadata ledger for each imported market or consensus baseline snapshot.

## Grain

One row per `snapshot_id`.

## Required Fields

- `snapshot_id`
- `source_id`
- `snapshot_type`
- `snapshot_date`
- `snapshot_timestamp`
- `season`
- `ingested_at`
- `row_count`

## Notes

`source_file_uri` may point to a local or Cloud Storage file. UI and Pigskin should not query the raw file directly.
