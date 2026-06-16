# compat_player_profiles_current Contract

SQL:

- [bigquery/migrations/0008__promote_compat_player_profiles_current.sql](../migrations/0008__promote_compat_player_profiles_current.sql)
- [bigquery/views/compat_player_profiles_current.sql](../views/compat_player_profiles_current.sql)

Materializer:

- [src/materialize_player_profiles.py](../../src/materialize_player_profiles.py)

Helper:

- [src/player_profiles.py](../../src/player_profiles.py)

## Purpose

Production compatibility layer for `fetch_player_profiles_data`, `app.py:1090-1275`.

This object moves Player Profiles away from Streamlit-side raw source joins and into a curated profile mart. It consolidates identity, current context, scoring-profile fantasy output, weekly role evidence, efficiency, Pigskin ranking context, contract/depth/prospect summaries, freshness, and missing-data flags.

`app.py` is not wired to this object by default yet. Current Streamlit behavior remains unchanged until a later default-off feature flag migration.

## Backing Object

`compat_player_profiles_current` is a view over:

- `mart_player_profiles_current`

The backing table is refreshed by `src/materialize_player_profiles.py`.

This mart-backed approach is intentional because Player Profiles will be a frequent admin and LLM context path. Precomputing the profile packet keeps UI reads cheap and keeps raw source joins out of the request path.

## Grain

One row per:

- `COALESCE(player_id_internal, source_player_key)`
- `scoring_profile_id`
- `as_of_season`
- `as_of_week`

Validation:

- [bigquery/validations/028_compat_player_profiles_current_grain.sql](../validations/028_compat_player_profiles_current_grain.sql)

## Sources

Primary safe sources:

- `dim_players_current`
- `player_identity_bridge`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`
- `analytics_pigskin_rankings`

Optional sources used only inside the controlled materializer:

- `player_contracts`
- `depth_charts`
- `college_player_stats`
- `rookie_scouting_metrics`

Forbidden direct UI or Pigskin sources:

- `player_rosters`
- `player_contracts`
- `depth_charts`
- `college_player_stats`
- `rookie_scouting_metrics`

The optional raw profile tables may be read by `src/materialize_player_profiles.py`, but they are not exposed by the compat view as raw rows.

## Required Fields

Identity:

- `player_id_internal`
- `source_player_key`
- `sleeper_player_id`
- `gsis_id`
- `pfr_id`
- `espn_id`
- `yahoo_id`
- `display_name`
- `full_name`
- `normalized_name`
- `position`
- `fantasy_positions`
- `current_team`
- `active_status`
- `rookie_year`
- `birth_date`
- `age`

Current context:

- `as_of_season`
- `as_of_week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `last_seen_season`
- `last_seen_week`
- `games_played_current_season`
- `bye_week`

Fantasy production:

- `fantasy_points_current_season`
- `fantasy_points_per_game_current_season`
- `fantasy_points_last_3`
- `fantasy_points_last_5`
- `fantasy_points_last_8`
- `total_fantasy_points_standard`
- `total_fantasy_points_half_ppr`
- `total_fantasy_points_ppr`
- `position_rank_by_profile`
- `overall_rank_by_profile`

Usage and role:

- `snaps_last_3`
- `snap_share_last_3`
- `targets_last_3`
- `target_share_last_3`
- `carries_last_3`
- `rush_share_last_3`
- `receptions_last_3`
- `air_yards_last_3`
- `air_yard_share_last_3`
- `red_zone_opportunities_last_3`
- `high_value_touches_last_3`
- `role_summary_json`

Efficiency:

- `yards_per_carry_current_season`
- `yards_per_target_current_season`
- `yards_per_reception_current_season`
- `catch_rate_current_season`
- `td_rate_current_season`
- `epa_summary_json`
- `efficiency_summary_json`

Pigskin ranking context:

- `model_run_id`
- `ranking_version`
- `pigskin_rank_overall`
- `pigskin_rank_position`
- `pigskin_tier`
- `pigskin_projection`
- `pigskin_confidence`
- `pigskin_summary`
- `pigskin_movement_json`

Profile context:

- `contract_summary_json`
- `depth_chart_summary_json`
- `college_summary_json`
- `rookie_scouting_summary_json`
- `prospect_summary_json`

Lineage:

- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `refreshed_at`

## Missing Data Rules

Missing evidence must be flagged instead of silently filled with generic values.

Expected flags include:

- `missing_player_id_internal`
- `missing_source_player_key`
- `missing_sleeper_player_id`
- `missing_gsis_id`
- `missing_current_season_scoring`
- `missing_weekly_truth`
- `missing_pigskin_rank`
- `missing_contract_summary`
- `missing_depth_chart_summary`
- `missing_college_summary`
- `missing_rookie_scouting_summary`
- `missing_player_contracts_source`
- `missing_depth_charts_source`
- `missing_college_player_stats_source`
- `missing_rookie_scouting_metrics_source`
- `temporary_name_join_college_summary`
- `temporary_name_join_rookie_scouting_summary`
- `missing_bye_week`
- `missing_snaps_last_3`

Known temporary nulls:

- `bye_week`
- `snaps_last_3`
- `pigskin_rank_overall`
- `league_type_id`
- `roster_format_id`

## Validation Set

- [028 grain](../validations/028_compat_player_profiles_current_grain.sql)
- [029 recent rows exist](../validations/029_compat_player_profiles_current_recent_rows_exist.sql)
- [030 identity coverage](../validations/030_compat_player_profiles_current_identity_coverage.sql)
- [031 scoring profiles exist](../validations/031_compat_player_profiles_current_scoring_profiles_exist.sql)
- [032 missing flags exist](../validations/032_compat_player_profiles_current_missing_flags_exist.sql)
- [033 no raw UI dependency](../validations/033_compat_player_profiles_current_no_raw_ui_dependency.sql)
- [034 top ranked players present](../validations/034_compat_player_profiles_current_top_ranked_players_present.sql)

## Helper Contract

`src/player_profiles.py` exposes:

- `get_player_profile()`
- `search_player_profiles()`
- `build_player_profile_query()`
- `build_player_profile_search_query()`

Rules:

- Query only `compat_player_profiles_current`.
- Pass lookup values and scoring profile IDs as BigQuery parameters.
- Build table identifiers only from trusted project and dataset config.
- Cap search limits at `100`.
- Return `None` or an empty list for missing players instead of fabricating context.

## Runtime Status

Not wired into `app.py` by default.

Future UI wiring should use a default-off flag such as `USE_COMPAT_PLAYER_PROFILES=false`, then replace `fetch_player_profiles_data` with a compat-backed path after validation.

## Future Use

This object is intended to feed:

- Player Profiles
- Pigskin player context packets
- Ranking defense evidence
- Trade review packets
- Sleeper breakout and fraud-watch profile context
