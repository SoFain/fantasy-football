# player_identity_overrides Contract

Migration: [bigquery/migrations/0005__player_identity_bridge.sql](../migrations/0005__player_identity_bridge.sql)

## Purpose

Manual correction table for player identity collisions, stale source IDs, name changes, and source-specific mismatches.

## Grain

One override row per `(source, source_player_id, player_id_internal)` decision.

Only rows with `active = TRUE` are applied by the identity builder.

## Fields

- `override_id`
- `source`
- `source_player_id`
- `player_id_internal`
- `reason`
- `active`
- `created_by`
- `created_at`

## Matching Rules

Manual overrides take priority over automated matching.

The `source` value may be a source table name, such as `sleeper_players_current`, or an ID namespace alias, such as:

- `sleeper`
- `gsis`
- `pfr`
- `espn`
- `yahoo`
- `nflverse`
- `fantasypros`

## Operational Notes

Use this table for high-impact ranking or roster players before changing automated matching logic.

Do not use overrides to hide bad source freshness. If a source is stale, fix the ingest or add a source freshness flag.
