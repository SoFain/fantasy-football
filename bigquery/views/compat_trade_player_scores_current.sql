-- Compatibility view for Trade Analyzer score reads.
-- Streamlit and Pigskin-visible helpers should read this view only.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_player_scores_current` AS
SELECT
    player_id,
    player_id AS player_id_internal,
    player_name,
    normalized_name,
    position,
    team,
    season,
    week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    current_market_value,
    projected_3_year_value,
    market_score,
    projection_score,
    recent_production_score,
    role_usage_score,
    positional_scarcity_score,
    efficiency_score,
    normalized_risk_score,
    fraud_score,
    confidence_score,
    trade_score,
    score_tier,
    source_freshness_json,
    missing_flags_json,
    component_json,
    model_version,
    model_run_id,
    ranking_version,
    feature_config_version_id,
    score_run_id,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores_current`;
