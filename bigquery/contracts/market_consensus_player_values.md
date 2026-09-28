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
2. non-player market asset classification
3. manual overrides by trusted source and player key
4. exact source IDs from `player_identity_bridge`
5. known aliases
6. normalized name plus team plus position
7. normalized name plus position when unique
8. unmatched retained with `missing_player_id_internal`

Name fallback matches must set `match_method` and include `identity_name_fallback_match` in `missing_data_flags`.

Rows representing draft picks or other non-player market assets must not receive fabricated player IDs. They should keep `player_id_internal` null, set `match_method = non_player_asset`, and include both `non_player_market_asset` and `player_identity_not_applicable` in `missing_data_flags`.

Unsafe fuzzy matching is not allowed. Ambiguous market rows stay unresolved until a deterministic alias or manual override is reviewed and added.

## No-Scraping Rule

Rows come from manual, CSV, approved API, or internal adapters only. This table does not permit scraping sources that forbid scraping.
