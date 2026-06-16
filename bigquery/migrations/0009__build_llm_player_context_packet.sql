-- LLM-ready player context packet foundation.
-- Additive migration: creates the backing packet mart and replaces the packet view.
-- Data is populated by src/materialize_llm_packets.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_llm_player_context_packet` (
    packet_id STRING NOT NULL,
    model_run_id STRING,
    ranking_version STRING,
    player_id_internal STRING,
    source_player_key STRING,
    display_name STRING,
    position STRING,
    team STRING,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    as_of_season INT64 NOT NULL,
    as_of_week INT64 NOT NULL,
    packet_json STRING,
    packet_text STRING,
    token_estimate INT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(updated_at)
CLUSTER BY player_id_internal, scoring_profile_id, position, team;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet` AS
SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_llm_player_context_packet`;
