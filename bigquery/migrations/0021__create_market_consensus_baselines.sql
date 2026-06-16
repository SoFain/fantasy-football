-- Source-agnostic market and consensus baseline layer.
-- Additive schema-only migration. No source data is scraped, backfilled, renamed, or deleted.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_sources` (
    source_id STRING NOT NULL,
    source_name STRING NOT NULL,
    source_type STRING NOT NULL,
    access_method STRING NOT NULL,
    license_notes STRING,
    automated_allowed BOOL NOT NULL,
    active BOOL NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY source_id, source_type, access_method, active;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_snapshots` (
    snapshot_id STRING NOT NULL,
    source_id STRING NOT NULL,
    snapshot_type STRING NOT NULL,
    snapshot_date DATE NOT NULL,
    snapshot_timestamp TIMESTAMP NOT NULL,
    season INT64 NOT NULL,
    week INT64,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    source_file_uri STRING,
    source_url STRING,
    ingested_by STRING,
    ingested_at TIMESTAMP NOT NULL,
    row_count INT64 NOT NULL,
    checksum STRING,
    notes STRING
)
PARTITION BY snapshot_date
CLUSTER BY source_id, snapshot_type, season, week;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_player_values` (
    snapshot_id STRING NOT NULL,
    source_id STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    source_player_name STRING,
    display_name STRING,
    position STRING,
    team STRING,
    season INT64 NOT NULL,
    week INT64,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    rank_overall INT64,
    rank_position INT64,
    tier STRING,
    projected_points FLOAT64,
    market_value FLOAT64,
    adp FLOAT64,
    prop_market STRING,
    prop_line FLOAT64,
    prop_over_odds FLOAT64,
    prop_under_odds FLOAT64,
    confidence FLOAT64,
    match_method STRING,
    source_payload_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY source_id, snapshot_id, scoring_profile_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_baseline_current` (
    source_id STRING NOT NULL,
    snapshot_id STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    season INT64 NOT NULL,
    week INT64,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    rank_overall INT64,
    rank_position INT64,
    projected_points FLOAT64,
    market_value FLOAT64,
    adp FLOAT64,
    baseline_type STRING NOT NULL,
    match_method STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY source_id, baseline_type, scoring_profile_id, position;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week`
ADD COLUMN IF NOT EXISTS market_source_id STRING,
ADD COLUMN IF NOT EXISTS market_snapshot_id STRING,
ADD COLUMN IF NOT EXISTS market_rank_overall INT64,
ADD COLUMN IF NOT EXISTS market_rank_position INT64,
ADD COLUMN IF NOT EXISTS market_projected_points FLOAT64,
ADD COLUMN IF NOT EXISTS market_value FLOAT64,
ADD COLUMN IF NOT EXISTS market_adp FLOAT64,
ADD COLUMN IF NOT EXISTS market_absolute_error FLOAT64,
ADD COLUMN IF NOT EXISTS market_rank_error_overall INT64,
ADD COLUMN IF NOT EXISTS market_rank_error_position INT64,
ADD COLUMN IF NOT EXISTS model_better_than_market BOOL;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_summary`
ADD COLUMN IF NOT EXISTS market_source_id STRING,
ADD COLUMN IF NOT EXISTS model_vs_market_mae_delta FLOAT64,
ADD COLUMN IF NOT EXISTS model_vs_market_rank_delta FLOAT64,
ADD COLUMN IF NOT EXISTS model_better_than_market_rate FLOAT64;
