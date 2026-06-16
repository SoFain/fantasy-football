# market_consensus_sources Contract

Migration: [bigquery/migrations/0021__create_market_consensus_baselines.sql](../migrations/0021__create_market_consensus_baselines.sql)

Helper: [src/market_consensus.py](../../src/market_consensus.py)

## Purpose

Registry of allowed market, consensus, analyst, ADP, prop, and manual baseline sources.

## Grain

One row per `source_id`.

## Source Types

- `adp`
- `ecr`
- `projection`
- `prop`
- `market_value`
- `analyst_rank`
- `manual`

## Access Methods

- `csv`
- `api`
- `manual`
- `internal`

## Rules

- `automated_allowed` must stay false unless source terms and credentials are explicitly configured.
- This table does not authorize scraping.
- Source-specific adapters must be isolated from UI and Pigskin paths.
