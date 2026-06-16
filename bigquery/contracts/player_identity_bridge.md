# player_identity_bridge Contract

Migration: [bigquery/migrations/0005__player_identity_bridge.sql](../migrations/0005__player_identity_bridge.sql)

Builder: [src/build_player_identity.py](../../src/build_player_identity.py)

## Purpose

Canonical bridge across nflverse, Sleeper, Pigskin rankings, market values, viewer rosters, and show-facing outputs.

Downstream marts should use `player_id_internal` instead of fragile name joins.

## Grain

One current canonical player identity row per `player_id_internal`.

The table is rebuilt by the identity builder and is partitioned by `DATE(updated_at)`.

## Source Priority

1. Active manual override in `player_identity_overrides`.
2. Exact Sleeper ID.
3. Exact GSIS or nflverse ID.
4. Exact PFR, ESPN, or Yahoo ID when available.
5. Exact normalized name plus current team plus position.
6. Exact normalized name plus position.
7. Heuristic name-only identity with low confidence.

## Required Fields

- `player_id_internal`
- source IDs: `gsis_id`, `sleeper_player_id`, `pfr_id`, `espn_id`, `yahoo_id`, `nflverse_id`, `fantasypros_id`
- names: `full_name`, `normalized_name`, `display_name`, `first_name`, `last_name`
- context: `position`, `fantasy_positions`, `current_team`, `previous_team`, `active_status`
- age inputs: `rookie_year`, `birth_date`
- matching metadata: `source_confidence`, `match_method`, `source_priority`
- lineage: `source_freshness_json`, `missing_data_flags`, `created_at`, `updated_at`

## Manual Override Behavior

An active override wins over every automated match.

Overrides are matched by `(source, source_player_id)`. The builder also supports source aliases for exact IDs, such as `sleeper` and `gsis`.

## Missing Data Rules

`missing_data_flags` is a JSON-encoded STRING. Current flags include:

- `missing_gsis_id`
- `missing_sleeper_player_id`
- `missing_current_team`
- `missing_birth_date`
- `low_confidence_match`

## Known Failure Modes

- Duplicate names at the same position can create low-confidence matches.
- Team abbreviations can lag after trades until Sleeper or nflverse refreshes.
- Market values may only provide name, team, and position.
- Viewer league snapshots may contain stale Sleeper player metadata.

## Future Consumers

- `compat_player_profiles_current`
- `compat_sleeper_watch_candidates`
- `compat_trade_assets_current`
- `compat_viewer_team_context`
- `llm_player_context_packet`
- rankings, projections, backtests, and evidence packets
