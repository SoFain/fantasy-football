# compat_viewer_team_context Contract

Migrations:

- [bigquery/migrations/0014__extend_compat_viewer_team_context_packet.sql](../migrations/0014__extend_compat_viewer_team_context_packet.sql)
- [bigquery/migrations/0015__filter_compat_viewer_team_context_packets.sql](../migrations/0015__filter_compat_viewer_team_context_packets.sql)

View: [bigquery/views/compat_viewer_team_context.sql](../views/compat_viewer_team_context.sql)

Materializer: [src/materialize_viewer_team_context.py](../../src/materialize_viewer_team_context.py)

Helper: [src/viewer_team_context.py](../../src/viewer_team_context.py)

## Purpose

Compatibility layer for `get_sleeper_viewer_team_context`, `app.py:3390-3570`.

This object replaces raw Sleeper joins and fragile player matching in Viewer Team Lab with a precomputed packet. Streamlit is not wired to it yet. Future wiring must be behind `USE_COMPAT_VIEWER_TEAM_CONTEXT=false` until live validation passes.

## Backing Object

- `mart_viewer_team_context`
- `compat_viewer_team_context` is a view over the mart.

The view filters to rows where `packet_json IS NOT NULL` so legacy mart rows are not exposed to Streamlit or Pigskin consumers.

## Grain

One row per:

- `league_id`
- `roster_id`
- `manager_id`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- latest Sleeper snapshot timestamp

Packet-level JSON is the primary payload for UI and LLM consumption.

## Required Fields

- `viewer_team_context_id`
- `league_id`
- `roster_id`
- `manager_id`
- `manager_display_name`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `model_run_id`
- `ranking_version`
- `snapshot_timestamp`
- `packet_json`
- `packet_text`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

## Packet JSON Structure

Top-level packet sections:

- `league_context`
- `team_context`
- `roster_rows`
- `lineup_rows`
- `bench_rows`
- `waiver_rows`
- `team_strengths`
- `team_weaknesses`
- `recommended_actions`
- `evidence_metadata`

Roster rows include identity, Sleeper player ID, display name, position, team, active status, lineup slot, starter or bench flags, injury flag, Pigskin rank and tier, projected points, trade asset value, recent points, role trend, risk score, breakout score, evidence summary, and row-level missing-data flags.

Waiver rows are sourced from `compat_sleeper_watch_candidates` and include streamer and breakout scores where available.

## Source Rules

Allowed inputs inside the materializer:

- `sleeper_leagues`
- `sleeper_rosters`
- `sleeper_roster_players`
- `sleeper_lineups`
- `sleeper_available_players`
- `sleeper_players_current`
- `sleeper_viewer_team_snapshots`
- `dim_players_current`
- `player_identity_bridge`
- `analytics_pigskin_rankings`
- `compat_trade_assets_current`
- `compat_sleeper_watch_candidates`
- `compat_player_profiles_current`
- `compat_trade_player_history`
- `llm_player_context_packet`

Raw Sleeper snapshots are allowed only inside the materializer. They should not be exposed directly to UI or Pigskin.

## Missing Data Behavior

If no matching league or roster packet exists, [src/viewer_team_context.py](../../src/viewer_team_context.py) returns a clean unavailable response with `viewer_team_context_not_materialized`.

Common missing-data flags:

- `missing_roster_rows`
- `missing_lineup_rows`
- `missing_waiver_rows`
- `missing_model_run_id`
- `missing_ranking_version`
- `missing_player_identity_rows`
- `missing_canonical_player_identity_rows`
- `missing_sleeper_rosters_source`
- `missing_sleeper_roster_players_source`
- `missing_sleeper_lineups_source`
- `missing_sleeper_available_players_source`
- `missing_sleeper_players_current_source`
- `missing_sleeper_watch_source`
- `missing_trade_asset_source`
- `missing_rankings_source`

## Validation

Validation files:

- `059_compat_viewer_team_context_grain.sql`
- `060_compat_viewer_team_context_recent_rows_exist.sql`
- `061_compat_viewer_team_context_required_json_keys.sql`
- `062_compat_viewer_team_context_packet_size_bounds.sql`
- `063_compat_viewer_team_context_identity_coverage.sql`
- `064_compat_viewer_team_context_model_run_join.sql`
- `065_compat_viewer_team_context_missing_flags_exist.sql`
- `066_compat_viewer_team_context_no_raw_ui_dependency.sql`

## Future Wiring

Future Streamlit wiring should:

1. Add `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`.
2. Use [src/viewer_team_context.py](../../src/viewer_team_context.py).
3. Keep the current Viewer Team Lab query path as fallback until live validation passes.
4. Remove direct UI reads from raw Sleeper snapshots only after packet parity is confirmed.
