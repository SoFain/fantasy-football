# compat_sleeper_watch_candidates Contract

Migration: [bigquery/migrations/0011__promote_compat_sleeper_watch_candidates.sql](../migrations/0011__promote_compat_sleeper_watch_candidates.sql)

View: [bigquery/views/compat_sleeper_watch_candidates.sql](../views/compat_sleeper_watch_candidates.sql)

Materializer: [src/materialize_sleeper_watch.py](../../src/materialize_sleeper_watch.py)

Helper: [src/sleeper_watch.py](../../src/sleeper_watch.py)

## Purpose

Compatibility layer for `render_sleeper_watch_segment`, `app.py:788-918`.

This object replaces UI reads from raw `weekly_metrics`, `sleeper_rosters`, and `sleeper_roster_players` with a curated Sleeper Watch mart. Streamlit is not wired to it yet. Future wiring must be behind `USE_COMPAT_SLEEPER_WATCH=false` until live validation is complete.

## Backing Object

- `mart_sleeper_watch_candidates`
- `compat_sleeper_watch_candidates` is a view over the mart.

## Grain

One row per:

- `player_id_internal`
- `league_id` or global context where `league_id IS NULL`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `season`
- `week`

If canonical identity is not available, the materializer uses a temporary `source:` key and adds a missing-data flag.

## Required Fields

Identity:

- `player_id_internal`
- `source_player_key`
- `sleeper_player_id`
- `display_name`
- `normalized_name`
- `position`
- `fantasy_positions`
- `team`
- `opponent`
- `age`
- `active_status`

Context:

- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `league_id`
- `model_run_id`
- `ranking_version`

Availability and market context:

- `rostered_rate`
- `available_in_league_flag`
- `rostered_in_league_flag`
- `waiver_candidate_flag`
- `starter_candidate_flag`
- `sleeper_trending_add_count`
- `sleeper_trending_drop_count`
- `market_or_roster_context_json`

Recent usage:

- `fantasy_points_last_1`
- `fantasy_points_last_3`
- `fantasy_points_last_5`
- `fantasy_points_per_game`
- `snap_share_last_3`
- `target_share_last_3`
- `rush_share_last_3`
- `targets_last_3`
- `carries_last_3`
- `receptions_last_3`
- `air_yards_last_3`
- `red_zone_opportunities_last_3`
- `high_value_touches_last_3`
- `usage_trend_score`
- `role_growth_score`

Efficiency and signal:

- `yards_per_target`
- `yards_per_carry`
- `yards_per_reception`
- `catch_rate`
- `td_dependency_score`
- `expected_vs_actual_signal`
- `fraud_risk_score`
- `breakout_score`

Matchup and environment:

- `game_id`
- `game_environment_json`
- `opponent_fantasy_points_allowed_proxy`
- `matchup_score`
- `streamer_score`
- `schedule_context_json`

Pigskin context:

- `pigskin_rank_overall`
- `pigskin_rank_position`
- `pigskin_tier`
- `pigskin_projection`
- `pigskin_confidence`
- `rank_vs_market_gap`
- `pigskin_summary`

Evidence:

- `candidate_reason`
- `evidence_json`
- `counterargument`
- `snark_hook`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

## Source Rules

Allowed inputs inside the materializer:

- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`
- `analytics_pigskin_rankings`
- `analytics_fraud_watch`
- `analytics_game_environment`
- `dim_players_current`
- `player_identity_bridge`
- `sleeper_rosters`
- `sleeper_roster_players`
- `sleeper_available_players`
- `sleeper_players_current`
- `realtime_player_news`
- `scoring_profiles`

`sleeper_rosters`, `sleeper_roster_players`, and `sleeper_available_players` are allowed only inside this controlled mart-building layer. They should not be exposed directly to UI or Pigskin.

## Global Versus League-Specific Rows

When no `league_id` is supplied, the materializer creates global candidates with `league_id IS NULL`. Roster availability is represented as global `rostered_rate`; league-specific availability fields are null or flagged.

When `league_id` is supplied and Sleeper snapshots exist, the materializer creates league-specific rows with `available_in_league_flag` and `rostered_in_league_flag`.

## Freshness And Missing Data

`source_freshness_json` stores source table existence, row count, and BigQuery table modified timestamps captured by the materializer.

Common missing-data flags:

- `missing_canonical_player_id_internal`
- `missing_sleeper_player_id`
- `missing_rostered_rate`
- `missing_league_availability`
- `missing_model_run_id`
- `missing_pigskin_ranking_context`
- `missing_game_environment`
- `missing_fraud_context`
- `missing_sleeper_rosters_source`
- `missing_sleeper_roster_players_source`
- `missing_sleeper_available_players_source`
- `temporary_source_key_identity`

## Validation

Validation files:

- `051_compat_sleeper_watch_candidates_grain.sql`
- `052_compat_sleeper_watch_candidates_recent_rows_exist.sql`
- `053_compat_sleeper_watch_candidates_identity_coverage.sql`
- `054_compat_sleeper_watch_candidates_scoring_profiles_exist.sql`
- `055_compat_sleeper_watch_candidates_model_run_join.sql`
- `056_compat_sleeper_watch_candidates_candidate_scores_not_null.sql`
- `057_compat_sleeper_watch_candidates_missing_flags_exist.sql`
- `058_compat_sleeper_watch_candidates_no_raw_ui_dependency.sql`

## Future Wiring

Future Streamlit wiring should:

1. Add `USE_COMPAT_SLEEPER_WATCH=false`.
2. Use [src/sleeper_watch.py](../../src/sleeper_watch.py).
3. Keep the current UI path as fallback until live validation passes.
4. Remove direct UI reads from `weekly_metrics`, `sleeper_rosters`, and `sleeper_roster_players` only after parity is confirmed.
