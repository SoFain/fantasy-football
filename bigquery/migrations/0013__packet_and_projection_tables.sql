-- Packet and projection tables for Phase 2 precomputations.
-- Data populated by src/materialize_packets.py.

-- 1. mart_trade_review_packets
CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_trade_review_packets` (
    packet_id STRING NOT NULL,
    model_run_id STRING,
    proposal_id STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    side_a_assets_json STRING,
    side_b_assets_json STRING,
    analysis_json STRING,
    verdict STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(updated_at)
CLUSTER BY scoring_profile_id, league_type_id, roster_format_id;

-- 2. mart_fraud_sleeper_packets
CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_fraud_sleeper_packets` (
    packet_id STRING NOT NULL,
    model_run_id STRING,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    candidates_json STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2030, 1))
CLUSTER BY season, week, scoring_profile_id;

-- 3. mart_projection_tables
CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_projection_tables` (
    player_id_internal STRING NOT NULL,
    source_player_key STRING,
    model_run_id STRING,
    scoring_profile_id STRING NOT NULL,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    projected_points FLOAT64,
    projection_metadata_json STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2030, 1))
CLUSTER BY player_id_internal, scoring_profile_id, season, week;
