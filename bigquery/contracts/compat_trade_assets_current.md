# compat_trade_assets_current Contract

Migration SQL: [bigquery/migrations/0010__promote_compat_trade_assets_current.sql](../migrations/0010__promote_compat_trade_assets_current.sql)

View SQL: [bigquery/views/compat_trade_assets_current.sql](../views/compat_trade_assets_current.sql)

Materializer: [src/materialize_trade_assets.py](../../src/materialize_trade_assets.py)

Helper: [src/trade_assets.py](../../src/trade_assets.py)

## Purpose

Compatibility layer for `render_value_analyzer.load_market_players`, `app.py:2761-2769`.

This object replaces future direct UI reads from `market_values` with a curated trade asset contract that combines market value, identity, scoring profile, Pigskin ranking context, recent usage, source freshness, and missing-data flags.

## Storage Pattern

- Backing table: `mart_trade_assets_current`
- Compatibility view: `compat_trade_assets_current`

The backing table is precomputed because Trade Lab, trade review packets, Pigskin context tools, and future trade-value projections will repeatedly read the same current asset board.

## Required Grain

One row per:

- `COALESCE(player_id_internal, source_player_key, market_player_id)`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `market_snapshot_date`

## Required Fields

Identity:

- `player_id_internal`
- `source_player_key`
- `sleeper_player_id`
- `gsis_id`
- `pfr_id`
- `display_name`
- `normalized_name`
- `position`
- `fantasy_positions`
- `team`
- `age`
- `rookie_year`
- `active_status`

Market value:

- `market_source`
- `market_player_id`
- `market_player_name`
- `market_value`
- `market_value_raw`
- `market_value_rank_overall`
- `market_value_rank_position`
- `market_tier`
- `market_snapshot_date`
- `market_snapshot_timestamp`
- `market_format_label`
- `market_scoring_label`
- `market_league_type_label`

Context IDs:

- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `model_run_id`
- `ranking_version`

Pigskin ranking context:

- `pigskin_rank_overall`
- `pigskin_rank_position`
- `pigskin_tier`
- `pigskin_projection`
- `pigskin_confidence`
- `pigskin_risk_score`
- `pigskin_breakout_score`
- `pigskin_fraud_risk_score`

Trade context:

- `recent_fantasy_points_per_game`
- `recent_usage_summary_json`
- `recent_trend_label`
- `position_scarcity_score`
- `replacement_value_estimate`
- `dynasty_value_placeholder`
- `redraft_value_placeholder`
- `risk_adjusted_trade_value`
- `trade_asset_summary_json`

Metadata:

- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

## Source Rules

1. `market_values` is a raw FantasyCalc source table. It may be read only by `src/materialize_trade_assets.py`.
2. UI, Pigskin, and helper code must read `compat_trade_assets_current`, not `market_values`.
3. Identity comes from `dim_players_current` and `player_identity_bridge`.
4. Pigskin ranking context comes from `analytics_pigskin_rankings`.
5. Recent scoring and usage context comes from `compat_trade_player_history`.
6. Fraud risk context comes from `analytics_fraud_watch`.
7. Any temporary name-based identity or ranking joins must be flagged in `missing_data_flags`.

## Freshness Behavior

`source_freshness_json` records:

- mart name
- market source table name
- identity sources
- ranking source
- recent history source
- fraud source
- source availability booleans
- `market_snapshot_timestamp`
- `market_snapshot_date`
- mart refresh timestamp

Because the current `market_values` ingestion recreates the table and does not store per-row snapshot timestamps, the materializer uses BigQuery table metadata for `market_snapshot_timestamp` by default.

Refresh cadence:

- August through January: refresh daily, or within 48 hours before current market analysis.
- February through July: refresh manually or weekly when trade-market context is being used.
- Offseason snapshots older than 14 days are warning-level freshness issues, not schema blockers.

Validation `044_compat_trade_assets_current_recent_market_snapshot.sql` follows that policy. It returns no rows when the snapshot is within the expected window. If the snapshot is stale, it returns a review row that the validation runner reports as a warning instead of a hard failure.

Refresh commands:

```powershell
.\venv\Scripts\python.exe -m src.materialize_trade_assets --dry-run
.\venv\Scripts\python.exe -m src.fetch_market_values --dataset fantasy_football_brain
.\venv\Scripts\python.exe -m src.materialize_trade_assets
```

The `fetch_market_values` command calls the external FantasyCalc API. Do not run it from validation unless source refresh has been explicitly authorized.

## Missing Data Flags

The materializer emits JSON array text in `missing_data_flags`.

Expected flags include:

- `missing_player_id_internal`
- `missing_source_player_key`
- `missing_sleeper_player_id`
- `missing_gsis_id`
- `missing_age`
- `missing_market_value`
- `temporary_name_join_identity`
- `missing_pigskin_ranking_context`
- `temporary_name_join_ranking`
- `missing_recent_trade_history`
- `missing_fraud_context`
- `missing_market_values_source`
- `missing_rankings_source`
- `missing_trade_history_source`

## Limitations

- `market_values` currently lacks raw source snapshot columns, format metadata, and provider player IDs.
- `market_player_id` is a normalized synthetic key until ingestion stores provider IDs.
- Dynasty and redraft placeholder values are simple compatibility fields, not final projection model outputs.
- `pigskin_rank_overall` is reserved and currently null until rankings publish an overall board.
- This contract is not wired into Streamlit by default. Future wiring must use a default-off flag such as `USE_COMPAT_TRADE_ASSETS=false`.

## Validation

Validation SQL:

- `043_compat_trade_assets_current_grain.sql`
- `044_compat_trade_assets_current_recent_market_snapshot.sql`
- `045_compat_trade_assets_current_identity_coverage.sql`
- `046_compat_trade_assets_current_market_value_not_null.sql`
- `047_compat_trade_assets_current_model_run_join.sql`
- `048_compat_trade_assets_current_scoring_profiles_exist.sql`
- `049_compat_trade_assets_current_missing_flags_exist.sql`
- `050_compat_trade_assets_current_no_raw_ui_dependency.sql`
