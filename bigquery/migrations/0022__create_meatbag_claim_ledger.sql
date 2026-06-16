-- Manual Meatbag Claim Ledger.
-- Additive schema-only migration. No claims are scraped, backfilled, renamed, or deleted.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.claim_sources` (
    source_id STRING NOT NULL,
    source_name STRING NOT NULL,
    source_type STRING NOT NULL,
    person_name STRING,
    show_name STRING,
    channel_name STRING,
    source_url STRING,
    notes STRING,
    active BOOL NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY source_id, source_type, active;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims` (
    claim_id STRING NOT NULL,
    source_id STRING NOT NULL,
    claim_source_type STRING NOT NULL,
    source_name STRING NOT NULL,
    person_name STRING,
    episode_or_video_title STRING,
    source_url STRING,
    published_at TIMESTAMP,
    claimed_at TIMESTAMP NOT NULL,
    entered_by STRING,
    claim_text STRING NOT NULL,
    claim_type STRING NOT NULL,
    claim_direction STRING,
    time_horizon STRING NOT NULL,
    season INT64 NOT NULL,
    week INT64,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    player_ids_json STRING,
    team_ids_json STRING,
    claimed_rank INT64,
    claimed_projection FLOAT64,
    claimed_value FLOAT64,
    confidence_claimed FLOAT64,
    model_run_id_at_claim STRING,
    pigskin_rank_at_claim INT64,
    market_rank_at_claim INT64,
    context_json STRING,
    review_status STRING NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY source_id, claim_type, time_horizon, review_status;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claim_players` (
    claim_id STRING NOT NULL,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING NOT NULL,
    position STRING,
    team STRING,
    player_role_in_claim STRING NOT NULL,
    claimed_rank INT64,
    claimed_projection FLOAT64,
    claimed_value FLOAT64,
    side STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY claim_id, player_role_in_claim, position, player_id_internal;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.claim_evaluation_windows` (
    claim_id STRING NOT NULL,
    evaluation_window_id STRING NOT NULL,
    time_horizon STRING NOT NULL,
    start_season INT64 NOT NULL,
    start_week INT64,
    end_season INT64 NOT NULL,
    end_week INT64,
    evaluation_status STRING NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY claim_id, time_horizon, evaluation_status;
