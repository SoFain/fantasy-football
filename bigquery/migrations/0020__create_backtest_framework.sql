-- First backtest and projection-evaluation framework.
-- Additive schema-only migration. No production data is backfilled or mutated.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_runs` (
    backtest_run_id STRING NOT NULL,
    model_run_id STRING,
    backtest_name STRING,
    backtest_version STRING,
    projection_horizon STRING NOT NULL,
    season_start INT64 NOT NULL,
    season_end INT64 NOT NULL,
    week_start INT64,
    week_end INT64,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    feature_config_version_id STRING,
    source_freshness_snapshot_id STRING,
    status STRING NOT NULL,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message STRING,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY backtest_run_id, model_run_id, status, projection_horizon;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week` (
    backtest_run_id STRING NOT NULL,
    model_run_id STRING,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    projection_horizon STRING NOT NULL,
    projected_points FLOAT64,
    actual_points FLOAT64,
    absolute_error FLOAT64,
    squared_error FLOAT64,
    projected_rank_overall INT64,
    actual_rank_overall INT64,
    projected_rank_position INT64,
    actual_rank_position INT64,
    rank_error_overall INT64,
    rank_error_position INT64,
    projected_floor FLOAT64,
    projected_ceiling FLOAT64,
    actual_inside_range BOOL,
    boom_threshold FLOAT64,
    bust_threshold FLOAT64,
    projected_boom_flag BOOL,
    actual_boom_flag BOOL,
    projected_bust_flag BOOL,
    actual_bust_flag BOOL,
    result_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY backtest_run_id, model_run_id, scoring_profile_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_summary` (
    backtest_run_id STRING NOT NULL,
    model_run_id STRING,
    projection_horizon STRING NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    position STRING,
    season INT64,
    week INT64,
    player_count INT64 NOT NULL,
    mae FLOAT64,
    rmse FLOAT64,
    mean_bias FLOAT64,
    rank_mae_overall FLOAT64,
    rank_mae_position FLOAT64,
    spearman_proxy FLOAT64,
    top_12_hit_rate FLOAT64,
    top_24_hit_rate FLOAT64,
    boom_precision FLOAT64,
    bust_precision FLOAT64,
    range_calibration_rate FLOAT64,
    summary_json STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY backtest_run_id, model_run_id, projection_horizon, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_calibration_bins` (
    backtest_run_id STRING NOT NULL,
    model_run_id STRING,
    projection_horizon STRING NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    position STRING,
    bin_name STRING NOT NULL,
    bin_min FLOAT64,
    bin_max FLOAT64,
    player_count INT64 NOT NULL,
    avg_projected FLOAT64,
    avg_actual FLOAT64,
    avg_error FLOAT64,
    calibration_json STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY backtest_run_id, model_run_id, projection_horizon, position;
