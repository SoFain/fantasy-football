# source_freshness_snapshots Contract

Migration SQL: [bigquery/migrations/0003__model_run_config_foundation.sql](../migrations/0003__model_run_config_foundation.sql)

## Purpose

Captures bounded warehouse freshness metadata at the time a projection, ranking, evidence packet, or backtest run starts.

## Required Grain

One row per source freshness snapshot.

## Required Fields

- `source_freshness_snapshot_id`
- `snapshot_json`
- `created_at`

## Snapshot Expectations

The snapshot should include known source table names, missing table flags, and row counts from metadata where available.

Max season/week values are optional bounded checks. The helper only runs max-value queries for allowlisted mart/output tables and only when metadata row counts are below the configured threshold. Raw/source tables should rely on metadata row counts and missing-table flags by default.

## Compatibility Rules

`model_runs.source_freshness_snapshot_id` is the forward path. Older `model_runs.source_freshness_json` remains backward-compatible until dependent outputs migrate.
