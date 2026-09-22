-- Ranking formula backtest foundation.
-- Additive schema-only migration. No candidate formulas or backtest rows are inserted.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_candidates` (
    candidate_id STRING NOT NULL,
    formula_set_id STRING,
    formula_name STRING NOT NULL,
    formula_version STRING NOT NULL,
    position STRING NOT NULL,
    formula_json STRING NOT NULL,
    feature_allowlist_json STRING NOT NULL,
    target_definition_json STRING NOT NULL,
    source_requirements_json STRING NOT NULL,
    status STRING NOT NULL,
    notes STRING,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY position, formula_version, status, candidate_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_runs` (
    backtest_run_id STRING NOT NULL,
    formula_set_id STRING,
    formula_version STRING NOT NULL,
    candidate_count INT64 NOT NULL,
    season_start INT64 NOT NULL,
    season_end INT64 NOT NULL,
    week_start INT64,
    week_end INT64,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    target_definition_json STRING NOT NULL,
    input_tables_json STRING NOT NULL,
    dry_run BOOL NOT NULL,
    status STRING NOT NULL,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message STRING,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY formula_version, status, backtest_run_id, formula_set_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_results` (
    backtest_run_id STRING NOT NULL,
    candidate_id STRING NOT NULL,
    formula_set_id STRING,
    formula_version STRING NOT NULL,
    position STRING NOT NULL,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    player_id_internal STRING NOT NULL,
    player_name STRING,
    team STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    predicted_score FLOAT64,
    predicted_rank_position INT64,
    actual_points FLOAT64,
    actual_rank_position INT64,
    target_name STRING NOT NULL,
    target_hit BOOL,
    win_rate FLOAT64,
    feature_values_json STRING NOT NULL,
    result_json STRING NOT NULL,
    missing_flags_json STRING NOT NULL,
    source_freshness_json STRING NOT NULL,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY backtest_run_id, position, scoring_profile_id, player_id_internal;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_candidate_summaries` (
    backtest_run_id STRING NOT NULL,
    candidate_id STRING NOT NULL,
    formula_version STRING NOT NULL,
    position STRING NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    target_name STRING NOT NULL,
    sample_size INT64 NOT NULL,
    pairwise_win_rate FLOAT64,
    top_n_hit_rate FLOAT64,
    rank_correlation FLOAT64,
    mean_absolute_error FLOAT64,
    regret_score FLOAT64,
    actual_points_captured_rate FLOAT64,
    missing_input_rate FLOAT64,
    metric_json STRING NOT NULL,
    missing_flags_json STRING NOT NULL,
    source_freshness_json STRING NOT NULL,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY backtest_run_id, position, scoring_profile_id, candidate_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_champions` (
    champion_id STRING NOT NULL,
    formula_set_id STRING NOT NULL,
    position STRING NOT NULL,
    candidate_id STRING NOT NULL,
    formula_version STRING NOT NULL,
    backtest_run_id STRING,
    champion_reason STRING,
    metric_name STRING NOT NULL,
    metric_value FLOAT64,
    season_start INT64,
    season_end INT64,
    week_start INT64,
    week_end INT64,
    active BOOL NOT NULL,
    selected_by STRING,
    selected_at TIMESTAMP NOT NULL,
    notes STRING
)
PARTITION BY DATE(selected_at)
CLUSTER BY formula_set_id, position, active, candidate_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_sets` (
    formula_set_id STRING NOT NULL,
    formula_set_name STRING NOT NULL,
    formula_set_version STRING NOT NULL,
    qb_candidate_id STRING,
    rb_candidate_id STRING,
    wr_candidate_id STRING,
    te_candidate_id STRING,
    status STRING NOT NULL,
    description STRING,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY status, formula_set_version, formula_set_id;
