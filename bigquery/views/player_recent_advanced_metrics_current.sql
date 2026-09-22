-- Current player recent advanced metrics view.
-- Reads only derived feature marts, not raw/source tables.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.player_recent_advanced_metrics_current` AS
SELECT
    metric_version,
    feature_run_id,
    season AS as_of_season,
    week AS as_of_week,
    player_id_internal,
    player_name,
    position,
    team,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS season_to_date_metrics_json,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS last_3_metrics_json,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS last_5_metrics_json,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS last_8_metrics_json,
    'needs_history' AS trend_label,
    missing_data_flags AS sample_size_flags,
    source_freshness_json,
    missing_data_flags,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY player_id_internal, scoring_profile_id, league_type_id, roster_format_id
    ORDER BY season DESC, week DESC, created_at DESC
) = 1;
