# trade_review_packet_players Contract

Migration: [bigquery/migrations/0016__create_trade_review_packets.sql](../migrations/0016__create_trade_review_packets.sql)

Helper: [src/trade_review_packets.py](../../src/trade_review_packets.py)

## Purpose

One evidence row per player or asset included in a trade review side.

## Grain

One row per:

- `trade_review_id`
- `side`
- `player_id_internal` or `source_player_key`

## Required Fields

- `trade_review_id`
- `side`
- `display_name`
- `position`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `short_term_value`
- `ros_value`
- `dynasty_value`
- `risk_score`
- `evidence_json`
- `missing_data_flags`
- `created_at`

## Evidence JSON

Each row should include:

- identity
- trade asset value
- Pigskin ranking context
- recent production
- usage trend
- risk, fraud, and breakout context where available
- age and dynasty context
- counterargument

## Runtime Status

No Streamlit runtime behavior is wired to this table yet.
