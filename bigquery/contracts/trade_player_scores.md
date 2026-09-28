# trade_player_scores Contract

Migration SQL: [bigquery/migrations/0025__trade_analyzer_score_v0.sql](../migrations/0025__trade_analyzer_score_v0.sql)

Spec: [docs/rebuild/trade-analyzer-scoring-model-v0.md](../../docs/rebuild/trade-analyzer-scoring-model-v0.md)

## Purpose

Stores deterministic Trade Analyzer score rows for the v0 scoring model. This is an output table populated by a future bounded builder, not by Streamlit request-time work.

## Grain

One row per:

- `model_version`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `player_id`

`score_run_id` identifies the materialization run. Multiple `model_version` values may coexist for backtesting and comparison.

## Required Fields

Identity and context:

- `score_run_id`
- `model_run_id`
- `model_version`
- `player_id`
- `player_name`
- `normalized_name`
- `position`
- `team`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

Value and component scores:

- `current_market_value`
- `projected_3_year_value`
- `market_score`
- `projection_score`
- `recent_production_score`
- `role_usage_score`
- `positional_scarcity_score`
- `efficiency_score`
- `normalized_risk_score`
- `fraud_score`
- `confidence_score`
- `trade_score`
- `score_tier`

Metadata:

- `source_freshness_json`
- `missing_flags_json`
- `component_json`
- `ranking_version`
- `feature_config_version_id`
- `created_by`
- `created_at`

## Score Range Rules

- Component scores use a `0` to `100` range unless explicitly noted.
- `market_score`, `projection_score`, `recent_production_score`, `role_usage_score`, `positional_scarcity_score`, `efficiency_score`, `fraud_score`, `confidence_score`, and `trade_score` use `0` to `100` where applicable.
- `normalized_risk_score` is the exception. It uses a `0.00` to `1.00` range where higher means more downside risk.
- `normalized_risk_score` is used by the formula as `risk_adjustment = -10 * normalized_risk_score`.
- `fraud_score` uses a `0` to `100` range where higher means more fraud or overperformance risk.
- `confidence_score` uses a `0` to `100` range.
- `trade_score` uses a `0` to `100` range.
- Missing or stale inputs must be represented in `missing_flags_json` and `source_freshness_json`.

## Source Rules

Future builders may read curated marts, projection outputs, compatibility views, packet tables, and backtest outputs. Builders must not expose raw/source tables to Streamlit or Pigskin.

Allowed builder inputs include:

- `compat_trade_assets_current`
- `compat_trade_player_history`
- `projection_rankings_current`
- `projections_player_weekly`
- `projections_player_ros`
- `projections_player_dynasty`
- `analytics_player_fantasy_points_by_profile`
- `analytics_player_weekly_truth`
- `analytics_fraud_watch`
- `fraud_watch_packets`
- `backtest_result_summary`
- `backtest_result_player_week`

Forbidden UI and Pigskin-visible inputs include:

- `weekly_metrics`
- `play_by_play`
- `market_values`
- raw NGS, FTN, snap, injury, schedule, roster, and Sleeper source tables
- arbitrary SQL tools

## Runtime Rules

- Streamlit must not write this table from request-time UI.
- Cloud Run Jobs or an explicit operator-run materializer should populate this table.
- Production flags remain default off until separately approved.
- No LLM calls are required or allowed to compute deterministic score values.

## Validation

Validation SQL:

- `150_trade_player_scores_grain.sql`
- `151_trade_player_scores_trade_score_range.sql`
- `152_trade_player_scores_component_score_range.sql`
- `153_trade_player_scores_confidence_range.sql`
- `154_trade_player_scores_required_json_fields.sql`
- `155_trade_player_scores_missing_flags_exist.sql`
- `156_trade_player_scores_source_freshness_exists.sql`
- `160_trade_player_scores_identity_coverage.sql`
