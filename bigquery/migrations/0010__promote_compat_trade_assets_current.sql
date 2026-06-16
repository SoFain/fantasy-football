-- Production compatibility foundation for Trade Lab assets.
-- Additive migration: creates the backing mart table and replaces the compat view.
-- Data is populated by src/materialize_trade_assets.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_trade_assets_current` (
    player_id_internal STRING,
    source_player_key STRING,
    sleeper_player_id STRING,
    gsis_id STRING,
    pfr_id STRING,
    display_name STRING,
    normalized_name STRING,
    position STRING,
    fantasy_positions STRING,
    team STRING,
    age FLOAT64,
    rookie_year INT64,
    active_status STRING,
    market_source STRING NOT NULL,
    market_player_id STRING,
    market_player_name STRING,
    market_value INT64,
    market_value_raw FLOAT64,
    market_value_rank_overall INT64,
    market_value_rank_position INT64,
    market_tier STRING,
    market_snapshot_date DATE NOT NULL,
    market_snapshot_timestamp TIMESTAMP,
    market_format_label STRING,
    market_scoring_label STRING,
    market_league_type_label STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    model_run_id STRING,
    ranking_version STRING,
    pigskin_rank_overall INT64,
    pigskin_rank_position INT64,
    pigskin_tier STRING,
    pigskin_projection FLOAT64,
    pigskin_confidence FLOAT64,
    pigskin_risk_score FLOAT64,
    pigskin_breakout_score FLOAT64,
    pigskin_fraud_risk_score FLOAT64,
    recent_fantasy_points_per_game FLOAT64,
    recent_usage_summary_json STRING,
    recent_trend_label STRING,
    position_scarcity_score FLOAT64,
    replacement_value_estimate FLOAT64,
    dynasty_value_placeholder FLOAT64,
    redraft_value_placeholder FLOAT64,
    risk_adjusted_trade_value FLOAT64,
    trade_asset_summary_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY market_snapshot_date
CLUSTER BY player_id_internal, position, team, scoring_profile_id;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current` AS
SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_trade_assets_current`;
