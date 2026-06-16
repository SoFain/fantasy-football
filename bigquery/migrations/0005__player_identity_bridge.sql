-- Canonical player identity foundation.
-- Additive only: creates identity tables if missing and does not backfill source tables.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge` (
    player_id_internal STRING NOT NULL,
    gsis_id STRING,
    sleeper_player_id STRING,
    pfr_id STRING,
    espn_id STRING,
    yahoo_id STRING,
    nflverse_id STRING,
    fantasypros_id STRING,
    full_name STRING,
    normalized_name STRING,
    display_name STRING,
    first_name STRING,
    last_name STRING,
    position STRING,
    fantasy_positions STRING,
    current_team STRING,
    previous_team STRING,
    active_status STRING,
    rookie_year INT64,
    birth_date DATE,
    source_confidence FLOAT64,
    match_method STRING,
    source_priority STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(updated_at)
CLUSTER BY position, current_team, player_id_internal;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.dim_players_current` (
    player_id_internal STRING NOT NULL,
    display_name STRING,
    full_name STRING,
    normalized_name STRING,
    position STRING,
    fantasy_positions STRING,
    current_team STRING,
    active_status STRING,
    sleeper_player_id STRING,
    gsis_id STRING,
    pfr_id STRING,
    espn_id STRING,
    yahoo_id STRING,
    rookie_year INT64,
    birth_date DATE,
    age FLOAT64,
    source_confidence FLOAT64,
    match_method STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(updated_at)
CLUSTER BY position, current_team, player_id_internal;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_overrides` (
    override_id STRING NOT NULL,
    source STRING NOT NULL,
    source_player_id STRING NOT NULL,
    player_id_internal STRING NOT NULL,
    reason STRING,
    active BOOL NOT NULL,
    created_by STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY active, source, source_player_id, player_id_internal;
