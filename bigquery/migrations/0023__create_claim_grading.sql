-- Deterministic claim grading and accountability scoreboards.
-- Additive schema-only migration. No claim data is graded, backfilled, renamed, or deleted.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.claim_grading_runs` (
    claim_grading_run_id STRING NOT NULL,
    grading_name STRING,
    grading_version STRING NOT NULL,
    season INT64,
    week INT64,
    model_run_id STRING,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    status STRING NOT NULL,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message STRING,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY claim_grading_run_id, status, model_run_id, grading_version;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.claim_grades` (
    claim_grading_run_id STRING NOT NULL,
    claim_id STRING NOT NULL,
    source_id STRING NOT NULL,
    source_name STRING NOT NULL,
    claim_type STRING NOT NULL,
    claim_direction STRING,
    time_horizon STRING NOT NULL,
    primary_player_id_internal STRING,
    season INT64 NOT NULL,
    week INT64,
    evaluation_window_id STRING NOT NULL,
    actual_points FLOAT64,
    actual_rank_overall INT64,
    actual_rank_position INT64,
    pigskin_projection_at_claim FLOAT64,
    pigskin_rank_at_claim INT64,
    market_projection_at_claim FLOAT64,
    market_rank_at_claim INT64,
    claim_accuracy_score FLOAT64,
    pigskin_accuracy_score FLOAT64,
    market_accuracy_score FLOAT64,
    meatbag_delta FLOAT64,
    model_delta FLOAT64,
    verdict STRING NOT NULL,
    confidence_score FLOAT64,
    grade_json STRING,
    evidence_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY claim_grading_run_id, source_id, verdict, claim_type;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.claim_source_scorecards` (
    claim_grading_run_id STRING NOT NULL,
    source_id STRING NOT NULL,
    source_name STRING NOT NULL,
    source_type STRING,
    season INT64,
    week INT64,
    claim_count INT64 NOT NULL,
    graded_count INT64 NOT NULL,
    average_claim_accuracy FLOAT64,
    average_meatbag_delta FLOAT64,
    pigskin_win_rate FLOAT64,
    market_win_rate FLOAT64,
    good_take_count INT64 NOT NULL,
    wrong_count INT64 NOT NULL,
    fraud_count INT64 NOT NULL,
    galaxy_brain_count INT64 NOT NULL,
    scorecard_json STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY claim_grading_run_id, source_id, source_type;
