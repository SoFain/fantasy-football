-- Current player role usage metrics view.
-- Reads only derived feature marts, not raw/source tables.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.player_role_usage_metrics_current` AS
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
    snap_share,
    CAST(NULL AS FLOAT64) AS route_share,
    target_share,
    air_yards_share,
    wopr,
    carry_share,
    opportunity_share,
    TO_JSON_STRING(STRUCT(red_zone_targets, red_zone_carries, red_zone_touches)) AS red_zone_role,
    high_value_touches,
    'needs_history' AS trend_direction,
    CAST(NULL AS FLOAT64) AS role_volatility,
    injury_status AS injury_summary,
    depth_chart_role AS depth_summary,
    source_freshness_json,
    CONCAT(COALESCE(missing_data_flags, '[]'), ';route_share_requires_true_route_source') AS missing_data_flags,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY player_id_internal, scoring_profile_id, league_type_id, roster_format_id
    ORDER BY season DESC, week DESC, created_at DESC
) = 1;
