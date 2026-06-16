-- Deterministic trade review packet tables.
-- Additive schema-only migration. Data is written by src/trade_review_packets.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_requests` (
    trade_review_id STRING NOT NULL,
    model_run_id STRING,
    request_source STRING,
    league_id STRING,
    roster_id STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    side_a_json STRING,
    side_b_json STRING,
    request_context_json STRING,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    status STRING NOT NULL,
    error_message STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY scoring_profile_id, league_type_id, roster_format_id, status;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets` (
    trade_review_id STRING NOT NULL,
    model_run_id STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    league_id STRING,
    roster_id STRING,
    side_a_value FLOAT64,
    side_b_value FLOAT64,
    side_a_short_term_value FLOAT64,
    side_b_short_term_value FLOAT64,
    side_a_ros_value FLOAT64,
    side_b_ros_value FLOAT64,
    side_a_dynasty_value FLOAT64,
    side_b_dynasty_value FLOAT64,
    side_a_risk_score FLOAT64,
    side_b_risk_score FLOAT64,
    value_delta FLOAT64,
    recommended_winner STRING,
    confidence_score FLOAT64,
    packet_json STRING,
    packet_text STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(updated_at)
CLUSTER BY scoring_profile_id, league_type_id, roster_format_id, recommended_winner;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packet_players` (
    trade_review_id STRING NOT NULL,
    side STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    market_value FLOAT64,
    pigskin_rank_overall INT64,
    pigskin_rank_position INT64,
    pigskin_tier STRING,
    recent_points_per_game FLOAT64,
    short_term_value FLOAT64,
    ros_value FLOAT64,
    dynasty_value FLOAT64,
    risk_score FLOAT64,
    evidence_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY trade_review_id, side, player_id_internal, position;
