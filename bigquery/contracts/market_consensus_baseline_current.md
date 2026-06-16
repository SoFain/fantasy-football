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

## Identity Rules

Player rows should resolve through `player_identity_bridge`, deterministic aliases, or audited manual overrides. Non-player market assets such as draft picks must keep `player_id_internal` null, set `match_method = non_player_asset`, and include both `non_player_market_asset` and `player_identity_not_applicable` in `missing_data_flags`.

Market identity coverage validations should calculate player identity coverage separately from overall null identity rate. Draft-pick rows can remain null by design, but true player rows with null `player_id_internal` should trigger identity cleanup.
