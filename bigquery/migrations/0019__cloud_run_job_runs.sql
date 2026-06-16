-- Cloud Run Job execution metadata.
-- Additive migration. Data is written by src/job_runner.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs` (
    job_run_id STRING NOT NULL,
    job_name STRING NOT NULL,
    job_type STRING NOT NULL,
    cloud_run_job_name STRING,
    cloud_run_execution_name STRING,
    model_run_id STRING,
    feature_config_version_id STRING,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    project_id STRING,
    dataset_id STRING,
    season INT64,
    week INT64,
    league_id STRING,
    status STRING NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_seconds FLOAT64,
    row_count INT64,
    bytes_processed INT64,
    source_freshness_snapshot_id STRING,
    error_message STRING,
    log_url STRING,
    created_by STRING,
    metadata_json STRING
)
PARTITION BY DATE(started_at)
CLUSTER BY job_name, status, season, week;
