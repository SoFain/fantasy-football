# dim_players_current Contract

Migration: [bigquery/migrations/0005__player_identity_bridge.sql](../migrations/0005__player_identity_bridge.sql)

Builder: [src/build_player_identity.py](../../src/build_player_identity.py)

## Purpose

Current player dimension for UI, rankings, projections, trade analysis, and evidence packets.

This table should be the default player dimension for downstream marts.

## Grain

One row per current canonical player, keyed by `player_id_internal`.

## Fields

- `player_id_internal`
- `display_name`
- `full_name`
- `normalized_name`
- `position`
- `fantasy_positions`
- `current_team`
- `active_status`
- `sleeper_player_id`
- `gsis_id`
- `pfr_id`
- `espn_id`
- `yahoo_id`
- `rookie_year`
- `birth_date`
- `age`
- `source_confidence`
- `match_method`
- `source_freshness_json`
- `missing_data_flags`
- `updated_at`

## Source Rules

`dim_players_current` is derived from `player_identity_bridge`. It should not directly join raw source tables.

## Downstream Use

Use this table to enrich:

- Player Profiles
- Sleeper Watch
- Trade Lab assets
- Viewer Team context
- Pigskin ranking and projection packets
- LLM player context packets

## Failure Rules

If `source_confidence < 0.8`, downstream outputs should show a missing-data flag or route the player to an override review queue before using the row as authoritative.
