# market_consensus_player_values Contract

Migration: [bigquery/migrations/0021__create_market_consensus_baselines.sql](../migrations/0021__create_market_consensus_baselines.sql)

Helper: [src/market_consensus.py](../../src/market_consensus.py)

## Purpose

Normalized player-level rows from outside market, consensus, ADP, projection, prop, or manual baseline sources.

## Grain

One row per:

- `snapshot_id`
- `source_id`
- player key
- `season`
- optional `week`
- optional scoring and format context
- optional `prop_market`

## Identity Rules

Matching priority:

1. `player_id_internal`
2. exact source IDs from `player_identity_bridge`
3. normalized name plus team plus position
4. normalized name plus position when unique
5. unmatched retained with `missing_player_id_internal`

Name fallback matches must set `match_method` and include `identity_name_fallback_match` in `missing_data_flags`.

## No-Scraping Rule

Rows come from manual, CSV, approved API, or internal adapters only. This table does not permit scraping sources that forbid scraping.
