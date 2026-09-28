-- Current deterministic Trade Analyzer score rows.
-- Reads only the Trade Analyzer score output table.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores_current` AS
SELECT
    score_run_id,
    model_run_id,
    model_version,
    player_id,
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
    ranking_version,
    feature_config_version_id,
    created_by,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY
        player_id,
        scoring_profile_id,
        league_type_id,
        roster_format_id
    ORDER BY
        season DESC,
        week DESC,
        created_at DESC,
        model_version DESC,
        score_run_id DESC
) = 1;
