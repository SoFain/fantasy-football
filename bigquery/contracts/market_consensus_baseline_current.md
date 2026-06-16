# market_consensus_baseline_current Contract

Migration: [bigquery/migrations/0021__create_market_consensus_baselines.sql](../migrations/0021__create_market_consensus_baselines.sql)

Helper: [src/market_consensus.py](../../src/market_consensus.py)

## Purpose

Current normalized baseline rows for backtests, dashboards, and future evidence packets.

## Grain

One current row per:

- `source_id`
- player key
- `season`
- optional `week`
- optional scoring and format context
- `baseline_type`

## Baseline Types

- `projection`
- `rank`
- `adp`
- `market_value`
- `prop`
- `manual`

## Consumer Rules

Backtests should read this table, not raw imported CSV files. Pigskin should consume later evidence packets built from this table, not the raw import path.
