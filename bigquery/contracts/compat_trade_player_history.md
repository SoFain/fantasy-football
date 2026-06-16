# compat_trade_player_history Contract

SQL:

- [bigquery/migrations/0007__promote_compat_trade_player_history.sql](../migrations/0007__promote_compat_trade_player_history.sql)
- [bigquery/views/compat_trade_player_history.sql](../views/compat_trade_player_history.sql)

Helper:

- [src/trade_history.py](../../src/trade_history.py)

## Purpose

Production compatibility layer for Trade Lab player history in `app.py:3147-3155`.

This object replaces raw `weekly_metrics` history with a curated player-week packet that combines scoring-profile-aware fantasy points, weekly role evidence, EPA splits, Pigskin ranking context, identity, and game environment.

`app.py` is not wired to this object by default yet. Current Streamlit runtime behavior remains unchanged until a later feature-flagged migration.

## Grain

One row per player, source player key, season, week, and scoring profile.

Expected key:

- `COALESCE(player_id_internal, source_player_key)`
- `source_player_key`
- `season`
- `week`
- `scoring_profile_id`

Validation:

- [bigquery/validations/022_compat_trade_player_history_grain.sql](../validations/022_compat_trade_player_history_grain.sql)

## Sources

Allowed sources:

- `analytics_player_fantasy_points_by_profile`
- `analytics_player_weekly_truth`
- `player_identity_bridge`
- `analytics_pigskin_rankings`
- `analytics_game_environment`

Forbidden direct source:

- `weekly_metrics`

Validation:

- [bigquery/validations/023_compat_trade_player_history_no_raw_weekly_metrics_reference.sql](../validations/023_compat_trade_player_history_no_raw_weekly_metrics_reference.sql)

## Required Fields

Identity:

- `player_id_internal`
- `source_player_key`
- `player_display_name`
- `normalized_name`
- `position`
- `team`
- `opponent`

Time and scoring:

- `season`
- `week`
- `scoring_profile_id`
- `total_fantasy_points`
- `passing_points`
- `rushing_points`
- `receiving_points`
- `reception_points`
- `turnover_points`
- `bonus_points`
- `fantasy_points_ppr`
- `fantasy_points_half_ppr`
- `fantasy_points_standard`

Role and usage:

- `snap_share`
- `targets`
- `receptions`
- `carries`
- `target_share`
- `rush_share`
- `air_yards`
- `air_yard_share`
- `red_zone_opportunities`
- `high_value_touches`

Production:

- `passing_yards`
- `passing_tds`
- `interceptions`
- `rushing_yards`
- `rushing_tds`
- `receiving_yards`
- `receiving_tds`
- `yards_per_carry`
- `yards_per_target`
- `yards_per_reception`
- `catch_rate`

Evidence packets:

- `epa_summary_json`
- `qb_split_json`
- `game_environment_json`
- `opponent_context_json`

Ranking context:

- `model_run_id`
- `ranking_version`
- `pigskin_rank_overall`
- `pigskin_rank_position`
- `pigskin_tier`

Lineage:

- `recency_order`
- `source_freshness_json`
- `missing_data_flags`
- `refreshed_at`

## Missing Data Rules

Do not backfill unknown evidence with generic box-score data.

Temporary nulls are allowed when flagged:

- `missing_player_id_internal`
- `missing_truth_row`
- `missing_snap_share`
- `missing_air_yards`
- `missing_red_zone_opportunities`
- `missing_game_environment`
- `missing_pigskin_ranking_context`
- `missing_routes_proxy`
- `missing_snaps`
- `scoring_missing_data_flags_present`

Known temporary nulls:

- `snaps`
- `routes_proxy`
- `opponent_context_json`
- `pigskin_rank_overall`

## Validation Set

- [022 grain](../validations/022_compat_trade_player_history_grain.sql)
- [023 no raw weekly_metrics reference](../validations/023_compat_trade_player_history_no_raw_weekly_metrics_reference.sql)
- [024 recent rows exist](../validations/024_compat_trade_player_history_recent_rows_exist.sql)
- [025 scoring profiles exist](../validations/025_compat_trade_player_history_scoring_profiles_exist.sql)
- [026 identity coverage](../validations/026_compat_trade_player_history_identity_coverage.sql)
- [027 score sanity](../validations/027_compat_trade_player_history_no_absurd_scores.sql)

## Helper Contract

`src/trade_history.py` exposes:

- `get_trade_player_history()`
- `resolve_trade_player_lookup()`
- `build_trade_player_history_query()`
- `build_trade_player_lookup_query()`

Rules:

- Query only `compat_trade_player_history`.
- Pass player values and scoring profiles as BigQuery query parameters.
- Build table identifiers only from trusted project and dataset config.
- Cap history limits at `100`.
- Return an empty dataframe or list for missing players instead of raising a fake-answer path.

## Runtime Status

Not wired into `app.py` by default.

The current Trade Lab still uses existing code until a future feature-flagged UI migration replaces its raw history query with this compatibility object.
