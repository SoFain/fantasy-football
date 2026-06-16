-- Harmless metadata-table migration for future model-run tracking.
-- This does not migrate existing data and does not touch current pipeline tables.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` (
    model_run_id STRING NOT NULL,
    run_type STRING NOT NULL,
    model_name STRING,
    prompt_version STRING,
    code_version STRING,
    source_freshness_json STRING,
    feature_config_version STRING,
    scoring_profile STRING,
    league_type STRING,
    roster_format STRING,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status STRING NOT NULL,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY run_type, scoring_profile, league_type, status;
