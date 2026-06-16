-- Versioned deterministic projection output tables.
-- Additive schema-only migration plus idempotent baseline projection config seeds.
-- Data is written by src/projection_engine.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_weekly` (
    model_run_id STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    opponent STRING,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    projection_horizon STRING NOT NULL,
    projected_points_mean FLOAT64,
    projected_points_median FLOAT64,
    projected_points_floor FLOAT64,
    projected_points_ceiling FLOAT64,
    projected_stat_json STRING,
    usage_projection_json STRING,
    efficiency_projection_json STRING,
    touchdown_projection_json STRING,
    confidence_score FLOAT64,
    risk_score FLOAT64,
    role_score FLOAT64,
    trend_score FLOAT64,
    fraud_risk_score FLOAT64,
    breakout_score FLOAT64,
    replacement_value FLOAT64,
    rank_source STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY model_run_id, scoring_profile_id, roster_format_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_ros` (
    model_run_id STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    as_of_season INT64 NOT NULL,
    as_of_week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    projection_horizon STRING NOT NULL,
    remaining_games INT64,
    projected_points_total FLOAT64,
    projected_points_per_game FLOAT64,
    projected_points_floor FLOAT64,
    projected_points_ceiling FLOAT64,
    projected_games_played FLOAT64,
    projected_stat_json STRING,
    value_json STRING,
    confidence_score FLOAT64,
    risk_score FLOAT64,
    role_score FLOAT64,
    trend_score FLOAT64,
    replacement_value FLOAT64,
    rank_source STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(as_of_season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY model_run_id, scoring_profile_id, roster_format_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_dynasty` (
    model_run_id STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    as_of_season INT64 NOT NULL,
    as_of_week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    projection_horizon STRING NOT NULL,
    year_1_value FLOAT64,
    year_2_value FLOAT64,
    year_3_value FLOAT64,
    total_dynasty_value FLOAT64,
    age_curve_adjustment FLOAT64,
    position_lifecycle_adjustment FLOAT64,
    rookie_or_prospect_adjustment FLOAT64,
    contract_or_team_stability_adjustment FLOAT64,
    projected_stat_json STRING,
    value_json STRING,
    confidence_score FLOAT64,
    risk_score FLOAT64,
    role_score FLOAT64,
    trend_score FLOAT64,
    rank_source STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(as_of_season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY model_run_id, scoring_profile_id, roster_format_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current` (
    model_run_id STRING NOT NULL,
    projection_horizon STRING NOT NULL,
    player_id_internal STRING,
    display_name STRING,
    position STRING,
    team STRING,
    season INT64,
    week INT64,
    as_of_season INT64,
    as_of_week INT64,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    rank_overall INT64,
    rank_position INT64,
    tier STRING,
    projected_points_or_value FLOAT64,
    replacement_value FLOAT64,
    confidence_score FLOAT64,
    risk_score FLOAT64,
    rank_source STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY model_run_id, scoring_profile_id, roster_format_id, position;

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.feature_config_versions` target
USING (
    SELECT
        'baseline_weekly_v1' AS feature_config_version_id,
        'baseline_weekly_v1' AS config_name,
        'baseline_projection_engine' AS model_name,
        'weekly' AS projection_horizon,
        '{"recent_points_weight":0.52,"profile_points_weight":0.18,"pigskin_projection_weight":0.12,"role_weight":0.08,"trend_weight":0.05,"fraud_penalty_weight":0.03,"breakout_weight":0.02}' AS config_json_text,
        'Deterministic weekly projection baseline. No ML or LLM.' AS notes
    UNION ALL
    SELECT
        'baseline_ros_v1',
        'baseline_ros_v1',
        'baseline_projection_engine',
        'ros',
        '{"weekly_baseline_weight":0.70,"role_stability_weight":0.12,"trend_weight":0.08,"risk_penalty_weight":0.06,"format_weight":0.04}',
        'Deterministic rest-of-season projection baseline. No ML or LLM.'
    UNION ALL
    SELECT
        'baseline_dynasty_v1',
        'baseline_dynasty_v1',
        'baseline_projection_engine',
        'dynasty',
        '{"year_1_weight":1.00,"year_2_weight":0.65,"year_3_weight":0.45,"age_curve_weight":0.18,"market_value_weight":0.15,"role_weight":0.10,"tier_weight":0.07}',
        'Deterministic dynasty projection baseline. No ML or LLM.'
) source
ON target.feature_config_version_id = source.feature_config_version_id
WHEN NOT MATCHED THEN
    INSERT (
        feature_config_version_id,
        config_name,
        model_name,
        projection_horizon,
        config_json,
        created_by,
        created_at,
        published_at,
        archived_at,
        active,
        notes
    )
    VALUES (
        source.feature_config_version_id,
        source.config_name,
        source.model_name,
        source.projection_horizon,
        PARSE_JSON(source.config_json_text),
        'migration_0018',
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        NULL,
        TRUE,
        source.notes
    );
