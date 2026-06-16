-- Deterministic show content brief tables.
-- Additive schema-only migration. No briefs are generated, backfilled, renamed, or deleted.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.content_brief_runs` (
    content_brief_run_id STRING NOT NULL,
    brief_type STRING NOT NULL,
    model_run_id STRING,
    season INT64 NOT NULL,
    week INT64,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    status STRING NOT NULL,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message STRING,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY content_brief_run_id, brief_type, status, model_run_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs` (
    content_brief_id STRING NOT NULL,
    content_brief_run_id STRING NOT NULL,
    brief_type STRING NOT NULL,
    title STRING NOT NULL,
    season INT64 NOT NULL,
    week INT64,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    model_run_id STRING,
    brief_json STRING NOT NULL,
    brief_text STRING NOT NULL,
    token_estimate INT64 NOT NULL,
    source_freshness_json STRING,
    missing_data_flags STRING,
    review_status STRING NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY content_brief_run_id, brief_type, review_status, season;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.content_brief_items` (
    content_brief_id STRING NOT NULL,
    item_id STRING NOT NULL,
    item_type STRING NOT NULL,
    item_order INT64 NOT NULL,
    player_id_internal STRING,
    claim_id STRING,
    trade_review_id STRING,
    packet_id STRING,
    title STRING NOT NULL,
    claim STRING,
    evidence_summary STRING,
    counterargument STRING,
    snark_hook STRING,
    confidence_score FLOAT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY content_brief_id, item_type, item_order;
