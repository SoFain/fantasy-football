# trade_review_packets Contract

Migration: [bigquery/migrations/0016__create_trade_review_packets.sql](../migrations/0016__create_trade_review_packets.sql)

Helper: [src/trade_review_packets.py](../../src/trade_review_packets.py)

## Purpose

Precomputed deterministic trade review packet for future Trade Lab, Pigskin chat, and show-writing tools.

## Grain

One row per `trade_review_id`.

## Required Fields

- `trade_review_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `side_a_value`
- `side_b_value`
- `value_delta`
- `recommended_winner`
- `confidence_score`
- `packet_json`
- `packet_text`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

## Packet JSON Sections

- `trade_summary`
- `verdict`
- `side_a_evidence`
- `side_b_evidence`
- `player_evidence`
- `roster_context`
- `counterarguments`
- `show_framing`
- `metadata`

## Deterministic Formula

The helper uses an explicit config dictionary in [src/trade_review_packets.py](../../src/trade_review_packets.py):

- market value component
- Pigskin rank component
- recent production component
- role trend component
- risk adjustment
- age and dynasty adjustment
- roster format adjustment
- league type adjustment

This is a baseline packet builder, not final machine learning.

## Source Rules

Allowed curated inputs:

- `compat_trade_assets_current`
- `compat_trade_player_history`
- `compat_player_profiles_current`
- `compat_viewer_team_context`
- `model_runs`
- optional config tables such as `scoring_profiles`, `league_types`, `roster_formats`, and `feature_config_versions`

The helper must not read raw market, weekly, play, or Sleeper source tables.

## Runtime Status

No Streamlit runtime behavior is wired to this table yet.
